"""
PocketOptionAPI - Interface Python não oficial para a plataforma PocketOption

Implementação da API da PocketOption fornecendo métodos
para autenticação, trading e obtenção de dados do mercado.

Versão: 1.0.99
"""

import asyncio
import sys
import json
from pocketoptionapi.api import PocketOptionAPI
import pocketoptionapi.constants as OP_code
import time
import pocketoptionapi.global_value as global_value
from pocketoptionapi.ssid_parser import process_ssid_input, validate_ssid_format
from collections import defaultdict
from collections import deque
from datetime import datetime, timezone
from loguru import logger

def nested_dict(n, type):
    """
    Cria um dicionário aninhado com profundidade n.
    
    Args:
        n (int): Número de níveis de aninhamento
        type: Tipo do valor final no dicionário
    
    Returns:
        defaultdict: Dicionário aninhado inicializado
    """
    if n == 1:
        return defaultdict(type)
    else:
        return defaultdict(lambda: nested_dict(n - 1, type))

async def get_balance():
    """Retorna o saldo atual da conta."""
    return global_value.balance

class PocketOption:
    """
    Classe principal para interação com a PocketOption.
    
    Fornece métodos para:
    - Conexão e autenticação
    - Trading
    - Obtenção de dados do mercado
    - Análise de mercado
    
    Attributes:
        __version__ (str): Versão atual da API
        ssid (str): ID de sessão para autenticação
        demo (bool): Modo de operação
    """
    
    __version__ = "1.0.99"

    def __init__(self, ssid):
        """
        Inicializa uma nova instância da API PocketOption.
        
        Args:
            ssid (str): ID de sessão para autenticação
        """
        # Parse e validação do SSID
        formatted_ssid, parsed_data = process_ssid_input(ssid, force_demo=True)
        
        if not formatted_ssid:
            raise ValueError("SSID inválido ou formato não suportado")
        
        # Usar SSID formatado
        global_value.SSID = formatted_ssid
        self.original_ssid = ssid
        self.formatted_ssid = formatted_ssid
        self.parsed_data = parsed_data
        
        # Configurar modo
        global_value.DEMO = True
        self.demo = True
        
        # Configuração básica
        self.api = PocketOptionAPI()

    def get_server_timestamp(self):
        """Retorna o timestamp atual do servidor em segundos."""
        return self.api.time_sync.server_timestamp
        
    def Stop(self):
        """Para a execução do programa."""
        sys.exit()

    def get_server_datetime(self):
        """Retorna o datetime atual do servidor."""
        return self.api.time_sync.server_datetime


    def get_async_order(self, buy_order_id):
        """
        Obtém informações de uma ordem assíncrona.
        
        Args:
            buy_order_id (str): ID da ordem de compra
            
        Returns:
            dict: Informações da ordem ou None se não encontrada
        """
        import pocketoptionapi.global_value as global_value
        
        # Verificar primeiro nos dados globais da ordem atual
        if global_value.order_data and isinstance(global_value.order_data, dict):
            if global_value.order_data.get("id") == buy_order_id:
                return global_value.order_data
        
        # Fallback para order_async (ordens fechadas)
        if not self.api.order_async or "deals" not in self.api.order_async:
            return None
            
        if not self.api.order_async["deals"] or len(self.api.order_async["deals"]) == 0:
            return None
            
        if self.api.order_async["deals"][0]["id"] == buy_order_id:
            return self.api.order_async["deals"][0]
        else:
            return None

    def get_async_order_id(self, buy_order_id):
        return self.api.order_async["deals"][0][buy_order_id]

    async def start_async(self):
        """Inicia a conexão assíncrona com o WebSocket."""
        return await self.api.async_connect()
        
    async def disconnect(self):
        """
        Fecha graciosamente a conexão WebSocket e limpa recursos de forma assíncrona.
        
        Este método:
        1. Fecha a conexão WebSocket
        2. Cancela todas as tasks pendentes
        3. Limpa recursos
        """
        try:
            if global_value.websocket_is_connected:
                await self.api.async_close()
                logger.success("Conexão WebSocket fechada com sucesso.")
            else:
                logger.info("WebSocket não estava conectado.")

            # Cancela task WebSocket se existir
            if hasattr(self, 'websocket_task') and self.websocket_task:
                self.websocket_task.cancel()
                try:
                    await self.websocket_task
                except asyncio.CancelledError:
                    logger.debug("Task WebSocket cancelada com sucesso.")

            # Limpa variáveis globais
            global_value.websocket_is_connected = False
            global_value.balance_updated = False
            
            logger.success("Desconexão realizada com sucesso.")

        except Exception as e:
            logger.error(f"Erro durante a desconexão: {e}")

    async def connect(self):
        """
        Estabelece conexão com a API da PocketOption.
        
        Este método conecta de forma assíncrona com o WebSocket.
        
        Returns:
            bool: True se a conexão foi iniciada com sucesso, False caso contrário
        """
        try:
            # Cria task assíncrona para conexão WebSocket
            self.websocket_task = asyncio.create_task(self.api.async_connect())
            
            # Aguarda conexão estabelecer com timeout maior para testar todos os servidores
            max_wait_time = 30  # 30 segundos para testar todos os servidores
            check_interval = 0.5  # Verificar a cada 500ms
            elapsed_time = 0
            
            while elapsed_time < max_wait_time and not global_value.websocket_is_connected:
                await asyncio.sleep(check_interval)
                elapsed_time += check_interval
            
            # Verifica se conectou
            if global_value.websocket_is_connected:
                logger.success("Conexão WebSocket estabelecida com sucesso")
                return True
            else:
                logger.error("Falha ao estabelecer conexão WebSocket - todos os servidores testados")
                return False

        except Exception as e:
            logger.error(f"Erro ao conectar: {e}")
            return False
    
    async def GetPayout(self, pair):
        """
        Obtém o payout (retorno percentual) para um par de moedas.
        
        Args:
            pair (str): Par de moedas (ex: "EURUSD")
            
        Returns:
            float: Percentual de payout ou None se não disponível
        """
        try:
            # Aguardar dados de payout estarem disponíveis
            max_wait = 10.0
            start_time = time.time()
            
            while (time.time() - start_time) < max_wait:
                data = self.api.GetPayoutData()
                if data and data != "{}":
                    try:
                        parsed_data = json.loads(data)
                        for item in parsed_data:
                            if len(item) > 5 and item[1] == pair:
                                return item[5]
                    except (json.JSONDecodeError, IndexError):
                        pass
                await asyncio.sleep(0.5)
            
            logger.warning(f"⚠️ Payout para {pair} não disponível após {max_wait}s")
            return None
            
        except Exception as e:
            logger.error(f"❌ Erro ao obter payout para {pair}: {e}")
            return None

    @staticmethod
    async def check_connect():
        """
        Verifica se a conexão WebSocket está ativa.
        
        Returns:
            bool: True se conectado, False caso contrário
        """
        if global_value.websocket_is_connected == 0:
            return False
        elif global_value.websocket_is_connected is None:
            return False
        else:
            return True

    @staticmethod
    async def get_balance():
        """
        Obtém o saldo atual da conta com retry automático.
        
        Returns:
            float: Saldo atual ou None se não disponível
        """
        # Aguarda até 10 segundos para o saldo ser atualizado
        max_wait = 10.0
        start_time = time.time()
        
        while (time.time() - start_time) < max_wait:
            if global_value.balance_updated and global_value.balance is not None:
                return global_value.balance
            await asyncio.sleep(0.5)  # Aguarda 500ms entre tentativas
        
        # Se ainda não tem saldo, tenta forçar atualização
        logger.warning("⚠️ Saldo não disponível, tentando forçar atualização...")
        return global_value.balance  # Retorna o que tiver, mesmo que None
            
    @staticmethod
    async def check_open():
        """
        Verifica se há ordens abertas.
        
        Returns:
            bool: True se há ordens abertas, False caso contrário
        """
        return global_value.order_open
        
    @staticmethod
    async def check_order_closed(ido):
        """
        Aguarda até que uma ordem específica seja fechada de forma assíncrona.
        
        Args:
            ido (int): ID da ordem
            
        Returns:
            int: ID da ordem fechada
        """
        logger.info(f"Aguardando fechamento da ordem {ido}")
        
        while ido not in global_value.order_closed:
            await asyncio.sleep(0.1)  # Sleep assíncrono

        for pack in global_value.stat:
            if pack[0] == ido:
               logger.success(f'Ordem {ido} fechada: {pack[1]}')

        return pack[0]
    
    async def buy(self, amount, active, action, expirations):
        """
        Realiza uma operação de compra assíncrona.
        
        Args:
            amount (float): Valor monetário da operação
            active (str): Ativo a ser negociado
            action (str): Tipo de operação ("call" ou "put")
            expirations (int): Tempo de expiração em segundos
            
        Returns:
            tuple: (bool, int) - (Sucesso da operação, ID da ordem ou None)
        """
        self.api.buy_multi_option = {}
        self.api.buy_successful = None
        req_id = "buy"

        try:
            if req_id not in self.api.buy_multi_option:
                self.api.buy_multi_option[req_id] = {"id": None}
            else:
                self.api.buy_multi_option[req_id]["id"] = None
        except Exception as e:
            logger.error(f"Erro ao inicializar buy_multi_option: {e}")
            return False, None

        global_value.order_data = None
        global_value.result = None

        await self.api.async_buyv3(amount, active, action, expirations, req_id)

        start_t = time.time()
        while True:
            if global_value.result is not None and global_value.order_data is not None:
                break
            if time.time() - start_t >= 5:
                if isinstance(global_value.order_data, dict) and "error" in global_value.order_data:
                    logger.error(global_value.order_data["error"])
                else:
                    logger.error("Erro desconhecido ocorreu durante a operação de compra")
                return False, None
            await asyncio.sleep(0.1)  # Mudança principal: sleep assíncrono

        logger.success(f"Ordem executada com sucesso: {global_value.order_data.get('id')}")
        return global_value.result, global_value.order_data.get("id", None)

    async def check_win(self, id_number):
        """
        Verifica o resultado de uma operação de forma assíncrona.
        
        Args:
            id_number (int): ID da ordem a ser verificada
            
        Returns:
            tuple: (float, str) - (Lucro/Prejuízo, Status da operação)
                Status pode ser: "ganhou", "perdeu" ou "desconhecido"
        """
        start_t = time.time()
        order_info = None
        
        logger.info(f"Aguardando resultado da ordem {id_number}...")

        # Aguardar resultado real da ordem via WebSocket
        import pocketoptionapi.global_value as global_value
        
        while True:
            try:
                # Verificar se há resultado nos dados do WebSocket
                if hasattr(self.api, 'order_async') and self.api.order_async:
                    if "deals" in self.api.order_async and self.api.order_async["deals"]:
                        for deal in self.api.order_async["deals"]:
                            if str(deal.get("id")) == str(id_number):
                                # Verificar se a ordem realmente finalizou (closePrice != 0)
                                close_price = deal.get("closePrice", 0)
                                if "profit" in deal and close_price != 0:
                                    profit = deal["profit"]
                                    logger.debug(f"🔍 DEBUG PROFIT - Deal completo: {deal}")
                                    logger.debug(f"🔍 DEBUG PROFIT - Profit: {profit}")
                                    
                                    # Lógica corrigida: profit positivo = ganhou, profit negativo = perdeu
                                    status = "ganhou" if profit > 0 else "perdeu"
                                    
                                    logger.success(f"Ordem {id_number} finalizada: {status} - Profit: {profit}")
                                    return profit, status
                
                # Verificar nos dados globais de ordem
                if global_value.order_data and str(global_value.order_data.get("id")) == str(id_number):
                    # Verificar se a ordem realmente finalizou (closePrice != 0)
                    close_price = global_value.order_data.get("closePrice", 0)
                    if "profit" in global_value.order_data and global_value.order_data["profit"] != 0 and close_price != 0:
                        profit = global_value.order_data["profit"]
                        logger.debug(f"🔍 DEBUG PROFIT GLOBAL - Order_data completo: {global_value.order_data}")
                        logger.debug(f"🔍 DEBUG PROFIT GLOBAL - Profit: {profit}")
                        
                        # Lógica corrigida: profit positivo = ganhou, profit negativo = perdeu
                        status = "ganhou" if profit > 0 else "perdeu"
                        
                        logger.success(f"Ordem {id_number} resultado final: {status} - Profit: {profit}")
                        return profit, status
                
            except Exception as e:
                logger.debug(f"Erro ao obter resultado da ordem: {e}")

            if time.time() - start_t >= 120:
                logger.warning(f"⏰ Timeout: Ordem {id_number} ainda não finalizada após 120s")
                # Retornar dados disponíveis mesmo sem resultado final
                order_info = self.get_async_order(id_number)
                if order_info:
                    logger.info(f"📊 Dados disponíveis da ordem: {order_info}")
                return None, "timeout"

            await asyncio.sleep(2.0)  # Aguardar mais tempo entre verificações

    @staticmethod
    def last_time(timestamp, period):
        """
        Calcula o timestamp do início do período atual.
        
        Args:
            timestamp (int): Timestamp em segundos
            period (int): Período em segundos
            
        Returns:
            int: Timestamp do início do período
        """
        timestamp_arredondado = (timestamp // period) * period
        return int(timestamp_arredondado)

    async def get_candles(self, active, period, start_time=None, count=6000, count_request=1):
        """
        Obtém dados históricos de velas (candles) para um ativo de forma assíncrona.
        
        Args:
            active (str): Código do ativo (ex: "EURUSD")
            period (int): Período de cada vela em segundos
            start_time (int, optional): Timestamp final para a última vela
            count (int): Número de velas por requisição (max: 9000)
            count_request (int): Número de requisições para dados históricos
            
        Returns:
            list: Lista de dicionários com os dados das velas, contendo:
                - time: Timestamp da vela
                - open: Preço de abertura
                - high: Preço máximo
                - low: Preço mínimo
                - close: Preço de fechamento
                - volume: Volume negociado
        """
        try:
            logger.info(f"Obtendo candles para {active} - período: {period}s")
            
            if start_time is None:
                time_sync = self.get_server_timestamp()
                time_red = self.last_time(time_sync, period)
            else:
                time_red = start_time
                time_sync = self.get_server_timestamp()

            all_candles = []

            for request_num in range(count_request):
                self.api.history_data = None
                logger.debug(f"Requisição {request_num + 1}/{count_request}")

                while True:
                    try:
                        await self.api.async_getcandles(active, 30, count, time_red)

                        # Aguarda dados de forma assíncrona
                        for i in range(1, 100):
                            if self.api.history_data is None:
                                await asyncio.sleep(0.1)  # Sleep assíncrono
                            if i == 99:
                                break

                        if self.api.history_data is not None:
                            all_candles.extend(self.api.history_data)
                            logger.debug(f"Obtidos {len(self.api.history_data)} candles")
                            break

                    except Exception as e:
                        logger.error(f"Erro ao obter candles: {e}")

                all_candles = sorted(all_candles, key=lambda x: x["time"])

                if all_candles:
                    time_red = all_candles[0]["time"]

            # Ordenar por tempo
            all_candles = sorted(all_candles, key=lambda x: x['time'])
            
            # Processar dados para OHLC usando JSON
            candles_json = self._process_candles_to_ohlc(all_candles, period)
            
            logger.success(f"Candles obtidos com sucesso: {len(candles_json)} registros")
            return candles_json
            
        except Exception as e:
            logger.error(f"Erro ao obter candles: {e}")
            return None

    def _process_candles_to_ohlc(self, candles_data, period):
        """Converte dados de velas para formato OHLC simples"""
        if not candles_data:
            return []
            
        # Processar dados simples
        ohlc_data = []
        for candle in candles_data:
            ohlc_data.append({
                'time': datetime.fromtimestamp(candle['time'], tz=timezone.utc),
                'open': candle.get('open', candle['price']),
                'high': candle.get('high', candle['price']),
                'low': candle.get('low', candle['price']), 
                'close': candle.get('close', candle['price'])
            })
        
        return ohlc_data

    def change_symbol(self, active, period):
        return self.api.change_symbol(active, period)

    def sync_datetime(self):
        return self.api.synced_datetime
