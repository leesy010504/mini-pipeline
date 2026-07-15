"""
storage -- CSV/Parquet 저장 및 읽기·쓰기 성능 비교

Pydantic 모델 리스트를 DataFrame으로 변환한 뒤 CSV와 Parquet 두 포맷으로
저장하고, 각각의 쓰기/읽기 소요 시간과 파일 크기를 측정해 비교한다.

작성자: 이상윤

구성
  records_to_df       -- BaseModel 리스트 -> DataFrame 변환
  save_and_benchmark  -- CSV/Parquet 저장 + 읽기 재실행 + 시간/용량 측정
  print_benchmark     -- 측정 결과를 표 형태로 출력

변경내역
  2026-07-15  최초 작성
"""


import time
from pathlib import Path

import pandas as pd
from pydantic import BaseModel

DATA_DIR = Path("data")

def records_to_df(records: list[BaseModel]) -> pd.DataFrame:
    return pd.DataFrame([r.model_dump() for r in records])

def save_and_benchmark(df: pd.DataFrame, filename: str) -> dict:
    DATA_DIR.mkdir(exist_ok=True)
    csv_path = DATA_DIR / f"{filename}.csv"
    parquet_path = DATA_DIR / f"{filename}.parquet"

    t0 = time.perf_counter()
    df.to_csv(csv_path, index = False)
    csv_write_time = time.perf_counter() - t0

    t0 = time.perf_counter()
    pd.read_csv(csv_path)
    csv_read_time = time.perf_counter() - t0
  
    t0 = time.perf_counter()
    df.to_parquet(parquet_path, engine = "pyarrow")
    parquet_write_time = time.perf_counter() - t0

    t0 = time.perf_counter()
    pd.read_parquet(parquet_path)
    parquet_read_time = time.perf_counter() - t0

    return {
        "csv": {
            "write_time": csv_write_time,
            "read_time": csv_read_time,
            "size_bytes": csv_path.stat().st_size / 1024
        },
        "parquet": {
            "write_time": parquet_write_time,
            "read_time": parquet_read_time,
            "size_bytes": parquet_path.stat().st_size / 1024
        }
    }

def print_benchmark(name: str, result: dict):
    print(f"\n {name} CSV vs Parquet Benchmark:")
    print(f"{'format':<10}{'write(s)':<12}{'read(s)':<12}{'size(KB)':<10}")
    for fmt, stats in result.items():
        print(
            f"{fmt:<10}{stats['write_time']:<12.4f}"
            f"{stats['read_time']:<12.4f}{stats['size_bytes']:<10.2f}"
        )