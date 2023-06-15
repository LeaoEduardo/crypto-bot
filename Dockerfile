FROM apache/airflow:slim-2.6.1-python3.10

COPY requirements.txt requirements.txt

RUN pip install --no-cache-dir -r requirements.txt
COPY db/ db/

USER root
RUN chmod -R 777 db
USER airflow

RUN pip install --no-cache-dir ./db