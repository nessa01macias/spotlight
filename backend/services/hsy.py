"""
HSY (Helsinki Region Environmental Services) - Population grid data
https://www.hsy.fi/en/environmental-information/open-data/avoin-data---sivut/population-grid-of-helsinki-metropolitan-area/
"""

import httpx
from typing import List, Dict, Any, Optional
import os


class HSYService:
    """Helsinki Region 250m population grid for heatmap data"""

    def __init__(self):
        self.wfs_url = os.getenv("HSY_WFS_URL", "https://kartta.hsy.fi/geoserver/wfs")

    async def get_population_grid(
        self,
        bbox: tuple[float, float, float, float]
    ) -> List[Dict[str, Any]]:
        """
        Get 250m population grid cells within bounding box

        Args:
            bbox: (min_lng, min_lat, max_lng, max_lat)

        Returns:
            List of grid cells with population data
        """
        min_lng, min_lat, max_lng, max_lat = bbox

        params = {
            "service": "WFS",
            "version": "2.0.0",
            "request": "GetFeature",
            "typeName": "asuminen_ja_maankaytto:Vaestotietoruudukko_250m",
            "outputFormat": "application/json",
            "srsName": "EPSG:4326",
            "bbox": f"{min_lat},{min_lng},{max_lat},{max_lng},EPSG:4326"
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    self.wfs_url,
                    params=params,
                    timeout=30.0
                )
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
                            "population": props.get("asukkaita", 0),
                            "grid_id": props.get("INDEX", "")
                        })

                return grid_cells

            except httpx.HTTPError as e:
                print(f"HSY WFS error: {e}")
                return []

    async def get_population_in_area(
        self,
        lat: float,
        lng: float,
        radius_km: float = 1.0
    ) -> Dict[str, Any]:
        """
        Get population count within radius using grid data

        Returns:
            {
                "total_population": 28000,
                "grid_cells_count": 16,
                "population_density": 8900  # per km²
            }
        """
        # Calculate bounding box for radius
        # Rough approximation: 1 degree lat ≈ 111km, 1 degree lng ≈ 55km at Helsinki latitude
        lat_offset = radius_km / 111.0
        lng_offset = radius_km / 55.0

        bbox = (
            lng - lng_offset,
            lat - lat_offset,
            lng + lng_offset,
            lat + lat_offset
        )

        grid_cells = await self.get_population_grid(bbox)

        # Filter to cells actually within radius
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

        total_population = sum(cell["population"] for cell in cells_in_radius)
        area_km2 = 3.14159 * (radius_km ** 2)
        density = total_population / area_km2 if area_km2 > 0 else 0

        return {
            "total_population": int(total_population),
            "grid_cells_count": len(cells_in_radius),
            "population_density": int(density)
        }

    def generate_mock_heatmap_data(
        self,
        city: str = "Helsinki"
    ) -> List[Dict[str, Any]]:
        """
        Generate mock heatmap data for MVP demo
        (Use this instead of real HSY data for speed during development)
        """
        # Pre-defined high-opportunity areas in Helsinki
        helsinki_areas = [
            # Kamppi - High score
            {"latitude": 60.1699, "longitude": 24.9342, "score": 91, "population": 28000},
            # Kallio - Medium-high score
            {"latitude": 60.1847, "longitude": 24.9504, "score": 82, "population": 24500},
            # Pasila - Medium score
            {"latitude": 60.1989, "longitude": 24.9339, "score": 71, "population": 8500},
            # Töölö - High score
            {"latitude": 60.1777, "longitude": 24.9157, "score": 85, "population": 18200},
            # Punavuori - High score
            {"latitude": 60.1585, "longitude": 24.9398, "score": 88, "population": 15800},
            # Kruununhaka - Medium score
            {"latitude": 60.1729, "longitude": 24.9560, "score": 78, "population": 5200},
            # Ullanlinna - High score
            {"latitude": 60.1586, "longitude": 24.9519, "score": 86, "population": 12400},
            # Eira - Very high score
            {"latitude": 60.1543, "longitude": 24.9374, "score": 93, "population": 6800},
        ]

        return helsinki_areas
