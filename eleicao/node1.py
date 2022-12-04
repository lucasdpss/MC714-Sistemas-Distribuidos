import time
import threading
import pika

LOCAL_NODE_NAME = 'node1'

eleicao = False
lider = 'node3'
wait_node2 = False
wait_node3 = False
node2_resp = 'NO_RESPONSE'
node3_resp = 'NO_RESPONSE'


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
	global lider, node2_resp, node3_resp
	origem, msg = body.decode(
		"utf-8").split("_")[0], body.decode("utf-8").split("_")[1]
	print(f"{LOCAL_NODE_NAME} received message: {msg} from {origem}")

	if msg == "teste":
		broker = Broker()
		broker.send(origem, f"{LOCAL_NODE_NAME}_OK")
		print(f"{LOCAL_NODE_NAME} sent {origem} message: OK")

	elif msg == "ELEICAO":
		broker = Broker()

		broker.send(origem, f"{LOCAL_NODE_NAME}_OK")
		print(f"{LOCAL_NODE_NAME} sent {origem} message: OK")

		broker.send('node2', 'node1_ELEICAO')
		print(f"{LOCAL_NODE_NAME} sent node1 message: ELEICAO")

		broker.send('node3', 'node3_ELEICAO')
		print(f"{LOCAL_NODE_NAME} sent node2 message: ELEICAO")

	elif origem == "node2" and msg == "OK":
		node2_resp = "OK"

	elif origem == "node3" and msg == "OK":
		node3_resp = "OK"

	elif msg == "WINNER":
		lider = origem
		print(f"{LOCAL_NODE_NAME} reconhece {lider} como coordenador.")


def thread_receive():
	receive_broker = Broker()
	receive_broker.start_receiving()


def nova_eleicao():
	global node3_resp, node2_resp, lider
	broker = Broker()

	broker.send(lider, 'node1_ELEICAO')
	print(f"{LOCAL_NODE_NAME} sent node3 message: ELEICAO")
	t1_start = time.perf_counter()

	# enquanto nó 3 não responder em até 5s
	while (time.perf_counter() - t1_start < 5):
		if node3_resp == "OK":
			break

	# enquanto nó 2 não responder em até 5s
	broker.send('node2', 'node1_ELEICAO')
	print(f"{LOCAL_NODE_NAME} sent node2 message: ELEICAO")
	t1_start = time.perf_counter()
	while (time.perf_counter() - t1_start < 5):
		if node2_resp == "OK":
			break

	# se ninguém responder, vence a eleição
	if node2_resp == "NO_RESPONSE" and node3_resp == "NO_RESPONSE":
		print(f"{LOCAL_NODE_NAME}: eu sou o líder eleito.")
		lider = LOCAL_NODE_NAME
		broker.send('node2', f'{LOCAL_NODE_NAME}_WINNER')
		broker.send('node3', f'{LOCAL_NODE_NAME}_WINNER')

	node2_resp = "NO_RESPONSE"
	node3_resp = "NO_RESPONSE"


if __name__ == "__main__":
	receiving = threading.Thread(target=thread_receive)
	receiving.start()
	broker = Broker()

	# processo convoca nova eleicao quando inicia
	nova_eleicao()

	while(True):
		time.sleep(2)
		
		print(f"lider: {lider}")
		if lider == LOCAL_NODE_NAME:
			continue

		# checa se lider está respondendo
		broker.send(lider, 'node1_teste')
		print(f"{LOCAL_NODE_NAME} sent {lider} message: teste")
		t1_start = time.perf_counter()

		# enquanto nó líder não responder em até 5s
		while (time.perf_counter() - t1_start < 5):
			pass

		# convoca nova eleição caso lider não responda
		if lider == 'node2' and node2_resp == "NO_RESPONSE":
			nova_eleicao()
		elif lider == 'node3' and node3_resp == "NO_RESPONSE":
			nova_eleicao()
		
		# reinicia resposta dos nós 2 e 3 ao default
		node2_resp = "NO_RESPONSE"
		node3_resp = "NO_RESPONSE"
