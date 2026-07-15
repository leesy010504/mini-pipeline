# mini-pipeline

Open-Meteo, RestCountries, ip-api 3개 API를 비동기로 수집해 Pydantic v2로 검증하고,
CSV/Parquet로 저장 후 읽기·쓰기 성능을 비교하는 미니 데이터 파이프라인.

## 사용 API

- Open-Meteo (서울 3일 시간대별 기온·강수확률)
- RestCountries (한국 국가 정보)
- ip-api (IP 기반 지역 정보)

## 설치

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 실행

```bash
python -m src.main
```

## 테스트 / 린트

```bash
pytest -v
ruff check .
```