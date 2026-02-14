"""
MobilityGraph FastAPI Application
Jakarta Tourism Route Planning API with Semantic Web/RDF backend
"""
import sys
from pathlib import Path
import uuid
import shutil
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request, Response, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import Optional
from pydantic import BaseModel
import folium

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from mobilitygraph.loader import MobilityGraphLoader
from mobilitygraph.graph_builder import GraphBuilder
from mobilitygraph.router import Router
from app.schemas import (
    RouteRequest, RouteResponse, PlaceOfInterest, Region, 
    DataSummary, TransportMode
)
from app.destinations_seed import DESTINATIONS_SEED, get_destination_by_slug, get_all_destinations
from app.fares import haversine_distance
# fare_assistant removed - fare queries handled by fares.py directly
from app.admin.auth import (
    verify_credentials, login_user, logout_user, 
    get_session_from_request, SESSION_COOKIE_NAME
)
from app.admin.crud import (
    add_destination, add_stop, add_edge,
    delete_destination, delete_stop,
    get_custom_destinations, get_custom_stops, export_ttl,
    update_destination, update_stop,
    get_destination_by_slug as get_custom_destination_by_slug,
    get_stop_by_id as get_custom_stop_by_id
)

# Global instances
loader: MobilityGraphLoader = None
graph_builder: GraphBuilder = None
router: Router = None
# fare_assistant module removed


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize RDF graph on startup"""
    global loader, graph_builder, router
    
    print("🚀 Starting MobilityGraph API...")
    
    # Initialize loader
    loader = MobilityGraphLoader()
    loader.load_all_ttl()
    
    # Build graph
    graph_builder = GraphBuilder(loader)
    graph_builder.build_graph()
    
    # Initialize router
    router = Router(graph_builder)
    
    # fare_assistant initialization removed
    
    print("✅ MobilityGraph API ready!")
    
    yield
    
    print("👋 Shutting down MobilityGraph API...")


app = FastAPI(
    title="MobilityGraph API",
    description="Jakarta Tourism Route Planning dengan Semantic Web/RDF",
    version="2.0.0",
    lifespan=lifespan
)

# Mount static files
static_dir = Path(__file__).parent.parent / "static"
if not static_dir.exists():
    static_dir.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Templates
templates_dir = Path(__file__).parent.parent / "templates"
if templates_dir.exists():
    templates = Jinja2Templates(directory=str(templates_dir))
else:
    templates = None


# ==================== PAGE ROUTES ====================

@app.get("/", response_class=HTMLResponse)
async def home(request: Request, destination: Optional[str] = None):
    """Serve the main Route Planner page"""
    if templates:
        return templates.TemplateResponse("index.html", {
            "request": request,
            "preselected_destination": destination
        })
    else:
        return HTMLResponse(content="""
        <html>
            <head><title>MobilityGraph</title></head>
            <body>
                <h1>MobilityGraph API</h1>
                <p>Visit <a href="/docs">/docs</a> for API documentation</p>
            </body>
        </html>
        """)


@app.get("/favorites", response_class=HTMLResponse)
async def favorites_page(request: Request):
    """Serve the Favorites/Destinations page"""
    if templates:
        return templates.TemplateResponse("favorites.html", {"request": request})
    return RedirectResponse(url="/")


@app.get("/stops", response_class=HTMLResponse)
async def stops_page(request: Request):
    """Serve the Stops/Pemberhentian page"""
    if templates:
        return templates.TemplateResponse("stops.html", {"request": request})
    return RedirectResponse(url="/")


@app.get("/about", response_class=HTMLResponse)
async def about_page(request: Request):
    """Serve the About/Tentang Kami page"""
    if templates:
        return templates.TemplateResponse("about.html", {"request": request})
    return RedirectResponse(url="/")


@app.get("/favorites/{slug}", response_class=HTMLResponse)
async def destination_detail_page(request: Request, slug: str):
    """Serve the Destination Detail page"""
    # First check seed data
    destination = get_destination_by_slug(slug)
    
    # If not found in seed, check TTL places
    if not destination:
        pois = loader.get_places_of_interest()
        for poi in pois:
            poi_slug = poi.get("name", "").lower().replace(" ", "-").replace("(", "").replace(")", "")
            if poi_slug == slug:
                destination = {
                    "slug": poi_slug,
                    "name": poi.get("name", ""),
                    "region": poi.get("region", ""),
                    "lat": poi.get("lat", 0),
                    "lon": poi.get("long", 0),
                    "image_url": "https://images.unsplash.com/photo-1555899434-94d1368aa7af?w=800",
                    "category": poi.get("category", ""),
                    "long_description": poi.get("description", ""),
                    "long_history": "",
                    "location": "",
                    "year_established": None,
                    "important_details": []
                }
                break
    
    if not destination:
        raise HTTPException(status_code=404, detail="Destination not found")
    
    if templates:
        return templates.TemplateResponse("detail.html", {
            "request": request,
            "destination": destination
        })
    return RedirectResponse(url="/favorites")


@app.get("/admin/login", response_class=HTMLResponse)
async def admin_login_page(request: Request):
    """Serve the Admin Login page"""
    # Check if already logged in
    session = get_session_from_request(request)
    if session:
        return RedirectResponse(url="/admin")
    
    if templates:
        return templates.TemplateResponse("admin_login.html", {"request": request})
    return HTMLResponse(content="<h1>Admin Login</h1><p>Template not found</p>")


@app.get("/admin", response_class=HTMLResponse)
async def admin_dashboard_page(request: Request):
    """Serve the Admin Dashboard (protected)"""
    session = get_session_from_request(request)
    if not session:
        return RedirectResponse(url="/admin/login")
    
    if templates:
        return templates.TemplateResponse("admin_dashboard.html", {
            "request": request,
            "admin_user": session.get("username")
        })
    return HTMLResponse(content="<h1>Admin Dashboard</h1><p>Template not found</p>")


# ==================== API ENDPOINTS ====================

@app.get("/api/summary")
async def get_summary():
    """Get data summary statistics"""
    summary = loader.get_summary()
    # Add destination count
    summary["destinations_count"] = len(DESTINATIONS_SEED) + len(loader.get_places_of_interest())
    return summary


@app.get("/api/places")
async def get_places():
    """Get all places of interest (tourist destinations)"""
    pois = loader.get_places_of_interest()
    return pois


@app.get("/api/destinations")
async def get_destinations(region: Optional[str] = None, q: Optional[str] = None):
    """Get all destinations (seed + TTL)"""
    # Combine seed data with TTL places
    all_destinations = []
    
    # Add seed destinations
    for dest in DESTINATIONS_SEED:
        all_destinations.append({
            "slug": dest["slug"],
            "name": dest["name"],
            "region": dest["region"],
            "lat": dest["lat"],
            "lon": dest["lon"],
            "image_url": dest["image_url"],
            "category": dest["category"],
            "description": dest.get("long_description", "")[:200] + "...",
            "long_description": dest.get("long_description", ""),
            "year_established": dest.get("year_established")
        })
    
    # Filter by region
    if region:
        all_destinations = [d for d in all_destinations if d["region"] == region]
    
    # Filter by search query
    if q:
        q_lower = q.lower()
        all_destinations = [d for d in all_destinations if q_lower in d["name"].lower()]
    
    return all_destinations


@app.get("/api/regions")
async def get_regions():
    """Get all regions/areas"""
    regions = loader.get_regions()
    return regions


@app.get("/api/modes")
async def get_modes():
    """Get available transport modes"""
    return {
        "modes": [
            {"id": "MRT", "name": "MRT Jakarta", "description": "Mass Rapid Transit"},
            {"id": "LRT", "name": "LRT Jabodebek", "description": "Light Rail Transit"},
            {"id": "TJ", "name": "TransJakarta", "description": "Bus Rapid Transit"},
            {"id": "ALL", "name": "Semua Moda", "description": "Multi-modal (kombinasi)"}
        ]
    }


@app.get("/api/stops")
async def get_stops(mode: Optional[str] = None, limit: int = 100):
    """Get stops, optionally filtered by mode"""
    stops = loader.get_stops(mode)
    return {"stops": stops[:limit], "total": len(stops)}


@app.get("/api/nearest-stops")
async def get_nearest_stops(lat: float, lon: float, limit: int = 3):
    """Get nearest stops to a coordinate"""
    all_stops = loader.get_stops(None)
    
    # Calculate distances
    stops_with_distance = []
    for stop in all_stops:
        stop_lat = float(stop.get("lat", 0))
        stop_lon = float(stop.get("long", 0))
        distance = haversine_distance(lat, lon, stop_lat, stop_lon)
        stops_with_distance.append({
            **stop,
            "distance": distance
        })
    
    # Sort by distance and return top N
    stops_with_distance.sort(key=lambda x: x["distance"])
    return stops_with_distance[:limit]


@app.post("/api/route")
async def find_route_api(request: RouteRequest):
    """
    Find route between stops and/or destinations
    
    - **start**: Starting point (stop ID or coordinates)
    - **selected_places**: List of destination slugs or POI IDs to visit
    - **mode**: Transport mode filter (MRT, LRT, TJ, ALL)
    - **strategy**: 'single' for one destination, 'multi' for itinerary
    """
    from app.fares import calculate_mrt_fare, calculate_lrt_fare, calculate_tj_fare, haversine_distance
    
    # Determine start stop
    if request.start.type == "coord":
        try:
            lat, lon = map(float, request.start.value.split(","))
            mode_filter = request.mode.value if request.mode != TransportMode.ALL else None
            nearest = graph_builder.find_nearest_stop(lat, lon, mode_filter)
            if not nearest:
                raise HTTPException(status_code=404, detail="No stop found near coordinates")
            start_id = nearest["id"]
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid coordinates format. Use 'lat,long'")
    else:
        start_id = request.start.value
    
    # Find route based on strategy
    if not request.selected_places:
        raise HTTPException(status_code=400, detail="No destinations selected")
    
    # Convert destination slugs to end stop IDs
    destination_stops = []
    destination_info = []
    
    for place_id in request.selected_places:
        # Check if it's a seed destination slug
        dest = get_destination_by_slug(place_id)
        if dest:
            # Find nearest stop to destination
            nearest = graph_builder.find_nearest_stop(dest["lat"], dest["lon"])
            if nearest:
                destination_stops.append(nearest["id"])
                destination_info.append({
                    "name": dest["name"],
                    "slug": dest["slug"],
                    "nearest_stop": nearest["id"],
                    "nearest_stop_name": nearest.get("name", nearest["id"]),
                    "lat": dest["lat"],
                    "lon": dest["lon"]
                })
        else:
            # Assume it's a POI ID from TTL
            pois = loader.get_places_of_interest()
            poi = next((p for p in pois if p["id"] == place_id), None)
            if poi:
                nearest = graph_builder.find_nearest_stop(poi["lat"], poi["long"])
                if nearest:
                    destination_stops.append(nearest["id"])
                    destination_info.append({
                        "name": poi.get("name", place_id),
                        "slug": place_id,
                        "nearest_stop": nearest["id"],
                        "nearest_stop_name": nearest.get("name", nearest["id"]),
                        "lat": poi["lat"],
                        "lon": poi["long"]
                    })
    
    if not destination_stops:
        raise HTTPException(status_code=404, detail="No valid destinations found")
    
    # Calculate route to first/all destinations
    all_legs = []
    all_stops_passed = []
    total_distance_km = 0
    total_time_minutes = 0
    total_cost_idr = 0
    all_geometry = []
    transfers = []
    current_stop = start_id
    
    # Walking speed: 4 km/h = 15 min/km (average person)
    WALKING_SPEED_KMH = 4
    
    for i, end_stop in enumerate(destination_stops):
        dest = destination_info[i] if i < len(destination_info) else None
        
        # Case 1: Start stop equals destination's nearest stop
        # Only need to calculate walking from stop to destination
        if current_stop == end_stop:
            if dest:
                # Get current stop coordinates
                current_stop_data = graph_builder.stops_by_id.get(current_stop, {})
                
                # Calculate walking distance to actual destination (haversine returns METERS)
                walk_distance_m = haversine_distance(
                    current_stop_data.get("lat", 0), current_stop_data.get("long", 0),
                    dest["lat"], dest["lon"]
                )
                walk_distance = walk_distance_m / 1000  # Convert meters to km
                
                if walk_distance > 0.03:  # More than 30 meters
                    walk_time = (walk_distance / WALKING_SPEED_KMH) * 60
                    
                    # Add walking leg
                    walking_leg = {
                        "mode": "WALK",
                        "from": current_stop,
                        "from_name": current_stop_data.get("name", current_stop),
                        "to": dest["slug"],
                        "to_name": dest["name"],
                        "distance_km": round(walk_distance, 2),
                        "time_minutes": round(walk_time, 1),
                        "cost_idr": 0,
                        "is_walk": True,
                        "line": "Jalan Kaki"
                    }
                    all_legs.append(walking_leg)
                    
                    # Add start stop to stops passed
                    if current_stop_data.get("name") and current_stop_data["name"] not in all_stops_passed:
                        all_stops_passed.append(current_stop_data["name"])
                    
                    # Add to totals
                    total_distance_km += walk_distance
                    total_time_minutes += walk_time
                    
                    # Add geometry: from stop to destination
                    if current_stop_data.get("lat") and current_stop_data.get("long"):
                        all_geometry.append([current_stop_data["lat"], current_stop_data["long"]])
                    all_geometry.append([dest["lat"], dest["lon"]])
            continue
        
        # Case 2: Normal route - find transit path
        result = router.find_route(current_stop, end_stop, request.mode.value)
        
        if result and "error" not in result:
            # Add geometry
            if result.get("geometry"):
                all_geometry.extend(result["geometry"])
            
            # Process legs
            for leg in result.get("legs", []):
                leg["destination"] = dest["name"] if dest else ""
                all_legs.append(leg)
                
                # Track stops passed
                if leg.get("from_name") and leg["from_name"] not in all_stops_passed:
                    all_stops_passed.append(leg["from_name"])
                if leg.get("to_name") and leg["to_name"] not in all_stops_passed:
                    all_stops_passed.append(leg["to_name"])
            
            # Add to totals
            summary = result.get("summary", {})
            total_distance_km += summary.get("total_distance_km", 0)
            total_time_minutes += summary.get("total_time_minutes", 0)
            total_cost_idr += summary.get("total_cost_idr", 0)
            
            # Get transfers
            if result.get("transfers"):
                transfers.extend(result["transfers"])
            
            # Move to end of this segment
            current_stop = end_stop
        
        # Case 3: Add walking segment from last stop to actual destination
        if dest:
            last_stop_data = graph_builder.stops_by_id.get(current_stop, {})
            
            # Calculate walking distance from last stop to actual destination (haversine returns METERS)
            walk_distance_m = haversine_distance(
                last_stop_data.get("lat", 0), last_stop_data.get("long", 0),
                dest["lat"], dest["lon"]
            )
            walk_distance = walk_distance_m / 1000  # Convert meters to km
            
            if walk_distance > 0.03:  # More than 30 meters
                walk_time = (walk_distance / WALKING_SPEED_KMH) * 60
                
                # Add walking leg
                walking_leg = {
                    "mode": "WALK",
                    "from": current_stop,
                    "from_name": last_stop_data.get("name", current_stop),
                    "to": dest["slug"],
                    "to_name": dest["name"],
                    "distance_km": round(walk_distance, 2),
                    "time_minutes": round(walk_time, 1),
                    "cost_idr": 0,
                    "is_walk": True,
                    "line": "Jalan Kaki"
                }
                all_legs.append(walking_leg)
                
                # Add to totals
                total_distance_km += walk_distance
                total_time_minutes += walk_time
                
                # Add destination coordinates to geometry
                all_geometry.append([dest["lat"], dest["lon"]])
    
    # Get start and end stop info
    start_stop_info = graph_builder.stops_by_id.get(start_id, {})
    end_stop_info = graph_builder.stops_by_id.get(current_stop, {})
    
    # Use destination coordinates for end marker if walking to destination
    final_destination = destination_info[-1] if destination_info else None
    
    # Build response
    response = {
        "summary": {
            "total_distance_km": round(total_distance_km, 2),
            "total_time_minutes": round(total_time_minutes, 1),
            "total_cost_idr": int(total_cost_idr),
            "stops_count": len(all_stops_passed),
            "transfers_count": len(transfers)
        },
        "legs": all_legs,
        "stops_passed": all_stops_passed,
        "transfers": transfers,
        "destinations": destination_info,
        "start_stop": {
            "id": start_id,
            "name": start_stop_info.get("name", start_id),
            "lat": start_stop_info.get("lat"),
            "long": start_stop_info.get("long")
        },
        "end_stop": {
            "id": current_stop,
            "name": end_stop_info.get("name", current_stop),
            "lat": end_stop_info.get("lat"),
            "long": end_stop_info.get("long")
        },
        "final_destination": {
            "name": final_destination["name"] if final_destination else None,
            "lat": final_destination["lat"] if final_destination else None,
            "lon": final_destination["lon"] if final_destination else None
        } if final_destination else None,
        "geometry": all_geometry
    }
    
    return response


@app.get("/api/route/map")
async def get_route_map(
    start_id: str,
    end_id: str,
    mode: str = "ALL"
):
    """Generate Folium map HTML for a route"""
    result = router.find_route(start_id, end_id, mode)
    
    if not result or "error" in result:
        raise HTTPException(status_code=404, detail=result.get("error", "No route found"))
    
    # Create Folium map
    geometry = result.get("geometry", [])
    if not geometry:
        raise HTTPException(status_code=404, detail="No geometry data")
    
    # Center map on route
    center_lat = sum(g[0] for g in geometry) / len(geometry)
    center_long = sum(g[1] for g in geometry) / len(geometry)
    
    m = folium.Map(location=[center_lat, center_long], zoom_start=13)
    
    # Add route line
    folium.PolyLine(
        geometry,
        weight=4,
        color='blue',
        opacity=0.8
    ).add_to(m)
    
    # Add markers
    if geometry:
        # Start marker
        folium.Marker(
            geometry[0],
            popup=result["start_stop"]["name"] if result.get("start_stop") else "Start",
            icon=folium.Icon(color='green', icon='play')
        ).add_to(m)
        
        # End marker
        folium.Marker(
            geometry[-1],
            popup=result["end_stop"]["name"] if result.get("end_stop") else "End",
            icon=folium.Icon(color='red', icon='stop')
        ).add_to(m)
    
    return HTMLResponse(content=m._repr_html_())


class ChatRequest(BaseModel):
    message: str

# /api/chat/fare endpoint removed - fare_assistant module deprecated


@app.get("/api/debug/graph-stats")
async def get_graph_stats():
    """Get graph statistics for debugging"""
    return {
        "nodes": graph_builder.graph.number_of_nodes(),
        "edges": graph_builder.graph.number_of_edges(),
        "stops_loaded": len(graph_builder.stops_by_id)
    }


# ==================== ADMIN API ENDPOINTS ====================

class LoginRequest(BaseModel):
    username: str
    password: str


class DestinationRequest(BaseModel):
    slug: str
    name: str
    region: str
    lat: float
    lon: float
    category: str = "Recreation"
    description: str = ""
    image_url: str = ""


class StopRequest(BaseModel):
    stop_id: str
    name: str
    lat: float
    lon: float
    mode: str = "TJ"


@app.post("/admin/api/login")
async def admin_login(request: Request, response: Response, login_data: LoginRequest):
    """Admin login endpoint"""
    if verify_credentials(login_data.username, login_data.password):
        login_user(response, login_data.username)
        return {"success": True, "message": "Login successful"}
    return JSONResponse(
        status_code=401,
        content={"success": False, "message": "Username atau password salah"}
    )


@app.post("/admin/logout")
async def admin_logout(request: Request, response: Response):
    """Admin logout endpoint"""
    logout_user(request, response)
    return RedirectResponse(url="/admin/login", status_code=303)


@app.post("/admin/api/destination")
async def create_destination(request: Request, dest: DestinationRequest):
    """Create a new destination"""
    session = get_session_from_request(request)
    if not session:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    success = add_destination(
        slug=dest.slug,
        name=dest.name,
        region_id=dest.region,
        lat=dest.lat,
        lon=dest.lon,
        description=dest.description,
        category=dest.category,
        image_url=dest.image_url
    )
    
    if success:
        return {"success": True, "message": "Destination created"}
    raise HTTPException(status_code=500, detail="Failed to create destination")


@app.delete("/admin/api/destination/{slug}")
async def remove_destination(request: Request, slug: str):
    """Delete a destination"""
    session = get_session_from_request(request)
    if not session:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    success = delete_destination(slug)
    return {"success": success}


@app.get("/admin/api/destination/{slug}")
async def get_single_destination(request: Request, slug: str):
    """Get a single custom destination by slug"""
    session = get_session_from_request(request)
    if not session:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    dest = get_custom_destination_by_slug(slug)
    if not dest:
        raise HTTPException(status_code=404, detail="Destination not found")
    
    return dest


class DestinationUpdateRequest(BaseModel):
    name: Optional[str] = None
    region: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None
    category: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None


@app.put("/admin/api/destination/{slug}")
async def update_destination_api(request: Request, slug: str, dest: DestinationUpdateRequest):
    """Update an existing destination"""
    session = get_session_from_request(request)
    if not session:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    success = update_destination(
        slug=slug,
        name=dest.name,
        region_id=dest.region,
        lat=dest.lat,
        lon=dest.lon,
        description=dest.description,
        category=dest.category,
        image_url=dest.image_url
    )
    
    if success:
        return {"success": True, "message": "Destination updated"}
    raise HTTPException(status_code=404, detail="Destination not found")


@app.post("/admin/api/stop")
async def create_stop(request: Request, stop: StopRequest):
    """Create a new stop"""
    session = get_session_from_request(request)
    if not session:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    success = add_stop(
        stop_id=stop.stop_id,
        name=stop.name,
        lat=stop.lat,
        lon=stop.lon,
        mode=stop.mode
    )
    
    if success:
        return {"success": True, "message": "Stop created"}
    raise HTTPException(status_code=500, detail="Failed to create stop")


@app.delete("/admin/api/stop/{stop_id:path}")
async def remove_stop(request: Request, stop_id: str):
    """Delete a stop"""
    session = get_session_from_request(request)
    if not session:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    success = delete_stop(stop_id)
    return {"success": success}


@app.get("/admin/api/stop/{stop_id:path}")
async def get_single_stop(request: Request, stop_id: str):
    """Get a single custom stop by ID"""
    session = get_session_from_request(request)
    if not session:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    stop = get_custom_stop_by_id(stop_id)
    if not stop:
        raise HTTPException(status_code=404, detail="Stop not found")
    
    return stop


class StopUpdateRequest(BaseModel):
    name: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None
    mode: Optional[str] = None


@app.put("/admin/api/stop/{stop_id:path}")
async def update_stop_api(request: Request, stop_id: str, stop: StopUpdateRequest):
    """Update an existing stop"""
    session = get_session_from_request(request)
    if not session:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    success = update_stop(
        stop_id=stop_id,
        name=stop.name,
        lat=stop.lat,
        lon=stop.lon,
        mode=stop.mode
    )
    
    if success:
        return {"success": True, "message": "Stop updated"}
    raise HTTPException(status_code=404, detail="Stop not found")


@app.get("/admin/api/custom-stops")
async def get_admin_custom_stops(request: Request):
    """Get custom stops added by admin"""
    session = get_session_from_request(request)
    if not session:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    return get_custom_stops()


@app.get("/admin/api/export-ttl")
async def export_custom_ttl(request: Request, download: Optional[int] = None):
    """Export custom TTL file"""
    session = get_session_from_request(request)
    if not session:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    ttl_content = export_ttl()
    
    if download:
        return Response(
            content=ttl_content,
            media_type="text/turtle",
            headers={"Content-Disposition": "attachment; filename=custom_routes.ttl"}
        )
    
    return PlainTextResponse(content=ttl_content)


@app.post("/admin/api/upload-image")
async def upload_image(request: Request, file: UploadFile = File(...)):
    """Upload an image file for destinations"""
    session = get_session_from_request(request)
    if not session:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Validate file type
    allowed_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Format file tidak valid. Gunakan JPG, PNG, GIF, atau WebP")
    
    # Create uploads directory if it doesn't exist
    uploads_dir = static_dir / "uploads"
    uploads_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate unique filename
    file_ext = Path(file.filename).suffix.lower()
    unique_filename = f"{uuid.uuid4().hex}{file_ext}"
    file_path = uploads_dir / unique_filename
    
    try:
        # Save the file
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Return the URL
        url = f"/static/uploads/{unique_filename}"
        return {"success": True, "url": url, "filename": unique_filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal menyimpan file: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)