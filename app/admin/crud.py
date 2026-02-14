"""
Admin CRUD Operations for MobilityGraph
Handles creation, update, and deletion of destinations, stops, and edges
Persists changes to custom_routes.ttl
"""
from pathlib import Path
from typing import Optional, List
from datetime import datetime
from rdflib import Graph, Namespace, Literal, URIRef
from rdflib.namespace import RDF, XSD

# Namespaces
MG = Namespace("http://example.org/mobilitygraph#")
TR = Namespace("http://example.com/tr#")
SCHEMA = Namespace("http://schema.org/")
GEO = Namespace("http://www.w3.org/2003/01/geo/wgs84_pos#")

# Path to custom routes file
DATA_DIR = Path(__file__).parent.parent.parent / "dataTTL"
CUSTOM_TTL_PATH = DATA_DIR / "custom_routes.ttl"


def ensure_custom_ttl_exists():
    """Ensure custom_routes.ttl exists with proper prefixes"""
    if not CUSTOM_TTL_PATH.exists():
        # Create with default prefixes
        content = """@prefix mg: <http://example.org/mobilitygraph#> .
@prefix tr: <http://example.com/tr#> .
@prefix schema1: <http://schema.org/> .
@prefix geo1: <http://www.w3.org/2003/01/geo/wgs84_pos#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

# Custom routes and data added by admin
# Created: """ + datetime.now().isoformat() + "\n"
        
        CUSTOM_TTL_PATH.write_text(content, encoding="utf-8")
    return CUSTOM_TTL_PATH


def load_custom_graph() -> Graph:
    """Load the custom TTL file as RDF graph"""
    ensure_custom_ttl_exists()
    g = Graph()
    g.parse(str(CUSTOM_TTL_PATH), format="turtle")
    return g


def save_custom_graph(g: Graph):
    """Save the RDF graph back to TTL file"""
    ensure_custom_ttl_exists()
    g.serialize(destination=str(CUSTOM_TTL_PATH), format="turtle")


def add_destination(
    slug: str,
    name: str,
    region_id: str,
    lat: float,
    lon: float,
    description: str = "",
    category: str = "Recreation",
    long_description: str = "",
    long_history: str = "",
    image_url: str = "",
    year_established: Optional[int] = None,
    location: str = ""
) -> bool:
    """
    Add a new destination to custom_routes.ttl
    
    Args:
        slug: URL-friendly identifier
        name: Display name
        region_id: Region URI (e.g., mg:JakartaPusat)
        lat, lon: Coordinates
        description: Short description
        category: Category (Recreation, Historical, Cultural, Shopping, Sports)
        long_description: Full description
        long_history: Historical background
        image_url: URL to destination image
        year_established: Year established (optional)
        location: Address string
    
    Returns:
        True if successful
    """
    g = load_custom_graph()
    
    # Create destination URI
    dest_uri = MG[f"Custom_{slug.replace('-', '_')}"]
    
    # Check if already exists
    if (dest_uri, None, None) in g:
        # Update existing
        g.remove((dest_uri, None, None))
    
    # Add triples
    g.add((dest_uri, RDF.type, MG.PlaceOfInterest))
    g.add((dest_uri, SCHEMA.name, Literal(name)))
    g.add((dest_uri, GEO.lat, Literal(str(lat))))
    g.add((dest_uri, GEO.long, Literal(str(lon))))
    g.add((dest_uri, MG.inRegion, URIRef(region_id.replace("mg:", str(MG)))))
    g.add((dest_uri, MG.category, Literal(category)))
    
    if description:
        g.add((dest_uri, SCHEMA.description, Literal(description)))
    if long_description:
        g.add((dest_uri, MG.longDescription, Literal(long_description)))
    if long_history:
        g.add((dest_uri, MG.longHistory, Literal(long_history)))
    if image_url:
        g.add((dest_uri, SCHEMA.image, Literal(image_url)))
    if year_established:
        g.add((dest_uri, MG.yearEstablished, Literal(year_established, datatype=XSD.integer)))
    if location:
        g.add((dest_uri, MG.location, Literal(location)))
    
    # Add slug for identification
    g.add((dest_uri, MG.slug, Literal(slug)))
    
    save_custom_graph(g)
    return True


