"""
test_models -- src.models 검증 로직 pytest 테스트

Weather/Country/IPInfo 모델의 값 범위 제약과, parse_weather/parse_country/parse_ip가
잘못된 레코드를 어떻게 처리하는지(스킵 또는 None 반환)를 확인한다.

작성자: 이상윤

변경내역
  2026-07-15  최초 작성
"""

import pytest
from pydantic import ValidationError

from src.models import Country, IPInfo, Weather, parse_country, parse_ip, parse_weather


# 정상 범위의 값이면 Weather 모델이 그대로 생성되는지 확인한다.
def test_weather_record_valid():
    record = Weather(
        time = "2026=07-15T00:00",
        temperature_2m = 25.5,
        precipitation_probability = 80
    )
    assert record.temperature_2m == 25.5
    assert record.precipitation_probability == 80

# hourly 배열 중 범위를 벗어난 레코드는 걸러지고 정상 레코드만 남는지 확인한다.
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

# 필드가 모두 유효하면 parse_country가 Country 인스턴스를 정상 반환하는지 확인한다.
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

# population <= 0처럼 Field(gt=0) 제약을 어기면 parse_country가 None을 반환하는지 확인한다.
def test_parse_country_invalid_population_returns_none():
    raw = {
        "name": "Korea",
        "capital": "Seoul",
        "region": "Asia",
        "population": -1000  # 유효하지 않은 인구 수
    }

    assert parse_country(raw) is None

# 필드가 모두 유효하면 parse_ip가 IPInfo 인스턴스를 정상 반환하는지 확인한다.
def test_parse_ip_valid():
    raw = {"query": "8.8.8.8", "country": "United States", "city": "Ashburn",     
  "lat": 39.03, "lon": -77.5}
    ip_info = parse_ip(raw)
    assert isinstance(ip_info, IPInfo)
    assert ip_info.query == "8.8.8.8"

# precipitation_probability가 0~100 범위를 벗어나면 Weather 생성 시 ValidationError가 발생하는지 확인한다.
def test_weather_record_invalid_precipitation_raises():
    with pytest.raises(ValidationError):
        Weather(
            time = "2026-07-15T00:00",
            temperature_2m = 25.5,
            precipitation_probability = 150  # 범위를 초과한 값
        )
