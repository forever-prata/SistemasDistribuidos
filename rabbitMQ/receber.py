import pika

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost')
)
channel = connection.channel()

channel.queue_declare(queue='fila_exemplo')

def callback(ch, method, properties, body):
    print(f"Mensagem recebida: {body.decode()}")

channel.basic_consume(queue='fila_exemplo',
                      on_message_callback=callback,
                      auto_ack=True)

print('Aguardando mensagens. Pressione Ctrl+C para sair.')
channel.start_consuming()
