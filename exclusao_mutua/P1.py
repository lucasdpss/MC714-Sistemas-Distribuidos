import time
import threading
import pika

LOCAL_NODE_NAME = 'process1'
node_in_CS = '' # no que esta na regiao critica
queue = []

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
    body = body.decode("utf-8") # mensagens do tipo: "REQUEST P2", um request do no P2
    print("Received:", body)
    msg = body.split()[0]
    node_name = body.split()[1]
    global node_in_CS
    if(msg == "REQUEST"):
        if(node_in_CS == ''):
            node_in_CS = node_name
            self.send(node_name, "OK "+ LOCAL_NODE_NAME)
            print(" [*] Sent: OK to "+ node_name)
        else:
            queue.append(node_name)
    elif(msg == "RELEASE"):
        if len(queue) > 0:
            node = queue.pop(0)
            node_in_CS = node
            self.send(node, "OK "+ LOCAL_NODE_NAME)
            print(" [*] Sent: OK to "+ node)
        else:
            node_in_CS = ''
    print(queue)
                

def thread_receive():
    receive_broker = Broker()
    receive_broker.start_receiving()

if __name__ == "__main__":
    node_in_CS = ''
    receiving = threading.Thread(target=thread_receive)
    receiving.start()

    while True:
        time.sleep(4) # Thread principal apenas recebe mensagens assincronamente, nao precisa fazer nada nesse loop
