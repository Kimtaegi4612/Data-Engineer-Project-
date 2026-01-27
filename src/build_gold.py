import psycopg2

DB_CONFIG = {
    "host": "postgres",
    "port": 5432,
    "user": "user",
    "password": "password",
    "database": "upbit_dw"
}

def run_gold_modeling():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    try:
        print("--- Gold(KPI) 요리 시작 ---")
        
        # 1. 가장 최근 수집된 시간 찾기
        cur.execute("SELECT MAX(created_at) FROM silver.ticker")
        latest_time = cur.fetchone()[0]
        
        if not latest_time:
            print("데이터가 없어서 Gold 생성을 건너뜁니다.")
            return

        # 2. 핵심 쿼리: 가장 최근 시간 기준 '거래량 TOP 10' 뽑아서 Gold에 저장
        # (ROW_NUMBER를 써서 마켓별로 가장 최신 데이터 1개만 딱 골라냄)
        query = """
        INSERT INTO gold.market_stats (stat_time, market, trade_price, daily_volume, rank_volume)
        SELECT 
            CURRENT_TIMESTAMP,
            market,
            trade_price,
            acc_trade_volume,
            RANK() OVER (ORDER BY acc_trade_volume DESC) as rk
        FROM (
            SELECT *,
                   ROW_NUMBER() OVER (PARTITION BY market ORDER BY created_at DESC) as rn
            FROM silver.ticker
            -- 속도 최적화: 최근 10분 데이터 중에서만 찾기 (인덱스 활용)
            WHERE created_at >= %s - INTERVAL '10 minutes'
        ) latest_data
        WHERE rn = 1
        ORDER BY acc_trade_volume DESC
        LIMIT 10;
        """
        
        cur.execute(query, (latest_time,))
        conn.commit()
        print(f"[성공] {latest_time} 기준 거래량 TOP 10을 Gold에 저장했습니다.")
        
    except Exception as e:
        print("Gold 구축 중 에러:", e)
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    run_gold_modeling()