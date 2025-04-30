"""
Módulo principal do servidor gRPC para gestão de pedidos

Implementa o serviço definido no proto e gerencia o fluxo completo de pedidos:
- Recebimento de novos pedidos
- Fila de preparação
- Atualização de status
- Notificação de observadores
"""

import grpc
from concurrent import futures
import time
import pedidos_pb2
import pedidos_pb2_grpc
from collections import deque
from datetime import datetime
import threading

# Estruturas globais de armazenamento
pedidos = {}            # Dicionário de pedidos (chave: número do pedido)
fila_pedidos = deque()  # Fila FIFO de pedidos pendentes
contador_pedidos = 0    # Contador sequencial para números de pedido
observadores = {}       # Observadores por pedido (padrão Observer)
pedido_em_preparo = None  # Pedido atualmente em preparação

class PedidoService(pedidos_pb2_grpc.PedidoServiceServicer):
    def EnviarPedido(self, request, context):
        """
        Implementação do RPC para envio de novo pedido
        
        Args:
            request (pedidos_pb2.Pedido): Dados do pedido recebido
            context (grpc.ServicerContext): Contexto da chamada RPC
            
        Returns:
            pedidos_pb2.RespostaPedido: Confirmação com número do pedido
        """
        global contador_pedidos
        contador_pedidos += 1
        
        # Cria e armazena novo pedido
        pedido = pedidos_pb2.Pedido(
            numero_pedido=contador_pedidos,
            cliente=request.cliente,
            itens=request.itens,
            status="PENDENTE"
        )
        
        pedidos[contador_pedidos] = pedido
        fila_pedidos.append(contador_pedidos)
        observadores[contador_pedidos] = []
        
        self._notificar_status(contador_pedidos, "PENDENTE")
        
        return pedidos_pb2.RespostaPedido(
            sucesso=True,
            mensagem=f"Pedido #{contador_pedidos} recebido com sucesso!",
            numero_pedido=contador_pedidos
        )

    def ReceberPedido(self, request, context):
        """
        Implementação do RPC para obtenção do próximo pedido (Cozinha)
        
        Args:
            request (pedidos_pb2.Vazio): Requisição vazia
            context (grpc.ServicerContext): Contexto da chamada RPC
            
        Returns:
            pedidos_pb2.Pedido: Próximo pedido da fila ou pedido vazio
        """
        global pedido_em_preparo
        
        if pedido_em_preparo is None and fila_pedidos:
            numero_pedido = fila_pedidos[0] 
            pedido = pedidos[numero_pedido]
            if pedido.status == "PENDENTE":
                pedido.status = "EM_PREPARO"
                pedido_em_preparo = numero_pedido
                self._notificar_status(numero_pedido, "EM_PREPARO")
                return pedido
        
        elif pedido_em_preparo is not None:
            return pedidos[pedido_em_preparo]
        
        return pedidos_pb2.Pedido(
            numero_pedido=0,
            cliente="",
            itens=[],
            status="SEM_PEDIDOS"
        )

    def AtualizarStatus(self, request, context):
        """
        Implementação do RPC para atualização de status
        
        Args:
            request (pedidos_pb2.AtualizacaoStatus): Nova configuração de status
            context (grpc.ServicerContext): Contexto da chamada RPC
            
        Returns:
            pedidos_pb2.RespostaPedido: Confirmação da operação
        """
        global pedido_em_preparo
        
        if request.numero_pedido in pedidos:
            pedido = pedidos[request.numero_pedido]
            pedido.status = request.novo_status
            
            # Lógica especial para status PRONTO
            if request.novo_status == "PRONTO":
                if request.numero_pedido in fila_pedidos:
                    fila_pedidos.popleft()
                if pedido_em_preparo == request.numero_pedido:
                    pedido_em_preparo = None
            
            self._notificar_status(request.numero_pedido, request.novo_status)
            
            return pedidos_pb2.RespostaPedido(
                sucesso=True,
                mensagem=f"Status do pedido #{request.numero_pedido} atualizado para {request.novo_status}",
                numero_pedido=request.numero_pedido
            )
        return pedidos_pb2.RespostaPedido(
            sucesso=False,
            mensagem=f"Pedido #{request.numero_pedido} não encontrado",
            numero_pedido=request.numero_pedido
        )

    def MonitorarStatus(self, request, context):
        """
        Implementação do RPC para monitoramento de status (streaming)
        
        Args:
            request (pedidos_pb2.NumeroPedido): Número do pedido a monitorar
            context (grpc.ServicerContext): Contexto da chamada RPC
            
        Yields:
            pedidos_pb2.StatusPedido: Atualizações de status em tempo real
        """
        numero_pedido = request.numero_pedido
        if numero_pedido in pedidos:
            # Envia status inicial
            yield pedidos_pb2.StatusPedido(
                numero_pedido=numero_pedido,
                status=pedidos[numero_pedido].status,
                timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
            
            # Mantém conexão aberta para atualizações
            while context.is_active():
                if numero_pedido in pedidos:
                    status_atual = pedidos[numero_pedido].status
                    yield pedidos_pb2.StatusPedido(
                        numero_pedido=numero_pedido,
                        status=status_atual,
                        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    )
                time.sleep(1)

    def _notificar_status(self, numero_pedido, status):
        """
        Método interno para notificação de observadores
        
        Args:
            numero_pedido (int): Número do pedido atualizado
            status (str): Novo status do pedido
        """
        if numero_pedido in observadores:
            for callback in observadores[numero_pedido]:
                try:
                    callback(status)
                except Exception as e:
                    print(f"Erro ao notificar status: {e}")

def iniciar_servidor():
    """
    Configura e inicia o servidor gRPC
    
    Configurações:
    - Porta: 50051
    - Workers: 10 threads
    - Conexão insegura (para ambiente de desenvolvimento)
    """
    servidor = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    pedidos_pb2_grpc.add_PedidoServiceServicer_to_server(
        PedidoService(), servidor)
    servidor.add_insecure_port('[::]:50051')
    servidor.start()
    print("Servidor de Pedidos iniciado na porta 50051")
    try:
        # Mantém o servidor ativo
        while True:
            time.sleep(86400)  # 24 horas
    except KeyboardInterrupt:
        servidor.stop(0)

if __name__ == '__main__':
    """Ponto de entrada principal para inicialização do servidor"""
    iniciar_servidor()