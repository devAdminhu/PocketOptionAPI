"""PocketOption API - v1.0.0"""

import asyncio
import sys
from tzlocal import get_localzone
import json
from pocketoptionapi.api import PocketOptionAPI
import pocketoptionapi.constants as OP_code
import time
from loguru import logger
import operator
import pocketoptionapi.global_value as global_value
from pocketoptionapi.ssid_parser import process_ssid_input, validate_ssid_format
from collections import defaultdict
from collections import deque
from datetime import datetime, timezone

local_zone_name = get_localzone()

def nested_dict(n, type):
    """Create nested dict with depth n"""
    if n == 1:
        return defaultdict(type)
    else:
        return defaultdict(lambda: nested_dict(n - 1, type))

async def get_balance():
    """Get current balance"""
    return global_value.balance

class PocketOption:
    """
    Classe principal para interação com a PocketOption.
    
    Fornece métodos para:
    - Conexão e autenticação
    - Trading (compra/venda)
    - Obtenção de dados do mercado
    - Gerenciamento de conta
    
    Attributes:
        __version__ (str): Versão atual da API
        ssid (str): ID de sessão para autenticação
        demo (bool): Se True, usa conta demo. Se False, usa conta real
    """
    
    __version__ = "1.0.0"

    def __init__(self, ssid, demo):
        """Clean docstring"""
        # Parse e validação do SSID
        logger.info("🔧 Processando SSID...")
        formatted_ssid, parsed_data = process_ssid_input(ssid, force_demo=demo)
        
        if not formatted_ssid:
            raise ValueError("❌ SSID inválido ou formato não suportado")
        
        # Usar SSID formatado
        global_value.SSID = formatted_ssid
        self.original_ssid = ssid
        self.formatted_ssid = formatted_ssid
        self.parsed_data = parsed_data
        
        # Configurar modo
        global_value.DEMO = demo
        self.demo = demo
        
        # Timeframes disponíveis em segundos
        self.size = [1, 5, 10, 15, 30, 60, 120, 300, 600, 900, 1800,
                     3600, 7200, 14400, 28800, 43200, 86400, 604800, 2592000]
        self.suspend = 0.5
        
        # Log informações de configuração
        logger.success(f"✅ PocketOption inicializada:")
        logger.info(f"   📋 Modo: {'Demo' if demo else 'Real'}")
        logger.info(f"   👤 UID: {parsed_data.get('uid', 'N/A')}")
        logger.info(f"   🖥️  Platform: {parsed_data.get('platform', 'N/A')}")
        logger.info(f"   🔧 SSID formatado e validado")
        self.thread = None
        self.subscribe_candle = []
        self.subscribe_candle_all_size = []
        self.subscribe_mood = []
        # Dados para operações digitais
        self.get_digital_spot_profit_after_sale_data = nested_dict(2, int)
        self.get_realtime_strike_list_temp_data = {}
        self.get_realtime_strike_list_temp_expiration = 0
        self.SESSION_HEADER = {
            "User-Agent": r"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          r"Chrome/66.0.3359.139 Safari/537.36"}
        self.SESSION_COOKIE = {}
        self.api = PocketOptionAPI()
        # Usar apenas métodos assíncronos

    def get_server_timestamp(self):
        """Get server timestamp"""
        return self.api.time_sync.server_timestamp
        
    def Stop(self):
        """Stop execution"""
        sys.exit()

    def get_server_datetime(self):
        """Get server datetime"""
        return self.api.time_sync.server_datetime

    def set_session(self, header, cookie):
        """Set session headers and cookies"""
        self.SESSION_HEADER = header
        self.SESSION_COOKIE = cookie

    def get_async_order(self, buy_order_id):
        """Get async order info"""
        import pocketoptionapi.global_value as global_value
        
        if global_value.order_data and isinstance(global_value.order_data, dict):
            if global_value.order_data.get("id") == buy_order_id:
                return global_value.order_data
        
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
        """Connect to WebSocket"""
        return await self.api.async_connect()
        
    async def disconnect(self):
        """Disconnect WebSocket"""
        try:
            if global_value.websocket_is_connected:
                await self.api.async_close()
                logger.success("Conexão WebSocket fechada com sucesso.")
            else:
                logger.info("WebSocket não estava conectado.")

            if hasattr(self, 'websocket_task') and self.websocket_task:
                self.websocket_task.cancel()
                try:
                    await self.websocket_task
                except asyncio.CancelledError:
                    logger.debug("Task WebSocket cancelada com sucesso.")

            global_value.websocket_is_connected = False
            global_value.balance_updated = False
            
            logger.success("Desconexão realizada com sucesso.")

        except Exception as e:
            logger.error(f"Erro durante a desconexão: {e}")

    async def connect(self):
        """Connect to API"""
        try:
            self.websocket_task = asyncio.create_task(self.api.async_connect())
            
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
        """Clean docstring"""
        try:
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
        """Clean docstring"""
        logger.info(f"Aguardando fechamento da ordem {ido}")
        
        while ido not in global_value.order_closed:
            await asyncio.sleep(0.1)  # Sleep assíncrono

        for pack in global_value.stat:
            if pack[0] == ido:
               logger.success(f'Ordem {ido} fechada: {pack[1]}')

        return pack[0]
    
    async def buy(self, amount, active, action, expirations):
        """Clean docstring"""
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
        """Clean docstring"""
        start_t = time.time()
        order_info = None
        
        logger.info(f"Aguardando resultado da ordem {id_number}...")

        import pocketoptionapi.global_value as global_value
        
        while True:
            try:
                if hasattr(self.api, 'order_async') and self.api.order_async:
                    if "deals" in self.api.order_async and self.api.order_async["deals"]:
                        for deal in self.api.order_async["deals"]:
                            if str(deal.get("id")) == str(id_number):
                                close_price = deal.get("closePrice", 0)
                                if "profit" in deal and close_price != 0:
                                    profit = deal["profit"]
                                    logger.debug(f"🔍 DEBUG PROFIT - Deal completo: {deal}")
                                    logger.debug(f"🔍 DEBUG PROFIT - Profit: {profit}")
                                    
                                    # Lógica corrigida: profit positivo = ganhou, profit negativo = perdeu
                                    status = "ganhou" if profit > 0 else "perdeu"
                                    
                                    logger.success(f"Ordem {id_number} finalizada: {status} - Profit: {profit}")
                                    return profit, status
                
                if global_value.order_data and str(global_value.order_data.get("id")) == str(id_number):
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
        """Clean docstring"""
        timestamp_arredondado = (timestamp // period) * period
        return int(timestamp_arredondado)

    async def get_candles(self, active, period, start_time=None, count=6000, count_request=1):
        """Clean docstring"""
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
        """Converte dados de velas para formato OHLC usando JSON puro"""
        if not candles_data:
            return []
            
        # Agrupar dados por período
        grouped_data = {}
        
        for candle in candles_data:
            # Arredondar timestamp para o período
            timestamp = candle['time']
            period_start = (timestamp // period) * period
            
            if period_start not in grouped_data:
                grouped_data[period_start] = []
            grouped_data[period_start].append(candle['price'])
        
        # Converter para OHLC
        ohlc_data = []
        for timestamp in sorted(grouped_data.keys()):
            prices = grouped_data[timestamp]
            if prices:
                ohlc_data.append({
                    'time': datetime.fromtimestamp(timestamp, tz=timezone.utc),
                    'open': prices[0],
                    'high': max(prices),
                    'low': min(prices), 
                    'close': prices[-1]
                })
        
        return ohlc_data

    @staticmethod
    def process_data_history(data, period):
        """
        Este método recebe dados históricos, processa usando JSON puro, arredonda os tempos para o período mais próximo,
        e calcula os valores OHLC (Abertura, Máxima, Mínima, Fechamento). Retorna uma lista de dicionários.

        :param dict data: Dados históricos que incluem marcas de tempo e preços.
        :param int period: Período em minutos
        :return: Lista de dicionários que contém os valores OHLC agrupados por períodos arredondados.
        """
        history_data = data['history']
        if not history_data:
            return []
            
        # Converter período de minutos para segundos
        period_seconds = period * 60
        
        # Agrupar dados por período
        grouped_data = {}
        
        for timestamp, price in history_data:
            # Arredondar timestamp para o período
            dt = datetime.fromtimestamp(timestamp, tz=timezone.utc)
            period_start = int((timestamp // period_seconds) * period_seconds)
            
            if period_start not in grouped_data:
                grouped_data[period_start] = []
            grouped_data[period_start].append(price)
        
        # Converter para OHLC
        ohlc_data = []
        for timestamp in sorted(grouped_data.keys()):
            prices = grouped_data[timestamp]
            if prices:
                ohlc_data.append({
                    'time': timestamp,
                    'open': prices[0],
                    'high': max(prices),
                    'low': min(prices), 
                    'close': prices[-1]
                })
        
        # Remover último item (equivalente ao iloc[:-1])
        if ohlc_data:
            ohlc_data = ohlc_data[:-1]
            
        return ohlc_data

    @staticmethod
    def process_candle(candle_data, period):
        """
        Resumo: Este método estático do Python processa dados de velas financeiras.
        Realiza operações de limpeza e organização usando JSON puro, incluindo ordenação por tempo,
        remoção de duplicatas e reindexação. Verifica se as diferenças de tempo entre entradas
        consecutivas são iguais ao período especificado.

        :param list candle_data: Dados das velas a processar.
        :param int period: Período de tempo entre as velas em segundos.
        :return: Tupla com (dados processados, validação de diferenças de tempo).
        """
        if not candle_data:
            return [], False
            
        # Ordenar por tempo
        sorted_data = sorted(candle_data, key=lambda x: x['time'])
        
        # Remover duplicatas mantendo primeiro
        seen_times = set()
        unique_data = []
        for candle in sorted_data:
            if candle['time'] not in seen_times:
                unique_data.append(candle)
                seen_times.add(candle['time'])
        
        # Forward fill - preencher valores faltantes com anterior
        processed_data = []
        last_values = {}
        
        for candle in unique_data:
            filled_candle = candle.copy()
            for key, value in candle.items():
                if value is None and key in last_values:
                    filled_candle[key] = last_values[key]
                else:
                    last_values[key] = value
            processed_data.append(filled_candle)
        
        diff_valid = True
        if len(processed_data) > 1:
            for i in range(1, len(processed_data)):
                time_diff = processed_data[i]['time'] - processed_data[i-1]['time']
                if time_diff != period:
                    diff_valid = False
                    break
        
        return processed_data, diff_valid

    def change_symbol(self, active, period):
        return self.api.change_symbol(active, period)

    def sync_datetime(self):
        return self.api.synced_datetime
