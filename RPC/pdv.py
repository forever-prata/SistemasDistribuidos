import grpc
import pedidos_pb2
import pedidos_pb2_grpc
import threading
import time
from datetime import datetime

class MonitorStatus(threading.Thread):
    def __init__(self, numero_pedido):
        super().__init__()
        self.numero_pedido = numero_pedido
        self.daemon = True
        self.ultimo_status = None

    def run(self):
        with grpc.insecure_channel('localhost:50051') as canal:
            stub = pedidos_pb2_grpc.PedidoServiceStub(canal)
            try:
                for status in stub.MonitorarStatus(pedidos_pb2.NumeroPedido(numero_pedido=self.numero_pedido)):
                    if status.status != self.ultimo_status:
                        print(f"\n[Pedido #{self.numero_pedido}] Status: {status.status} ({status.timestamp})")
                        self.ultimo_status = status.status
            except grpc.RpcError as e:
                print(f"Erro ao monitorar status: {e}")

def enviar_pedido(cliente, itens):
    """Envia um novo pedido para o servidor"""
    with grpc.insecure_channel('localhost:50051') as canal:
        stub = pedidos_pb2_grpc.PedidoServiceStub(canal)
        pedido = pedidos_pb2.Pedido(
            cliente=cliente,
            itens=itens
        )
        resposta = stub.EnviarPedido(pedido)
        print(f"\nResposta do servidor: {resposta.mensagem}")
        
        monitor = MonitorStatus(resposta.numero_pedido)
        monitor.start()
        
        return resposta.numero_pedido

def menu_pdv():
    """Interface do PDV"""
    print("\n=== Sistema de Pedidos - PDV ===")
    print("1. Novo pedido")
    print("2. Sair")
    
    opcao = input("\nEscolha uma opção: ")
    
    if opcao == "1":
        cliente = input("Nome do cliente: ")
        itens = []
        print("\nDigite os itens do pedido (digite 'fim' para terminar):")
        while True:
            item = input("Item: ")
            if item.lower() == 'fim':
                break
            itens.append(item)
        
        if itens:
            enviar_pedido(cliente, itens)
        else:
            print("Pedido vazio! Adicione pelo menos um item.")
    
    return opcao != "2"

if __name__ == '__main__':
    print("PDV iniciado. Conectado ao servidor de pedidos.")
    while menu_pdv():
        pass 