def add_stop(
    stop_id: str,
    name: str,
    lat: float,
    lon: float,
    mode: str = "TJ"
) -> bool:
    """
    Add a new stop/station to custom_routes.ttl
    
    Args:
        stop_id: Unique stop identifier
        name: Stop name
        lat, lon: Coordinates
        mode: Transport mode (MRT, LRT, TJ)
    
    Returns:
        True if successful
    """
    g = load_custom_graph()
    
    # Create stop URI based on mode
    prefix = f"Custom_Stop_{mode}_"
    stop_uri = TR[f"{prefix}{stop_id.replace('-', '_')}"]
    
    # Check if already exists
    if (stop_uri, None, None) in g:
        g.remove((stop_uri, None, None))
    
    # Add triples
    g.add((stop_uri, RDF.type, TR.StopPoint))
    g.add((stop_uri, SCHEMA.name, Literal(name)))
    g.add((stop_uri, GEO.lat, Literal(str(lat))))
    g.add((stop_uri, GEO.long, Literal(str(lon))))
    g.add((stop_uri, TR.mode, Literal(mode)))
    
    save_custom_graph(g)
    return True


def add_edge(
    from_stop_id: str,
    to_stop_id: str,
    mode: str,
    distance_m: float,
    duration_min: Optional[float] = None
) -> bool:
    """
    Add a new edge/segment between stops
    
    Args:
        from_stop_id: Starting stop ID
        to_stop_id: Ending stop ID
        mode: Transport mode
        distance_m: Distance in meters
        duration_min: Optional duration in minutes
    
    Returns:
        True if successful
    """
    g = load_custom_graph()
    
    # Create edge URI
    edge_id = f"{from_stop_id}_to_{to_stop_id}_{mode}"
    edge_uri = TR[f"Custom_Edge_{edge_id.replace('-', '_')}"]
    
    # Check if already exists
    if (edge_uri, None, None) in g:
        g.remove((edge_uri, None, None))
    
    # Add triples
    g.add((edge_uri, RDF.type, TR.RouteSegment))
    g.add((edge_uri, TR.fromStop, URIRef(from_stop_id)))
    g.add((edge_uri, TR.toStop, URIRef(to_stop_id)))
    g.add((edge_uri, TR.mode, Literal(mode)))
    g.add((edge_uri, TR.distance, Literal(distance_m, datatype=XSD.float)))
    
    if duration_min is not None:
        g.add((edge_uri, TR.duration, Literal(duration_min, datatype=XSD.float)))
    
    save_custom_graph(g)
    return True


def delete_destination(slug: str) -> bool:
    """Delete a custom destination by slug"""
    g = load_custom_graph()
    
    # Find destination by slug
    for s in g.subjects(MG.slug, Literal(slug)):
        g.remove((s, None, None))
        save_custom_graph(g)
        return True
    
    return False


def delete_stop(stop_id: str) -> bool:
    """Delete a custom stop by ID"""
    g = load_custom_graph()
    
    # Try to find and remove
    stop_uri = TR[stop_id]
    if (stop_uri, None, None) in g:
        g.remove((stop_uri, None, None))
        save_custom_graph(g)
        return True
    
    return False


def get_custom_destinations() -> List[dict]:
    """Get all custom destinations"""
    g = load_custom_graph()
    destinations = []
    
    for s in g.subjects(RDF.type, MG.PlaceOfInterest):
        dest = {
            "id": str(s),
            "slug": str(g.value(s, MG.slug) or ""),
            "name": str(g.value(s, SCHEMA.name) or ""),
            "lat": float(g.value(s, GEO.lat) or 0),
            "lon": float(g.value(s, GEO.long) or 0),
            "category": str(g.value(s, MG.category) or ""),
            "description": str(g.value(s, SCHEMA.description) or "")
        }
        destinations.append(dest)
    
    return destinations


def get_custom_stops() -> List[dict]:
    """Get all custom stops"""
    g = load_custom_graph()
    stops = []
    
    for s in g.subjects(RDF.type, TR.StopPoint):
        stop = {
            "id": str(s),
            "name": str(g.value(s, SCHEMA.name) or ""),
            "lat": float(g.value(s, GEO.lat) or 0),
            "lon": float(g.value(s, GEO.long) or 0),
            "mode": str(g.value(s, TR.mode) or "TJ")
        }
        stops.append(stop)
    
    return stops


def get_destination_by_slug(slug: str) -> Optional[dict]:
    """Get a specific custom destination by slug"""
    g = load_custom_graph()
    
    for s in g.subjects(MG.slug, Literal(slug)):
        region_uri = g.value(s, MG.inRegion)
        region_str = ""
        if region_uri:
            region_str = str(region_uri).replace(str(MG), "mg:")
        
        return {
            "id": str(s),
            "slug": str(g.value(s, MG.slug) or ""),
            "name": str(g.value(s, SCHEMA.name) or ""),
            "lat": float(g.value(s, GEO.lat) or 0),
            "lon": float(g.value(s, GEO.long) or 0),
            "region": region_str,
            "category": str(g.value(s, MG.category) or ""),
            "description": str(g.value(s, SCHEMA.description) or ""),
            "image_url": str(g.value(s, SCHEMA.image) or "")
        }
    
    return None


