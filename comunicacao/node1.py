import time
import threading
import pika

LOCAL_NODE_NAME = 'node1'

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
        print(body)


def thread_receive():
    receive_broker = Broker()
    receive_broker.start_receiving()

if __name__ == "__main__":
    receiving = threading.Thread(target=thread_receive)
    receiving.start()
    broker = Broker()
    
    while True:
        time.sleep(4)
        broker.send('node2', 'Hello from node 1')
        broker.send('node3', 'Hello from node 1')
        print("[x] Sent msg to node 2 and 3")