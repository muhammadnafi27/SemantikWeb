"""
RDF/TTL Loader for MobilityGraph
Loads and parses all Turtle files from dataTTL directory
"""
from pathlib import Path
from rdflib import Graph, Namespace
from typing import Dict, List, Optional

# Namespaces
TR = Namespace("http://example.com/tr#")
GEO = Namespace("http://www.w3.org/2003/01/geo/wgs84_pos#")
SCHEMA = Namespace("http://schema.org/")
MG = Namespace("http://example.org/mobilitygraph#")


class MobilityGraphLoader:
    """Loads RDF data from TTL files"""
    
    def __init__(self, data_dir: str = None):
        self.graph = Graph()
        self.graph.bind("tr", TR)
        self.graph.bind("geo1", GEO)
        self.graph.bind("schema1", SCHEMA)
        self.graph.bind("mg", MG)
        
        if data_dir is None:
            # Default to dataTTL in project root
            project_root = Path(__file__).parent.parent
            data_dir = project_root / "datattl" / "data TTL"
        
        self.data_dir = Path(data_dir)
        
    def load_all_ttl(self) -> Graph:
        """Load all TTL files from data directory"""
        if not self.data_dir.exists():
            raise FileNotFoundError(f"Data directory not found: {self.data_dir}")
        
        ttl_files = list(self.data_dir.glob("*.ttl"))
        for ttl_file in ttl_files:
            print(f"Loading {ttl_file.name}...")
            self.graph.parse(ttl_file, format="turtle")
        
        print(f"Total triples loaded: {len(self.graph)}")
        return self.graph
    
    def get_stops(self, mode: str = None) -> List[Dict]:
        """Get all stop points, optionally filtered by mode"""
        query = """
        SELECT ?stop ?name ?lat ?long WHERE {
            ?stop a tr:StopPoint ;
                  schema1:name ?name ;
                  geo1:lat ?lat ;
                  geo1:long ?long .
        }
        """
        
        results = []
        for row in self.graph.query(query, initNs={"tr": TR, "schema1": SCHEMA, "geo1": GEO}):
            stop_id = str(row.stop).split("#")[-1] if "#" in str(row.stop) else str(row.stop).split("/")[-1]
            
            # Filter by mode based on stop ID prefix
            if mode:
                if mode == "MRT" and "MRT" not in stop_id:
                    continue
                elif mode == "LRT" and "LRT" not in stop_id:
                    continue
                elif mode == "TJ" and ("MRT" in stop_id or "LRT" in stop_id):
                    continue
            
            results.append({
                "id": stop_id,
                "uri": str(row.stop),
                "name": str(row.name),
                "lat": float(row.lat),
                "long": float(row.long)
            })
        
        return results
    
    def get_routes(self) -> List[Dict]:
        """Get all routes with their stops"""
        query = """
        SELECT ?route ?name ?stop WHERE {
            ?route a tr:Route ;
                   schema1:name ?name ;
                   tr:stopAt ?stop .
        }
        """
        
        routes = {}
        for row in self.graph.query(query, initNs={"tr": TR, "schema1": SCHEMA}):
            route_id = str(row.route)
            if route_id not in routes:
                routes[route_id] = {
                    "id": route_id.split("#")[-1] if "#" in route_id else route_id.split("/")[-1],
                    "name": str(row.name),
                    "stops": []
                }
            routes[route_id]["stops"].append(str(row.stop))
        
        return list(routes.values())
    
    def get_transport_options(self) -> List[Dict]:
        """Get transport options with prices"""
        query = """
        SELECT ?option ?name ?price ?route WHERE {
            ?option a tr:TransportOption ;
                    schema1:name ?name ;
                    tr:price ?price ;
                    tr:hasRoute ?route .
        }
        """
        
        results = []
        for row in self.graph.query(query, initNs={"tr": TR, "schema1": SCHEMA}):
            results.append({
                "id": str(row.option).split("#")[-1],
                "name": str(row.name),
                "price": int(row.price),
                "route": str(row.route).split("#")[-1]
            })
        
        return results
    
    def get_places_of_interest(self) -> List[Dict]:
        """Get places of interest (POI)"""
        query = """
        SELECT ?place ?name ?lat ?long ?nearStop WHERE {
            ?place a mg:PlaceOfInterest ;
                   schema1:name ?name ;
                   geo1:lat ?lat ;
                   geo1:long ?long .
            OPTIONAL { ?place mg:nearStop ?nearStop }
        }
        """
        
        results = []
        for row in self.graph.query(query, initNs={"mg": MG, "schema1": SCHEMA, "geo1": GEO}):
            results.append({
                "id": str(row.place).split("#")[-1],
                "name": str(row.name),
                "lat": float(row.lat),
                "long": float(row.long),
                "nearStop": str(row.nearStop).split("#")[-1] if row.nearStop else None
            })
        
        return results
    
    def get_regions(self) -> List[Dict]:
        """Get all regions"""
        query = """
        SELECT ?region ?name WHERE {
            ?region a mg:Region ;
                    schema1:name ?name .
        }
        """
        
        results = []
        for row in self.graph.query(query, initNs={"mg": MG, "schema1": SCHEMA}):
            results.append({
                "id": str(row.region).split("#")[-1],
                "name": str(row.name)
            })
        
        return results
    
    def get_summary(self) -> Dict:
        """Get summary of loaded data"""
        stops = self.get_stops()
        routes = self.get_routes()
        pois = self.get_places_of_interest()
        regions = self.get_regions()
        
        # Count by mode
        mrt_stops = len([s for s in stops if "MRT" in s["id"]])
        lrt_stops = len([s for s in stops if "LRT" in s["id"]])
        tj_stops = len(stops) - mrt_stops - lrt_stops
        
        return {
            "total_triples": len(self.graph),
            "total_stops": len(stops),
            "mrt_stops": mrt_stops,
            "lrt_stops": lrt_stops,
            "tj_stops": tj_stops,
            "total_routes": len(routes),
            "total_pois": len(pois),
            "total_regions": len(regions)
        }


if __name__ == "__main__":
    # Test loader
    loader = MobilityGraphLoader()
    loader.load_all_ttl()
    
    print("\n=== Data Summary ===")
    summary = loader.get_summary()
    for key, value in summary.items():
        print(f"{key}: {value}")
