import pika, json, os, time
from app.services.database_service import create_database
from app.services.collection_service import create_collection
from app.services.document_service import insert_document

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://dbaas_rabbitmq")

def callback(ch, method, properties, body):
    try:
        data = json.loads(body)
        action = data.get("action")
        
        if action == "create_database":
            create_database(data["user_id"], data["db_name"])
            print(f"BD {data['db_name']} creada en background.")
            ch.basic_ack(delivery_tag=method.delivery_tag)
            
        elif action == "create_collection":
            create_collection(data["db_name"], data["collection_name"], data["user_id"])
            print(f"Colección {data['collection_name']} creada en background.")
            ch.basic_ack(delivery_tag=method.delivery_tag)
            
        elif action == "insert_document":
            insert_document(data["db_name"], data["collection_name"], data["document"], data["owner_id"])
            print(f"Documento insertado en {data['collection_name']} en background.")
            ch.basic_ack(delivery_tag=method.delivery_tag)
            
        else:
            print(f"Acción desconocida: {action}")
            ch.basic_ack(delivery_tag=method.delivery_tag)
            
    except Exception as e:
        print(f"Error procesando mensaje en worker: {e}")
        # Rechazamos el mensaje sin encolar de nuevo para evitar bucles infinitos en caso de errores de validación
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

def start_worker():
    while True:
        try:
            connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
            channel = connection.channel()
            
            # Declarar colas
            channel.queue_declare(queue='db_tasks', durable=True)
            channel.queue_declare(queue='table_tasks', durable=True)
            channel.queue_declare(queue='insert_tasks', durable=True)
            
            channel.basic_qos(prefetch_count=1)
            
            # Consumir de las colas
            channel.basic_consume(queue='db_tasks', on_message_callback=callback)
            channel.basic_consume(queue='table_tasks', on_message_callback=callback)
            channel.basic_consume(queue='insert_tasks', on_message_callback=callback)
            
            print('RabbitMQ Worker conectado y esperando mensajes en db_tasks, table_tasks, insert_tasks...')
            channel.start_consuming()
        except Exception as e:
            print(f"Error conectando a RabbitMQ en worker, reintentando en 5s: {e}")
            time.sleep(5)

if __name__ == '__main__':
    start_worker()