# dbass_proyecto_distribuida


#Instalacion de las microservicios

#Para ejecutar la MV servicios 
cd MV3

hectorcortes@MacBook-Air-de-Hector MV3 % docker rm -f mv3_auth

# Reconstruir la imagen (descargará la versión correcta de bcrypt)
docker build -t dbaas-mv3 .

# Levantar el contenedor nuevamente en la red interna
docker run -d --name mv3_auth --network dbaas_proyecto_default --env-file ../dbaas_proyecto/.env dbaas-mv3

cd MV2
hectorcortes@MacBook-Air-de-Hector MV2 % docker rm -f mv2_query
docker run -d --name mv2_query --network dbaas_proyecto_default --env-file ../dbaas_proyecto/.env dbaas-mv2

cd MV1
hectorcortes@MacBook-Air-de-Hector MV1 % docker rm -f mv1_database
docker run -d --name mv1_database --network dbaas_proyecto_default --env-file ../dbaas_proyecto/.env dbaas-mv1


# Instalar el backend en docker 

cd dbaas_proyecto
docker compose up --build
 
# Autenticación y Seguridad

POST /auth/register - Registro de nuevo usuario.

POST /auth/login - Inicio de sesión para obtener el token.

# Interfaz SQL-like 
POST /sql/execute

Ejemplo:
{
  "command": "USE mi_empresa; CREATE TABLE empleados"
}
{
  "db_name": "mi_empresa",
  "command": "INSERT INTO empleados (nombre, edad, salario) VALUES ('Ana', 28, 4500)"
}
{
  "db_name": "mi_empresa",
  "command": "SELECT * FROM empleados WHERE edad > 25"
}
{
  "db_name": "mi_empresa",
  "command": "UPDATE empleados SET salario = 5000 WHERE nombre = 'Ana'"
}
{
  "db_name": "mi_empresa",
  "command": "UPDATE empleados SET salario = 5000 WHERE nombre = 'Ana'"
}
{
  "db_name": "mi_empresa",
  "command": "DELETE FROM empleados WHERE edad < 20"
}

{
  "command": "DROP DATABASE stress_db"
}


# Interfaz NoSQL 

# Administración
POST /db/create : {"db_name": "string"}
GET /db/list : Lista bases de datos del usuario.
DELETE /db/delete/{db_name} : Elimina una base de datos.

# Operaciones CRUD
POST /document/insert

{"db_name": "db1", "collection_name": "col1", "document": {"key": "value"}}


# Consultas y Agregaciones (MPI)
Operaciones procesadas de forma distribuida para alto rendimiento.

/query/count Cuenta registros en una colección.
/query/sum Suma los valores de un campo numérico.
/query/avg Calcula el promedio de un campo.
/query/distinct Obtiene valores únicos de un campo.
/query/join Realiza un INNER JOIN simple entre dos colecciones.



# Para pruebas de carga de estres

En la carpeta de PruebaEstres esta el script para hacer pruebas de carga 
Instala un entorno virtual 
python3 -m venv venv
source venv/bin/activate
pip install requests
ejecutar el archivo stress_test.py 
Cambia el token de lqqogin en el archivo 
python3 stress_test.py