import pika, json, os
from app.services.database_service import create_database

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://dbaas_rabbitmq")

def callback(ch, method, properties, body):
    data = json.loads(body)
    if data.get("action") == "create_database":
        try:
            # Ejecuta el código de tu monolito original
            create_database(data["user_id"], data["db_name"])
            print(f"BD {data['db_name']} creada en background.")
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            print(f"Error creando BD: {e}")

import time

def start_worker():
    while True:
        try:
            connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
            channel = connection.channel()
            channel.queue_declare(queue='db_tasks', durable=True)
            channel.basic_qos(prefetch_count=1)
            channel.basic_consume(queue='db_tasks', on_message_callback=callback)
            print('RabbitMQ Worker conectado y esperando mensajes...')
            channel.start_consuming()
        except Exception as e:
            print(f"Error conectando a RabbitMQ en worker, reintentando en 5s: {e}")
            time.sleep(5)

if __name__ == '__main__':
    start_worker()