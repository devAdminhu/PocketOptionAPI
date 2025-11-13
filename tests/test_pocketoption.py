"""
Testes unitários para PocketOption API
Autor: AdminhuDev
"""

import asyncio
import unittest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
import logging

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from pocketoptionapi.stable_api import PocketOption
from pocketoptionapi.ssid_parser import process_ssid_input
import pocketoptionapi.global_value as global_value

# Configuração de logging para testes
logging.basicConfig(level=logging.ERROR)

class TestPocketOption(unittest.TestCase):
    """
    Testes para a classe PocketOption
    """

    def setUp(self):
        """Configuração inicial para cada teste"""
        # SSID de teste válido
        self.valid_ssid = '42["auth",{"session":"test_session_123","isDemo":1,"uid":123456,"platform":2}]'
        self.demo_mode = True

        # Resetar variáveis globais
        global_value.SSID = None
        global_value.DEMO = None
        global_value.websocket_is_connected = False

    def tearDown(self):
        """Limpeza após cada teste"""
        # Resetar variáveis globais
        global_value.SSID = None
        global_value.DEMO = None
        global_value.websocket_is_connected = False

    def test_init_valid_ssid(self):
        """Teste de inicialização com SSID válido"""
        api = PocketOption(self.valid_ssid, self.demo_mode)

        self.assertIsNotNone(api)
        self.assertEqual(api.demo, self.demo_mode)
        self.assertIsNotNone(api.api)
        self.assertEqual(global_value.SSID, self.valid_ssid)
        self.assertEqual(global_value.DEMO, self.demo_mode)

    def test_init_invalid_ssid(self):
        """Teste de inicialização com SSID inválido"""
        invalid_ssid = "invalid_ssid_format"

        with self.assertRaises(ValueError) as context:
            PocketOption(invalid_ssid, self.demo_mode)

        self.assertIn("SSID inválido", str(context.exception))

    @patch('pocketoptionapi.stable_api.global_value.websocket_is_connected', True)
    async def test_check_connect_connected(self):
        """Teste de verificação de conexão quando conectado"""
        result = await PocketOption.check_connect()
        self.assertTrue(result)

    @patch('pocketoptionapi.stable_api.global_value.websocket_is_connected', False)
    async def test_check_connect_not_connected(self):
        """Teste de verificação de conexão quando desconectado"""
        result = await PocketOption.check_connect()
        self.assertFalse(result)

    @patch('pocketoptionapi.stable_api.global_value.websocket_is_connected', None)
    async def test_check_connect_none(self):
        """Teste de verificação de conexão quando None"""
        result = await PocketOption.check_connect()
        self.assertFalse(result)

    @patch('pocketoptionapi.stable_api.global_value.balance_updated', True)
    @patch('pocketoptionapi.stable_api.global_value.balance', 100.50)
    async def test_get_balance_success(self):
        """Teste de obtenção de saldo com sucesso"""
        result = await PocketOption.get_balance()
        self.assertEqual(result, 100.50)

    @patch('pocketoptionapi.stable_api.global_value.balance_updated', False)
    @patch('pocketoptionapi.stable_api.global_value.balance', None)
    async def test_get_balance_no_update(self):
        """Teste de obtenção de saldo sem atualização"""
        result = await PocketOption.get_balance()
        self.assertIsNone(result)

    @patch('pocketoptionapi.stable_api.global_value.order_open')
    async def test_check_open(self, mock_order_open):
        """Teste de verificação de ordens abertas"""
        mock_order_open.return_value = True
        result = await PocketOption.check_open()
        self.assertTrue(result)

        mock_order_open.return_value = False
        result = await PocketOption.check_open()
        self.assertFalse(result)

    def test_last_time_calculation(self):
        """Teste do cálculo de last_time"""
        # Teste com timestamp e período
        timestamp = 1640995200  # 2022-01-01 00:00:00 UTC
        period = 60  # 1 minuto

        result = PocketOption.last_time(timestamp, period)
        expected = 1640995200 - (1640995200 % 60)  # Arredondar para minuto

        self.assertEqual(result, expected)

    def test_process_data_history_empty(self):
        """Teste de processamento de dados históricos vazios"""
        result = PocketOption.process_data_history({"history": []}, 60)
        self.assertEqual(result, [])

    def test_process_data_history_valid(self):
        """Teste de processamento de dados históricos válidos"""
        data = {
            "history": [
                [1640995200, 1.0500],
                [1640995260, 1.0505],
                [1640995320, 1.0502]
            ]
        }

        result = PocketOption.process_data_history(data, 60)

        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)

        # Verificar estrutura do primeiro item
        first_candle = result[0]
        self.assertIn("time", first_candle)
        self.assertIn("open", first_candle)
        self.assertIn("high", first_candle)
        self.assertIn("low", first_candle)
        self.assertIn("close", first_candle)

    def test_process_candle_empty(self):
        """Teste de processamento de candles vazios"""
        result, diff_valid = PocketOption.process_candle([], 60)
        self.assertEqual(result, [])
        self.assertFalse(diff_valid)

    def test_process_candle_valid(self):
        """Teste de processamento de candles válidos"""
        candles = [
            {"time": 1640995200, "price": 1.0500},
            {"time": 1640995260, "price": 1.0505},
            {"time": 1640995320, "price": 1.0502}
        ]

        result, diff_valid = PocketOption.process_candle(candles, 60)

        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
        self.assertTrue(diff_valid)  # Deve ser válido pois diferenças são constantes

    def test_process_candle_with_duplicates(self):
        """Teste de processamento de candles com duplicatas"""
        candles = [
            {"time": 1640995200, "price": 1.0500},
            {"time": 1640995200, "price": 1.0505},  # Duplicata
            {"time": 1640995260, "price": 1.0502}
        ]

        result, diff_valid = PocketOption.process_candle(candles, 60)

        # Deve manter apenas uma entrada por timestamp
        unique_times = set(candle["time"] for candle in result)
        self.assertEqual(len(unique_times), 2)


class TestPocketOptionIntegration(unittest.TestCase):
    """
    Testes de integração (requerem configuração real)
    Estes testes são desabilitados por padrão
    """

    @unittest.skip("Requer SSID real para teste")
    def test_real_connection(self):
        """Teste com conexão real (desabilitado)"""
        # Este teste seria usado com um SSID real para testes de integração
        pass

    @unittest.skip("Requer SSID real para teste")
    async def test_real_operations(self):
        """Teste com operações reais (desabilitado)"""
        # Este teste seria usado para testar operações reais
        pass


if __name__ == '__main__':
    # Executar testes
    unittest.main(verbosity=2)
