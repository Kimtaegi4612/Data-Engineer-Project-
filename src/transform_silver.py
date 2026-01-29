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
        
        # 현업 피드백 반영: 
        # 재처리를 위해 "이미 Silver에 있는 데이터(중복)"는 건너뛰고 
        # "새로 들어온 Bronze 데이터"만 넣는 로직.
        
        elt_query = """
        INSERT INTO silver.ticker (market, trade_date, trade_time, trade_price, acc_trade_volume, ingested_at)
        SELECT 
            r.raw_data->>'market',
            r.raw_data->>'trade_date_kst',
            r.raw_data->>'trade_time_kst',
            (r.raw_data->>'trade_price')::numeric,
            (r.raw_data->>'acc_trade_volume')::numeric,
            NOW()  -- Silver에 적재되는 현재 시각 (ingested_at)
        FROM bronze.ticker_raw r
        WHERE NOT EXISTS (
            -- 이미 Silver에 존재하는지 거래시간 기준으로 체크
            SELECT 1 FROM silver.ticker s 
            WHERE s.market = r.raw_data->>'market' 
            AND s.trade_date = r.raw_data->>'trade_date_kst' 
            AND s.trade_time = r.raw_data->>'trade_time_kst'
        )
        -- (옵션) 성능 최적화: 최근 1시간 내 수집된 Bronze 데이터만 대상으로 함
        AND r.ingested_at > NOW() - INTERVAL '1 hour'
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