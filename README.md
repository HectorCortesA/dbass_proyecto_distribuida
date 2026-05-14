# dbass_proyecto_distribuida

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


#Para el backend  
 docker compose up --build 
 