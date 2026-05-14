FROM python:3.11-slim
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Generar archivos gRPC automáticamente dentro del contenedor
RUN mkdir -p app/proto_generated
RUN python -m grpc_tools.protoc -I./app/proto --python_out=./app/proto_generated --grpc_python_out=./app/proto_generated ./app/proto/dbaas.proto
RUN echo "import sys\nimport os\nsys.path.append(os.path.dirname(os.path.abspath(__file__)))" > app/proto_generated/__init__.py

EXPOSE 50051
# Usamos -m para que Python reconozca 'app' como paquete
CMD ["python", "-m", "app.server"]