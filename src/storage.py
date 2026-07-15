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