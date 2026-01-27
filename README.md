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

## Quick Start
```bash
docker compose up -d
