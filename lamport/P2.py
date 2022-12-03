import time
import threading
import pika

LOCAL_NODE_NAME = 'P2'
lock = threading.Lock()
lamport_clock = 0

class Broker:
  def __init__(self):
    self.connection = pika.BlockingConnection(pika.URLParameters('amqp://rasp:hissa@52.67.48.137:5672/%2F')) # Blocking
    self.channel = self.connection.channel()

  def start_receiving(self):
    self.channel.queue_declare(queue=LOCAL_NODE_NAME, auto_delete=True, arguments={'x-message-ttl' : 2000})
    self.channel.basic_consume(queue=LOCAL_NODE_NAME, on_message_callback=callback, auto_ack=True)
    self.channel.start_consuming() # Blocking 

  def send(self, node_name, msg):
    self.channel.queue_declare(queue=node_name, auto_delete=True, arguments={'x-message-ttl' : 2000})
    self.channel.basic_publish(exchange='', routing_key=node_name, body=msg)

def callback(ch, method, properties, body):
        print("Received:", body)
        msg = int(body)
        global lamport_clock
        lock.acquire() # regiao critica
        lamport_clock = max(msg, lamport_clock)
        lock.release()


def thread_receive():
    receive_broker = Broker()
    receive_broker.start_receiving()

if __name__ == "__main__":
    receiving = threading.Thread(target=thread_receive)
    receiving.start()
    broker = Broker()

    time.sleep(4)
    lock.acquire() # regiao critica
    lamport_clock += 1 # C1 <- C1 + 1 antes de qualquer evento
    lock.release()
    broker.send('P3', str(lamport_clock)) # envia para 2 seu relógio lógico atual
    print("Mensagem enviada para P3: ", lamport_clock)

    time.sleep(4)
    lock.acquire() # regiao critica
    lamport_clock += 1 # Evento local em P2
    lock.release()
    print("Evento local:", lamport_clock)

    print("lamport_clock final:", lamport_clock)
