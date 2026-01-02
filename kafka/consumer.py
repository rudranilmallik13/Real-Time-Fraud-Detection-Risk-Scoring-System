import json
import requests
from kafka import KafkaConsumer

consumer = KafkaConsumer(
    "transactions",
    bootstrap_servers="127.0.0.1:9092",
    value_deserializer=lambda v: json.loads(v.decode("utf-8"))
)

print("🚀 Consumer started")

for msg in consumer:
    txn = msg.value
    try:
        res = requests.post("http://127.0.0.1:8000/predict", json=txn)
        print("Scored:", res.json())
    except Exception as e:
        print("API error:", e)
