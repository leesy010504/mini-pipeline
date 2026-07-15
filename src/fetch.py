"""
fetch -- 외부 API 3종을 비동기로 수집하는 모듈

기능: Open-Meteo(서울 3일 시간대별 기온·강수확률), RestCountries(한국 국가 정보),
ip-api(IP 기반 지역 정보)를 httpx.AsyncClient로 동시에 호출한다.

작성자: 이상윤

구성
  fetch_weather / fetch_country / fetch_ip -- 개별 API 호출, 실패 시 로깅 후 raise
  fetch_all                                -- asyncio.gather로 3개 요청을 동시 실행

변경내역
  2026-07-15  최초 작성
"""
import asyncio
import logging

import httpx

logger = logging.getLogger(__name__)

SOURCES = {
    "weather": "https://api.open-meteo.com/v1/forecast?latitude=37.5665&longitude=126.9780&hourly=temperature_2m,precipitation_probability&forecast_days=3&timezone=Asia/Seoul",
    "country": "https://countries.dev/alpha/KR",
    "ip": "http://ip-api.com/json/8.8.8.8"
}

# 이름표 하나(name)에 대해 URL 하나를 호출하고 JSON으로 반환한다.
async def fetch_json(client: httpx.AsyncClient, name: str, url: str) -> dict:
    try:
        response = await client.get(url)
        response.raise_for_status()
        logger.info("%s 응답 정상 (status=%s)", name, response.status_code)
        return response.json()
    except httpx.HTTPError as e:
        logger.error("%s 수집 실패: %s", name, e)
        raise

# SOURCES에 등록된 API를 전부 동시에 호출해 {이름: 응답} 딕셔너리로 모은다.
async def fetch_all() -> dict:
    async with httpx.AsyncClient(timeout=20.0) as client:
        async with asyncio.TaskGroup() as tg:
            tasks = {
                name: tg.create_task(fetch_json(client, name, url))
                for name, url in SOURCES.items()
            }
    return {name: t.result() for name, t in tasks.items()}


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    result = asyncio.run(fetch_all())
    print("수집 완료: ", list(result.keys()))