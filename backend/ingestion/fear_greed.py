import requests
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'db'))

from datetime import date
from connection import engine
from models import FearGreed
from sqlalchemy.orm import Session

def fetch_fear_greed():
    url = "https://api.alternative.me/fng/?limit=0"

    response = requests.get(url)
    data = response.json()

    entries = data["data"]

    with Session(engine) as session:
        count = 0
        for entry in entries:
            d = date.fromtimestamp(int(entry["timestamp"]))

            exists = session.query(FearGreed).filter_by(date=d).first()
            if exists:
                continue

            record = FearGreed(
                date=d,
                value=float(entry["value"]),
                classification=entry["value_classification"]
            )
            session.add(record)
            count += 1

        session.commit()
        print(f"{count} registros salvos no banco.")

fetch_fear_greed()
