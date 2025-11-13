"""
Autor: AdminhuDev
Async-safe global state management
"""
import asyncio
from threading import Lock

# Estado de conexão
websocket_is_connected = False

# Mutex async-safe para controle de concorrência
_connection_lock = asyncio.Lock()
_write_lock = asyncio.Lock()

# Legacy - mantido para compatibilidade
ssl_Mutual_exclusion = False
ssl_Mutual_exclusion_write = False

SSID = None

check_websocket_if_error = False
websocket_error_reason = None

balance_id = None
balance = None
balance_type = None
balance_updated = None
result = None

# Estado das ordens com locks para thread-safety
_order_lock = Lock()
order_data = {}
order_open = []
order_closed = []
stat = []
DEMO = None

# Para obter os dados de pagamento para os diferentes pares
PayoutData = None
ParsedAssets = {}  # Dados de ativos processados pelo parser

# Funções helper async-safe
async def get_connection_lock():
    """Retorna o lock de conexão assíncrono"""
    return _connection_lock

async def get_write_lock():
    """Retorna o lock de escrita assíncrono"""
    return _write_lock

def get_order_lock():
    """Retorna o lock de ordens síncrono"""
    return _order_lock