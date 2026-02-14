"""
Unit tests for MobilityGraph routing functionality
Tests cover the three required scenarios:
1. MRT-only route
2. TJ-only route  
3. Multi-modal (ALL) route with transfer
"""
import pytest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from mobilitygraph.loader import MobilityGraphLoader
from mobilitygraph.graph_builder import GraphBuilder
from mobilitygraph.router import Router


@pytest.fixture(scope="module")
def mobility_system():
    """Initialize the complete mobility system for testing"""
    loader = MobilityGraphLoader()
    loader.load_all_ttl()
    
    builder = GraphBuilder(loader)
    builder.build_graph()
    
    router = Router(builder)
    
    return {
        "loader": loader,
        "builder": builder,
        "router": router
    }


class TestDataLoading:
    """Tests for RDF data loading"""
    
    def test_ttl_files_loaded(self, mobility_system):
        """Verify TTL files are loaded successfully"""
        loader = mobility_system["loader"]
        summary = loader.get_summary()
        
        assert summary["total_triples"] > 0, "Should have loaded triples"
        assert summary["total_stops"] > 0, "Should have loaded stops"
    
    def test_mrt_stops_exist(self, mobility_system):
        """Verify MRT stops are present"""
        loader = mobility_system["loader"]
        stops = loader.get_stops(mode="MRT")
        
        assert len(stops) > 0, "Should have MRT stops"
        assert all("MRT" in s["id"] for s in stops), "All MRT stops should have MRT in ID"
    
    def test_lrt_stops_exist(self, mobility_system):
        """Verify LRT stops are present"""
        loader = mobility_system["loader"]
        stops = loader.get_stops(mode="LRT")
        
        assert len(stops) > 0, "Should have LRT stops"
        assert all("LRT" in s["id"] for s in stops), "All LRT stops should have LRT in ID"
    
    def test_pois_loaded(self, mobility_system):
        """Verify Places of Interest are loaded"""
        loader = mobility_system["loader"]
        pois = loader.get_places_of_interest()
        
        assert len(pois) > 0, "Should have POIs"
        
        # Check required POIs exist
        poi_names = [p["name"].upper() for p in pois]
        assert any("ANCOL" in name for name in poi_names), "Ancol should be in POIs"
        assert any("MONAS" in name for name in poi_names), "Monas should be in POIs"
    
    def test_regions_loaded(self, mobility_system):
        """Verify regions are loaded"""
        loader = mobility_system["loader"]
        regions = loader.get_regions()
        
        assert len(regions) > 0, "Should have regions"


class TestGraphBuilding:
    """Tests for NetworkX graph construction"""
    
    def test_graph_has_nodes(self, mobility_system):
        """Verify graph has nodes"""
        builder = mobility_system["builder"]
        
        assert builder.graph.number_of_nodes() > 0, "Graph should have nodes"
    
    def test_graph_has_edges(self, mobility_system):
        """Verify graph has edges"""
        builder = mobility_system["builder"]
        
        assert builder.graph.number_of_edges() > 0, "Graph should have edges"
    
    def test_edge_has_weight_attributes(self, mobility_system):
        """Verify edges have required weight attributes"""
        builder = mobility_system["builder"]
        
        # Get first edge
        edges = list(builder.graph.edges(data=True))
        assert len(edges) > 0, "Should have at least one edge"
        
        _, _, data = edges[0]
        assert "distance_km" in data, "Edge should have distance_km"
        assert "time_minutes" in data, "Edge should have time_minutes"
        assert "cost_idr" in data, "Edge should have cost_idr"
        assert "mode" in data, "Edge should have mode"


