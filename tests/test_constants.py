"""
Testes unitários para constantes e utilitários
Autor: AdminhuDev
"""

import unittest
import sys
import os

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from pocketoptionapi.constants import (
    ACTIVES,
    REGION,
    TIMEFRAMES,
    CONNECTION_SETTINGS,
    API_LIMITS
)


class TestConstants(unittest.TestCase):
    """
    Testes para constantes da API
    """

    def test_actives_structure(self):
        """Teste da estrutura de ativos"""
        self.assertIsInstance(ACTIVES, dict)
        self.assertGreater(len(ACTIVES), 0)

        # Verificar alguns ativos conhecidos
        self.assertIn("EURUSD_otc", ACTIVES)
        self.assertIn("BTCUSD_otc", ACTIVES)
        self.assertIn("#AAPL_otc", ACTIVES)

        # Verificar que valores são inteiros
        for active, value in ACTIVES.items():
            self.assertIsInstance(value, int)
            self.assertGreater(value, 0)

    def test_actives_otc_format(self):
        """Teste de ativos no formato OTC"""
        otc_actives = [active for active in ACTIVES.keys() if "_otc" in active]
        self.assertGreater(len(otc_actives), 0)

        # Verificar que ativos OTC têm valores diferentes dos normais
        if "EURUSD" in ACTIVES and "EURUSD_otc" in ACTIVES:
            self.assertNotEqual(ACTIVES["EURUSD"], ACTIVES["EURUSD_otc"])

    def test_actives_categories(self):
        """Teste de categorias de ativos"""
        # Commodity
        commodity_actives = [a for a in ACTIVES.keys() if any(x in a.upper() for x in ["OIL", "GOLD", "SILVER"])]
        self.assertGreater(len(commodity_actives), 0)

        # Crypto
        crypto_actives = [a for a in ACTIVES.keys() if any(x in a.upper() for x in ["BTC", "ETH", "ADA"])]
        self.assertGreater(len(crypto_actives), 0)

        # Currency
        currency_actives = [a for a in ACTIVES.keys() if any(x in a.upper() for x in ["EUR", "USD", "GBP"]) and "#" not in a]
        self.assertGreater(len(currency_actives), 0)

        # Stock
        stock_actives = [a for a in ACTIVES.keys() if "#" in a]
        self.assertGreater(len(stock_actives), 0)

    def test_region_class(self):
        """Teste da classe REGION"""
        self.assertTrue(hasattr(REGION, 'get_all'))
        self.assertTrue(hasattr(REGION, 'get_regions'))
        self.assertTrue(hasattr(REGION, 'get_demo_regions'))
        self.assertTrue(hasattr(REGION, 'get_priority_regions'))

    def test_region_get_all(self):
        """Teste de obtenção de todas as regiões"""
        regions = REGION.get_all()
        self.assertIsInstance(regions, list)
        self.assertGreater(len(regions), 0)

        # Verificar que são URLs válidas
        for region in regions:
            self.assertTrue(region.startswith('wss://'))
            self.assertIn('.po.market', region)

    def test_region_get_all_no_randomize(self):
        """Teste de obtenção de regiões sem randomização"""
        regions = REGION.get_all(randomize=False)
        self.assertIsInstance(regions, list)
        self.assertGreater(len(regions), 0)

    def test_region_get_regions(self):
        """Teste de obtenção de região específica"""
        # Teste região conhecida
        europa = REGION.get_regions("EUROPA")
        self.assertIsNotNone(europa)
        self.assertTrue(europa.startswith('wss://'))
        self.assertIn('eu.po.market', europa)

        # Teste região inexistente
        nonexistent = REGION.get_regions("NONEXISTENT")
        self.assertIsNone(nonexistent)

        # Teste case insensitive
        europa_upper = REGION.get_regions("EUROPA")
        europa_lower = REGION.get_regions("europa")
        self.assertEqual(europa_upper, europa_lower)

    def test_region_get_demo_regions(self):
        """Teste de obtenção de regiões demo"""
        demo_regions = REGION.get_demo_regions()
        self.assertIsInstance(demo_regions, list)
        self.assertGreater(len(demo_regions), 0)

        # Verificar que são regiões demo
        for region in demo_regions:
            self.assertTrue(region.startswith('wss://'))
            self.assertTrue(
                'demo' in region or
                'try-demo' in region or
                any(x in region for x in ['demo-eu', 'try-demo-eu'])
            )

    def test_region_get_priority_regions(self):
        """Teste de obtenção de regiões prioritárias"""
        priority_regions = REGION.get_priority_regions()
        self.assertIsInstance(priority_regions, list)
        self.assertGreater(len(priority_regions), 0)

        # EUROPA deve ser a primeira
        europa = REGION.get_regions("EUROPA")
        self.assertEqual(priority_regions[0], europa)

    def test_region_get_all_regions_dict(self):
        """Teste de obtenção de todas as regiões como dicionário"""
        regions_dict = REGION.get_all_regions()
        self.assertIsInstance(regions_dict, dict)
        self.assertGreater(len(regions_dict), 0)

        # Verificar estrutura
        for name, url in regions_dict.items():
            self.assertIsInstance(name, str)
            self.assertIsInstance(url, str)
            self.assertTrue(url.startswith('wss://'))

    def test_timeframes(self):
        """Teste de timeframes disponíveis"""
        self.assertIsInstance(TIMEFRAMES, dict)
        self.assertGreater(len(TIMEFRAMES), 0)

        # Verificar timeframes conhecidos
        self.assertIn("1m", TIMEFRAMES)
        self.assertIn("5m", TIMEFRAMES)
        self.assertIn("1h", TIMEFRAMES)
        self.assertIn("1d", TIMEFRAMES)

        # Verificar que valores são inteiros (segundos)
        for timeframe, seconds in TIMEFRAMES.items():
            self.assertIsInstance(seconds, int)
            self.assertGreater(seconds, 0)

        # Verificar ordem crescente
        values = list(TIMEFRAMES.values())
        self.assertEqual(values, sorted(values))

    def test_connection_settings(self):
        """Teste de configurações de conexão"""
        self.assertIsInstance(CONNECTION_SETTINGS, dict)
        self.assertGreater(len(CONNECTION_SETTINGS), 0)

        # Verificar campos obrigatórios
        required_fields = ["ping_interval", "ping_timeout", "close_timeout",
                          "max_reconnect_attempts", "reconnect_delay", "message_timeout"]
        for field in required_fields:
            self.assertIn(field, CONNECTION_SETTINGS)

        # Verificar tipos
        self.assertIsInstance(CONNECTION_SETTINGS["ping_interval"], int)
        self.assertIsInstance(CONNECTION_SETTINGS["ping_timeout"], int)
        self.assertIsInstance(CONNECTION_SETTINGS["max_reconnect_attempts"], int)

    def test_api_limits(self):
        """Teste de limites da API"""
        self.assertIsInstance(API_LIMITS, dict)
        self.assertGreater(len(API_LIMITS), 0)

        # Verificar campos obrigatórios
        required_fields = ["min_order_amount", "max_order_amount", "min_duration",
                          "max_duration", "max_concurrent_orders", "rate_limit"]
        for field in required_fields:
            self.assertIn(field, API_LIMITS)

        # Verificar limites lógicos
        self.assertLess(API_LIMITS["min_order_amount"], API_LIMITS["max_order_amount"])
        self.assertLess(API_LIMITS["min_duration"], API_LIMITS["max_duration"])
        self.assertGreater(API_LIMITS["rate_limit"], 0)

    def test_active_values_uniqueness(self):
        """Teste de unicidade dos valores de ativos"""
        values = list(ACTIVES.values())
        unique_values = set(values)

        # Deve haver pelo menos alguns ativos com valores únicos
        self.assertGreater(len(unique_values), len(values) // 2)

    def test_active_names_format(self):
        """Teste do formato dos nomes de ativos"""
        for active_name in ACTIVES.keys():
            # Não deve conter espaços
            self.assertNotIn(" ", active_name)

            # Deve conter apenas caracteres válidos
            import re
            self.assertTrue(re.match(r'^[A-Za-z0-9_#]+$', active_name))


class TestConstantsIntegration(unittest.TestCase):
    """
    Testes de integração para constantes
    """

    def test_region_connectivity(self):
        """Teste básico de conectividade das regiões"""
        # Este teste verifica se as URLs das regiões estão bem formadas
        regions = REGION.get_all()

        for region_url in regions:
            # Verificar formato da URL
            self.assertTrue(region_url.startswith('wss://'))
            self.assertTrue(region_url.endswith('.po.market/socket.io/?EIO=4&transport=websocket'))

            # Verificar que contém domínio válido
            self.assertTrue(any(domain in region_url for domain in [
                'api-eu.po.market',
                'api-sc.po.market',
                'api-hk.po.market',
                'demo-api-eu.po.market',
                'try-demo-eu.po.market'
            ]))

    def test_timeframes_conversion(self):
        """Teste de conversão de timeframes"""
        # Verificar conversão de minutos para segundos
        self.assertEqual(TIMEFRAMES["1m"], 60)
        self.assertEqual(TIMEFRAMES["5m"], 300)
        self.assertEqual(TIMEFRAMES["15m"], 900)
        self.assertEqual(TIMEFRAMES["1h"], 3600)
        self.assertEqual(TIMEFRAMES["1d"], 86400)

    def test_api_limits_reasonable(self):
        """Teste se os limites da API são razoáveis"""
        # Valores mínimos devem ser positivos
        self.assertGreater(API_LIMITS["min_order_amount"], 0)
        self.assertGreater(API_LIMITS["min_duration"], 0)

        # Máximos devem ser maiores que mínimos
        self.assertGreater(API_LIMITS["max_order_amount"], API_LIMITS["min_order_amount"])
        self.assertGreater(API_LIMITS["max_duration"], API_LIMITS["min_duration"])

        # Rate limit deve ser razoável
        self.assertGreater(API_LIMITS["rate_limit"], 10)
        self.assertLess(API_LIMITS["rate_limit"], 10000)


if __name__ == '__main__':
    # Executar testes
    unittest.main(verbosity=2)
