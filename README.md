# Real-Time Fraud Detection — Risk Scoring System

Lightweight repository for a real-time fraud detection demo using Kafka, a simple API, a dashboard, and a trained model.

## Project overview
- Streams transaction data via Kafka (producer/consumer).
- Real-time scoring served from `api/main.py`.
- Simple dashboard in `dashboard/app.py` for visualization.
- Model training script in `model/train_model.py` produces `model/fraud_model.pkl`.
- Alerts are sent by `alerts/email_alert.py` (example only).

## Repository structure

- `api/` — FastAPI (or Flask) app entrypoint (`main.py`).
- `dashboard/` — small dashboard app (`app.py`).
- `kafka/` — `producer.py` and `consumer.py` to simulate/consume streams.
- `model/` — training and model artifacts.
- `alerts/` — alerting example code.
- `data/` — sample dataset `transactions.csv`.

## Quickstart (Windows)

1. Create and activate a virtual environment:

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

2. Install dependencies (add `requirements.txt` if missing):

```powershell
pip install -r requirements.txt
```

3. Run the API server:

```powershell
cd api
python main.py
```

4. Run Kafka producer (in another terminal):

```powershell
cd kafka
python producer.py
```

5. Run Kafka consumer / scoring pipeline:

```powershell
cd kafka
python consumer.py
```

6. Open the dashboard (if using a local server defined in `dashboard/app.py`).

## Model training

To retrain the model (this will overwrite `model/fraud_model.pkl`):

```powershell
cd model
python train_model.py
```

## Notes and recommendations

- The repository intentionally excludes the `venv/` directory and other large binary dependencies from git; `venv` is listed in `.gitignore`.
- Large compiled libraries (for example `xgboost.dll`, `llvmlite.dll`) should not be committed. Use Git LFS or store prebuilt wheels/artifacts in releases if you need them in the repo.
- Sensitive credentials (email passwords, API keys) should be stored in environment variables or a secrets manager — do not commit them.

## Docker / Compose

Two docker-compose files are present (`docker-compose.yml` and `docker-compose.updated.yml`) — inspect them for service definitions if you prefer containerized runs.

## License & Contact

This is a demo project. For questions or to collaborate, open an issue or contact the repository owner.
