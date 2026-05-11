FROM python:3.10-slim

WORKDIR /app

# Upgrade packaging tools first so the runtime image does not retain
# known vulnerabilities from the base Python image's bundled installers.
COPY frontend/requirements.txt .
RUN pip install --no-cache-dir --upgrade pip wheel setuptools && \
    pip install --no-cache-dir -r requirements.txt

# Copy only the frontend application into the runtime image.
COPY frontend/ ./frontend/

EXPOSE 8501

ENV PYTHONUNBUFFERED=1

# Start the Streamlit user interface.
CMD ["streamlit", "run", "frontend/streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
