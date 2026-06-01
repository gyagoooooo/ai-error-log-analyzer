# 🤖 AI Error Log Analyzer

> Gemini AI를 활용하여 Docker, Nginx, Redis, MariaDB, FastAPI 등 다양한 인프라 및 서버 에러 로그를 분석하는 서비스

<br>

## 📌 프로젝트 소개

AI Error Log Analyzer는 개발 과정에서 발생하는 에러 로그를 AI가 분석하여 원인과 해결 방법을 제안하는 서비스입니다.

사용자는 에러 로그를 입력하기만 하면 Gemini AI가 로그를 분석하여 문제 원인, 해결 절차, 확인 명령어 등을 제공받을 수 있습니다.

또한 Redis 캐싱을 통해 동일한 에러에 대한 분석 결과를 빠르게 제공하고, MariaDB를 활용하여 분석 이력을 저장합니다.

<br>

## ✨ 주요 기능

### 🤖 AI 에러 로그 분석

* Gemini API 기반 에러 분석
* 원인 및 해결 방법 자동 제안
* Docker / Nginx / Redis / MariaDB / FastAPI / Linux 서버 에러 지원

### ⚡ Redis 캐싱

* 동일한 에러 로그 재분석 최소화
* 빠른 응답 제공
* Cache HIT / MISS 확인 가능

### 📝 분석 이력 관리

* 최근 분석 이력 조회
* 에러 분석 결과 저장
* 인기 에러 조회

### 📊 통계 기능

* 총 분석 횟수
* Cache HIT
* Cache MISS
* Cache Hit Rate

### 🐳 Docker Swarm 지원

* Replica 기반 서비스 운영
* Rolling Update 지원
* 수평 확장 가능

<br>

## 🏗️ 시스템 아키텍처

```text
User
 │
 ▼
Cloudflare Tunnel
 │
 ▼
Nginx
 │
 ▼
FastAPI
 │
 ├── Gemini API
 │
 ├── Redis Cache
 │
 └── MariaDB
```

<br>

## 🛠️ 기술 스택

### Backend

* FastAPI
* Python

### AI

* Gemini API

### Database

* MariaDB

### Cache

* Redis

### Infra

* Docker
* Docker Compose
* Docker Swarm
* Nginx
* Cloudflare Tunnel

<br>

## 📂 프로젝트 구조

```text
ai-error-log-analyzer
│
├── app
│   ├── static
│   │   ├── css
│   │   └── js
│   │
│   ├── templates
│   │   └── index.html
│   │
│   └── main.py
│
├── nginx
│   └── default.conf
│
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── .env.example
└── README.md
```

<br>

## 🚀 실행 방법

### 1. 프로젝트 클론

```bash
git clone https://github.com/gyagoooooo/ai-error-log-analyzer.git

cd ai-error-log-analyzer
```

### 2. 환경변수 설정

```bash
cp .env.example .env
```

`.env` 파일에 Gemini API Key 입력

```env
GEMINI_API_KEY=YOUR_GEMINI_API_KEY
```

### 3. Docker Compose 실행

```bash
docker compose up -d --build
```

### 4. 접속

```text
http://localhost:8080
```

또는

```text
https://ai.gyagoodev.store
```

<br>

## 📈 API 목록

| Method | URL          | 설명         |
| ------ | ------------ | ---------- |
| GET    | /            | 메인 페이지     |
| GET    | /api/health  | 서버 상태 확인   |
| POST   | /api/analyze | 에러 로그 분석   |
| GET    | /api/logs    | 최근 분석 이력   |
| GET    | /api/stats   | 분석 통계      |
| GET    | /api/popular | 인기 에러 TOP5 |

<br>

## ⚠️ 주의사항

### 🤖 Gemini API 관련

본 서비스는 Gemini API를 사용하여 에러 로그를 분석합니다.

다음과 같은 경우 분석 기능이 정상적으로 동작하지 않을 수 있습니다.

* API Key 오류
* Gemini 사용량 초과
* 모델 접근 권한 문제
* 토큰 제한 초과
* Gemini 서비스 장애

이 경우 분석 결과 대신 오류 메시지가 반환될 수 있습니다.

---

### 🖥️ 서버 운영 관련

현재 서비스는 개인 서버 환경에서 운영되고 있습니다.

다음과 같은 경우 서비스 접속이 불가능할 수 있습니다.

* 서버 종료
* Docker 컨테이너 중지
* 인터넷 연결 장애
* Cloudflare Tunnel 중단
* 시스템 점검 및 배포 작업

따라서 서버가 실행 중인 경우에만 서비스 이용이 가능합니다.

<br>

## 🎯 향후 개선 계획

* [ ] 사용자 로그인 기능
* [ ] 분석 결과 북마크
* [ ] AI 분석 정확도 향상
* [ ] 에러 카테고리 자동 분류
* [ ] Slack / Discord 알림 연동
* [ ] Kubernetes 배포 지원
