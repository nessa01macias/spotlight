"""
Data Collector - Fetch and aggregate data from all sources
"""

from typing import Dict, Any, Optional
from services.digitransit import DigitransitService
from services.osm import OSMService
from services.statfin import StatFinService
from services.population_grid import PopulationGridService


class DataCollector:
    """Collect data from all Finnish data sources"""

    def __init__(self):
        self.geocoder = DigitransitService()
        self.osm = OSMService()
        self.statfin = StatFinService()
        self.population_grid = PopulationGridService()

    async def collect_site_data(
        self,
        address: str,
        concept: str
    ) -> Dict[str, Any]:
        """
        Collect all data for a specific address

        Returns complete feature set for scoring
        """
        # Step 1: Geocode address
        geocode_result = await self.geocoder.geocode_address(address)
        if not geocode_result:
            raise ValueError(f"Could not geocode address: {address}")

        lat = geocode_result["latitude"]
        lng = geocode_result["longitude"]
        postal_code = geocode_result.get("postal_code")

        # Step 2: Collect data in parallel
        import asyncio

        demographics_task = self.statfin.get_demographics_by_postal_code(postal_code) if postal_code else None
        population_task = self.population_grid.get_population_in_area(lat, lng, radius_km=1.0)
        competitors_task = self.osm.get_competitors(lat, lng, radius_m=1000, concept=concept)
        transit_task = self.osm.get_transit_stops(lat, lng, radius_m=500)
        walkability_task = self.osm.get_walkability_pois(lat, lng, radius_m=500)

        tasks = [
            demographics_task if demographics_task else asyncio.sleep(0),
            population_task,
            competitors_task,
            transit_task,
            walkability_task
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        demographics = results[0] if not isinstance(results[0], Exception) else None
        population_data = results[1] if not isinstance(results[1], Exception) else {}
        competitors = results[2] if not isinstance(results[2], Exception) else []
        transit = results[3] if not isinstance(results[3], Exception) else {}
        walkability_poi_count = results[4] if not isinstance(results[4], Exception) else 0

        # Step 3: Aggregate features
        features = {
            # Location
            "address": address,
            "latitude": lat,
            "longitude": lng,
            "postal_code": postal_code,

            # Demographics
            "population_1km": population_data.get("total_population"),
            "population_density": population_data.get("population_density"),
            "median_income": demographics.get("median_income") if demographics else None,
            "mean_income": demographics.get("mean_income") if demographics else None,
            "age_18_24_percent": demographics.get("age_18_24_percent") if demographics else None,
            "higher_education_percent": demographics.get("higher_education_percent") if demographics else None,

            # Competition
            "competitors_count": len(competitors),
            "competitors": competitors[:5],  # Top 5 closest
            "competitors_per_1k_residents": (
                len(competitors) / (population_data.get("total_population", 1) / 1000)
                if population_data.get("total_population", 0) > 0
                else 0
            ),

            # Transit & Access
            "nearest_metro_distance_m": transit.get("nearest_metro_distance_m"),
            "nearest_tram_distance_m": transit.get("nearest_tram_distance_m"),
            "metro_stations": transit.get("metro_stations", [])[:3],
            "tram_stops": transit.get("tram_stops", [])[:3],

            # Walkability
            "walkability_poi_count": walkability_poi_count,

            # Data quality
            "data_sources_available": {
                "geocoding": True,
                "demographics": demographics is not None,
                "population_grid": population_data.get("total_population") is not None,
                "competitors": len(competitors) > 0,
                "transit": transit.get("nearest_metro_distance_m") is not None or transit.get("nearest_tram_distance_m") is not None,
                "walkability": walkability_poi_count > 0
            }
        }

        return features

    async def collect_area_data(
        self,
        area_name: str,
        lat: float,
        lng: float,
        concept: str
    ) -> Dict[str, Any]:
        """
        Collect data for a pre-defined area (for discovery view)
        """
        # Use lat/lng directly instead of geocoding
        postal_code = None  # Could reverse geocode if needed

        # Collect data (similar to site data)
        import asyncio

        population_task = self.population_grid.get_population_in_area(lat, lng, radius_km=1.0)
        competitors_task = self.osm.get_competitors(lat, lng, radius_m=1000, concept=concept)
        transit_task = self.osm.get_transit_stops(lat, lng, radius_m=500)
        walkability_task = self.osm.get_walkability_pois(lat, lng, radius_m=500)

        results = await asyncio.gather(
            population_task,
            competitors_task,
            transit_task,
            walkability_task,
            return_exceptions=True
        )

        population_data = results[0] if not isinstance(results[0], Exception) else {}
        competitors = results[1] if not isinstance(results[1], Exception) else []
        transit = results[2] if not isinstance(results[2], Exception) else {}
        walkability_poi_count = results[3] if not isinstance(results[3], Exception) else 0

        # Estimate demographics (for MVP, use mock data)
        median_income = self._estimate_income_for_area(area_name)

        features = {
            "area_name": area_name,
            "latitude": lat,
            "longitude": lng,

            # Demographics
            "population_1km": population_data.get("total_population"),
            "population_density": population_data.get("population_density"),
            "median_income": median_income,

            # Competition
            "competitors_count": len(competitors),
            "competitors_per_1k_residents": (
                len(competitors) / (population_data.get("total_population", 1) / 1000)
                if population_data.get("total_population", 0) > 0
                else 0
            ),

            # Transit
            "nearest_metro_distance_m": transit.get("nearest_metro_distance_m"),
            "nearest_tram_distance_m": transit.get("nearest_tram_distance_m"),

            # Walkability
            "walkability_poi_count": walkability_poi_count,
        }

        return features

    def _estimate_income_for_area(self, area_name: str) -> Optional[float]:
        """
        Estimate median income for known Helsinki areas (MVP shortcut)
        """
        income_map = {
            "Kamppi": 54000,
            "Kallio": 42000,
            "Pasila": 45000,
            "Töölö": 58000,
            "Punavuori": 51000,
            "Kruununhaka": 48000,
            "Ullanlinna": 55000,
            "Eira": 68000,
        }
        return income_map.get(area_name)