def get_stop_by_id(stop_id: str) -> Optional[dict]:
    """Get a specific custom stop by ID"""
    g = load_custom_graph()
    
    # Try different URI patterns
    for prefix in ["Custom_Stop_MRT_", "Custom_Stop_LRT_", "Custom_Stop_TJ_"]:
        stop_uri = TR[f"{prefix}{stop_id.replace('-', '_')}"]
        if (stop_uri, RDF.type, TR.StopPoint) in g:
            return {
                "id": stop_id,
                "uri": str(stop_uri),
                "name": str(g.value(stop_uri, SCHEMA.name) or ""),
                "lat": float(g.value(stop_uri, GEO.lat) or 0),
                "lon": float(g.value(stop_uri, GEO.long) or 0),
                "mode": str(g.value(stop_uri, TR.mode) or "TJ")
            }
    
    return None


def update_destination(
    slug: str,
    name: Optional[str] = None,
    region_id: Optional[str] = None,
    lat: Optional[float] = None,
    lon: Optional[float] = None,
    description: Optional[str] = None,
    category: Optional[str] = None,
    image_url: Optional[str] = None
) -> bool:
    """
    Update an existing destination by slug
    Only updates fields that are not None
    
    Returns:
        True if successful, False if not found
    """
    g = load_custom_graph()
    
    # Find destination by slug
    dest_uri = None
    for s in g.subjects(MG.slug, Literal(slug)):
        dest_uri = s
        break
    
    if not dest_uri:
        return False
    
    # Update fields if provided
    if name is not None:
        g.remove((dest_uri, SCHEMA.name, None))
        g.add((dest_uri, SCHEMA.name, Literal(name)))
    
    if region_id is not None:
        g.remove((dest_uri, MG.inRegion, None))
        g.add((dest_uri, MG.inRegion, URIRef(region_id.replace("mg:", str(MG)))))
    
    if lat is not None:
        g.remove((dest_uri, GEO.lat, None))
        g.add((dest_uri, GEO.lat, Literal(str(lat))))
    
    if lon is not None:
        g.remove((dest_uri, GEO.long, None))
        g.add((dest_uri, GEO.long, Literal(str(lon))))
    
    if description is not None:
        g.remove((dest_uri, SCHEMA.description, None))
        if description:
            g.add((dest_uri, SCHEMA.description, Literal(description)))
    
    if category is not None:
        g.remove((dest_uri, MG.category, None))
        g.add((dest_uri, MG.category, Literal(category)))
    
    if image_url is not None:
        g.remove((dest_uri, SCHEMA.image, None))
        if image_url:
            g.add((dest_uri, SCHEMA.image, Literal(image_url)))
    
    save_custom_graph(g)
    return True


def update_stop(
    stop_id: str,
    name: Optional[str] = None,
    lat: Optional[float] = None,
    lon: Optional[float] = None,
    mode: Optional[str] = None
) -> bool:
    """
    Update an existing stop by ID
    Only updates fields that are not None
    
    Returns:
        True if successful, False if not found
    """
    g = load_custom_graph()
    
    # Try to find the stop with different prefixes
    stop_uri = None
    for prefix in ["Custom_Stop_MRT_", "Custom_Stop_LRT_", "Custom_Stop_TJ_"]:
        uri = TR[f"{prefix}{stop_id.replace('-', '_')}"]
        if (uri, RDF.type, TR.StopPoint) in g:
            stop_uri = uri
            break
    
    if not stop_uri:
        return False
    
    # Update fields if provided
    if name is not None:
        g.remove((stop_uri, SCHEMA.name, None))
        g.add((stop_uri, SCHEMA.name, Literal(name)))
    
    if lat is not None:
        g.remove((stop_uri, GEO.lat, None))
        g.add((stop_uri, GEO.lat, Literal(str(lat))))
    
    if lon is not None:
        g.remove((stop_uri, GEO.long, None))
        g.add((stop_uri, GEO.long, Literal(str(lon))))
    
    if mode is not None:
        g.remove((stop_uri, TR.mode, None))
        g.add((stop_uri, TR.mode, Literal(mode)))
    
    save_custom_graph(g)
    return True


def export_ttl() -> str:
    """Export custom TTL file content"""
    ensure_custom_ttl_exists()
    return CUSTOM_TTL_PATH.read_text(encoding="utf-8")
