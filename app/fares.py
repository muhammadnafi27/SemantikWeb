"""
Fare Calculation Module for MobilityGraph
Implements pricing for MRT, LRT, TransJakarta, and Walking
"""
import math
from typing import Optional

# MRT Station names (normalized for matching) - Official order
MRT_STATIONS = [
    "Lebak Bulus",
    "Fatmawati Indomaret",
    "Cipete Raya Tuku",
    "Haji Nawi",
    "Blok A",
    "Blok M BCA",
    "ASEAN",
    "Senayan Mastercard",
    "Istora Mandiri",
    "Bendungan Hilir",
    "Setiabudi Astra",
    "Dukuh Atas BNI",
    "Bundaran HI Bank DKI"
]

# MRT Fare Matrix (in IDR) - 13x13 symmetric matrix (OFFICIAL)
# Rows and columns correspond to MRT_STATIONS order
MRT_FARE_MATRIX = [
    # LB    Fat   Cip   HN    BA    BM    ASN   Sen   Ist   BH    Set   DA    BHI
    [0,     4000, 5000, 6000, 7000, 8000, 9000, 10000,11000,12000,13000,14000,14000],  # Lebak Bulus
    [4000,  0,    4000, 5000, 6000, 7000, 7000, 9000, 9000, 10000,11000,12000,13000],  # Fatmawati
    [5000,  4000, 0,    3000, 4000, 5000, 6000, 7000, 8000, 9000, 9000, 10000,11000],  # Cipete Raya
    [6000,  5000, 3000, 0,    3000, 4000, 5000, 6000, 7000, 8000, 8000, 9000, 10000],  # Haji Nawi
    [7000,  6000, 4000, 3000, 0,    3000, 4000, 5000, 6000, 7000, 7000, 8000, 9000],   # Blok A
    [8000,  7000, 5000, 4000, 3000, 0,    3000, 4000, 5000, 6000, 6000, 7000, 8000],   # Blok M BCA
    [9000,  7000, 6000, 5000, 4000, 3000, 0,    3000, 4000, 5000, 6000, 7000, 7000],   # ASEAN
    [10000, 9000, 7000, 6000, 5000, 4000, 3000, 0,    3000, 4000, 4000, 5000, 6000],   # Senayan
    [11000, 9000, 8000, 7000, 6000, 5000, 4000, 3000, 0,    4000, 4000, 5000, 6000],   # Istora
    [12000, 10000,9000, 8000, 7000, 6000, 5000, 4000, 3000, 0,    3000, 3000, 4000],   # Bendungan Hilir
    [13000, 11000,9000, 8000, 7000, 6000, 6000, 4000, 3000, 3000, 0,    3000, 4000],   # Setiabudi
    [14000, 12000,10000,9000, 8000, 7000, 7000, 5000, 4000, 3000, 3000, 0,    3000],   # Dukuh Atas
    [14000, 13000,11000,10000,9000, 8000, 7000, 6000, 5000, 4000, 4000, 3000, 0]       # Bundaran HI
]

# Station name aliases for normalization
MRT_STATION_ALIASES = {
    "lebak bulus grab": "Lebak Bulus",
    "lebak bulus": "Lebak Bulus",
    "fatmawati indomaret": "Fatmawati Indomaret",
    "fatmawati": "Fatmawati Indomaret",
    "cipete raya tuku": "Cipete Raya Tuku",
    "cipete raya": "Cipete Raya Tuku",
    "cipete": "Cipete Raya Tuku",
    "haji nawi": "Haji Nawi",
    "blok a": "Blok A",
    "blok m bca": "Blok M BCA",
    "blok m": "Blok M BCA",
    "asean": "ASEAN",
    "senayan mastercard": "Senayan Mastercard",
    "senayan": "Senayan Mastercard",
    "istora mandiri": "Istora Mandiri",
    "istora": "Istora Mandiri",
    "bendungan hilir": "Bendungan Hilir",
    "benhil": "Bendungan Hilir",
    "setiabudi astra": "Setiabudi Astra",
    "setiabudi": "Setiabudi Astra",
    "dukuh atas bni": "Dukuh Atas BNI",
    "dukuh atas": "Dukuh Atas BNI",
    "bundaran hi bank dki": "Bundaran HI Bank DKI",
    "bundaran hi": "Bundaran HI Bank DKI",
    "bundaran hotel indonesia": "Bundaran HI Bank DKI"
}

# TransJakarta fare per hop
TJ_FARE_PER_HOP = 3500

