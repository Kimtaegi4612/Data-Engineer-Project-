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



with DAG(
    'upbit_collect_dag',
    default_args=default_args,
    schedule_interval='* * * * *',  # 크론 표현식: 매 1분마다 실행
    catchup=False,  # 과거 데이터는 무시하고 현재부터 실행
    tags=['upbit', 'bronze', 'silver'],
) as dag:
    
    # 1. 수집 태스크 (기존)
    collect_task = BashOperator(
        task_id='collect_all_markets',
        bash_command='python /opt/airflow/src/collect_price.py'
    )

    # 2. 변환 태스크 Silver 변환 (새로 추가!)
    transform_task = BashOperator(
        task_id='transform_to_silver',
        bash_command='python /opt/airflow/src/transform_silver.py'
    )

    # 순서 연결: 수집이 끝나면(>>) 변환해라
    collect_task >> transform_task
