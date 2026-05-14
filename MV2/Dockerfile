FROM python:3.11-slim
WORKDIR /app

# Instalar OpenMPI y compiladores C necesarios para mpi4py
RUN apt-get update && apt-get install -y \
    openmpi-bin \
    libopenmpi-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Generar archivos gRPC
RUN mkdir -p app/proto_generated
RUN python -m grpc_tools.protoc -I./app/proto --python_out=./app/proto_generated --grpc_python_out=./app/proto_generated ./app/proto/dbaas.proto
RUN echo "import sys\nimport os\nsys.path.append(os.path.dirname(os.path.abspath(__file__)))" > app/proto_generated/__init__.py

EXPOSE 50053
CMD ["python", "-m", "app.server"]