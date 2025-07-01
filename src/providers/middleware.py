from collections import defaultdict
from typing import List, Dict, Tuple
from datetime import datetime, date, timedelta
from dataclasses import dataclass
from models.forecast import ForecastData, Location

@dataclass
class AggregatedForecast:
    merged: ForecastData
    by_source: Dict[str, ForecastData]  

class ForecastAggregator:
    def __init__(self, providers: List):
        self.providers = providers  

    def aggregate_daily_forecasts(self, location: Location, date_range: Tuple[date, date]) -> List[AggregatedForecast]:
        all_forecasts: List[ForecastData] = []
        for provider in self.providers:
            try:
                forecasts = provider.fetch_forecast(location)
                all_forecasts.extend(forecasts)
            except Exception as e:
                print(f"Error en {provider.__class__.__name__}: {e}")

        start_date, end_date = date_range
        filtered = [
            f for f in all_forecasts
            if start_date <= f.date.date() <= end_date
        ]

        daily_buckets: Dict[Tuple[date, str], List[ForecastData]] = defaultdict(list)
        for forecast in filtered:
            key = (forecast.date.date(), forecast.source_name)
            daily_buckets[key].append(forecast)

        daily_by_source: Dict[date, Dict[str, ForecastData]] = defaultdict(dict)
        for (day, source), records in daily_buckets.items():
            averaged = self._average_daily(records, day, source)
            daily_by_source[day][source] = averaged

        results: List[AggregatedForecast] = []
        for day in sorted(daily_by_source.keys()):
            sources = daily_by_source[day]
            merged = self._merge_sources(day, list(sources.values()))
            results.append(AggregatedForecast(merged=merged, by_source=sources))

        return results

    def _average_daily(self, records: List[ForecastData], day: date, source: str) -> ForecastData:
        def avg(values):
            valid = [v for v in values if v is not None]
            return sum(valid) / len(valid) if valid else None

        return ForecastData(
            date=datetime.combine(day, datetime.min.time()),
            temperature=avg([f.temperature for f in records]),
            apparent_temperature=avg([f.apparent_temperature for f in records]),
            humidity=avg([f.humidity for f in records]),
            dew_point=avg([f.dew_point for f in records]),
            cloud_cover=avg([f.cloud_cover for f in records]),
            precipitation_prob=avg([f.precipitation_prob for f in records]),
            rain_intensity=avg([f.rain_intensity for f in records]),
            snow_intensity=avg([f.snow_intensity for f in records]),
            hail_probability=avg([f.hail_probability for f in records]),
            hail_size=avg([f.hail_size for f in records]),
            wind_speed=avg([f.wind_speed for f in records]),
            wind_gust=avg([f.wind_gust for f in records]),
            wind_direction=avg([f.wind_direction for f in records]),
            pressure_sea_level=avg([f.pressure_sea_level for f in records]),
            pressure_surface_level=avg([f.pressure_surface_level for f in records]),
            uv_index=avg([f.uv_index for f in records]),
            visibility=avg([f.visibility for f in records]),
            weather_code=None,
            description=None,
            source_name=source
        )

    def _merge_sources(self, day: date, forecasts: List[ForecastData]) -> ForecastData:
        def avg(values):
            valid = [v for v in values if v is not None]
            return sum(valid) / len(valid) if valid else None

        return ForecastData(
            date=datetime.combine(day, datetime.min.time()),
            temperature=avg([f.temperature for f in forecasts]),
            apparent_temperature=avg([f.apparent_temperature for f in forecasts]),
            humidity=avg([f.humidity for f in forecasts]),
            dew_point=avg([f.dew_point for f in forecasts]),
            cloud_cover=avg([f.cloud_cover for f in forecasts]),
            precipitation_prob=avg([f.precipitation_prob for f in forecasts]),
            rain_intensity=avg([f.rain_intensity for f in forecasts]),
            snow_intensity=avg([f.snow_intensity for f in forecasts]),
            hail_probability=avg([f.hail_probability for f in forecasts]),
            hail_size=avg([f.hail_size for f in forecasts]),
            wind_speed=avg([f.wind_speed for f in forecasts]),
            wind_gust=avg([f.wind_gust for f in forecasts]),
            wind_direction=avg([f.wind_direction for f in forecasts]),
            pressure_sea_level=avg([f.pressure_sea_level for f in forecasts]),
            pressure_surface_level=avg([f.pressure_surface_level for f in forecasts]),
            uv_index=avg([f.uv_index for f in forecasts]),
            visibility=avg([f.visibility for f in forecasts]),
            weather_code=None,
            description=None,
            source_name=", ".join(set(f.source_name for f in forecasts))
        )
    
    def prepare_llm_input(self, location: str, aggregated: List[AggregatedForecast]) -> dict:
        payload = {"location": location, "daily_summary": []}
        for day in aggregated:
            entry = {
                "date": day.merged.date.date().isoformat(),
                "averaged": {
                    "temperature": day.merged.temperature,
                    "apparent_temperature": day.merged.apparent_temperature,
                    "precipitation_probability": day.merged.precipitation_prob,
                    "wind_speed": day.merged.wind_speed,
                    "cloud_cover": day.merged.cloud_cover,
                    "uv_index": day.merged.uv_index,
                    "visibility": day.merged.visibility
                },
                "by_source": {
                    src: {
                        "temperature": f.temperature,
                        "precipitation_probability": f.precipitation_prob,
                        "wind_speed": f.wind_speed,
                        "cloud_cover": f.cloud_cover,
                        "uv_index": f.uv_index,
                        "visibility": f.visibility
                    }
                    for src, f in day.by_source.items()
                }
            }
            payload["daily_summary"].append(entry)
        return payload