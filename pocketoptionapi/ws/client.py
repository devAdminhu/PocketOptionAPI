import asyncio
from datetime import datetime, timedelta, timezone
import os

import websockets
import json
import logging
import ssl
from loguru import logger

# Importando os módulos necessários
import pocketoptionapi.constants as OP_code
import pocketoptionapi.global_value as global_value
from pocketoptionapi.constants import REGION
from pocketoptionapi.ws.objects.timesync import TimeSync
from pocketoptionapi.ws.objects.time_sync import TimeSynchronizer
from pocketoptionapi.assets_parser import assets_parser

timesync = TimeSync()
sync = TimeSynchronizer()


async def on_open():
    """Método para processar a abertura do websocket."""
    logger.debug("Cliente websocket conectado (CONEXÃO BEM SUCEDIDA)")
    global_value.websocket_is_connected = True


async def send_ping(ws):
    while global_value.websocket_is_connected is False:
        await asyncio.sleep(0.1)
    
    while global_value.websocket_is_connected:
        try:
            await asyncio.sleep(20)
            if global_value.websocket_is_connected:
                ping_msg = '42["ps"]'
                await ws.send(ping_msg)
                # logger.debug("🏓 Ping enviado")
        except Exception as e:
            logger.warning(f"⚠️ Erro ao enviar ping: {e}")
            break


async def process_message(message):
    try:
        data = json.loads(message)
        print(f"Mensagem recebida: {data}")

        # Processa a mensagem dependendo do tipo
        if isinstance(data, dict) and 'uid' in data:
            uid = data['uid']
            print(f"UID: {uid}")
        elif isinstance(data, list) and len(data) > 0:
            event_type = data[0]
            event_data = data[1]
            print(f"Tipo do evento: {event_type}, Dados do evento: {event_data}")
            # Aqui você pode adicionar mais lógica para lidar com diferentes tipos de eventos

    except json.JSONDecodeError as e:
        print(f"Erro ao decodificar JSON: {e}")
    except KeyError as e:
        print(f"Erro de chave: {e}")
    except Exception as e:
        print(f"Erro ao processar mensagem: {e}")


