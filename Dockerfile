FROM python:3.10-slim

RUN apt-get update && apt-get install -y \
    portaudio19-dev \
    python3-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install --upgrade pip \
    && pip install flake8 pytest \
    && if [ -f requirements.txt ]; then pip install -r requirements.txt; fi

EXPOSE 5000
CMD ["python", "app.py"]