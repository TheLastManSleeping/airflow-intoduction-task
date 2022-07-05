from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python_operator import PythonOperator
import pandas as pd
from pymongo import MongoClient

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2015, 6, 1),
    "email": ["airflow@airflow.com"],
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}


def lte_task():
    data = pd.read_csv('csv/tiktok_google_play_reviews.csv', delimiter=',')
    data = data.fillna('-')
    data = data.sort_values("at")
    data['content'].replace(regex=True, inplace=True, to_replace=r'[^A-Za-z0-9,:;\- ]', value=r'')
    client = MongoClient("mongodb://monke:27017/")
    db = client["tiktok_db"]
    coll = db["content"]
    data_dict = data.to_dict("records")
    coll.insert_many(data_dict)


dag = DAG("DAG", default_args=default_args, schedule_interval=timedelta(100000))
dag.max_active_tasks = 1

t1 = PythonOperator(task_id='lte_task', python_callable=lte_task, dag=dag)
