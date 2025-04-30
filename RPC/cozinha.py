"""
Módulo principal do cliente da cozinha para integração com serviço gRPC de pedidos.
"""

import grpc
import pedidos_pb2
import pedidos_pb2_grpc
import time
import os

def processar_pedido(pedido):
    """
    Processa e exibe os detalhes de um pedido recebido.

    Args:
        pedido (pedidos_pb2.Pedido): Objeto contendo os dados do pedido

    Returns:
        bool: True se o pedido é válido e foi processado, False se é um pedido vazio
    """
    if pedido.numero_pedido == 0:
        return False
    
    # Exibe os detalhes do pedido formatados
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
    """
    Envia atualização de status para PRONTO para o servidor gRPC.

    Args:
        stub (pedidos_pb2_grpc.PedidoServiceStub): Cliente stub para comunicação com o servidor
        numero_pedido (int): Número de identificação do pedido a ser atualizado
    """
    # Cria a mensagem de atualização de status
    atualizacao = pedidos_pb2.AtualizacaoStatus(
        numero_pedido=numero_pedido,
        novo_status="PRONTO"
    )
    
    # Envia a atualização para o servidor
    resposta = stub.AtualizarStatus(atualizacao)
    print(f"\n{resposta.mensagem}")

def receber_pedidos():
    """
    Função principal que gerencia o fluxo de recebimento de pedidos.
    Configura a conexão gRPC e mantém loop contínuo para verificação de novos pedidos.
    """
    # Configuração do canal de comunicação gRPC
    with grpc.insecure_channel('localhost:50051') as canal:
        stub = pedidos_pb2_grpc.PedidoServiceStub(canal)
        print("Cozinha iniciada. Aguardando pedidos...")
        pedido_atual = None
        
        # Loop principal de verificação de pedidos
        while True:
            try:
                # Solicita novo pedido ao servidor
                pedido = stub.ReceberPedido(pedidos_pb2.Vazio())
                
                # Verifica se é um novo pedido válido
                if pedido.numero_pedido != 0 and (pedido_atual is None or pedido.numero_pedido != pedido_atual.numero_pedido):
                    if processar_pedido(pedido):
                        pedido_atual = pedido
                        # Aguarda confirmação do usuário para marcar como pronto
                        print("\nPressione ENTER para marcar o pedido como pronto...")
                        input()
                        marcar_como_pronto(stub, pedido.numero_pedido)
                        pedido_atual = None
                
            except grpc.RpcError as e:
                print(f"Erro ao receber pedido: {e}")
            time.sleep(2)  # Intervalo entre verificações de novos pedidos

if __name__ == '__main__':
    """
    Ponto de entrada principal da aplicação cliente da cozinha.
    """
    receber_pedidos()