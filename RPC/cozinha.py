import grpc
import pedidos_pb2
import pedidos_pb2_grpc
import time
import os

def processar_pedido(pedido):
    """Exibe os detalhes do pedido recebido"""
    if pedido.numero_pedido == 0:
        return False
    
    print("\n=== Pedido em Preparo ===")
    print(f"Pedido #{pedido.numero_pedido}")
    print(f"Cliente: {pedido.cliente}")
    print("\nItens:")
    for item in pedido.itens:
        print(f"- {item}")
    print(f"\nStatus: {pedido.status}")
    print("===========================")
    return True

def marcar_como_pronto(stub, numero_pedido):
    """Marca um pedido como pronto"""
    atualizacao = pedidos_pb2.AtualizacaoStatus(
        numero_pedido=numero_pedido,
        novo_status="PRONTO"
    )
    resposta = stub.AtualizarStatus(atualizacao)
    print(f"\n{resposta.mensagem}")

def receber_pedidos():
    """Recebe pedidos do servidor"""
    with grpc.insecure_channel('localhost:50051') as canal:
        stub = pedidos_pb2_grpc.PedidoServiceStub(canal)
        print("Cozinha iniciada. Aguardando pedidos...")
        pedido_atual = None
        
        while True:
            try:
                pedido = stub.ReceberPedido(pedidos_pb2.Vazio())
                
                if pedido.numero_pedido != 0 and (pedido_atual is None or pedido.numero_pedido != pedido_atual.numero_pedido):
                    if processar_pedido(pedido):
                        pedido_atual = pedido
                        print("\nPressione ENTER para marcar o pedido como pronto...")
                        input()
                        marcar_como_pronto(stub, pedido.numero_pedido)
                        pedido_atual = None
                
            except grpc.RpcError as e:
                print(f"Erro ao receber pedido: {e}")
            time.sleep(2)

if __name__ == '__main__':
    receber_pedidos() 