Crypto Bot
===
Crypto bot stands for a fully automated pipeline to predict cryptocurrency prices over a certain period of time.

Some of the technologies involved are:
* [Mage](https://www.mage.ai/): a data orchestrator self-claimed "the modern replacement for Airflow";
* [AutoTS](https://github.com/winedarksea/AutoTS): extraordinary library for forecasting on time series;
* [MLFlow](https://mlflow.org/docs/latest/index.html): open-source MLOps library, used for model tracking and experimenting.

Data was fetched from [Binance API](https://www.binance.com/en/binance-api) and [CoinGecko](https://www.coingecko.com/).

### Requirements
* You should have [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/) installed.

## Quickstart

To setup your environment, just run:
```
docker compose up
```
This will automatically install all dependencies and run the containers.
You can access the Mage editor on [localhost:6789](localhost:6789) and the mlflow ui at [localhost:5050](localhost:5050).

See [docker-compose.yml](docker-compose.yml) and [Dockerfile](Dockerfile) for more information.



