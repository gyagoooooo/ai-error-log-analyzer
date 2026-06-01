from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

import hashlib
import os
import socket

import pymysql
import redis
import google.generativeai as genai


app = FastAPI(title="AI Error Log Analyzer")

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")


class LogRequest(BaseModel):
    error_log: str


redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "redis"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    db=0,
    decode_responses=True
)


def get_db():
    return pymysql.connect(
        host=os.getenv("DB_HOST", "mariadb"),
        port=int(os.getenv("DB_PORT", 3306)),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", "1234"),
        database=os.getenv("DB_NAME", "log_ai_db"),
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor
    )


def fake_ai_analyze(error_log: str) -> str:
    return f"""
## 에러 유형
기본 분석

## 원인
Gemini API Key가 없거나 Gemini API 호출 중 오류가 발생했습니다.

## 입력 로그

{error_log}

## 해결 절차

1. .env 파일에 GEMINI_API_KEY가 있는지 확인
2. docker-compose.yml에 env_file 설정 확인
3. 컨테이너 환경변수 확인

## 확인 명령어

docker compose exec app env | grep GEMINI
docker compose logs app --tail=100
"""


def gemini_analyze(error_log: str) -> str:
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        return fake_ai_analyze(error_log)

    try:
        genai.configure(api_key=api_key)

        model = genai.GenerativeModel("gemini-2.5-flash")

        prompt = f"""
너는 Docker, Docker Compose, Docker Swarm, Nginx, Redis, MariaDB, FastAPI, Linux 서버 에러를 분석하는 인프라 전문가다.

아래 형식으로 답변해.

## 에러 유형
## 원인
## 해결 절차
## 확인 명령어
## 재발 방지

에러 로그:
{error_log}
"""

        response = model.generate_content(prompt)

        if not response.text:
            return fake_ai_analyze(error_log)

        return response.text

    except Exception as e:
        return f"""
## 에러 유형
Gemini API 호출 실패

## 원인
Gemini API 호출 중 오류 발생

## 오류 내용

{str(e)}
"""


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html"
    )


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "server": socket.gethostname()
    }


@app.post("/api/analyze")
def analyze_log(req: LogRequest):
    error_log = req.error_log.strip()

    if not error_log:
        return {
            "cache_hit": False,
            "analysis": "에러 로그가 비어 있습니다.",
            "server": socket.gethostname()
        }

    cache_key = "log:" + hashlib.sha256(error_log.encode()).hexdigest()

    cached_result = redis_client.get(cache_key)

    if cached_result:
        cache_hit = True
        result = cached_result
    else:
        cache_hit = False
        result = gemini_analyze(error_log)

        redis_client.setex(
            cache_key,
            3600,
            result
        )

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO analysis_logs
        (
            error_log,
            analysis_result,
            cache_hit
        )
        VALUES
        (
            %s,
            %s,
            %s
        )
        """,
        (
            error_log,
            result,
            cache_hit
        )
    )

    conn.commit()

    cursor.close()
    conn.close()

    return {
        "cache_hit": cache_hit,
        "analysis": result,
        "server": socket.gethostname()
    }


@app.get("/api/logs")
def get_logs():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            id,
            error_log,
            analysis_result,
            cache_hit,
            created_at
        FROM analysis_logs
        ORDER BY created_at DESC
        LIMIT 20
        """
    )

    logs = cursor.fetchall()

    cursor.close()
    conn.close()

    return logs


@app.get("/api/stats")
def get_stats():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT COUNT(*) AS total_requests
        FROM analysis_logs
        """
    )

    total_requests = cursor.fetchone()["total_requests"]

    cursor.execute(
        """
        SELECT COUNT(*) AS cache_hit_count
        FROM analysis_logs
        WHERE cache_hit = TRUE
        """
    )

    cache_hit_count = cursor.fetchone()["cache_hit_count"]

    cache_miss_count = total_requests - cache_hit_count

    if total_requests == 0:
        cache_hit_rate = 0
    else:
        cache_hit_rate = round(
            (cache_hit_count / total_requests) * 100,
            2
        )

    cursor.close()
    conn.close()

    return {
        "total_requests": total_requests,
        "cache_hit": cache_hit_count,
        "cache_miss": cache_miss_count,
        "cache_hit_rate": f"{cache_hit_rate}%"
    }


@app.get("/api/popular")
def get_popular_errors():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            error_log,
            COUNT(*) AS count
        FROM analysis_logs
        GROUP BY error_log
        ORDER BY count DESC
        LIMIT 5
        """
    )

    popular_errors = cursor.fetchall()

    cursor.close()
    conn.close()

    return popular_errors
