// DOM 요소 가져오기
const errorLogInput = document.getElementById("errorLog");
const analyzeBtn = document.getElementById("analyzeBtn");
const analysisResult = document.getElementById("analysisResult");
const cacheStatus = document.getElementById("cacheStatus");
const serverName = document.getElementById("serverName");
const historyList = document.getElementById("historyList");
const popularList = document.getElementById("popularList");
const refreshBtn = document.getElementById("refreshBtn");

const totalRequests = document.getElementById("totalRequests");
const cacheHit = document.getElementById("cacheHit");
const cacheMiss = document.getElementById("cacheMiss");
const cacheHitRate = document.getElementById("cacheHitRate");


// 에러 로그 분석 요청
async function analyzeError() {
    const errorLog = errorLogInput.value.trim();

    if (!errorLog) {
        alert("에러 로그를 입력하세요.");
        return;
    }

    analyzeBtn.disabled = true;
    analyzeBtn.textContent = "분석 중...";
    analysisResult.innerHTML = "<p>AI가 에러 로그를 분석하고 있습니다.</p>";

    try {
        const response = await fetch("/api/analyze", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                error_log: errorLog
            })
        });

        const data = await response.json();

        // 캐시 상태 표시
        cacheStatus.textContent = `Cache: ${data.cache_hit ? "HIT" : "MISS"}`;
        cacheStatus.className = data.cache_hit ? "cache-hit" : "cache-miss";

        // Swarm replica 확인용 서버 hostname 표시
        serverName.textContent = `Server: ${data.server || "-"}`;

        // Gemini 응답 Markdown 렌더링
        if (window.marked) {
            analysisResult.innerHTML = marked.parse(data.analysis || "분석 결과가 없습니다.");
        } else {
            analysisResult.textContent = data.analysis || "분석 결과가 없습니다.";
        }

        // 분석 후 통계/히스토리/인기 에러 갱신
        await loadStats();
        await loadHistory();
        await loadPopularErrors();

    } catch (error) {
        analysisResult.textContent = "요청 중 오류가 발생했습니다.";
        console.error(error);
    } finally {
        analyzeBtn.disabled = false;
        analyzeBtn.textContent = "분석하기";
    }
}


// 최근 분석 히스토리 조회
async function loadHistory() {
    try {
        const response = await fetch("/api/logs");
        const logs = await response.json();

        historyList.innerHTML = "";

        if (!logs.length) {
            historyList.innerHTML = "<p>아직 분석 히스토리가 없습니다.</p>";
            return;
        }

        logs.forEach((log) => {
            const item = document.createElement("div");
            item.className = "history-item";

            const cacheClass = log.cache_hit ? "cache-hit" : "cache-miss";
            const cacheText = log.cache_hit ? "HIT" : "MISS";

            item.innerHTML = `
                <div class="history-item-header">
                    <span>#${log.id} · ${log.created_at}</span>
                    <span class="${cacheClass}">Cache ${cacheText}</span>
                </div>
                <div class="history-error">${escapeHtml(shorten(log.error_log, 120))}</div>
                <div class="history-analysis">${escapeHtml(shorten(log.analysis_result, 180))}</div>
            `;

            historyList.appendChild(item);
        });

    } catch (error) {
        historyList.innerHTML = "<p>히스토리를 불러오지 못했습니다.</p>";
        console.error(error);
    }
}


// 캐시 통계 조회
async function loadStats() {
    try {
        const response = await fetch("/api/stats");
        const stats = await response.json();

        totalRequests.textContent = stats.total_requests;
        cacheHit.textContent = stats.cache_hit;
        cacheMiss.textContent = stats.cache_miss;
        cacheHitRate.textContent = stats.cache_hit_rate;

    } catch (error) {
        console.error("통계 로딩 실패:", error);
    }
}


// 인기 에러 TOP 5 조회
async function loadPopularErrors() {
    try {
        const response = await fetch("/api/popular");
        const errors = await response.json();

        popularList.innerHTML = "";

        if (!errors.length) {
            popularList.innerHTML = "<p>아직 인기 에러가 없습니다.</p>";
            return;
        }

        errors.forEach((errorItem, index) => {
            const item = document.createElement("div");
            item.className = "popular-item";

            item.innerHTML = `
                <div class="popular-rank">#${index + 1}</div>
                <div class="popular-error">${escapeHtml(shorten(errorItem.error_log, 120))}</div>
                <div class="popular-count">분석 횟수: ${errorItem.count}</div>
            `;

            popularList.appendChild(item);
        });

    } catch (error) {
        popularList.innerHTML = "<p>인기 에러를 불러오지 못했습니다.</p>";
        console.error(error);
    }
}


// 문자열 길이 줄이기
function shorten(text, maxLength) {
    if (!text) return "";
    return text.length > maxLength ? text.slice(0, maxLength) + "..." : text;
}


// XSS 방지용 HTML escape
function escapeHtml(text) {
    return text
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}


// 이벤트 등록
analyzeBtn.addEventListener("click", analyzeError);
refreshBtn.addEventListener("click", async () => {
    await loadStats();
    await loadHistory();
    await loadPopularErrors();
});


// 페이지 최초 로딩 시 데이터 불러오기
loadStats();
loadHistory();
loadPopularErrors();
