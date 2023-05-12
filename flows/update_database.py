import os
from datetime import datetime, timedelta

from airflow.decorators import task
from airflow import DAG
from dotenv import load_dotenv

from tasks.extract_latest_info import extract_latest_info
from tasks.load import load

load_dotenv("../.env")

EMAIL = os.environ.get("EMAIL", None)

with DAG(
    "update_database",
    default_args={
        "depends_on_past": True,
        "email": [EMAIL],
        "email_on_failure": True,
        "email_on_retry": False,
        "retries": 2,
        "retry_delay": timedelta(minutes=5),
        'execution_timeout': timedelta(seconds=300),
    },
    description="Update the database with latest info",
    schedule=timedelta(days=1),
    start_date=datetime(2023, 4, 1),
    catchup=True,
    tags=["etl"],
) as dag:

  csv_path = "..data/crypto_info.csv"

  @task(task_id="extract_daily_info")
  def extract_daily_info():
    extract_latest_info(output_path=csv_path)

  @task(task_id="upload_storage")
  def upload_storage():
    load(csv_path=csv_path)

  extract_daily_info() >> upload_storage()

  
  

