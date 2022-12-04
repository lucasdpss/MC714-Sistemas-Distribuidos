import time
import threading
import pika

LOCAL_NODE_NAME = 'node1'

lider = 'node3'
node2_resp = 'NO_RESPONSE'
node1_resp = 'NO_RESPONSE'


class Broker:
    def __init__(self):
        self.connection = pika.BlockingConnection(pika.URLParameters(
            'amqp://rasp:hissa@52.67.48.137:5672/%2F'))  # Blocking
        self.channel = self.connection.channel()

    def start_receiving(self):
        self.channel.queue_declare(queue=LOCAL_NODE_NAME, auto_delete=True, arguments={
                                   'x-message-ttl': 2000})
        self.channel.basic_consume(
            queue=LOCAL_NODE_NAME, on_message_callback=callback, auto_ack=True)
        self.channel.start_consuming()  # Blocking

    def send(self, node_name, msg):
        self.channel.queue_declare(queue=node_name, auto_delete=True, arguments={
                                   'x-message-ttl': 2000})
        self.channel.basic_publish(
            exchange='', routing_key=node_name, body=msg)


def callback(ch, method, properties, body):

    origem, msg = body.split("_")[0], body.split("_")[1]
    print(f"{LOCAL_NODE_NAME} received message: {msg} from {origem}")

    # responde "teste" com OK
    if msg == "teste":
        broker = Broker()
        broker.send(origem, "OK")
        print(f"{LOCAL_NODE_NAME} sent {origem} message: OK")

    # responde "ELEICAO" com "OK" e propaga para nós superiores
    elif msg == "ELEICAO":
        broker = Broker()

        broker.send(origem, "OK")
        print(f"{LOCAL_NODE_NAME} sent {origem} message: OK")


def thread_receive():
    receive_broker = Broker()
    receive_broker.start_receiving()


def nova_eleicao():
    broker = Broker()

    # nó 3, por ser o maior, sempre será o lider quando ativo
    print(f"{LOCAL_NODE_NAME}: eu sou o líder eleito.")
    lider = LOCAL_NODE_NAME
    broker.send('node1', f'{LOCAL_NODE_NAME}_WINNER')
    broker.send('node2', f'{LOCAL_NODE_NAME}_WINNER')



if __name__ == "__main__":
    receiving = threading.Thread(target=thread_receive)
    receiving.start()
    broker = Broker()

    # processo convoca nova eleicao quando inicia
    nova_eleicao()

