"""
Pydantic schemas for API request/response models
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from enum import Enum


class TransportMode(str, Enum):
    MRT = "MRT"
    LRT = "LRT"
    TJ = "TJ"
    ALL = "ALL"


class RouteStrategy(str, Enum):
    SINGLE = "single"
    MULTI = "multi"


class StartPoint(BaseModel):
    type: Literal["stop_id", "coord"] = "stop_id"
    value: str = Field(..., description="Stop ID or 'lat,long' coordinates")


class RouteRequest(BaseModel):
    start: StartPoint
    selected_places: List[str] = Field(default=[], description="List of POI IDs to visit")
    region: Optional[str] = Field(default=None, description="Region filter")
    mode: TransportMode = TransportMode.ALL
    strategy: RouteStrategy = RouteStrategy.SINGLE

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "start": {"type": "stop_id", "value": "Stop_MRT_13"},
                    "selected_places": ["Monas", "KotaTua"],
                    "mode": "ALL",
                    "strategy": "single"
                }
            ]
        }
    }


class StopInfo(BaseModel):
    id: str
    name: str
    lat: float
    long: float
    mode: Optional[str] = None
    distance_km: Optional[float] = None


class LegInfo(BaseModel):
    from_stop: str = Field(alias="from")
    from_name: str
    to_stop: str = Field(alias="to")
    to_name: str
    mode: str
    line: str
    distance_km: float
    time_minutes: float
    cost_idr: int
    is_transfer: bool = False
    destination_poi: Optional[str] = None

    model_config = {"populate_by_name": True}


class TransferInfo(BaseModel):
    at: str
    from_mode: str
    to_mode: str


class RouteSummary(BaseModel):
    total_distance_km: float
    total_time_minutes: float
    total_cost_idr: int


class GeoJSONFeature(BaseModel):
    type: str = "Feature"
    geometry: dict
    properties: dict


class GeoJSONResponse(BaseModel):
    type: str = "FeatureCollection"
    features: List[dict]


class RouteResponse(BaseModel):
    summary: RouteSummary
    legs: List[dict]
    path: Optional[List[str]] = None
    start_stop: Optional[dict] = None
    end_stop: Optional[dict] = None
    transfers: List[dict] = []
    visited_pois: Optional[List[str]] = None
    geometry: Optional[List[List[float]]] = None
    geojson: Optional[dict] = None
    error: Optional[str] = None


class PlaceOfInterest(BaseModel):
    id: str
    name: str
    lat: float
    long: float
    region: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    nearStop: Optional[str] = None


class Region(BaseModel):
    id: str
    name: str
    lat: Optional[float] = None
    long: Optional[float] = None


class DataSummary(BaseModel):
    total_triples: int
    total_stops: int
    mrt_stops: int
    lrt_stops: int
    tj_stops: int
    total_routes: int
    total_pois: int
    total_regions: int
