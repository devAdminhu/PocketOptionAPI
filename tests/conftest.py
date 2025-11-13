"""
Configuração do pytest para testes da PocketOption API
Autor: AdminhuDev
"""

import pytest
import asyncio
import sys
import os
import logging

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


@pytest.fixture(scope="session")
def event_loop():
    """Criar um event loop para testes assíncronos"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def sample_ssid():
    """Fixture com SSID de exemplo para testes"""
    return '42["auth",{"session":"test_session_123","isDemo":1,"uid":123456,"platform":2}]'


@pytest.fixture
def invalid_ssid():
    """Fixture com SSID inválido para testes"""
    return "invalid_ssid_format"


@pytest.fixture
def demo_mode():
    """Fixture com modo demo"""
    return True


@pytest.fixture
def real_mode():
    """Fixture com modo real"""
    return False


@pytest.fixture(autouse=True)
def setup_logging():
    """Configurar logging para testes"""
    logging.basicConfig(
        level=logging.ERROR,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


@pytest.fixture(autouse=True)
def cleanup_global_state():
    """Limpar estado global entre testes"""
    import pocketoptionapi.global_value as global_value

    # Salvar estado original
    original_values = {
        'SSID': global_value.SSID,
        'DEMO': global_value.DEMO,
        'websocket_is_connected': global_value.websocket_is_connected,
        'balance': global_value.balance,
        'balance_updated': global_value.balance_updated
    }

    yield

    # Restaurar estado original
    global_value.SSID = original_values['SSID']
    global_value.DEMO = original_values['DEMO']
    global_value.websocket_is_connected = original_values['websocket_is_connected']
    global_value.balance = original_values['balance']
    global_value.balance_updated = original_values['balance_updated']


def pytest_configure(config):
    """Configuração global do pytest"""
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )


def pytest_collection_modifyitems(config, items):
    """Modificar itens de teste coletados"""
    for item in items:
        # Adicionar marker unit por padrão
        if "integration" not in item.keywords:
            item.add_marker(pytest.mark.unit)

        # Adicionar marker slow para testes de integração
        if "integration" in item.keywords:
            item.add_marker(pytest.mark.slow)
