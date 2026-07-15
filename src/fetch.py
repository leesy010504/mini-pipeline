import asyncio
import logging

import httpx

logger = logging.getLogger(__name__)

WEATHER_URL = "https://api.open-meteo.com/v1/forecast?latitude=37.5665&longitude=126.9780&hourly=temperature_2m,precipitation_probability&forecast_days=3&timezone=Asia/Seoul"  
COUNTRY_URL = "https://countries.dev/alpha/KR"
IP_URL = "http://ip-api.com/json/8.8.8.8"

async def fetch_weather(client: httpx.AsyncClient) -> dict:
    try : 
        response = await client.get(WEATHER_URL)
        response.raise_for_status()
        logger.info("Weather 응답 정상 (status=%s)", response.status_code)
        return response.json()
    except httpx.HTTPError as e:
        logger.error("Weather 수집 실패: %s", e)
        raise
    
async def fetch_country(client: httpx.AsyncClient) -> dict:
    try : 
        response = await client.get(COUNTRY_URL)
        response.raise_for_status()
        logger.info("Country 응답 정상 (status=%s)", response.status_code)
        return response.json()
    except httpx.HTTPError as e:
        logger.error("Country 수집 실패: %s", e)
        raise
    

async def fetch_ip(client: httpx.AsyncClient) -> dict:
    try : 
        response = await client.get(IP_URL)
        response.raise_for_status()
        logger.info("IP 응답 정상 (status=%s)", response.status_code)
        return response.json()
    except httpx.HTTPError as e:
        logger.error("IP 수집 실패: %s", e)
        raise
    
    

async def fetch_all() -> dict:
    async with httpx.AsyncClient(timeout = 20.0) as client:
        weather, country, ip = await asyncio.gather(
            fetch_weather(client),
            fetch_country(client),
            fetch_ip(client)
        )
    return {"weather": weather, "country": country, "ip": ip}

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    result = asyncio.run(fetch_all())
    print("수집 완료: ", list(result.values()))