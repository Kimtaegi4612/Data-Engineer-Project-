# 🤖 Vibe Coding: AI Collaboration Log

이 프로젝트는 AI Assistant와 협업하여 아키텍처 설계, 코드 구현, 트러블 슈팅을 진행했습니다.
단순 코드 생성이 아닌, **설계 의사결정(Decision Making)**과 **운영 효율화**에 집중했습니다.

## 📅 Day 1: Architecture & Infra Setup
**User Prompt:**
> "데이터 엔지니어 포트폴리오용으로 업비트 API 데이터를 수집해 Bronze/Silver/Gold 레이어로 구축하고 싶어. Docker Compose로 Postgres, Airflow, Metabase를 엮는 `docker-compose.yml` 초안을 작성해줘."

**AI Response Summary:**
* Postgres 15, Airflow 2.9, Metabase 최신 이미지 조합 제안.
* `volumes` 설정을 통해 컨테이너 재시작 시 데이터 유지되도록 구성.
* **My Decision:** Airflow Executor 설정 충돌 이슈 발생 → `Standalone` 모드로 변경하여 로컬 리소스 최적화 결정.

---

## 📅 Day 3: Pipeline Implementation (ELT)
**User Prompt:**
> "Bronze 테이블에 있는 JSONB 데이터를 파싱해서 Silver 테이블로 옮기고 싶어. 단, 중복 데이터는 제외하고 새로운 데이터만 넣는 파이썬(psycopg2) 코드를 짜줘."

**AI Response Summary:**
* `INSERT INTO ... SELECT ... WHERE NOT EXISTS` 구문 제안.
* **Refinement:** 초기 코드는 전체 데이터를 스캔하는 구조라 비효율적이었음. 
* **My Decision:** `ingested_at` 컬럼을 활용해 최근 1시간 데이터만 스캔하도록 `WHERE` 절을 튜닝하여 처리 속도 개선.

---

## 📅 Day 6: Troubleshooting & Data Quality
**User Prompt:**
> "Airflow에서 `value too long for type character varying(10)` 에러가 떴어. 원인이 뭐고 어떻게 해결해야 운영 중단 없이 처리가 가능할까?"

**AI Response Summary:**
* 원인: `market` 컬럼 길이가 10자로 제한되어 있는데, 긴 종목 코드가 들어옴.
* 해결책: `ALTER TABLE`로 컬럼 확장 제안.
* **My Decision:** 단순 컬럼 확장뿐만 아니라, `ingested_at`을 기준으로 에러 발생 시간대의 원본 데이터(Raw JSON)를 조회하는 디버깅 쿼리를 작성하여 재발 방지 프로세스 수립.

---

## 💡 Key Takeaways
* **AI 활용:** 보일러플레이트 코드(기본 설정, 단순 쿼리) 작성 시간을 90% 단축.
* **Human Touch:** 아키텍처 설계, 데이터 정합성 검증, 장애 대응 시나리오는 직접 설계하여 엔지니어링 역량 강화.