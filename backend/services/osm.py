"""
OpenStreetMap Overpass API - Competitor POIs and infrastructure
https://wiki.openstreetmap.org/wiki/Overpass_API
"""

import httpx
from typing import List, Dict, Any, Optional
import os
import asyncio


class OSMService:
    """OpenStreetMap data via Overpass API"""

    def __init__(self):
        self.overpass_url = os.getenv("OVERPASS_URL", "https://overpass-api.de/api/interpreter")

    async def get_competitors(
        self,
        lat: float,
        lng: float,
        radius_m: int = 1000,
        concept: str = "QSR"
    ) -> List[Dict[str, Any]]:
        """
        Get competitor POIs within radius

        Args:
            lat, lng: Center point
            radius_m: Search radius in meters (default 1km)
            concept: Restaurant concept to filter appropriately

        Returns:
            List of competitor POIs with name, type, distance
        """
        # Map concepts to OSM tags
        amenity_filters = self._get_amenity_filters(concept)

        # Build Overpass QL query
        query = f"""
        [out:json][timeout:25];
        (
            {self._build_node_queries(lat, lng, radius_m, amenity_filters)}
        );
        out body;
        >;
        out skel qt;
        """

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    self.overpass_url,
                    data={"data": query},
                    timeout=30.0
                )
                response.raise_for_status()
                data = response.json()

                competitors = []
                for element in data.get("elements", []):
                    if element["type"] == "node":
                        competitors.append({
                            "name": element.get("tags", {}).get("name", "Unknown"),
                            "amenity": element.get("tags", {}).get("amenity", ""),
                            "cuisine": element.get("tags", {}).get("cuisine", ""),
                            "latitude": element["lat"],
                            "longitude": element["lon"],
                            "distance_m": self._haversine_distance(lat, lng, element["lat"], element["lon"])
                        })

                return sorted(competitors, key=lambda x: x["distance_m"])

            except httpx.HTTPError as e:
                print(f"OSM Overpass error: {e}")
                return []

    def _get_amenity_filters(self, concept: str) -> List[str]:
        """Map concept to OSM amenity types"""
        concept_map = {
            "QSR": ["fast_food", "restaurant"],
            "FastCasual": ["restaurant", "cafe"],
            "Coffee": ["cafe"],
            "CasualDining": ["restaurant"],
            "FineDining": ["restaurant"]
        }
        return concept_map.get(concept, ["restaurant", "fast_food", "cafe"])

    def _build_node_queries(self, lat: float, lng: float, radius_m: int, amenities: List[str]) -> str:
        """Build Overpass QL node queries for multiple amenity types"""
        queries = []
        for amenity in amenities:
            queries.append(f'node["amenity"="{amenity}"](around:{radius_m},{lat},{lng});')
        return "\n  ".join(queries)

    async def get_transit_stops(
        self,
        lat: float,
        lng: float,
        radius_m: int = 500
    ) -> Dict[str, Any]:
        """
        Get nearby public transit stops (metro, tram, bus)

        Returns:
            {
                "metro_stations": [...],
                "tram_stops": [...],
                "nearest_metro_distance_m": 450,
                "nearest_tram_distance_m": 120
            }
        """
        query = f"""
        [out:json][timeout:25];
        (
            node["railway"="subway_entrance"](around:{radius_m},{lat},{lng});
            node["railway"="tram_stop"](around:{radius_m},{lat},{lng});
            node["public_transport"="stop_position"](around:{radius_m},{lat},{lng});
        );
        out body;
        """

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    self.overpass_url,
                    data={"data": query},
                    timeout=30.0
                )
                response.raise_for_status()
                data = response.json()

                metro_stations = []
                tram_stops = []

                for element in data.get("elements", []):
                    if element["type"] == "node":
                        distance = self._haversine_distance(lat, lng, element["lat"], element["lon"])
                        stop_info = {
                            "name": element.get("tags", {}).get("name", "Unknown"),
                            "latitude": element["lat"],
                            "longitude": element["lon"],
                            "distance_m": distance
                        }

                        railway = element.get("tags", {}).get("railway")
                        if railway == "subway_entrance":
                            metro_stations.append(stop_info)
                        elif railway == "tram_stop":
                            tram_stops.append(stop_info)

                return {
                    "metro_stations": sorted(metro_stations, key=lambda x: x["distance_m"]),
                    "tram_stops": sorted(tram_stops, key=lambda x: x["distance_m"]),
                    "nearest_metro_distance_m": metro_stations[0]["distance_m"] if metro_stations else None,
                    "nearest_tram_distance_m": tram_stops[0]["distance_m"] if tram_stops else None
                }

            except httpx.HTTPError as e:
                print(f"Transit stops error: {e}")
                return {
                    "metro_stations": [],
                    "tram_stops": [],
                    "nearest_metro_distance_m": None,
                    "nearest_tram_distance_m": None
                }

    async def get_walkability_pois(
        self,
        lat: float,
        lng: float,
        radius_m: int = 500
    ) -> int:
        """
        Count diverse POIs for walkability score
        (shops, cafes, parks, etc.)
        """
        query = f"""
        [out:json][timeout:25];
        (
            node["amenity"](around:{radius_m},{lat},{lng});
            node["shop"](around:{radius_m},{lat},{lng});
        );
        out count;
        """

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    self.overpass_url,
                    data={"data": query},
                    timeout=30.0
                )
                response.raise_for_status()
                data = response.json()

                # Count total POIs
                return len(data.get("elements", []))

            except httpx.HTTPError as e:
                print(f"Walkability POIs error: {e}")
                return 0

    def _haversine_distance(self, lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """Calculate distance between two points in meters"""
        from math import radians, sin, cos, sqrt, atan2

        R = 6371000  # Earth radius in meters

        lat1_rad = radians(lat1)
        lat2_rad = radians(lat2)
        delta_lat = radians(lat2 - lat1)
        delta_lng = radians(lng2 - lng1)

        a = sin(delta_lat / 2) ** 2 + cos(lat1_rad) * cos(lat2_rad) * sin(delta_lng / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))

        return R * c
