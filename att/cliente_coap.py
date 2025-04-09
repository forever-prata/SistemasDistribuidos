import asyncio
from aiocoap import *

async def main():
    context = await Context.create_client_context()

    num1 = input("Digite o primeiro número: ")
    num2 = input("Digite o segundo número: ")
    dados = f"{num1} {num2}".encode('utf-8')

    request = Message(code=POST, payload=dados, uri="coap://127.0.0.1:5683/soma")

    try:
        response = await context.request(request).response
        print("Resposta do servidor:", response.payload.decode())
    except Exception as e:
        print("Erro ao enviar requisição:", e)

if __name__ == "__main__":
    asyncio.run(main())
