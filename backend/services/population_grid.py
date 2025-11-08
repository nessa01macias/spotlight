"""
Statistics Finland - Population Grid Database (1km resolution)
https://stat.fi/tup/avoin-data/paikkatietoaineistot/vaestoruutuaineisto_1km_en.html

WFS API Documentation:
https://geo.stat.fi/geoserver/vaestoruutu/wfs
"""

import httpx
from typing import List, Dict, Any, Optional
import os
from datetime import datetime


class PopulationGridService:
    """Statistics Finland 1km population grid covering all of Finland"""

    def __init__(self):
        self.wfs_url = os.getenv(
            "STATFIN_WFS_URL",
            "https://geo.stat.fi/geoserver/vaestoruutu/wfs"
        )
        # Use latest available year (2023 as of 2025)
        self.current_year = 2023
        self.layer_name = f"vaestoruutu:vaki{self.current_year}_1km"
        self.cache = {}  # Simple in-memory cache

    async def get_population_grid(
        self,
        bbox: tuple[float, float, float, float]
    ) -> List[Dict[str, Any]]:
        """
        Get 1km population grid cells within bounding box for ALL of Finland

        Args:
            bbox: (min_lng, min_lat, max_lng, max_lat) in WGS84 (EPSG:4326)

        Returns:
            List of grid cells with population data:
            [
                {
                    "latitude": 60.17,
                    "longitude": 24.93,
                    "population": 1850,
                    "males": 920,
                    "females": 930,
                    "age_0_14": 245,
                    "age_15_64": 1280,
                    "age_65_plus": 325,
                    "grid_id": "1kmN6717E385",
                    "municipality": "Helsinki"
                },
                ...
            ]
        """
        min_lng, min_lat, max_lng, max_lat = bbox

        # Check cache
        cache_key = f"grid_{min_lng}_{min_lat}_{max_lng}_{max_lat}"
        if cache_key in self.cache:
            return self.cache[cache_key]

        params = {
            "service": "WFS",
            "version": "2.0.0",
            "request": "GetFeature",
            "typeName": self.layer_name,
            "outputFormat": "application/json",
            "srsName": "EPSG:4326",  # WGS84 for lat/lng
            "bbox": f"{min_lat},{min_lng},{max_lat},{max_lng},EPSG:4326"
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(self.wfs_url, params=params)
                response.raise_for_status()
                data = response.json()

                grid_cells = []
                for feature in data.get("features", []):
                    props = feature["properties"]
                    geometry = feature["geometry"]

                    # Get center of grid cell
                    if geometry["type"] == "Polygon":
                        coords = geometry["coordinates"][0]
                        center_lng = sum(c[0] for c in coords) / len(coords)
                        center_lat = sum(c[1] for c in coords) / len(coords)

                        grid_cells.append({
                            "latitude": center_lat,
                            "longitude": center_lng,
                            "population": props.get("vaesto", 0),
                            "males": props.get("miehet", 0),
                            "females": props.get("naiset", 0),
                            "age_0_14": props.get("ika_0_14", 0),
                            "age_15_64": props.get("ika_15_64", 0),
                            "age_65_plus": props.get("ika_65_", 0),
                            "grid_id": props.get("grd_id", ""),
                            "municipality": props.get("kunta", "")
                        })

                # Cache the result
                self.cache[cache_key] = grid_cells
                return grid_cells

            except httpx.HTTPError as e:
                print(f"Statistics Finland WFS error: {e}")
                return []

    async def get_population_in_area(
        self,
        lat: float,
        lng: float,
        radius_km: float = 1.0
    ) -> Dict[str, Any]:
        """
        Get population count within radius using 1km grid data

        Works for ANY location in Finland (not just Helsinki)

        Returns:
            {
                "total_population": 28000,
                "grid_cells_count": 16,
                "population_density": 8900,  # per km²
                "age_0_14": 3200,
                "age_15_64": 19600,
                "age_65_plus": 5200,
                "demographics": {
                    "age_0_14_percent": 11.4,
                    "age_15_64_percent": 70.0,
                    "age_65_plus_percent": 18.6
                }
            }
        """
        # Calculate bounding box for radius
        # Rough approximation: 1 degree lat ≈ 111km, 1 degree lng ≈ 55km at Finland latitude
        lat_offset = radius_km / 111.0
        lng_offset = radius_km / 55.0

        bbox = (
            lng - lng_offset,
            lat - lat_offset,
            lng + lng_offset,
            lat + lat_offset
        )

        grid_cells = await self.get_population_grid(bbox)

        # Filter to cells actually within radius using haversine
        from math import radians, sin, cos, sqrt, atan2

        def distance(lat1, lng1, lat2, lng2):
            R = 6371  # Earth radius in km
            dlat = radians(lat2 - lat1)
            dlng = radians(lng2 - lng1)
            a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlng/2)**2
            c = 2 * atan2(sqrt(a), sqrt(1-a))
            return R * c

        cells_in_radius = [
            cell for cell in grid_cells
            if distance(lat, lng, cell["latitude"], cell["longitude"]) <= radius_km
        ]

        # Aggregate demographics
        total_population = sum(cell["population"] for cell in cells_in_radius)
        age_0_14 = sum(cell["age_0_14"] for cell in cells_in_radius)
        age_15_64 = sum(cell["age_15_64"] for cell in cells_in_radius)
        age_65_plus = sum(cell["age_65_plus"] for cell in cells_in_radius)

        # Calculate percentages
        age_0_14_pct = (age_0_14 / total_population * 100) if total_population > 0 else 0
        age_15_64_pct = (age_15_64 / total_population * 100) if total_population > 0 else 0
        age_65_plus_pct = (age_65_plus / total_population * 100) if total_population > 0 else 0

        area_km2 = 3.14159 * (radius_km ** 2)
        density = total_population / area_km2 if area_km2 > 0 else 0

        return {
            "total_population": int(total_population),
            "grid_cells_count": len(cells_in_radius),
            "population_density": int(density),
            "age_0_14": int(age_0_14),
            "age_15_64": int(age_15_64),
            "age_65_plus": int(age_65_plus),
            "demographics": {
                "age_0_14_percent": round(age_0_14_pct, 1),
                "age_15_64_percent": round(age_15_64_pct, 1),
                "age_65_plus_percent": round(age_65_plus_pct, 1)
            }
        }

    async def get_heatmap_data_for_city(
        self,
        city_name: str,
        city_coords: tuple[float, float],
        radius_km: float = 10.0
    ) -> List[Dict[str, Any]]:
        """
        Generate heatmap data for any Finnish city

        Args:
            city_name: Name of the city (for logging)
            city_coords: (latitude, longitude) of city center
            radius_km: Radius to fetch grid data (default 10km)

        Returns:
            List of grid cells for heatmap visualization
        """
        lat, lng = city_coords

        # Calculate bbox
        lat_offset = radius_km / 111.0
        lng_offset = radius_km / 55.0

        bbox = (
            lng - lng_offset,
            lat - lat_offset,
            lng + lng_offset,
            lat + lat_offset
        )

        grid_cells = await self.get_population_grid(bbox)

        # Transform for heatmap (include population density as intensity)
        heatmap_data = []
        for cell in grid_cells:
            if cell["population"] > 0:  # Only show inhabited cells
                heatmap_data.append({
                    "latitude": cell["latitude"],
                    "longitude": cell["longitude"],
                    "population": cell["population"],
                    "intensity": min(cell["population"] / 100, 50)  # Normalize for heatmap
                })

        print(f"Generated heatmap for {city_name}: {len(heatmap_data)} populated cells")
        return heatmap_data

    def generate_mock_heatmap_data(
        self,
        city: str = "Helsinki"
    ) -> List[Dict[str, Any]]:
        """
        DEPRECATED: Use get_heatmap_data_for_city() instead

        This method is kept for backwards compatibility only.
        The new method fetches real data from Statistics Finland.
        """
        # Finnish city coordinates
        city_coords = {
            "Helsinki": (60.1699, 24.9384),
            "Tampere": (61.4978, 23.7610),
            "Turku": (60.4518, 22.2666),
            "Oulu": (65.0121, 25.4651),
            "Jyväskylä": (62.2426, 25.7473),
            "Kuopio": (62.8924, 27.6782),
            "Lahti": (60.9827, 25.6612),
            "Pori": (61.4847, 21.7972),
            "Vaasa": (63.0951, 21.6164),
        }

        coords = city_coords.get(city, city_coords["Helsinki"])

        print(f"⚠️ DEPRECATED: Using mock data for {city}. Please migrate to get_heatmap_data_for_city()")

        # Return placeholder - should be replaced with real API call
        return [
            {"latitude": coords[0], "longitude": coords[1], "population": 10000, "intensity": 50}
        ]
