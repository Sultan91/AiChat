# AI Chat Application

A modern, asynchronous chat application built with FastAPI, SQLAlchemy, and WebSockets. This application provides a RESTful API for chat functionality with session management and supports real-time communication.

## Features

- Asynchronous chat messaging
- Session-based chat history
- RESTful API endpoints
- WebSocket support for real-time updates
- SQLite database with SQLAlchemy ORM
- User authentication via session cookies
- Clean, modular architecture

## Prerequisites

- Python 3.12+
- Poetry (for dependency management)
- SQLite (included with Python)

## Setup and Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd AiChat
   ```

2. **Set up environment variables**
   Copy the example environment file and update it with your configuration:
   ```bash
   cp .env.example .env
   # Edit .env with your preferred settings
   ```

3. **Install dependencies**
   ```bash
   poetry install
   ```

4. **Initialize the database**
   ```bash
   poetry run alembic upgrade head
   ```

## Running the Application

### Development Mode
```bash
poetry run uvicorn src.main:app --reload
```

### Production Mode
```bash
gunicorn src.main:app -k uvicorn.workers.UvicornWorker --workers 4 --bind 0.0.0.0:8000
```

The application will be available at `http://localhost:8000`

## API Usage Examples

### Send a Message
```http
POST /chat/
Content-Type: application/json

{
  "message": "Hello, how are you?",
  "session_id": "optional-session-id"
}
```

### Get Chat History
```http
GET /chat/history/{session_id}
```

### List All Chat Sessions
```http
GET /chat/sessions
```

### Delete a Chat Session
```http
DELETE /chat/sessions/{session_id}
```

## Design Decisions

### Architecture
- **Asynchronous by Design**: Built using Python's asyncio and FastAPI's async capabilities for high performance
- **Modular Structure**: Separated into routers, services, and models for better maintainability
- **Dependency Injection**: Uses FastAPI's dependency injection system for clean code organization

### Security
- **Session Management**: Uses HTTP-only cookies for secure session handling
- **CORS**: Configured to prevent cross-origin attacks
- **Input Validation**: Uses Pydantic models for request/response validation

### Database
- **SQLAlchemy ORM**: For database operations with async support
- **Alembic Migrations**: For database version control and schema migrations
- **Connection Pooling**: For efficient database connection management

### Performance
- **Async Database Operations**: Non-blocking database operations for better concurrency
- **Connection Pooling**: Reuses database connections to reduce overhead
- **Static File Serving**: Efficient static file handling with FastAPI's StaticFiles

## Development

### Running Tests
```bash
poetry run pytest
```

### Database Migrations
To create a new migration:
```bash
alembic revision --autogenerate -m "description of changes"
```

To apply migrations:
```bash
alembic upgrade head
```

## Deployment

The application includes Docker and docker-compose configuration for easy deployment:

```bash
docker-compose up --build
```

## License

MIT