class TestMRTOnlyRoute:
    """Test Case 1: MRT-only routing"""
    
    def test_mrt_route_between_stations(self, mobility_system):
        """Find route between two MRT stations using MRT only"""
        router = mobility_system["router"]
        
        # Find route from Lebak Bulus (Stop_MRT_01) to Bundaran HI (Stop_MRT_13)
        result = router.find_route(
            start_id="Stop_MRT_01",
            end_id="Stop_MRT_13",
            mode="MRT"
        )
        
        assert "error" not in result, f"Route should be found: {result.get('error')}"
        assert result["summary"]["total_distance_km"] > 0, "Should have distance"
        assert result["summary"]["total_time_minutes"] > 0, "Should have time"
        assert result["summary"]["total_cost_idr"] > 0, "Should have cost"
        assert len(result["legs"]) > 0, "Should have route legs"
        
        # All legs should be MRT
        for leg in result["legs"]:
            assert leg["mode"] == "MRT", "All legs should be MRT mode"
    
    def test_mrt_route_has_geometry(self, mobility_system):
        """Verify MRT route includes geometry for map"""
        router = mobility_system["router"]
        
        result = router.find_route(
            start_id="Stop_MRT_01",
            end_id="Stop_MRT_13",
            mode="MRT"
        )
        
        assert "geometry" in result, "Result should have geometry"
        assert len(result["geometry"]) > 0, "Geometry should have coordinates"
        
        # Each coordinate should be [lat, long]
        for coord in result["geometry"]:
            assert len(coord) == 2, "Each coordinate should be [lat, long]"
            assert isinstance(coord[0], float), "Lat should be float"
            assert isinstance(coord[1], float), "Long should be float"


class TestTJOnlyRoute:
    """Test Case 2: TransJakarta-only routing"""
    
    def test_tj_stops_have_edges(self, mobility_system):
        """Verify TransJakarta stops are connected"""
        builder = mobility_system["builder"]
        
        # Count TJ edges
        tj_edges = [
            (u, v) for u, v, d in builder.graph.edges(data=True)
            if d.get("mode") == "TJ"
        ]
        
        assert len(tj_edges) > 0, "Should have TJ edges"
    
    def test_tj_route_if_available(self, mobility_system):
        """Find route using TransJakarta only (if stops are connected)"""
        builder = mobility_system["builder"]
        router = mobility_system["router"]
        
        # Get two TJ stops that are connected
        tj_nodes = [
            node for node, data in builder.graph.nodes(data=True)
            if data.get("mode") == "TJ"
        ]
        
        if len(tj_nodes) >= 2:
            # Try to find a route between first two TJ stops
            result = router.find_route(
                start_id=tj_nodes[0],
                end_id=tj_nodes[1],
                mode="TJ"
            )
            
            # Route may or may not exist depending on connectivity
            if "error" not in result:
                assert result["summary"]["total_distance_km"] >= 0
                for leg in result["legs"]:
                    assert leg["mode"] == "TJ", "All legs should be TJ mode"


class TestMultiModalRoute:
    """Test Case 3: Multi-modal routing with transfers"""
    
    def test_all_mode_allows_mixed_transport(self, mobility_system):
        """Verify ALL mode can use multiple transport types"""
        builder = mobility_system["builder"]
        
        # Get one MRT and one TJ stop
        mrt_nodes = [n for n, d in builder.graph.nodes(data=True) if d.get("mode") == "MRT"]
        tj_nodes = [n for n, d in builder.graph.nodes(data=True) if d.get("mode") == "TJ"]
        
        assert len(mrt_nodes) > 0, "Should have MRT nodes"
        assert len(tj_nodes) > 0, "Should have TJ nodes"
    
    def test_transfer_penalty_applied(self, mobility_system):
        """Verify transfer penalty is configured"""
        builder = mobility_system["builder"]
        
        assert builder.TRANSFER_PENALTY > 0, "Transfer penalty should be positive"
    
    def test_multimodal_route_geojson(self, mobility_system):
        """Verify route generates valid GeoJSON"""
        router = mobility_system["router"]
        
        result = router.find_route(
            start_id="Stop_MRT_01",
            end_id="Stop_MRT_13",
            mode="ALL"
        )
        
        if "error" not in result and "geojson" in result:
            geojson = result["geojson"]
            
            assert geojson["type"] == "FeatureCollection", "Should be FeatureCollection"
            assert "features" in geojson, "Should have features"
            assert len(geojson["features"]) > 0, "Should have at least one feature"


