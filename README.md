# Python Chart API

A simple REST API built with FastAPI Python.

## Features

- ✅ Basic Python Chart endpoint

## Installation

1. **Clone repository:**
```bash
git clone <repository-url>
cd python-api
```

2. **Create virtual environment (recommended):**
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

## Running the Application

### Method 1: Run directly
```bash
python main.py
```

### Method 2: Using uvicorn
```bash
uvicorn main:app --host 0.0.0.0 --port 5000 --reload
```

The application will run at: `http://localhost:5000`

## API Endpoints

### 1. Root Endpoint
- **URL:** `GET /`
- **Description:** Welcome page
- **Response:**
```json
{
  "message": "Welcome to Python Chart API!",
  "status": "running"
}
```

### 2. Health Check
- **URL:** `GET /healthz`
- **Description:** Check API status
- **Response:**
```json
{
  "status": "healthy",
  "service": "Python Chart API"
}
```

## API Documentation

FastAPI automatically generates interactive documentation:

- **Swagger UI:** `http://localhost:5000/docs`
- **ReDoc:** `http://localhost:5000/redoc`


## Testing

### Using curl

```bash
# Root endpoint
curl http://localhost:5000/

# Health check
curl http://localhost:5000/healthz

## Project Structure

```
python-api/
├── main.py              # Main file containing FastAPI app
├── requirements.txt      # Dependencies
└── README.md           # Usage guide
```

## Development

To extend the development:

1. Add new endpoints in `main.py`
2. Use Pydantic models for validation
3. Add error handling with HTTPException
4. Integrate database if needed

## License

MIT License 