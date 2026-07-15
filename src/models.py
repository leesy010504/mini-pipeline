"""
models -- 수집 데이터 검증용 Pydantic 스키마

fetch 모듈이 받아온 raw dict를 Weather/Country/IPInfo 모델로 검증한다.
레코드 하나의 검증 실패가 전체 파이프라인을 중단시키지 않도록,
예외를 올리는 대신 로깅만 남기고 넘어간다.

작성자: 이상윤

구성
  Weather / Country / IPInfo               -- 응답 스키마 정의 (Field로 값 범위 제약)
  parse_weather / parse_country / parse_ip -- raw dict -> 모델 변환 + 검증

변경내역
  2026-07-15  최초 작성
"""

import logging

from pydantic import BaseModel, Field, ValidationError

logger = logging.getLogger(__name__)

# Open-Meteo 시간대별 응답 스키마
class Weather(BaseModel):
    time: str
    temperature_2m: float
    precipitation_probability: int = Field(..., ge=0, le=100)  # 0~100 사이의 값만 허용

# RestCountries 응답 스키마
class Country(BaseModel):
    name: str
    capital: str
    region: str
    population: int = Field(gt=0)

# ip-api 응답 스키마
class IPInfo(BaseModel):
    query: str
    country: str
    city: str
    lat: float
    lon: float

# hourly 배열 3개(time/온도/강수확률)를 같은 인덱스끼리 묶어 레코드별로 검증한다.
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
            # 한 시간대 검증만 실패한 것이므로 나머지는 계속 처리한다.
            logger.error("Weather 데이터 검증 실패(time: %s): %s", time, e)
    return records

# 필요한 필드만 추려 Country로 검증하고, 실패하면 None을 반환한다.
def parse_country(data: dict) -> Country:
    data = {
        "name": data["name"],
        "capital": data["capital"],
        "population": data["population"],
        "region": data["region"],
    }
    try:
        return Country.model_validate(data)
    except ValidationError as e:
        logger.error("Country 레코드 검증 실패: %s", e)
        return None

# 필요한 필드만 추려 IPInfo로 검증하고, 실패하면 None을 반환한다.
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