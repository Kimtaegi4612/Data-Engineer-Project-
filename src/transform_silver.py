import psycopg2

# 도커 내부 주소 사용
DB_CONFIG = {
    "host": "postgres",
    "port": 5432,
    "user": "user",
    "password": "password",
    "database": "upbit_dw"
}

def run_silver_transformation():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    try:
        print("--- Silver 변환 시작 ---")
        
        # ELT 핵심 쿼리: Bronze의 JSON을 찢어서 Silver로 복사
        # (주의: 중복 방지를 위해 간단히 최근 데이터만 넣는 방식 사용)
        query = """
        INSERT INTO silver.ticker (market, trade_date, trade_time, trade_price, acc_trade_volume)
        SELECT 
            raw_data->>'market',
            raw_data->>'trade_date_kst',
            raw_data->>'trade_time_kst',
            (raw_data->>'trade_price')::numeric,
            (raw_data->>'acc_trade_volume')::numeric
        FROM bronze.ticker_raw
        WHERE id > (SELECT COALESCE(MAX(id), 0) FROM silver.ticker_log) -- (임시) 로그 테이블 없으니 전체 다 넣으면 중복됨.
        -- 초보자용 단순화: 일단 다 지우고 다시 넣거나, 중복 무시하거나 해야 함.
        -- 오늘은 가장 쉬운 방법: "최근 수집된 1000개만 가져와서 중복 없으면 넣기"로 갑니다.
        """
        
        # 더 쉬운 방법 (초보자용): 
        # 복잡한 중복 처리 대신, 매번 실행할 때 "새로운 데이터만" 긁어오도록
        # Airflow가 관리하겠지만, 여기선 SQL 한방으로 처리합니다.
        
        elt_query = """
        INSERT INTO silver.ticker (market, trade_date, trade_time, trade_price, acc_trade_volume)
        SELECT 
            r.raw_data->>'market',
            r.raw_data->>'trade_date_kst',
            r.raw_data->>'trade_time_kst',
            (r.raw_data->>'trade_price')::numeric,
            (r.raw_data->>'acc_trade_volume')::numeric
        FROM bronze.ticker_raw r
        WHERE NOT EXISTS (
            SELECT 1 FROM silver.ticker s 
            WHERE s.market = r.raw_data->>'market' 
            AND s.trade_date = r.raw_data->>'trade_date_kst' 
            AND s.trade_time = r.raw_data->>'trade_time_kst'
        )
        """
        
        cur.execute(elt_query)
        rows = cur.rowcount
        conn.commit()
        print(f"[성공] {rows}건의 데이터를 Silver로 변환 적재했습니다.")
        
    except Exception as e:
        print("에러 발생:", e)
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    run_silver_transformation()