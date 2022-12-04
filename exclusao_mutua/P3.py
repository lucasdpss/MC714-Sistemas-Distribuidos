import time
import threading
import pika

LOCAL_NODE_NAME = 'process3'
access = False

class Broker:
  def __init__(self):
    self.connection = pika.BlockingConnection(pika.URLParameters('amqp://rasp:hissa@52.67.48.137:5672/%2F')) # Blocking
    self.channel = self.connection.channel()

  def start_receiving(self):
    self.channel.queue_declare(queue=LOCAL_NODE_NAME, auto_delete=True, arguments={'x-message-ttl' : 2000})
    self.channel.basic_consume(queue=LOCAL_NODE_NAME, on_message_callback=self.callback, auto_ack=True)
    self.channel.start_consuming() # Blocking 

  def send(self, node_name, msg):
    self.channel.queue_declare(queue=node_name, auto_delete=True, arguments={'x-message-ttl' : 2000})
    self.channel.basic_publish(exchange='', routing_key=node_name, body=msg)

  def callback(self, ch, method, properties, body):
    global access
    body = body.decode("utf-8") # mensagens do tipo: "OK P2", um request do no P2
    print("Received:", body)
    msg = body.split()[0]
    if(msg == "OK"):
      access = True
    
                

def thread_receive():
    receive_broker = Broker()
    receive_broker.start_receiving()

if __name__ == "__main__":
    receiving = threading.Thread(target=thread_receive)
    receiving.start()
    broker = Broker()
    coordinator = 'process1'
    access = False

    while True:
        time.sleep(3)
        broker.send(coordinator, "REQUEST " + LOCAL_NODE_NAME) # envia para o coordenador um request com o seu nome
        print("Sent REQUEST to coordinator")
        while(access == False): # espera ter acesso ao recurso
          pass

        print("Entering critical section")
        time.sleep(1) # 2 segundos fazendo a operacao critica

        access = False
        broker.send(coordinator, "RELEASE " + LOCAL_NODE_NAME) # envia para o coordenador um request com o seu nome
        print("Sent RELEASE to coordinator")


