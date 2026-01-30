# 📈 Upbit Real-time Data Pipeline (Crypto Dashboard)

## 📝 프로젝트 개요
업비트(Upbit) API를 활용하여 가상화폐 거래 데이터를 실시간으로 수집하고, **Bronze-Silver-Gold** 레이어 아키텍처를 통해 정제 및 가공하여 시각화 대시보드까지 제공하는 **End-to-End 데이터 파이프라인**입니다.

Docker 환경에서 Airflow를 이용해 워크플로우를 자동화하였으며, 대용량 데이터 처리를 가정한 PostgreSQL 튜닝 및 데이터 모델링을 수행했습니다.

* **진행 기간:** 2026.01.xx ~ 2026.01.xx (2주)
* **참여 인원:** 개인 프로젝트 (1인)
* **역할:** Data Engineer (인프라 구축, 파이프라인 설계, 데이터 모델링, 시각화)

---

## 🏗 아키텍처 (Architecture)

**Data Pipeline Flow:**
`Upbit API` → **[Collect]** → `PostgreSQL (Bronze)` → **[Transform]** → `PostgreSQL (Silver)` → **[Aggregate]** → `PostgreSQL (Gold)` → `Metabase (Dashboard)`

* **Orchestration:** Apache Airflow (Docker)
* **Database:** PostgreSQL 15
* **Visualization:** Metabase
* **Language:** Python 3.9, SQL

---

## 🛠 기술적 핵심 (Key Features)

### 1. Medallion Architecture 적용 (ELT)
데이터의 안정성과 재사용성을 위해 데이터를 3단계 레이어로 관리했습니다.
* **Bronze Layer:** API 응답(JSON)을 가공 없이 `JSONB` 타입으로 적재하여 원본 데이터의 불변성(Immutability) 보장.
* **Silver Layer:** JSON 데이터를 파싱하여 정형 테이블(Table)로 변환. 데이터 타입 캐스팅 및 결측치 처리 수행.
* **Gold Layer:** 비즈니스 KPI(거래대금 TOP 10, 변동성 순위 등)를 집계하여 대시보드 조회 속도 최적화.

### 2. Airflow 워크플로우 자동화
* `docker-compose`를 통해 Airflow 환경을 구축하고, `BashOperator`를 활용해 파이썬 스크립트 실행.
* Task 간 의존성(`>>`)을 설정하여 **수집 → 정제 → 집계** 순서의 데이터 정합성 보장.

### 3. SQL 튜닝 및 성능 최적화
* 대시보드 조회 성능 향상을 위해 `market`, `created_at` 컬럼에 **복합 인덱스(Composite Index)** 적용.
* Gold 데이터 생성 시 **Window Function (`RANK()`, `ROW_NUMBER()`)**을 활용해 쿼리 효율성 증대.

---

# Upbit API Layered Data Pipeline (Bronze–Silver–Gold)

Upbit 공개 API(시세/체결/호가/캔들)를 수집하여 **Bronze(원본) → Silver(정제) → Gold(KPI)** 레이어로 적재하고,
Airflow로 스케줄링하여 재현 가능한 데이터 파이프라인과 지표 데이터마트를 구축한 프로젝트입니다.

## Architecture
- **Ingestion (Bronze)**: Upbit API 호출 → 원본 데이터 저장(JSON/Raw Table)
- **Transform (Silver)**: 스키마 표준화, 타입 변환, 중복 제거, 결측/이상치 처리
- **Mart (Gold)**: KPI 집계 테이블 생성 (예: VWAP, 변동성, 거래대금 상위 코인 등)
- **Orchestration**: Airflow DAG로 수집/변환/적재 자동화
- **Infra**: Docker Compose로 로컬에서 일괄 실행

## Project Structure
- `airflow/` : DAG 및 스케줄링/오케스트레이션 코드
- `src/` : 수집/정제/집계(ETL/ELT) 파이프라인 코드
- `docker-compose.yml` : Airflow/DB 등 로컬 실행 환경

---

# 📚 데이터 사전 (Data Dictionary)
## 1. Bronze Layer (Raw Data)
Table: bronze.ticker_raw

**설명: Upbit API로부터 수집한 JSON 원본 데이터를 저장하는 적재 테이블 (ELT 원본 보존용)**

컬럼명 (Column),데이터 타입,설명 (Description),비고  
id,SERIAL (PK),고유 식별자,자동 증가  
market,VARCHAR(10),종목 코드,예: KRW-BTC  
raw_data,JSONB,API 응답 원본,스키마 변경 대응을 위한 비정형 저장  
ingested_at,TIMESTAMP,데이터 적재 시각,수집된 시점 (파티셔닝 및 재처리 기준)  

## 2. Silver Layer (Cleansed Data)
Table: silver.ticker

**설명: JSON 원본을 파싱하여 정형화된 형태로 변환한 테이블 (분석용)**

컬럼명 (Column),데이터 타입,설명 (Description),비고  
id,SERIAL (PK),고유 식별자,  
market,VARCHAR(30),종목 코드,예: KRW-BTC  
trade_date,VARCHAR(8),거래 일자 (KST),포맷: YYYYMMDD  
trade_time,VARCHAR(6),거래 시각 (KST),포맷: HHMMSS  
trade_price,NUMERIC,거래 가격,  
acc_trade_volume,NUMERIC,누적 거래량 (24h),  
ingested_at,TIMESTAMP,데이터 적재 시각,Bronze 데이터가 Silver로 변환된 시점  

## 3. Gold Layer (Data Mart)
Table: gold.market_stats

**설명: 비즈니스 KPI(거래대금 순위 등)를 집계하여 대시보드 서빙 속도를 최적화한 마트**

컬럼명 (Column),데이터 타입,설명 (Description),비고  
id,SERIAL (PK),고유 식별자,  
ingested_at,TIMESTAMP,지표 집계 시각,대시보드 기준 시간  
market,VARCHAR(30),종목 코드,  
trade_price,NUMERIC,현재가,  
daily_volume,NUMERIC,24시간 누적 거래량,정렬 기준  
rank_volume,INT,거래대금 순위,윈도우 함수(RANK) 계산 결과  


### 🛡️ 장애 대응 가이드 (Backfill Process)
API 장애나 로직 오류로 인해 잘못된 데이터가 적재되었을 경우, `ingested_at`(적재 시각)을 기준으로 빠르고 정확하게 복구를 수행합니다.

**상황 예시:** 14:00 ~ 14:10 사이에 수집된 데이터의 환율 계산 로직 오류 발생.

**1. 오염된 데이터 범위 파악 및 삭제 (Rollback)**
```sql
-- 문제가 된 적재 시간대(ingested_at)의 데이터만 특정하여 삭제.
DELETE FROM silver.ticker 
WHERE ingested_at BETWEEN '2026-01-29 14:00:00' AND '2026-01-29 14:10:00';