FROM python:3.11
WORKDIR /app
# Instalar OpenMPI
RUN apt-get update && apt-get install -y openmpi-bin libopenmpi-dev && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 50053
CMD ["python", "app/server.py"]