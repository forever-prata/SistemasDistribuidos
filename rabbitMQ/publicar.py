import pika

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost')
)
channel = connection.channel()

channel.queue_declare(queue='fila_exemplo')

print("Digite suas mensagens. Digite 'sair' para encerrar.")

while True:
    mensagem = input("Mensagem: ")
    if mensagem.lower() == "sair":
        break
    channel.basic_publish(
        exchange='',
        routing_key='fila_exemplo',
        body=mensagem
    )
    print(f"Mensagem enviada: {mensagem}")

connection.close()
