# ChemThisTry web backend image.
# Build from the server/ directory so the build context is just the backend:
#   cd server && docker build -t chemthis-backend .
# Run:
#   docker run -p 8000:8000 -e CORS_ORIGINS="https://your-frontend.example.com" chemthis-backend
FROM python:3.11-slim

# cairosvg needs libcairo + pango at runtime; rdkit/ASE pull in a few more.
RUN apt-get update && apt-get install -y --no-install-recommends \
        libcairo2 \
        libpango-1.0-0 \
        libpangocairo-1.0-0 \
        libgdk-pixbuf2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# PORT / CORS_ORIGINS are overridable at runtime.
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