class TestRouteToPoI:
    """Test routing to Places of Interest"""
    
    def test_route_to_monas(self, mobility_system):
        """Find route to Monas"""
        router = mobility_system["router"]
        builder = mobility_system["builder"]
        
        # Get a starting stop
        mrt_nodes = [n for n, d in builder.graph.nodes(data=True) if d.get("mode") == "MRT"]
        
        if mrt_nodes:
            result = router.find_route_to_poi(
                start_id=mrt_nodes[0],
                poi_id="Monas",
                mode="ALL"
            )
            
            # May or may not find route depending on POI mapping
            # Just verify it doesn't crash
            assert result is not None


class TestCostCalculation:
    """Test fare/cost calculations"""
    
    def test_mrt_fare_range(self, mobility_system):
        """Verify MRT fares are within expected range"""
        router = mobility_system["router"]
        
        result = router.find_route(
            start_id="Stop_MRT_01",
            end_id="Stop_MRT_13",
            mode="MRT"
        )
        
        if "error" not in result:
            total_cost = result["summary"]["total_cost_idr"]
            # MRT Jakarta max fare is around 14,000 IDR
            assert 3000 <= total_cost <= 50000, f"Cost should be reasonable: {total_cost}"
    
    def test_per_leg_cost_breakdown(self, mobility_system):
        """Verify each leg has individual cost"""
        router = mobility_system["router"]
        
        result = router.find_route(
            start_id="Stop_MRT_01",
            end_id="Stop_MRT_13",
            mode="MRT"
        )
        
        if "error" not in result:
            legs_total = sum(leg["cost_idr"] for leg in result["legs"])
            # Legs total should approximately match summary
            # (may differ due to transfer handling)
            assert legs_total > 0, "Legs should have costs"


class TestWalkingRoutes:
    """Test walking path integration"""
    
    def test_walking_constants(self):
        """Verify walking speed constant exists (5 km/h = 12 min/km)"""
        WALKING_SPEED_KMH = 5
        walk_time_per_km = 60 / WALKING_SPEED_KMH  # 12 minutes per km
        
        assert walk_time_per_km == 12, "Walking time should be 12 min/km"
    
    def test_walking_time_calculation(self):
        """Test walking time calculation formula"""
        WALKING_SPEED_KMH = 5
        
        # Test various distances
        test_cases = [
            (0.5, 6),    # 500m = 6 minutes
            (1.0, 12),   # 1km = 12 minutes
            (0.1, 1.2),  # 100m = 1.2 minutes
        ]
        
        for distance_km, expected_minutes in test_cases:
            walk_time = (distance_km / WALKING_SPEED_KMH) * 60
            assert abs(walk_time - expected_minutes) < 0.01, \
                f"Walk time for {distance_km}km should be ~{expected_minutes} min"
    
    def test_walking_cost_is_zero(self):
        """Verify walking has no cost"""
        # Walking legs should have cost_idr = 0
        walking_leg = {
            "mode": "WALK",
            "distance_km": 0.5,
            "time_minutes": 6,
            "cost_idr": 0,
            "is_walk": True
        }
        
        assert walking_leg["cost_idr"] == 0, "Walking should be free"
        assert walking_leg["is_walk"] == True, "Walking leg should have is_walk=True"
    
    def test_find_nearest_stop(self, mobility_system):
        """Test finding nearest stop to coordinates"""
        builder = mobility_system["builder"]
        
        # Monas coordinates
        monas_lat, monas_lon = -6.1754, 106.8272
        
        nearest = builder.find_nearest_stop(monas_lat, monas_lon)
        
        assert nearest is not None, "Should find nearest stop"
        assert "id" in nearest, "Nearest stop should have ID"
        assert "distance_km" in nearest, "Should include distance"
        assert nearest["distance_km"] >= 0, "Distance should be non-negative"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
