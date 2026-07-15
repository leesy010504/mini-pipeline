import logging

from pydantic import BaseModel, Field, ValidationError

logger = logging.getLogger(__name__)

class Weather(BaseModel):
    time: str
    temperature_2m: float
    precipitation_probability: int = Field(..., ge=0, le=100)  # 0~100 사이의 값만 허용

class Country(BaseModel):
    name: str
    capital: str
    region: str
    population: int

class IPInfo(BaseModel):
    query: str
    country: str
    city: str
    lat: float
    lon: float

def parse_weather(data: dict) -> list[Weather]:
    hourly = data.get("hourly", {})
    times = hourly.get("time", [])
    temperatures = hourly.get("temperature_2m", [])
    precipitation_probs = hourly.get("precipitation_probability", [])

    records = []
    for time, temp, precip in zip(times, temperatures, precipitation_probs):
        data = {"time": time, "temperature_2m": temp, "precipitation_probability": precip}
        try:
            records.append(Weather.model_validate(data))
        except ValidationError as e:
            logger.error("Weather 데이터 검증 실패(time: %s): %s", time, e)
    return records

def parse_country(data: dict) -> CountryInfo:
    data = {
        "name": data["name"],
        "capital": data["capital"],
        "population": data["population"],
        "region": data["region"],
    }
    try:
        return CountryInfo.model_validate(data)
    except ValidationError as e:
        logger.error("Country 레코드 검증 실패: %s", e)
        return None

def parse_ip(data: dict) -> IPInfo:
    data = {
        "query": data["query"],
        "country": data["country"],
        "city": data["city"],
        "lat": data["lat"],
        "lon": data["lon"],
    }
    try:
        return IPInfo.model_validate(data)
    except ValidationError as e:
        logger.error("IP 레코드 검증 실패: %s", e)
        return None