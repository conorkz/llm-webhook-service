from prometheus_client import Counter, Histogram
from prometheus_fastapi_instrumentator import Instrumentator

REQUESTS_TOTAL = Counter(
    "llm_requests_total",
    "Total number of LLM requests",
    ["status"]
)

RESPONSE_TIME = Histogram(
    "llm_response_time_seconds",
    "Time spent processing LLM requests"
)

def init_monitoring(app):
    Instrumentator().instrument(app).expose(app) 