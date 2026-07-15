import pytest
from pydantic import ValidationError

from src.models import Country, IPInfo, Weather, parse_country, parse_ip, parse_weather


def test_weather_record_valid():
    record = Weather(
        time = "2026=07-15T00:00",
        temperature_2m = 25.5,
        precipitation_probability = 80
    )
    assert record.temperature_2m == 25.5
    assert record.precipitation_probability == 80

def test_parse_weather_skips_invalid_record():
    raw = {
        "hourly": {
            "time": ["2026-07-15T00:00", "2026-07-15T01:00"],
            "temperature_2m": [25.1, 26.0],
            "precipitation_probability": [80, 160] # 두번째는 범위 초과
        }
    }
    records = parse_weather(raw)
    assert len(records) == 1
    assert records[0].precipitation_probability == 80

def test_parse_country_valid():
    raw = {
        "name": "Korea",
        "capital": "Seoul",
        "region": "Asia",
        "population": 51780579
    }
    country = parse_country(raw)
    isinstance(country, Country)
    assert country.capital == "Seoul"

def test_parse_country_invalid_population_returns_none():
    raw = {
        "name": "Korea",
        "capital": "Seoul",
        "region": "Asia",
        "population": -1000  # 유효하지 않은 인구 수
    }

    assert parse_country(raw) is None

def test_parse_ip_valid():
    raw = {"query": "8.8.8.8", "country": "United States", "city": "Ashburn",     
  "lat": 39.03, "lon": -77.5}
    ip_info = parse_ip(raw)
    assert isinstance(ip_info, IPInfo)
    assert ip_info.query == "8.8.8.8"

def test_weather_record_invalid_precipitation_raises():
    with pytest.raises(ValidationError):
        Weather(
            time = "2026-07-15T00:00",
            temperature_2m = 25.5,
            precipitation_probability = 150  # 범위를 초과한 값
        )
