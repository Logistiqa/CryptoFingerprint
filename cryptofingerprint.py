import requests
import hashlib
from datetime import datetime
from collections import Counter

ADDRESS = "1BoatSLRHtKNngkdXEeobR76b53LETtpyT"  # Пример, замени на нужный адрес

API_URL = f"https://blockchain.info/rawaddr/{ADDRESS}"

def fetch_address_data():
    response = requests.get(API_URL)
    response.raise_for_status()
    return response.json()

def build_behavioral_fingerprint(data):
    txs = data.get("txs", [])
    if not txs:
        return "no-fingerprint"

    intervals = []
    values = []
    last_time = None
    outputs = []

    for tx in txs:
        timestamp = tx.get("time")
        if not timestamp:
            continue

        dt = datetime.utcfromtimestamp(timestamp)
        if last_time:
            delta = (dt - last_time).total_seconds()
            intervals.append(int(delta))
        last_time = dt

        total_out = sum([o.get("value", 0) for o in tx.get("out", [])])
        values.append(total_out)
        outputs.append(len(tx.get("out", [])))

    pattern = {
        "interval_mode": Counter(intervals).most_common(1)[0][0] if intervals else 0,
        "avg_tx_value": sum(values) // len(values),
        "common_output_count": Counter(outputs).most_common(1)[0][0] if outputs else 0,
        "tx_count": len(txs)
    }

    fingerprint_str = f"{pattern['interval_mode']}-{pattern['avg_tx_value']}-{pattern['common_output_count']}-{pattern['tx_count']}"
    fingerprint = hashlib.sha256(fingerprint_str.encode()).hexdigest()

    return fingerprint

def run():
    print("🔍 Получаем данные о кошельке...")
    data = fetch_address_data()
    fingerprint = build_behavioral_fingerprint(data)
    print(f"🧬 Поведенческий отпечаток кошелька: {fingerprint}")

if __name__ == "__main__":
    run()
