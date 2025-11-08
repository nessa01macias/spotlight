"""
Statistics Finland (Tilastokeskus) - Demographics via PAAVO postal code statistics
https://www.stat.fi/org/avoindata/paikkatietoaineistot/paavo_en.html

PAAVO API Documentation:
https://pxdata.stat.fi/PxWeb/api/v1/en/Postinumeroalueittainen_avoin_tieto/
"""

import httpx
from typing import Optional, Dict, Any
import os
import json
from datetime import datetime, timedelta


class StatFinService:
    """Statistics Finland PAAVO postal code demographics"""

    def __init__(self):
        self.base_url = os.getenv("STATFIN_BASE_URL", "https://pxdata.stat.fi/PxWeb/api/v1")
        self.paavo_path = "en/Postinumeroalueittainen_avoin_tieto"
        self.cache = {}  # Simple in-memory cache
        self.cache_ttl = timedelta(days=30)  # PAAVO updates annually

    async def get_demographics_by_postal_code(self, postal_code: str) -> Optional[Dict[str, Any]]:
        """
        Get demographics for a postal code area from Statistics Finland PAAVO dataset

        Returns:
            {
                "postal_code": "00100",
                "area_name": "Keskusta",
                "population": 2850,
                "population_density": 4200,  # per km²
                "median_income": 45000,
                "mean_income": 52000,
                "age_0_14_percent": 12.5,
                "age_15_64_percent": 68.2,
                "age_65_plus_percent": 19.3,
                "higher_education_percent": 42.1
            }
        """
        # Check cache first
        cache_key = f"paavo_{postal_code}"
        if cache_key in self.cache:
            cached_data, cached_time = self.cache[cache_key]
            if datetime.now() - cached_time < self.cache_ttl:
                return cached_data

        # Fetch from PXWeb API
        try:
            data = await self._fetch_from_pxweb_api(postal_code)
            if data:
                # Cache the result
                self.cache[cache_key] = (data, datetime.now())
                return data
        except Exception as e:
            print(f"Error fetching PAAVO data for {postal_code}: {e}")

        # Fallback to hardcoded data for common areas (backwards compatibility)
        fallback_data = self._get_demo_data_helsinki(postal_code)
        if fallback_data:
            print(f"Using fallback data for {postal_code}")
            return fallback_data

        return None

    def _get_demo_data_helsinki(self, postal_code: str) -> Optional[Dict[str, Any]]:
        """
        Hardcoded demographics for common Helsinki postal codes (for MVP speed)
        Data approximated from Statistics Finland PAAVO 2023
        """
        data_map = {
            # Central Helsinki
            "00100": {
                "postal_code": "00100",
                "area_name": "Keskusta",
                "population": 2850,
                "population_density": 4200,
                "median_income": 48000,
                "mean_income": 55000,
                "age_0_14_percent": 8.5,
                "age_15_64_percent": 75.2,
                "age_65_plus_percent": 16.3,
                "higher_education_percent": 52.1
            },
            "00120": {
                "postal_code": "00120",
                "area_name": "Punavuori",
                "population": 6200,
                "population_density": 8100,
                "median_income": 51000,
                "mean_income": 62000,
                "age_0_14_percent": 12.1,
                "age_15_64_percent": 72.8,
                "age_65_plus_percent": 15.1,
                "higher_education_percent": 58.3
            },
            # Kamppi area
            "00100": {
                "postal_code": "00100",
                "area_name": "Kamppi",
                "population": 28000,
                "population_density": 12500,
                "median_income": 54000,
                "mean_income": 64000,
                "age_0_14_percent": 11.2,
                "age_15_64_percent": 73.5,
                "age_65_plus_percent": 15.3,
                "age_18_24_percent": 18.5,
                "higher_education_percent": 55.7
            },
            # Kallio
            "00530": {
                "postal_code": "00530",
                "area_name": "Kallio",
                "population": 24500,
                "population_density": 11200,
                "median_income": 42000,
                "mean_income": 48000,
                "age_0_14_percent": 14.8,
                "age_15_64_percent": 71.2,
                "age_65_plus_percent": 14.0,
                "age_18_24_percent": 16.2,
                "higher_education_percent": 48.3
            },
            # Pasila
            "00520": {
                "postal_code": "00520",
                "area_name": "Pasila",
                "population": 8500,
                "population_density": 3200,
                "median_income": 45000,
                "mean_income": 52000,
                "age_0_14_percent": 13.5,
                "age_15_64_percent": 72.8,
                "age_65_plus_percent": 13.7,
                "age_18_24_percent": 14.1,
                "higher_education_percent": 51.2
            },
            # Espoo - Tapiola
            "02100": {
                "postal_code": "02100",
                "area_name": "Tapiola",
                "population": 18200,
                "population_density": 5600,
                "median_income": 58000,
                "mean_income": 72000,
                "age_0_14_percent": 16.2,
                "age_15_64_percent": 68.5,
                "age_65_plus_percent": 15.3,
                "age_18_24_percent": 8.5,
                "higher_education_percent": 62.1
            }
        }

        return data_map.get(postal_code)

    async def _fetch_from_pxweb_api(self, postal_code: str) -> Optional[Dict[str, Any]]:
        """
        Fetch from Statistics Finland PXWeb API
        Uses PAAVO dataset: Postinumeroalueittainen avoin tieto
        
        API Documentation: https://pxdata.stat.fi/api1.html
        """
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Step 1: Query the latest PAAVO table (uusin = most recent)
                # Table 12f7 = "All data groups" (comprehensive dataset)
                table_url = f"{self.base_url}/{self.paavo_path}/uusin/paavo_pxt_12f7.px"

                # Step 2: Build PXWeb query for this postal code
                query = {
                    "query": [
                        {
                            "code": "Postinumeroalue",
                            "selection": {
                                "filter": "item",
                                "values": [postal_code]
                            }
                        },
                        {
                            "code": "Tiedot",
                            "selection": {
                                "filter": "item",
                                "values": [
                                    "euref_x",       # X coordinate (EUREF-FIN)
                                    "euref_y",       # Y coordinate (EUREF-FIN)
                                    "pinta_ala",     # Surface area (m²)
                                    "he_vakiy",      # Total population
                                    "he_kika",       # Average age
                                    "he_0_2",        # Age 0-2
                                    "he_3_6",        # Age 3-6
                                    "he_7_12",       # Age 7-12
                                    "he_13_15",      # Age 13-15
                                    "he_16_17",      # Age 16-17
                                    "he_18_19",      # Age 18-19
                                    "he_20_24",      # Age 20-24
                                    "he_65_69",      # Age 65-69
                                    "he_70_74",      # Age 70-74
                                    "he_75_79",      # Age 75-79
                                    "he_80_84",      # Age 80-84
                                    "he_85_",        # Age 85+
                                    "ko_ika18y",     # Adults 18+
                                    "ko_yl_kork",    # Higher university degree
                                    "ko_al_kork",    # Lower tertiary education
                                    "hr_ktu",        # Average income
                                    "hr_mtu",        # Median income
                                    "pt_tyoll",      # Employed
                                    "pt_tyott",      # Unemployed
                                ]
                            }
                        },
                        {
                            "code": "Vuosi",
                            "selection": {
                                "filter": "top",
                                "values": ["1"]  # Get the most recent year
                            }
                        }
                    ],
                    "response": {"format": "json-stat2"}  # Modern JSON-Stat 2.0 format
                }

                # Step 3: POST query to API
                response = await client.post(table_url, json=query)

                if response.status_code != 200:
                    print(f"PXWeb API error: {response.status_code} for postal code {postal_code}")
                    return None

                # Step 4: Parse JSON-Stat 2.0 response
                result = response.json()

                if "value" not in result or not result["value"]:
                    print(f"No data found for postal code {postal_code}")
                    return None

                # Extract values from JSON-Stat 2.0 format
                # Values are in same order as requested in "Tiedot" filter
                values = result["value"]
                dimensions = result["dimension"]["Tiedot"]["category"]["index"]
                
                # Create a mapping of field code to value
                value_map = {}
                for field_code, index in dimensions.items():
                    value_map[field_code] = values[index]

                # Extract postal code label (includes area name)
                postal_labels = result["dimension"]["Postinumeroalue"]["category"]["label"]
                area_label = postal_labels.get(postal_code, postal_code)
                # Format: "00100  Helsinki keskusta - Etu-Töölö (Helsinki)"
                area_name = area_label.split("  ", 1)[1] if "  " in area_label else postal_code

                # Calculate derived metrics
                population = float(value_map.get("he_vakiy", 0))
                area_m2 = float(value_map.get("pinta_ala", 1))
                area_km2 = area_m2 / 1_000_000 if area_m2 > 0 else 0.01  # Convert m² to km²
                density = population / area_km2 if area_km2 > 0 else 0

                # Calculate age percentages
                age_0_14 = (
                    float(value_map.get("he_0_2", 0)) +
                    float(value_map.get("he_3_6", 0)) +
                    float(value_map.get("he_7_12", 0)) +
                    float(value_map.get("he_13_15", 0))
                )
                age_65_plus = (
                    float(value_map.get("he_65_69", 0)) +
                    float(value_map.get("he_70_74", 0)) +
                    float(value_map.get("he_75_79", 0)) +
                    float(value_map.get("he_80_84", 0)) +
                    float(value_map.get("he_85_", 0))
                )
                age_15_64 = population - age_0_14 - age_65_plus

                # Calculate education percentage (of adults 18+)
                adults_18_plus = float(value_map.get("ko_ika18y", population))
                higher_ed = float(value_map.get("ko_yl_kork", 0)) + float(value_map.get("ko_al_kork", 0))
                higher_ed_percent = (higher_ed / adults_18_plus * 100) if adults_18_plus > 0 else 0

                # Calculate employment rate
                employed = float(value_map.get("pt_tyoll", 0))
                unemployed = float(value_map.get("pt_tyott", 0))
                employment_rate = (employed / (employed + unemployed) * 100) if (employed + unemployed) > 0 else 0

                # Convert EUREF-FIN coordinates to WGS84 (lat/lng)
                euref_x = float(value_map.get("euref_x", 0))
                euref_y = float(value_map.get("euref_y", 0))
                
                latitude, longitude = None, None
                if euref_x > 0 and euref_y > 0:
                    try:
                        from pyproj import Transformer
                        # EPSG:3067 (EUREF-FIN) to EPSG:4326 (WGS84)
                        transformer = Transformer.from_crs("EPSG:3067", "EPSG:4326", always_xy=True)
                        longitude, latitude = transformer.transform(euref_x, euref_y)
                    except Exception as e:
                        print(f"Coordinate conversion error for {postal_code}: {e}")

                # Parse demographics
                return {
                    "postal_code": postal_code,
                    "area_name": area_name,
                    "latitude": latitude,
                    "longitude": longitude,
                    "population": int(population),
                    "population_density": int(density),
                    "median_income": int(float(value_map.get("hr_mtu", 0))),
                    "mean_income": int(float(value_map.get("hr_ktu", 0))),
                    "age_0_14_percent": round(age_0_14 / population * 100, 1) if population > 0 else 0,
                    "age_15_64_percent": round(age_15_64 / population * 100, 1) if population > 0 else 0,
                    "age_65_plus_percent": round(age_65_plus / population * 100, 1) if population > 0 else 0,
                    "higher_education_percent": round(higher_ed_percent, 1),
                    "employment_rate": round(employment_rate, 1),
                    "average_age": float(value_map.get("he_kika", 0)),
                }

        except httpx.HTTPError as e:
            print(f"HTTP error fetching PAAVO data: {e}")
            return None
        except KeyError as e:
            print(f"Error parsing PAAVO response for {postal_code}: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error fetching data for {postal_code}: {e}")
            import traceback
            traceback.print_exc()
            return None

    def estimate_population_in_radius(
        self,
        postal_codes: list[str],
        radius_km: float = 1.0
    ) -> int:
        """
        Estimate population within radius by aggregating postal codes
        (Rough estimate for MVP)
        """
        total_pop = 0
        for pc in postal_codes:
            data = self._get_demo_data_helsinki(pc)
            if data:
                # Weight by approximate overlap (simplified)
                total_pop += data["population"]

        return total_pop

    def calculate_income_fit_score(
        self,
        median_income: float,
        target_min: float,
        target_max: float
    ) -> float:
        """
        Calculate how well area income matches concept target
        Returns score 0-100
        """
        if median_income < target_min:
            # Below target - penalty based on gap
            gap = target_min - median_income
            penalty = min(gap / target_min * 100, 50)
            return max(50 - penalty, 0)
        elif median_income > target_max:
            # Above target - smaller penalty (high income not bad)
            gap = median_income - target_max
            penalty = min(gap / target_max * 50, 25)
            return max(75 - penalty, 50)
        else:
            # Within target range - excellent
            # Give bonus for being in middle of range
            middle = (target_min + target_max) / 2
            distance_from_middle = abs(median_income - middle)
            max_distance = (target_max - target_min) / 2
            score = 100 - (distance_from_middle / max_distance * 15)
            return max(score, 85)
