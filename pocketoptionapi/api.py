"""
Interface principal para comunicação com a API da PocketOption.
"""
import asyncio
import datetime
import time
import json
import logging
import threading
import requests
import ssl
import atexit
from collections import deque
from loguru import logger
from pocketoptionapi.ws.client import WebsocketClient
from pocketoptionapi.ws.channels.get_balances import *
from pocketoptionapi.ws.channels.ssid import Ssid
from pocketoptionapi.ws.channels.candles import GetCandles
from pocketoptionapi.ws.channels.buyv3 import *
from pocketoptionapi.ws.objects.timesync import TimeSync
from pocketoptionapi.ws.objects.candles import Candles
import pocketoptionapi.global_value as global_value
from pocketoptionapi.ws.channels.change_symbol import ChangeSymbol
from collections import defaultdict
from pocketoptionapi.ws.objects.time_sync import TimeSynchronizer

def nested_dict(n, type):
    if n == 1:
        return defaultdict(type)
    else:
        return defaultdict(lambda: nested_dict(n - 1, type))

class PocketOptionAPI(object):
    """Classe para comunicação com a API da Pocket Option."""

    socket_option_opened = {}
    time_sync = TimeSync()
    sync = TimeSynchronizer()
    timesync = None
    candles = Candles()
    api_option_init_all_result = []
    api_option_init_all_result_v2 = []
    underlying_list_data = None
    position_changed = None
    instrument_quites_generated_data = nested_dict(2, dict)
    instrument_quotes_generated_raw_data = nested_dict(2, dict)
    instrument_quites_generated_timestamp = nested_dict(2, dict)
    strike_list = None
    leaderboard_deals_client = None
    order_async = None
    instruments = None
    financial_information = None
    buy_id = None
    buy_order_id = None
    traders_mood = {}  # obtém porcentagem alta (put)
    order_data = None
    positions = None
    position = None
    deferred_orders = None
    position_history = None
    position_history_v2 = None
    available_leverages = None
    order_canceled = None
    close_position_data = None
    overnight_fee = None
    digital_option_placed_id = None
    live_deal_data = nested_dict(3, deque)
    subscribe_commission_changed_data = nested_dict(2, dict)
    real_time_candles = nested_dict(3, dict)
    real_time_candles_maxdict_table = nested_dict(2, dict)
    candle_generated_check = nested_dict(2, dict)
    candle_generated_all_size_check = nested_dict(1, dict)
    api_game_getoptions_result = None
    sold_options_respond = None
    tpsl_changed_respond = None
    auto_margin_call_changed_respond = None
    top_assets_updated_data = {}
    get_options_v2_data = None
    buy_multi_result = None
    buy_multi_option = {}
    result = None
    training_balance_reset_request = None
    balances_raw = None
    user_profile_client = None
    leaderboard_userinfo_deals_client = None
    users_availability = None
    history_data = None
    historyNew = None
    server_timestamp = None
    sync_datetime = None

    def __init__(self, proxies=None):
        """
        :param dict proxies: (opcional) Os proxies para requisições http.
        """
        self.websocket_client = None
        self.websocket_thread = None
        self.session = requests.Session()
        self.session.verify = False
        self.session.trust_env = False
        self.proxies = proxies
        # usado para determinar se uma ordem de compra foi definida ou falhou
        # Se for None, não houve ordem de compra ainda ou acabou de ser enviada
        # Se for False, a última falhou
        # Se for True, a última ordem de compra foi bem-sucedida
        self.buy_successful = None
        self.loop = asyncio.get_event_loop()
        self.websocket_client = WebsocketClient(self)

    @property
    def websocket(self):
        """Propriedade para obter websocket.

        :returns: A instância de :class:`WebSocket <websocket.WebSocket>`.
        """
        return self.websocket_client
    
    def GetPayoutData(self):
        return global_value.PayoutData

    async def send_websocket_request(self, name, msg, request_id="", no_force_send=True):
        """Envia requisição websocket de forma assíncrona.

        :param no_force_send: Se não deve forçar o envio
        :param request_id: ID da requisição
        :param str name: Nome da requisição websocket
        :param dict msg: Mensagem da requisição websocket
        """
        return await self.async_send_websocket_request(name, msg, request_id, no_force_send)

    async def async_send_websocket_request(self, name, msg, request_id="", no_force_send=True):
        """Versão assíncrona do send_websocket_request com locks async-safe."""
        logger = logging.getLogger(__name__)

        data = f'42{json.dumps(msg)}'

        # Usar locks async-safe quando disponíveis, senão fallback para legacy
        try:
            write_lock = await global_value.get_write_lock()
            async with write_lock:
                if self.websocket and hasattr(self.websocket, 'send_message'):
                    await self.websocket.send_message(data)
                else:
                    logger.error("WebSocket não disponível para envio")
        except Exception as e:
            logger.warning(f"Fallback para método legacy: {e}")
            while (global_value.ssl_Mutual_exclusion or global_value.ssl_Mutual_exclusion_write) and no_force_send:
                await asyncio.sleep(0.001)
            
            global_value.ssl_Mutual_exclusion_write = True
            try:
                if self.websocket and hasattr(self.websocket, 'send_message'):
                    await self.websocket.send_message(data)
            finally:
                global_value.ssl_Mutual_exclusion_write = False
        
        logger.debug(data)

    async def start_websocket(self):
        """Inicia websocket de forma assíncrona."""
        return await self._async_start_websocket()
    
    async def _async_start_websocket(self):
        """Versão assíncrona interna do start_websocket"""
        global_value.websocket_is_connected = False
        global_value.check_websocket_if_error = False
        global_value.websocket_error_reason = None

        try:
            await self.websocket.connect()
            
            timeout = 10
            start_time = time.time()
            
            while not global_value.websocket_is_connected and (time.time() - start_time) < timeout:
                if global_value.check_websocket_if_error:
                    return False, global_value.websocket_error_reason
                await asyncio.sleep(0.1)
            
            if global_value.websocket_is_connected:
                return True, None
            else:
                return False, "Timeout na conexão websocket"
                
        except Exception as e:
            return False, f"Erro na conexão: {e}"

    async def connect(self):
        """Conexão assíncrona com a API."""
        return await self.async_connect()

    async def close(self, error=None):
        try:
            if self.websocket and hasattr(self.websocket, 'websocket') and self.websocket.websocket:
                await self.websocket.websocket.close()
                logger.debug("🔌 WebSocket fechado pelo método close")
            if self.websocket_thread and self.websocket_thread.is_alive():
                self.websocket_thread.join(timeout=5.0)
                logger.debug("🧵 Thread WebSocket finalizada")
        except Exception as e:
            logger.warning(f"⚠️ Aviso ao fechar no método close: {e}")

    def websocket_alive(self):
        return self.websocket_thread.is_alive()

    @property
    def get_balances(self):
        """Propriedade para obter o recurso http getprofile da Pocket Option.

        :returns: A instância de :class:`Login
            <pocketoptionapi.http.getprofile.Getprofile>`.
        """
        return Get_Balances(self)

    @property
    def buyv3(self):
        return Buyv3(self)

    async def async_buyv3(self, amount, active, action, expirations, req_id):
        """Versão assíncrona do buyv3"""
        buyv3_instance = Buyv3(self)
        await buyv3_instance.async_call(amount, active, action, expirations, req_id)

    @property
    def getcandles(self):
        """Propriedade para obter o canal websocket de velas da Pocket Option.

        :returns: A instância de :class:`GetCandles
            <pocketoptionapi.ws.channels.candles.GetCandles>`.
        """
        return GetCandles(self)

    async def async_getcandles(self, active_id, interval, count, end_time):
        """Versão assíncrona do getcandles"""
        candles_instance = GetCandles(self)
        await candles_instance.async_call(active_id, interval, count, end_time)

    @property
    def change_symbol(self):
        """Propriedade para obter o canal websocket change_symbol da Pocket Option.

        :returns: A instância de :class:`ChangeSymbol
            <pocketoptionapi.ws.channels.change_symbol.ChangeSymbol>`.
        """
        return ChangeSymbol(self)

    @property
    def synced_datetime(self):
        try:
            if self.time_sync is not None:
                self.sync.synchronize(self.time_sync.server_timestamp)
                self.sync_datetime = self.sync.get_synced_datetime()
            else:
                logging.error("timesync não está definido")
                self.sync_datetime = None
        except Exception as e:
            logging.error(e)
            self.sync_datetime = None

        return self.sync_datetime

    async def async_connect(self):
        """Método assíncrono para conexão com a API da Pocket Option."""
        global_value.ssl_Mutual_exclusion = False
        global_value.ssl_Mutual_exclusion_write = False

        # Inicializa conexão WebSocket de forma assíncrona
        global_value.websocket_is_connected = False
        global_value.check_websocket_if_error = False
        global_value.websocket_error_reason = None

        # Conecta WebSocket
        try:
            await self.websocket.connect()
            
            timeout = 10  # 10 segundos timeout
            start_time = time.time()
            
            while not global_value.websocket_is_connected and (time.time() - start_time) < timeout:
                if global_value.check_websocket_if_error:
                    raise Exception(global_value.websocket_error_reason)
                await asyncio.sleep(0.1)
            
            if not global_value.websocket_is_connected:
                raise Exception("Timeout na conexão WebSocket")
                
            self.time_sync.server_timestamps = None
            timeout = 5
            start_time = time.time()
            
            while self.time_sync.server_timestamps is None and (time.time() - start_time) < timeout:
                await asyncio.sleep(0.1)
                
            return True, None
            
        except Exception as e:
            return False, str(e)

    async def async_close(self):
        """Método assíncrono para fechar conexão."""
        try:
            if hasattr(self.websocket, 'websocket') and self.websocket.websocket:
                await self.websocket.websocket.close()
            global_value.websocket_is_connected = False
            logger.debug("🔌 Conexão WebSocket fechada pelo async_close")
        except Exception as e:
            logger.warning(f"⚠️ Aviso ao fechar conexão: {e}")
