from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

# DAG 설정 (이름, 시작일, 반복 주기 등)
default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}



# ... (위쪽 생략) ...

with DAG(
    'upbit_collect_dag',
    default_args=default_args,
    schedule_interval='* * * * *',
    catchup=False,
    tags=['upbit', 'bronze', 'silver', 'gold'], # 태그 업데이트
) as dag:

    # 1. 수집
    collect_task = BashOperator(
        task_id='collect_all_markets',
        bash_command='python /opt/airflow/src/collect_price.py'
    )

    # 2. 정제
    transform_task = BashOperator(
        task_id='transform_to_silver',
        bash_command='python /opt/airflow/src/transform_silver.py'
    )

    # 3. 집계 (새로 추가!)
    mart_task = BashOperator(
        task_id='build_gold_mart',
        bash_command='python /opt/airflow/src/build_gold.py'
    )

    # 순서: 수집 >> 정제 >> 요리
    collect_task >> transform_task >> mart_task