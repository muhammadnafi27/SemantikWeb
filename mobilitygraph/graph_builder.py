"""
Graph Builder - Converts RDF data to NetworkX graph for routing
"""
import networkx as nx
from typing import Dict, List, Optional
from geopy.distance import geodesic
from .loader import MobilityGraphLoader


class GraphBuilder:
    """Builds a NetworkX graph from RDF mobility data"""
    
    # Transfer penalty in minutes when switching modes
    TRANSFER_PENALTY = 5
    
    # Average speeds in km/h for travel time estimation
    SPEEDS = {
        "MRT": 40,
        "LRT": 35,
        "TJ": 20
    }
    
    # Base fares in IDR
    BASE_FARES = {
        "MRT": 3000,  # 3000-14000 based on distance
        "LRT": 3000,  # 3000-20000 based on distance
        "TJ": 3500    # Flat fare
    }
    
    def __init__(self, loader: MobilityGraphLoader):
        self.loader = loader
        self.graph = nx.DiGraph()
        self.stops_by_id = {}
        self.routes_info = {}
        
    def build_graph(self) -> nx.DiGraph:
        """Build the complete routing graph"""
        # Load all stops
        stops = self.loader.get_stops()
        self.stops_by_id = {s["id"]: s for s in stops}
        
        # Add all stops as nodes
        for stop in stops:
            mode = self._get_mode_from_id(stop["id"])
            self.graph.add_node(
                stop["id"],
                name=stop["name"],
                lat=stop["lat"],
                long=stop["long"],
                mode=mode
            )
        
        # Build edges from routes (MRT/LRT)
        self._build_route_edges()
        
        # Build edges for TransJakarta (proximity-based)
        self._build_tj_edges()
        
        # Build transfer edges between modes
        self._build_transfer_edges()
        
        print(f"Graph built: {self.graph.number_of_nodes()} nodes, {self.graph.number_of_edges()} edges")
        return self.graph
    
    def _get_mode_from_id(self, stop_id: str) -> str:
        """Determine transport mode from stop ID"""
        if "MRT" in stop_id:
            return "MRT"
        elif "LRT" in stop_id:
            return "LRT"
        else:
            return "TJ"
    
    def _calculate_distance(self, stop1: Dict, stop2: Dict) -> float:
        """Calculate distance in km between two stops"""
        coord1 = (stop1["lat"], stop1["long"])
        coord2 = (stop2["lat"], stop2["long"])
        return geodesic(coord1, coord2).kilometers
    
    def _calculate_edge_weight(self, distance_km: float, mode: str, is_transfer: bool = False) -> Dict:
        """Calculate edge weight including time, distance, and cost"""
        speed = self.SPEEDS.get(mode, 20)
        time_minutes = (distance_km / speed) * 60
        
        # Calculate cost
        if mode == "TJ":
            cost = 0  # Flat fare handled per trip/tap in Router
        else:
            # Distance-based incremental cost for MRT/LRT (approximate)
            # Base fare added once per segment in Router
            cost = int(distance_km * 1000)
        
        # Add transfer penalty
        if is_transfer:
            time_minutes += self.TRANSFER_PENALTY
        
        return {
            "distance_km": round(distance_km, 3),
            "time_minutes": round(time_minutes, 2),
            "cost_idr": cost,
            "mode": mode,
            "is_transfer": is_transfer
        }
    
    def _build_route_edges(self):
        """Build edges from defined routes (MRT/LRT)"""
        routes = self.loader.get_routes()
        
        for route in routes:
            mode = "MRT" if "MRT" in route["id"] else "LRT"
            stops = route["stops"]
            
            # Get ordered stop IDs
            stop_ids = []
            for stop_uri in stops:
                stop_id = stop_uri.split("#")[-1] if "#" in stop_uri else stop_uri.split("/")[-1]
                if stop_id in self.stops_by_id:
                    stop_ids.append(stop_id)
            
            # Create edges between consecutive stops (bidirectional)
            for i in range(len(stop_ids) - 1):
                from_stop = self.stops_by_id.get(stop_ids[i])
                to_stop = self.stops_by_id.get(stop_ids[i + 1])
                
                if from_stop and to_stop:
                    distance = self._calculate_distance(from_stop, to_stop)
                    edge_data = self._calculate_edge_weight(distance, mode)
                    edge_data["line"] = route["name"]
                    
                    # Bidirectional edges
                    self.graph.add_edge(stop_ids[i], stop_ids[i + 1], **edge_data)
                    self.graph.add_edge(stop_ids[i + 1], stop_ids[i], **edge_data)
    
    def _build_tj_edges(self):
        """Build TransJakarta edges based on proximity - OPTIMIZED"""
        # Get all TJ stops
        tj_stops = [s for s in self.stops_by_id.values() if self._get_mode_from_id(s["id"]) == "TJ"]
        
        if not tj_stops:
            return
        
        print(f"Building TJ edges for {len(tj_stops)} stops (optimized)...")
        
        # Use spatial binning for faster neighbor lookup
        # Bin size ~0.01 degrees ≈ 1km
        BIN_SIZE = 0.01
        MAX_CONNECTIONS = 3  # Max connections per stop
        
        # Create spatial bins
        bins = {}
        for stop in tj_stops:
            bin_key = (int(stop["lat"] / BIN_SIZE), int(stop["long"] / BIN_SIZE))
            if bin_key not in bins:
                bins[bin_key] = []
            bins[bin_key].append(stop)
        
        # For each stop, only check nearby bins
        edges_added = 0
        for stop1 in tj_stops:
            bin_key = (int(stop1["lat"] / BIN_SIZE), int(stop1["long"] / BIN_SIZE))
            
            # Check current bin and 8 neighbors
            nearby = []
            for di in [-1, 0, 1]:
                for dj in [-1, 0, 1]:
                    neighbor_bin = (bin_key[0] + di, bin_key[1] + dj)
                    if neighbor_bin in bins:
                        for stop2 in bins[neighbor_bin]:
                            if stop1["id"] != stop2["id"]:
                                # Simple euclidean approx for speed
                                dist = ((stop1["lat"] - stop2["lat"])**2 + 
                                       (stop1["long"] - stop2["long"])**2) ** 0.5 * 111  # km approx
                                if dist <= 1.5:  # 1.5km threshold
                                    nearby.append((stop2, dist))
            
            # Connect to closest neighbors
            nearby.sort(key=lambda x: x[1])
            for stop2, distance in nearby[:MAX_CONNECTIONS]:
                edge_data = self._calculate_edge_weight(distance, "TJ")
                edge_data["line"] = "TransJakarta"
                self.graph.add_edge(stop1["id"], stop2["id"], **edge_data)
                edges_added += 1
        
        print(f"TJ edges added: {edges_added}")
    
    def _build_transfer_edges(self):
        """Build transfer edges between different modes at nearby stops"""
        MAX_TRANSFER_DISTANCE = 0.5  # 500 meters
        
        stops = list(self.stops_by_id.values())
        
        for i, stop1 in enumerate(stops):
            mode1 = self._get_mode_from_id(stop1["id"])
            
            for stop2 in stops[i+1:]:
                mode2 = self._get_mode_from_id(stop2["id"])
                
                # Only create transfer edges between different modes
                if mode1 != mode2:
                    distance = self._calculate_distance(stop1, stop2)
                    if distance <= MAX_TRANSFER_DISTANCE:
                        edge_data = self._calculate_edge_weight(distance, mode2, is_transfer=True)
                        edge_data["line"] = f"Transfer {mode1}-{mode2}"
                        
                        # Bidirectional transfer
                        self.graph.add_edge(stop1["id"], stop2["id"], **edge_data)
                        
                        # Reverse direction uses opposite mode
                        edge_data_reverse = self._calculate_edge_weight(distance, mode1, is_transfer=True)
                        edge_data_reverse["line"] = f"Transfer {mode2}-{mode1}"
                        self.graph.add_edge(stop2["id"], stop1["id"], **edge_data_reverse)
    
    def get_filtered_graph(self, mode: str = None, region: str = None) -> nx.DiGraph:
        """Get a filtered subgraph based on mode and region"""
        if mode is None or mode == "ALL":
            return self.graph.copy()
        
        # Filter by mode (nodes)
        filtered_nodes = [
            node for node, data in self.graph.nodes(data=True)
            if data.get("mode") == mode
        ]
        
        subgraph = self.graph.subgraph(filtered_nodes).copy()
        
        # Filter edges (remove edges that don't match mode)
        # This handles cases where edges might span differently classified nodes
        edges_to_remove = [
            (u, v) for u, v, data in subgraph.edges(data=True)
            if data.get("mode") != mode
        ]
        subgraph.remove_edges_from(edges_to_remove)
        
        return subgraph
    
    def find_nearest_stop(self, lat: float, long: float, mode: str = None) -> Optional[Dict]:
        """Find the nearest stop to given coordinates"""
        min_distance = float('inf')
        nearest = None
        
        for stop_id, stop in self.stops_by_id.items():
            if mode and self._get_mode_from_id(stop_id) != mode:
                continue
            
            distance = geodesic((lat, long), (stop["lat"], stop["long"])).kilometers
            if distance < min_distance:
                min_distance = distance
                nearest = {**stop, "distance_km": round(distance, 3)}
        
        return nearest


if __name__ == "__main__":
    # Test graph builder
    loader = MobilityGraphLoader()
    loader.load_all_ttl()
    
    builder = GraphBuilder(loader)
    graph = builder.build_graph()
    
    print(f"\nGraph Statistics:")
    print(f"  Nodes: {graph.number_of_nodes()}")
    print(f"  Edges: {graph.number_of_edges()}")