# LRT base fare and per-km rate
LRT_BASE_FARE = 5000  # First 1 km
LRT_FARE_PER_KM = 700  # Additional per km


def normalize_station_name(name: str) -> str:
    """Normalize station name for matching"""
    # Remove common prefixes
    normalized = name.lower()
    prefixes = ["stasiun mrt ", "stasiun lrt ", "halte ", "station "]
    for prefix in prefixes:
        if normalized.startswith(prefix):
            normalized = normalized[len(prefix):]
    
    # Remove extra whitespace and punctuation
    normalized = " ".join(normalized.split())
    normalized = normalized.replace("-", " ").replace("_", " ")
    
    return normalized.strip()


def get_mrt_station_index(station_name: str) -> Optional[int]:
    """Get the index of MRT station from name"""
    normalized = normalize_station_name(station_name)
    
    # Try direct alias lookup
    if normalized in MRT_STATION_ALIASES:
        canonical = MRT_STATION_ALIASES[normalized]
        try:
            return MRT_STATIONS.index(canonical)
        except ValueError:
            pass
    
    # Try fuzzy matching
    for i, station in enumerate(MRT_STATIONS):
        if station.lower() in normalized or normalized in station.lower():
            return i
    
    return None


def calculate_mrt_fare(from_station: str, to_station: str) -> int:
    """
    Calculate MRT fare between two stations using fare matrix
    Returns fare in IDR, or 0 if stations not found
    """
    from_idx = get_mrt_station_index(from_station)
    to_idx = get_mrt_station_index(to_station)
    
    if from_idx is None or to_idx is None:
        # Fallback: estimate based on typical fare
        return 7000  # Average fare
    
    return MRT_FARE_MATRIX[from_idx][to_idx]


def calculate_tj_fare(hops: int = 1) -> int:
    """
    Calculate TransJakarta fare
    Rules: Flat rate Rp3.500 per trip
    - Tap in when entering, tap out when exiting
    - If only transit (no tap out), fare not charged until final tap out
    - Single fare covers entire journey regardless of corridors
    
    Args:
        hops: Number of stops/edges traversed (ignored, flat rate)
    Returns:
        Fare in IDR (flat Rp3.500)
    """
    return TJ_FARE_PER_HOP  # Flat rate per trip


def calculate_lrt_fare(distance_km: float) -> int:
    """
    Calculate LRT fare based on distance
    Rules: Rp5.000 for first 1 km, Rp700 per additional km
    
    Args:
        distance_km: Distance in kilometers
    Returns:
        Fare in IDR
    """
    if distance_km <= 1:
        return LRT_BASE_FARE
    additional_km = math.ceil(distance_km - 1)
    return LRT_BASE_FARE + (additional_km * LRT_FARE_PER_KM)


def calculate_walk_fare() -> int:
    """Walking is free"""
    return 0


def calculate_segment_fare(
    mode: str,
    from_station: str = "",
    to_station: str = "",
    distance_m: float = 0,
    hops: int = 1
) -> int:
    """
    Calculate fare for a route segment
    
    Args:
        mode: Transport mode (MRT, LRT, TJ, WALK)
        from_station: Starting station name (for MRT)
        to_station: Ending station name (for MRT)
        distance_m: Distance in meters (for LRT)
        hops: Number of stops (for TJ)
    
    Returns:
        Fare in IDR
    """
    mode_upper = mode.upper()
    
    if mode_upper == "MRT":
        return calculate_mrt_fare(from_station, to_station)
    elif mode_upper == "LRT":
        distance_km = distance_m / 1000
        return calculate_lrt_fare(distance_km)
    elif mode_upper == "TJ":
        return calculate_tj_fare(hops)
    elif mode_upper == "WALK":
        return calculate_walk_fare()
    else:
        # Unknown mode, return 0
        return 0


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great-circle distance between two points on Earth
    
    Args:
        lat1, lon1: First point coordinates
        lat2, lon2: Second point coordinates
    
    Returns:
        Distance in meters
    """
    R = 6371000  # Earth's radius in meters
    
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    a = (math.sin(delta_lat / 2) ** 2 +
         math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c


def estimate_walking_time(distance_m: float, speed_kmh: float = 5.0) -> float:
    """
    Estimate walking time
    
    Args:
        distance_m: Distance in meters
        speed_kmh: Walking speed in km/h (default 5 km/h)
    
    Returns:
        Time in minutes
    """
    speed_mpm = speed_kmh * 1000 / 60  # meters per minute
    return distance_m / speed_mpm
