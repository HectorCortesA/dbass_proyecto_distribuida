import requests
import time
import random
from concurrent.futures import ProcessPoolExecutor, as_completed

#configuracion de ip 
BASE_URL = "http://localhost:8000"

# Cambiar el token por el que te de el login
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjZhMDVlMTlmZGQ1MzI5YTFlMWEyYjU5ZiIsImVtYWlsIjoiYWRtaW5AdGVzdC5jb20iLCJyb2xlIjoiYWRtaW4iLCJleHAiOjE3Nzg4MDE3NjZ9.lnMYeDPnZ93srxqe4QxwqMn0BXL-1HTAoziqOwlKhb0"

DB_NAME = "stress_db"
TABLE_NAME = "datos_masivos"
TOTAL_REQUESTS = 50000    # Cantidad total de registros a insertar
CONCURRENCY = 100         # Cantidad de procesos simultáneos (trabajadores)

def preparar_entorno(token):
    """Crea la base de datos y la tabla de prueba usando tu interfaz SQL"""
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    print(f"Creando base de datos '{DB_NAME}'...")
    requests.post(f"{BASE_URL}/sql/execute", json={"command": f"CREATE DATABASE {DB_NAME}"}, headers=headers)
    
    print(f"Creando tabla '{TABLE_NAME}'...")
    requests.post(f"{BASE_URL}/sql/execute", json={"command": f"USE {DB_NAME}; CREATE TABLE {TABLE_NAME}"}, headers=headers)
    time.sleep(2) # Dar tiempo a que RabbitMQ procese la creación

def insertar_dato(params):
    """Función que ejecutará cada proceso trabajador"""
    request_id, token = params
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Generamos datos aleatorios para la prueba
    edad = random.randint(18, 60)
    salario = random.randint(1000, 9000)
    
    payload = {
        "db_name": DB_NAME,
        "command": f"INSERT INTO {TABLE_NAME} (req_id, edad, salario) VALUES ({request_id}, {edad}, {salario})"
    }
    
    try:
        inicio = time.time()
        response = requests.post(f"{BASE_URL}/sql/execute", json=payload, headers=headers, timeout=10)
        tiempo_respuesta = time.time() - inicio
        
        if response.status_code == 200:
            return {"status": "success", "id": request_id, "time": tiempo_respuesta}
        else:
            return {"status": "error", "id": request_id, "error": response.text, "time": tiempo_respuesta}
    except Exception as e:
        return {"status": "exception", "id": request_id, "error": str(e), "time": 0}

def main():
    # Usamos la variable global TOKEN en lugar de hacer login
    token = TOKEN

    preparar_entorno(token)
    
    print(f"Total de peticiones a enviar: {TOTAL_REQUESTS}")
    print(f"Procesos concurrentes: {CONCURRENCY}\n")

    # Preparamos los parámetros para cada trabajador (ID de petición y el token)
    tareas = [(i, token) for i in range(1, TOTAL_REQUESTS + 1)]
    
    exitosos = 0
    fallidos = 0
    tiempos = []

    start_time = time.time()

    # ProcessPoolExecutor crea verdaderos procesos en el sistema operativo
    with ProcessPoolExecutor(max_workers=CONCURRENCY) as executor:
        # Mapeamos la función insertar_dato a nuestras tareas
        futuros = {executor.submit(insertar_dato, tarea): tarea for tarea in tareas}
        
        for futuro in as_completed(futuros):
            resultado = futuro.result()
            if resultado["status"] == "success":
                exitosos += 1
                tiempos.append(resultado["time"])
            else:
                fallidos += 1
                # Solo imprimimos errores para no saturar la consola
                # print(f"❌ Fallo en req_id {resultado['id']}: {resultado.get('error')}")
            
            # Imprimir progreso cada 100 peticiones
            if (exitosos + fallidos) % 100 == 0:
                print(f"Progreso: {exitosos + fallidos} / {TOTAL_REQUESTS}")

    total_time = time.time() - start_time
    avg_time = sum(tiempos) / len(tiempos) if tiempos else 0


    print("RESULTADOS DE LA PRUEBA DE ESTRÉS ")
    print(f"Tiempo total de ejecución : {total_time:.2f} segundos")
    print(f"Peticiones Exitosas       : {exitosos}")
    print(f"Peticiones Fallidas       : {fallidos}")
    print(f"Rendimiento (Req/seg)     : {TOTAL_REQUESTS / total_time:.2f} req/s")
    print(f"Tiempo prom. por petición : {avg_time:.4f} segundos")

if __name__ == "__main__":
    main()