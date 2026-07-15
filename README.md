# Azure Claude Weather Agent

An AI-powered weather assistant built using:

- Anthropic Claude
- Azure Container Apps
- Azure Maps
- Azure Container Registry
- Azure Key Vault
- FastAPI
- Docker
- Application Insights

## Features

- Current weather
- Daily forecasts
- Natural language weather answers
- Claude Tool Calling
- Secure secrets using Azure Key Vault

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt

uvicorn app.main:app --reload
```

## Test

https://<APP_URL>
https://<APP_URL>/health
https://<APP_URL>/docs
https://<APP_URL>/chat