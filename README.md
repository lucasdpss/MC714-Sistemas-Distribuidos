# MC714-Sistemas-Distribuidos
Repositório para o projeto 2 da disciplina de Sistemas Distribuídos.
* Gabriel Dourado Seabra - RA: 216213
* Lucas de Paula Soares   - RA: 201867


## Como compilar e executar
Dentro de cada pasta "comunicacao", "eleicao", "exclusao mutua" e "lamport" tem o código python de cada nó.

Utilizamos Python 3.9 e o serviço de message broker "RabbitMQ", o pacote python utilizado por ele é o pika, e é preciso instalá-lo nas máquinas que vão rodar os algoritmos:
```
pip3 install pika
```

E para rodar em cada instância basta rodar o script python:
```
python3 node_x.py
```

Para que a comunicação entre os nós funcione é preciso ter um servidor rodando o serviço do RabbitMQ, por padrão é utilizado a porta 5672, portanto deve ser considerada na regra de firewall do serviço de nuvem. No nosso projeto utilizamos um servidor aws EC2 para o nosso servidor RabbitMQ. 
