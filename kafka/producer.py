import json
import random
import time
from kafka import KafkaProducer

producer = KafkaProducer(
    bootstrap_servers="127.0.0.1:9092",
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

while True:
    txn = {
        "amount": random.randint(100, 10000),
        "hour": random.randint(0, 23),
        "location_risk": random.randint(0, 1),
        "device_risk": random.randint(0, 1),
        "previous_fraud_count": random.randint(0, 5),
    }

    producer.send("transactions", txn)
    print("Sent:", txn)
    time.sleep(2)
