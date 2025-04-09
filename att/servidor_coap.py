import asyncio
from aiocoap import resource, Context, Message, Code

class SomaResource(resource.Resource):
    async def render_post(self, request):
        try:
            dados = request.payload.decode('utf-8')
            num1, num2 = map(float, dados.strip().split())
            resultado = num1 + num2
            resposta = f"Resultado da soma: {resultado}"
        except:
            resposta = "Erro: envie dois números separados por espaço."

        return Message(payload=resposta.encode('utf-8'))

async def main():
    root = resource.Site()
    root.add_resource(['soma'], SomaResource())

    await Context.create_server_context(root, bind=('127.0.0.1', 5683))

    print("Servidor CoAP rodando em coap://127.0.0.1/soma")
    await asyncio.get_running_loop().create_future()

if __name__ == "__main__":
    asyncio.run(main())
