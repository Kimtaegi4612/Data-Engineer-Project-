import requests
import psycopg2
import json
from datetime import datetime
import os

# 환경 변수에 따라 DB 주소 결정 (로컬 테스트 vs 도커 내부 실행)
# 도커 안에서는 'postgres'라는 이름으로 서로를 찾습니다.
DB_HOST = "postgres" 

DB_CONFIG = {
    "host": DB_HOST,
    "port": 5432,
    "user": "user",
    "password": "password",
    "database": "upbit_dw"
}

def get_krw_markets():
    """업비트의 모든 원화(KRW) 마켓 코드 가져오기"""
    url = "https://api.upbit.com/v1/market/all?isDetails=false"
    res = requests.get(url)
    if res.status_code == 200:
        markets = [m['market'] for m in res.json() if m['market'].startswith('KRW-')]
        return markets
    return []

def get_current_prices(markets):
    """여러 종목의 현재가를 한 번에 가져오기"""
    url = "https://api.upbit.com/v1/ticker"
    # 업비트 API는 쉼표로 구분해서 최대 100개까지 요청 가능
    # 예: KRW-BTC,KRW-ETH
    market_str = ",".join(markets)
    params = {"markets": market_str}
    
    res = requests.get(url, params=params)
    if res.status_code == 200:
        return res.json()
    return []

def save_to_bronze(data_list):
    conn = None
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        # 테이블 생성 (없으면)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS bronze.ticker_raw (
            id SERIAL PRIMARY KEY,
            market VARCHAR(20),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            raw_data JSONB
        );
        """)
        
        # 데이터 삽입 (Batch Insert가 더 좋지만 일단 Loop로 구현)
        insert_sql = "INSERT INTO bronze.ticker_raw (market, raw_data) VALUES (%s, %s);"
        
        for item in data_list:
            cur.execute(insert_sql, (item['market'], json.dumps(item)))
        
        conn.commit()
        print(f"[성공] {len(data_list)}개 종목 저장 완료!")
        
    except Exception as e:
        print("DB 에러:", e)
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    print("--- 전 종목 수집 시작 ---")
    markets = get_krw_markets()
    # 너무 많으면 테스트용으로 10개만 (필요하면 슬라이싱 제거하세요)
    # markets = markets[:10] 
    
    if markets:
        prices = get_current_prices(markets)
        save_to_bronze(prices)
    print("--- 수집 끝 ---")