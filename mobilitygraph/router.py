"""
Router - Pathfinding algorithms for MobilityGraph
"""
import networkx as nx
from typing import Dict, List, Optional
from .graph_builder import GraphBuilder
from .loader import MobilityGraphLoader


class Router:
    """Handles route finding between stops"""
    
    def __init__(self, graph_builder: GraphBuilder):
        self.graph_builder = graph_builder
        self.graph = graph_builder.graph
        self.loader = graph_builder.loader
        
    def find_route(
        self,
        start_id: str,
        end_id: str,
        mode: str = "ALL",
        weight: str = "time_minutes"
    ) -> Optional[Dict]:
        """
        Find the best route between two stops
        
        Args:
            start_id: Starting stop ID
            end_id: Destination stop ID
            mode: Transport mode filter (MRT, LRT, TJ, ALL)
            weight: Weight to optimize (time_minutes, distance_km, cost_idr)
        
        Returns:
            Route dictionary with path, legs, and summary
        """
        # Get filtered graph based on mode
        if mode and mode != "ALL":
            graph = self.graph_builder.get_filtered_graph(mode)
        else:
            graph = self.graph
        
        # Check if nodes exist
        if start_id not in graph:
            return {"error": f"Start stop '{start_id}' not found"}
        if end_id not in graph:
            return {"error": f"End stop '{end_id}' not found"}
        
        try:
            # Find shortest path
            path = nx.dijkstra_path(graph, start_id, end_id, weight=weight)
            
            # Build route details
            return self._build_route_response(path, graph)
            
        except nx.NetworkXNoPath:
            return {"error": f"No route found from '{start_id}' to '{end_id}' with mode '{mode}'"}
    
    def find_route_to_poi(
        self,
        start_id: str,
        poi_id: str,
        mode: str = "ALL"
    ) -> Optional[Dict]:
        """Find route from a stop to a Place of Interest"""
        # Get POI info
        pois = self.loader.get_places_of_interest()
        poi = next((p for p in pois if p["id"] == poi_id), None)
        
        if not poi:
            return {"error": f"POI '{poi_id}' not found"}
        
        # Get nearest stop to POI
        if poi.get("nearStop"):
            end_id = poi["nearStop"]
        else:
            nearest = self.graph_builder.find_nearest_stop(poi["lat"], poi["long"], mode if mode != "ALL" else None)
            if not nearest:
                return {"error": f"No stop found near POI '{poi_id}'"}
            end_id = nearest["id"]
        
        # Find route
        route = self.find_route(start_id, end_id, mode)
        if route and "error" not in route:
            route["destination_poi"] = poi
        
        return route
    
    def find_multi_stop_route(
        self,
        start_id: str,
        poi_ids: List[str],
        mode: str = "ALL"
    ) -> Optional[Dict]:
        """Find route visiting multiple POIs (nearest neighbor heuristic)"""
        if not poi_ids:
            return {"error": "No POIs selected"}
        
        # Get POI info
        pois = self.loader.get_places_of_interest()
        selected_pois = [p for p in pois if p["id"] in poi_ids]
        
        if not selected_pois:
            return {"error": "No valid POIs found"}
        
        # Order POIs by nearest neighbor heuristic
        current_stop = start_id
        ordered_pois = []
        remaining = selected_pois.copy()
        
        while remaining:
            current_data = self.graph_builder.stops_by_id.get(current_stop)
            if not current_data:
                break
                
            # Find nearest remaining POI
            min_dist = float('inf')
            nearest_poi = None
            
            for poi in remaining:
                from geopy.distance import geodesic
                dist = geodesic(
                    (current_data["lat"], current_data["long"]),
                    (poi["lat"], poi["long"])
                ).kilometers
                if dist < min_dist:
                    min_dist = dist
                    nearest_poi = poi
            
            if nearest_poi:
                ordered_pois.append(nearest_poi)
                remaining.remove(nearest_poi)
                
                # Get stop near this POI
                if nearest_poi.get("nearStop"):
                    current_stop = nearest_poi["nearStop"]
                else:
                    nearest_stop = self.graph_builder.find_nearest_stop(
                        nearest_poi["lat"], nearest_poi["long"]
                    )
                    if nearest_stop:
                        current_stop = nearest_stop["id"]
        
        # Build complete route through all POIs
        all_legs = []
        total_distance = 0
        total_time = 0
        total_cost = 0
        current = start_id
        
        for poi in ordered_pois:
            # Get end stop for this POI
            if poi.get("nearStop"):
                end = poi["nearStop"]
            else:
                nearest = self.graph_builder.find_nearest_stop(poi["lat"], poi["long"])
                end = nearest["id"] if nearest else None
            
            if end and end != current:
                segment = self.find_route(current, end, mode)
                if segment and "error" not in segment:
                    for leg in segment.get("legs", []):
                        leg["destination_poi"] = poi["name"]
                        all_legs.append(leg)
                    total_distance += segment["summary"]["total_distance_km"]
                    total_time += segment["summary"]["total_time_minutes"]
                    total_cost += segment["summary"]["total_cost_idr"]
                    current = end
        
        return {
            "summary": {
                "total_distance_km": round(total_distance, 2),
                "total_time_minutes": round(total_time, 2),
                "total_cost_idr": total_cost
            },
            "legs": all_legs,
            "visited_pois": [p["name"] for p in ordered_pois],
            "start_stop": self.graph_builder.stops_by_id.get(start_id),
            "end_stop": self.graph_builder.stops_by_id.get(current),
            "transfers": self._count_transfers(all_legs)
        }
    
    def _build_route_response(self, path: List[str], graph: nx.DiGraph) -> Dict:
        """Build detailed route response from path"""
        legs = []
        geometry = []
        
        # 1. Build basic legs from graph data
        for i in range(len(path) - 1):
            from_id = path[i]
            to_id = path[i + 1]
            
            from_stop = self.graph_builder.stops_by_id.get(from_id, {})
            to_stop = self.graph_builder.stops_by_id.get(to_id, {})
            edge_data = graph.edges[from_id, to_id]
            
            leg = {
                "from": from_id,
                "from_name": from_stop.get("name", from_id),
                "to": to_id,
                "to_name": to_stop.get("name", to_id),
                "mode": edge_data.get("mode", "Unknown"),
                "line": edge_data.get("line", "Unknown"),
                "distance_km": edge_data.get("distance_km", 0),
                "time_minutes": edge_data.get("time_minutes", 0),
                "cost_idr": 0, # Will be calculated by segment
                "is_transfer": edge_data.get("is_transfer", False)
            }
            legs.append(leg)
            
            # Add coordinates for geometry
            if from_stop:
                geometry.append([from_stop.get("lat"), from_stop.get("long")])
        
        # Add last stop to geometry
        if path:
            last_stop = self.graph_builder.stops_by_id.get(path[-1], {})
            if last_stop:
                geometry.append([last_stop.get("lat"), last_stop.get("long")])
                
        # 2. Adjust costs based on segments (continuous usage of same mode)
        self._calculate_segment_costs(legs)
        
        # 3. Calculate totals
        total_distance = sum(leg["distance_km"] for leg in legs)
        total_time = sum(leg["time_minutes"] for leg in legs)
        total_cost = sum(leg["cost_idr"] for leg in legs)
        
        return {
            "summary": {
                "total_distance_km": round(total_distance, 2),
                "total_time_minutes": round(total_time, 2),
                "total_cost_idr": total_cost
            },
            "legs": legs,
            "path": path,
            "start_stop": self.graph_builder.stops_by_id.get(path[0]) if path else None,
            "end_stop": self.graph_builder.stops_by_id.get(path[-1]) if path else None,
            "transfers": self._count_transfers(legs),
            "geometry": geometry,
            "geojson": self._build_geojson(legs, geometry)
        }
        
    def _calculate_segment_costs(self, legs: List[Dict]):
        """Calculate costs for continuous segments of same mode"""
        if not legs:
            return

        from app.fares import calculate_mrt_fare, calculate_lrt_fare, calculate_tj_fare
        
        current_segment = []
        current_mode = None
        
        for leg in legs:
            mode = leg["mode"]
            # Treat transfers as breaks in segment, or ignore?
            # Usually transfers (WALK) separate modes.
            
            if mode != current_mode:
                # Process completed segment
                if current_segment:
                    self._apply_cost_to_segment(current_segment, current_mode)
                
                current_segment = [leg]
                current_mode = mode
            else:
                current_segment.append(leg)
        
        # Process final segment
        if current_segment:
            self._apply_cost_to_segment(current_segment, current_mode)
            
    def _apply_cost_to_segment(self, legs: List[Dict], mode: str):
        """Apply fare rules to a segment"""
        from app.fares import calculate_mrt_fare, calculate_lrt_fare, calculate_tj_fare
        
        if mode == "MRT":
            # Fare based on entry and exit station
            start_stop = legs[0]["from_name"]
            end_stop = legs[-1]["to_name"]
            cost = calculate_mrt_fare(start_stop, end_stop)
            # Assign cost to the last leg (exit)
            legs[-1]["cost_idr"] = cost
            
        elif mode == "LRT":
            # Fare based on total distance
            dist = sum(leg["distance_km"] for leg in legs)
            cost = calculate_lrt_fare(dist)
            legs[-1]["cost_idr"] = cost
            
        elif mode == "TJ":
            # Flat fare per entry
            cost = calculate_tj_fare()
            legs[0]["cost_idr"] = cost
            
        elif mode == "WALK" or "Transfer" in str(legs[0].get("line", "")):
            # Free
            pass
    
    def _count_transfers(self, legs: List[Dict]) -> List[Dict]:
        """Count and list transfer points"""
        transfers = []
        for leg in legs:
            if leg.get("is_transfer"):
                transfers.append({
                    "at": leg["from_name"],
                    "from_mode": leg["line"].split("-")[0].replace("Transfer ", "") if "Transfer" in leg.get("line", "") else "",
                    "to_mode": leg["mode"]
                })
        return transfers
    
    def _build_geojson(self, legs: List[Dict], geometry: List[List[float]]) -> Dict:
        """Build GeoJSON representation of the route"""
        features = []
        
        # Route line
        if geometry:
            features.append({
                "type": "Feature",
                "geometry": {
                    "type": "LineString",
                    "coordinates": [[g[1], g[0]] for g in geometry]  # GeoJSON uses [long, lat]
                },
                "properties": {
                    "type": "route"
                }
            })
        
        # Stop points
        for i, coord in enumerate(geometry):
            is_start = i == 0
            is_end = i == len(geometry) - 1
            
            features.append({
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [coord[1], coord[0]]
                },
                "properties": {
                    "type": "start" if is_start else ("end" if is_end else "stop"),
                    "index": i
                }
            })
        
        return {
            "type": "FeatureCollection",
            "features": features
        }


if __name__ == "__main__":
    # Test router
    loader = MobilityGraphLoader()
    loader.load_all_ttl()
    
    builder = GraphBuilder(loader)
    builder.build_graph()
    
    router = Router(builder)
    
    # Test MRT route
    result = router.find_route("Stop_MRT_01", "Stop_MRT_13", mode="MRT")
    if result and "error" not in result:
        print(f"\nMRT Route: {result['summary']}")
        print(f"Path: {' -> '.join(result['path'])}")
