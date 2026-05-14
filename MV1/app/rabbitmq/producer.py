import pika, json, os

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://dbaas_rabbitmq")

def publish_db_creation_task(user_id: str, db_name: str):
    try:
        connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
        channel = connection.channel()
        channel.queue_declare(queue='db_tasks', durable=True)
        
        msg = {"action": "create_database", "user_id": user_id, "db_name": db_name}
        
        channel.basic_publish(
            exchange='', routing_key='db_tasks',
            body=json.dumps(msg), properties=pika.BasicProperties(delivery_mode=2)
        )
        connection.close()
        return True
    except Exception as e:
        print(f"Error RabbitMQ: {e}")
        return False

def publish_table_creation_task(user_id: str, db_name: str, collection_name: str):
    try:
        connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
        channel = connection.channel()
        channel.queue_declare(queue='table_tasks', durable=True)
        
        msg = {
            "action": "create_collection",
            "user_id": user_id,
            "db_name": db_name,
            "collection_name": collection_name
        }
        
        channel.basic_publish(
            exchange='', routing_key='table_tasks',
            body=json.dumps(msg), properties=pika.BasicProperties(delivery_mode=2)
        )
        connection.close()
        return True
    except Exception as e:
        print(f"Error RabbitMQ table_tasks: {e}")
        return False

def publish_insert_task(db_name: str, collection_name: str, document: dict, owner_id: str):
    try:
        connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
        channel = connection.channel()
        channel.queue_declare(queue='insert_tasks', durable=True)
        
        msg = {
            "action": "insert_document",
            "db_name": db_name,
            "collection_name": collection_name,
            "document": document,
            "owner_id": owner_id
        }
        
        channel.basic_publish(
            exchange='', routing_key='insert_tasks',
            body=json.dumps(msg), properties=pika.BasicProperties(delivery_mode=2)
        )
        connection.close()
        return True
    except Exception as e:
        print(f"Error RabbitMQ insert_tasks: {e}")
        return False