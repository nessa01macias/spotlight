"""
Digitransit Pelias API - Geocoding for Finnish addresses
https://digitransit.fi/en/developers/apis/2-geocoding-api/
"""

import httpx
from typing import Optional, Dict, Any, List
import os


class DigitransitService:
    """Geocoding service using Digitransit Pelias API"""

    def __init__(self):
        self.base_url = os.getenv("DIGITRANSIT_URL", "https://api.digitransit.fi")
        self.geocoding_endpoint = f"{self.base_url}/geocoding/v1"
        # Digitransit now requires a subscription key header (get free key from digitransit.fi)
        self.api_key = os.getenv("DIGITRANSIT_API_KEY")

    async def geocode_address(self, address: str) -> Optional[Dict[str, Any]]:
        """
        Geocode a Finnish address to lat/lng

        Returns:
            {
                "address": "Mannerheimintie 20, Helsinki",
                "latitude": 60.1699,
                "longitude": 24.9384,
                "postal_code": "00100",
                "confidence": 0.95
            }
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.geocoding_endpoint}/search",
                    params={
                        "text": address,
                        "size": 1,  # Only need top result
                        "lang": "fi"
                    },
                    timeout=10.0
                )
                response.raise_for_status()
                data = response.json()

                if data.get("features") and len(data["features"]) > 0:
                    feature = data["features"][0]
                    coords = feature["geometry"]["coordinates"]
                    props = feature["properties"]

                    return {
                        "address": props.get("label", address),
                        "latitude": coords[1],
                        "longitude": coords[0],
                        "postal_code": props.get("postalcode"),
                        "city": props.get("locality", "Helsinki"),
                        "confidence": props.get("confidence", 0.5)
                    }
                return None

            except httpx.HTTPError as e:
                print(f"Digitransit geocoding error: {e}")
                return None

    async def reverse_geocode(self, lat: float, lng: float) -> Optional[Dict[str, Any]]:
        """
        Reverse geocode coordinates to address
        
        MVP: If no API key, returns mock address with coords
        """
        # If no API key, skip API call and return mock
        if not self.api_key:
            return {
                "address": f"Helsinki, {lat:.4f}, {lng:.4f}",
                "postal_code": "00100",
                "city": "Helsinki"
            }
        
        async with httpx.AsyncClient() as client:
            try:
                headers = {"digitransit-subscription-key": self.api_key}
                response = await client.get(
                    f"{self.geocoding_endpoint}/reverse",
                    params={
                        "point.lat": lat,
                        "point.lon": lng,
                        "size": 1,
                        "lang": "fi"
                    },
                    headers=headers,
                    timeout=10.0
                )
                response.raise_for_status()
                data = response.json()

                if data.get("features") and len(data["features"]) > 0:
                    feature = data["features"][0]
                    props = feature["properties"]

                    return {
                        "address": props.get("label", ""),
                        "postal_code": props.get("postalcode"),
                        "city": props.get("locality", "Helsinki")
                    }
                return None

            except httpx.HTTPError as e:
                # Fallback to mock on error
                return {
                    "address": f"Helsinki, {lat:.4f}, {lng:.4f}",
                    "postal_code": "00100",
                    "city": "Helsinki"
                }

    async def search_places(self, query: str, boundary_circle: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """
        Search for places (for autocomplete, etc.)

        Args:
            query: Search text
            boundary_circle: (lat, lng, radius_km) to limit search area
        """
        params = {
            "text": query,
            "size": 10,
            "lang": "fi"
        }

        if boundary_circle:
            lat, lng, radius_km = boundary_circle
            params["boundary.circle.lat"] = lat
            params["boundary.circle.lon"] = lng
            params["boundary.circle.radius"] = radius_km

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.geocoding_endpoint}/search",
                    params=params,
                    timeout=10.0
                )
                response.raise_for_status()
                data = response.json()

                results = []
                for feature in data.get("features", []):
                    coords = feature["geometry"]["coordinates"]
                    props = feature["properties"]
                    results.append({
                        "label": props.get("label", ""),
                        "latitude": coords[1],
                        "longitude": coords[0],
                        "postal_code": props.get("postalcode"),
                        "confidence": props.get("confidence", 0.5)
                    })

                return results

            except httpx.HTTPError as e:
                print(f"Place search error: {e}")
                return []

    def is_helsinki_area(self, lat: float, lng: float) -> bool:
        """Check if coordinates are within Greater Helsinki area"""
        # Rough bounding box for Helsinki region
        # Helsinki coordinates: 60.1699° N, 24.9384° E
        return (60.0 <= lat <= 60.5) and (24.6 <= lng <= 25.3)
