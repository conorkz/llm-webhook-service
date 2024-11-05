# LLM Webhook Service

A REST API service that handles webhook requests using LLM (Language Learning Model) and sends generated responses to specified endpoints.

## 🚀 Features

- 🎯 Webhook endpoint for receiving requests
- 🤖 Integration with OpenRouter API for LLM capabilities
- 📨 Asynchronous request processing with RabbitMQ
- 💾 Message history support with PostgreSQL
- 🚦 Rate limiting with Redis
- 📊 Prometheus metrics
- 🐳 Docker support

## 📋 Prerequisites

- Docker Desktop
- Git

## 🛠️ Installation

1. Clone the repository
```bash
git clone https://github.com/conorkz/llm-webhook-service.git
cd llm-webhook-service
```

2. Update `.env` with your OpenRouter API key
```env
OPENROUTER_API_KEY=YOUR_OPENROUTER_API_KEY
REDIS_URL=redis://redis:6379
RABBITMQ_URL=amqp://rabbitmq:5672
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/llm_service
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_PERIOD=3600
```

3. Build and run with Docker Compose
```bash
docker-compose up --build
```

## 🔧 Usage

### API Endpoints

Access the Swagger UI documentation at: http://localhost:8000/docs

#### Send a webhook request:
```bash
curl -X 'POST' \
  'http://localhost:8000/api/v1/webhook' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "message": "Your message here",
  "callback_url": "https://example.com"
}'
```

## 🔍 Monitoring

- **API Documentation**: http://localhost:8000/docs
- **Metrics**: http://localhost:8000/metrics
- **RabbitMQ Management**: http://localhost:15672 (guest/guest)
- **Health Check**: http://localhost:8000/health

## 📊 Database

Connect to PostgreSQL:
```bash
docker-compose exec postgres psql -U postgres -d llm_service
```

View messages:
```sql
SELECT * FROM messages ORDER BY created_at DESC LIMIT 5;
```

## 🧪 Testing

Run tests:
```bash
docker-compose exec api pytest
```

Run with verbose output:
```bash
docker-compose exec api pytest -v
```

## 📝 Logs

View all logs:
```bash
docker-compose logs -f
```

View specific service logs:
```bash
docker-compose logs -f api
docker-compose logs -f rabbitmq
docker-compose logs -f postgres
```

## 🛑 Stopping the Service

```bash
# Stop services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

## 🔧 Troubleshooting

### Common Issues

1. **Services not starting**
```bash
# Restart specific service
docker-compose restart [service_name]
```

2. **Database connection issues**
```bash
# Check PostgreSQL logs
docker-compose logs postgres
```

3. **RabbitMQ connection issues**
```bash
# Check RabbitMQ logs
docker-compose logs rabbitmq
```

