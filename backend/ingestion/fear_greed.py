import requests
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'db'))

from datetime import date
from connection import engine
from models import FearGreed
from sqlalchemy.dialects.postgresql import insert

def fetch_fear_greed() -> int:
    try:
        response = requests.get("https://api.alternative.me/fng/?limit=0", timeout=10)
        response.raise_for_status()
        entries = response.json()["data"]
        if not entries:
            return 0

        rows = [
            {
                "date": date.fromtimestamp(int(e["timestamp"])),
                "value": float(e["value"]),
                "classification": e["value_classification"],
            }
            for e in entries
        ]

        with engine.begin() as conn:
            stmt = insert(FearGreed).values(rows).on_conflict_do_nothing(index_elements=["date"])
            result = conn.execute(stmt)
            count = result.rowcount
            print(f"{count} registros de fear/greed salvos.")
            return count
    except Exception as e:
        print(f"Erro ao buscar fear/greed: {e}")
        return 0

if __name__ == "__main__":
    fetch_fear_greed()