class WebsocketClient(object):
    def __init__(self, api) -> None:
        """
        Inicializa o cliente WebSocket.

        :param api: Instância da classe PocketOptionApi
        """
        self.updateHistoryNew = None
        self.updateStream = None
        self.history_data_ready = None
        self.successCloseOrder = False
        self.api = api
        self.message = None
        self.url = None
        self.ssid = global_value.SSID
        self.websocket = None
        self.region = REGION()
        self.loop = asyncio.get_event_loop()
        self.wait_second_message = False
        self._updateClosedDeals = False

    async def websocket_listener(self, ws):
        logger.info("🎧 WebSocket listener iniciado")
        try:
            async for message in ws:
                try:
                    await self.on_message(message)
                except Exception as msg_error:
                    logger.error(f"❌ Erro ao processar mensagem: {msg_error}")
                    logger.debug(f"🔍 Tipo da mensagem: {type(message)}")
                    logger.debug(f"🔍 Primeiros 100 chars: {str(message)[:100]}")
        except websockets.exceptions.ConnectionClosed as e:
            if e.code == 1005:
                logger.warning("🔌 Conexão fechada pelo servidor (código 1005) - reconectando...")
                global_value.websocket_is_connected = False
            else:
                logger.warning(f"🔌 Conexão WebSocket fechada: {e}")
        except Exception as e:
            logger.error(f"❌ Erro no WebSocket listener: {e}")
            logger.debug(f"🔍 Detalhes do erro: {str(e)}")
            global_value.websocket_is_connected = False

    async def connect(self):
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

        try:
            await self.api.close()
        except:
            pass

        logger.info("🔗 Iniciando conexão WebSocket...")

        # 🌐 Verificar se há servidor preferencial no .env
        preferred_server = os.getenv('PREFERRED_SERVER', '').strip().upper()

        # Escolher regiões baseado no modo demo com prioridade
        if global_value.DEMO:
            urls = self.region.get_demo_regions()
            logger.info("🎮 Modo DEMO - testando servidores demo prioritários (DEMO, DEMO_2)")
        elif preferred_server:
            # Usar servidor preferencial do .env
            preferred_url = self.region.get_regions(preferred_server)
            if preferred_url:
                urls = [preferred_url] + [url for url in self.region.get_priority_regions() if url != preferred_url]
                logger.info(f"🎯 Servidor preferencial: {preferred_server} (fallback automático se falhar)")
            else:
                logger.warning(f"⚠️ Servidor '{preferred_server}' inválido - usando auto-seleção")
                urls = self.region.get_priority_regions()
                logger.info("💰 Modo REAL - testando EUROPA primeiro, depois outros servidores prioritários")
        else:
            urls = self.region.get_priority_regions()
            logger.info("💰 Modo REAL - testando EUROPA primeiro, depois outros servidores prioritários")
        
        retry_count = 0
        max_retries = 2  # 🔄 Retry cada servidor até 2x antes de próximo
        use_proxy_fallback = False  # Começa SEM proxy

        proxy_enabled = os.getenv('PROXY_ENABLED', 'false').lower() == 'true'
        proxy_url = os.getenv('PROXY_URL', '').strip()

        while not global_value.websocket_is_connected:
            for url in urls:
                for attempt in range(max_retries):
                    if attempt > 0:
                        backoff = min(2 ** attempt, 5)  # Backoff exponencial (máx 5s)
                        logger.debug(f"⏳ Aguardando {backoff}s antes do retry {attempt + 1}/{max_retries}...")
                        await asyncio.sleep(backoff)

                    logger.debug(f"🌐 Tentando conectar em: {url} (tentativa {attempt + 1}/{max_retries})")

                    connect_kwargs = {
                        "ssl": ssl_context,
                        "open_timeout": 30,
                        "close_timeout": 10,
                        "ping_interval": 20,
                        "ping_timeout": 10,
                        "extra_headers": {
                            "Origin": "https://pocketoption.com",
                            "Cache-Control": "no-cache",
                            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
                        }
                    }

                    # 🔐 Usar proxy APENAS se fallback estiver ativo
                    if use_proxy_fallback and proxy_enabled and proxy_url:
                        try:
                            from python_socks.async_.asyncio import Proxy
                            proxy = Proxy.from_url(proxy_url)
                            connect_kwargs["sock"] = await proxy.connect(
                                dest_host=url.split("//")[1].split("/")[0].split(":")[0],
                                dest_port=443,
                                timeout=30
                            )
                            logger.info(f"🔐 Usando proxy fallback: {proxy_url.split('@')[-1]}")
                        except ImportError:
                            logger.warning("⚠️ python-socks não instalado - ignorando proxy")
                        except Exception as e:
                            logger.warning(f"⚠️ Erro ao configurar proxy: {e}")

                    try:
                        async with websockets.connect(url, **connect_kwargs) as ws:
                            self.websocket = ws
                            self.url = url
                            global_value.websocket_is_connected = True
                            logger.success(f"✅ WebSocket conectado em: {url}")

                            logger.info("🚀 Iniciando tarefas WebSocket (listener, sender, ping)")
                            on_message_task = asyncio.create_task(self.websocket_listener(ws))
                            sender_task = asyncio.create_task(self.send_message(self.message))
                            ping_task = asyncio.create_task(send_ping(ws))

                            await asyncio.gather(on_message_task, sender_task, ping_task)

                    except websockets.ConnectionClosed as e:
                        global_value.websocket_is_connected = False
                        await self.on_close(e)
                        if attempt < max_retries - 1:
                            logger.debug(f"🔄 Retry servidor {url}...")
                        else:
                            logger.warning(f"⚠️ Servidor {url} rejeitou conexão - tentando próximo")
                        continue  # Próximo retry

                    except Exception as e:
                        global_value.websocket_is_connected = False
                        await self.on_error(e)
                        if attempt < max_retries - 1:
                            logger.debug(f"🔄 Retry servidor {url}...")
                        else:
                            logger.warning(f"⚠️ Erro no servidor {url}: {str(e)[:50]}... - tentando próximo")
                        continue  # Próximo retry

                    # Se chegou aqui, conectou com sucesso
                    break

            retry_count += 1

            # 🔐 Ativar proxy fallback após primeira rodada falhar
            if retry_count == 1 and not use_proxy_fallback and proxy_enabled and proxy_url:
                logger.warning("⚠️ Conexão direta falhou em todos servidores")
                logger.info("🔐 Ativando PROXY FALLBACK para próxima tentativa...")
                use_proxy_fallback = True
                continue  # Tenta novamente com proxy

            if retry_count > 1:
                logger.error("❌ Falha em todos servidores após múltiplas tentativas (direto + proxy)")
                break
            await asyncio.sleep(1)  # Esperar antes de tentar reconectar

        return True

    async def send_message(self, message):
        while global_value.websocket_is_connected is False:
            await asyncio.sleep(0.1)

        self.message = message

        if global_value.websocket_is_connected and message is not None:
            try:
                await self.websocket.send(message)
            except Exception as e:
                logger.warning(f"Erro ao enviar mensagem: {e}")
        elif message is not None:
            logger.warning("WebSocket não está conectado")

    @staticmethod
    def dict_queue_add(self, dict, maxdict, key1, key2, key3, value):
        if key3 in dict[key1][key2]:
            dict[key1][key2][key3] = value
        else:
            while True:
                try:
                    dic_size = len(dict[key1][key2])
                except:
                    dic_size = 0
                if dic_size < maxdict:
                    dict[key1][key2][key3] = value
                    break
                else:
                    # Remover a menor chave
                    del dict[key1][key2][sorted(dict[key1][key2].keys(), reverse=False)[0]]

    async def on_message(self, message):
        """Método para processar mensagens do websocket."""
        
        # Primeiro converter bytes para string se necessário
        if type(message) is bytes:
            message2 = message.decode('utf-8')
            message_str = message.decode('utf-8')
        else:
            message2 = message
            message_str = message
        
        # # Log apenas para mensagens importantes, evitando spam
        # if '[[5,"#AAPL","Apple","stock' in message_str:
        #     logger.debug("📨 Mensagem de ativos detectada")
        # elif "NotAuthorized" in message_str:
        #     logger.debug("📨 Mensagem de autorização detectada")
        # elif "sid" in message_str:
        #     logger.debug("📨 Mensagem de sessão detectada")
        # else:
        #     logger.trace(f"📨 Mensagem: {message_str[:50]}..." if len(message_str) > 50 else f"📨 Mensagem: {message_str}")

        # Tentar fazer parse JSON da string
        if type(message) is bytes:
            message = message_str
            try:
                message = json.loads(message)
            except (json.JSONDecodeError, ValueError):
                # Se não for JSON válido, manter como string
                pass

            if isinstance(message, dict) and "balance" in message:
                if "uid" in message:
                    global_value.balance_id = message["uid"]
                global_value.balance = message["balance"]
                global_value.balance_type = message["isDemo"]
                logger.info(f"💰 Saldo atualizado: ${message['balance']}")

            elif isinstance(message, dict) and "requestId" in message and message["requestId"] == 'buy':
                global_value.order_data = message
                logger.info("📈 Dados de ordem atualizados")

            elif self.wait_second_message and isinstance(message, list):
                self.wait_second_message = False  # Resetar para futuras mensagens
                self._updateClosedDeals = False  # Resetar o estado

            elif isinstance(message, dict) and self.successCloseOrder:
                self.api.order_async = message
                self.successCloseOrder = False  # Resetar para futuras mensagens

            elif self.history_data_ready and isinstance(message, dict):
                self.history_data_ready = False
                self.api.history_data = message["data"]

            elif self.updateStream and isinstance(message, list):
                self.updateStream = False
                self.api.time_sync.server_timestamp = message[0][1]

            elif self.updateHistoryNew and isinstance(message, dict):
                self.updateHistoryNew = False
                self.api.historyNew = message
            elif '[[5,"#AAPL","Apple","stock' in message2:
                # logger.debug("📊 Dados de ativos recebidos via WebSocket")
                # logger.debug(f"🔍 Dados completos (primeiros 500 chars): {message2[:500]}...")
                # logger.debug(f"🔍 Tamanho total da mensagem: {len(message2)} chars")
                try:
                    # Processar dados usando o novo parser
                    parsed_assets = assets_parser.parse_assets_data(message2)
                    
                    if parsed_assets:
                        # logger.debug(f"✅ {len(parsed_assets)} ativos processados")
                        
                        # Armazenar dados processados no global_value
                        global_value.PayoutData = message2  # Raw data para compatibilidade
                        global_value.ParsedAssets = parsed_assets  # Dados processados
                        
                        # logger.debug("💾 Dados processados armazenados em global_value")
                    else:
                        logger.warning("⚠️ Nenhum ativo válido encontrado nos dados")
                        # logger.debug(f"🔍 Dados que falharam no parse: {message2}")
                        global_value.PayoutData = message2
                    
                except Exception as e:
                    logger.error(f"❌ Erro ao processar dados de ativos: {e}")
                    # logger.debug(f"🔍 Dados que causaram erro: {message2[:200]}...")
                    global_value.PayoutData = message2
            return

        else:
            pass

        if message.startswith('0') and "sid" in message:
            await self.websocket.send("40")

        elif message == "2":
            await self.websocket.send("3")

        elif "40" and "sid" in message:
            logger.info(f"🔑 Enviando SSID para autenticação...")
            logger.debug(f"🔍 SSID enviado (primeiros 200 chars): {self.ssid[:200]}...")
            logger.debug(f"🔍 SSID enviado (últimos 50 chars): ...{self.ssid[-50:]}")
            await self.websocket.send(self.ssid)

        elif message.startswith('451-['):
            json_part = message.split("-", 1)[1]  # Remover o prefixo numérico e o hífen para obter o JSON válido

            # Converter a parte JSON para um objeto Python
            message = json.loads(json_part)
            
            # Filtrar mensagens repetitivas de updateStream para reduzir spam no log
            if not (len(message) >= 2 and message[0] == "updateStream" and 
                   isinstance(message[1], dict) and message[1].get("_placeholder")):
                # logger.debug(f"🔍 Mensagem 451 processada: {message}")
                pass

            if message[0] == "successauth":
                logger.debug("🎉 AUTENTICAÇÃO BEM SUCEDIDA!")
                await on_open()

            elif message[0] == "successupdateBalance":
                global_value.balance_updated = True
                logger.debug("💰 Balance update success")
            elif message[0] == "successopenOrder":
                global_value.result = True
                logger.debug("📈 Open order success")

            elif message[0] == "updateClosedDeals":
                # Estabelecemos que recebemos a primeira mensagem de interesse
                self._updateClosedDeals = True
                self.wait_second_message = True  # Estabelecemos que esperamos a segunda mensagem de interesse
                await self.websocket.send('42["changeSymbol",{"asset":"AUDNZD_otc","period":60}]')

            elif message[0] == "successcloseOrder":
                self.successCloseOrder = True
                self.wait_second_message = True  # Estabelecemos que esperamos a segunda mensagem de interesse

            elif message[0] == "loadHistoryPeriod":
                self.history_data_ready = True

            elif message[0] == "updateStream":
                self.updateStream = True

            elif message[0] == "updateHistoryNew":
                self.updateHistoryNew = True
                # self.api.historyNew = None

        elif message.startswith("42") and "NotAuthorized" in message:
            logger.error("❌ User not Authorized: SSID inválido ou expirado")
            logger.error("💡 Dica: Obtenha um novo SSID usando tools/get_ssid.py")
            logger.error(f"🔍 SSID enviado: {self.ssid[:100]}...")
            logger.error(f"🔍 Mensagem completa: {message}")
            global_value.websocket_is_connected = False
            global_value.check_websocket_if_error = True
            global_value.websocket_error_reason = "SSID inválido ou expirado"
            global_value.ssl_Mutual_exclusion = False
            await self.websocket.close()

    async def on_error(self, error):  # pylint: disable=unused-argument
        logger.error(error)
        global_value.websocket_error_reason = str(error)
        global_value.check_websocket_if_error = True

    async def on_close(self, error):  # pylint: disable=unused-argument
        # logger.debug("Websocket connection closed.")
        # logger.warning(f"Websocket connection closed. Reason: {error}")
        global_value.websocket_is_connected = False
