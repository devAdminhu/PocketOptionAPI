"""
Testes de integração da PocketOption API
Autor: AdminhuDev

⚠️  ATENÇÃO: Estes testes requerem configuração real da API
    Não execute sem configurar SSID_REAL no ambiente
"""

import pytest
import asyncio
import os
import sys
import logging

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from pocketoptionapi.stable_api import PocketOption
import pocketoptionapi.global_value as global_value

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@pytest.mark.integration
@pytest.mark.slow
class TestPocketOptionIntegration:
    """
    Testes de integração com a API real
    """

    SSID_REAL = os.getenv('POCKETOPTION_SSID')
    DEMO_MODE = os.getenv('POCKETOPTION_DEMO', 'true').lower() == 'true'

    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Configuração para cada teste"""
        if not self.SSID_REAL:
            pytest.skip("SSID_REAL não configurado. Configure a variável de ambiente POCKETOPTION_SSID")

        self.api = PocketOption(self.SSID_REAL, self.DEMO_MODE)

    @pytest.fixture(autouse=True)
    def teardown_method(self):
        """Limpeza após cada teste"""
        if hasattr(self, 'api'):
            try:
                asyncio.run(self.api.disconnect())
            except:
                pass

    @pytest.mark.asyncio
    async def test_real_connection(self):
        """Teste de conexão real com timeout"""
        logger.info("🧪 Testando conexão real...")

        connected = await asyncio.wait_for(
            self.api.connect(),
            timeout=30.0
        )

        assert connected, "Falha ao conectar com a API"
        assert global_value.websocket_is_connected, "WebSocket não está conectado"

        logger.info("✅ Conexão estabelecida com sucesso")

    @pytest.mark.asyncio
    async def test_get_balance_real(self):
        """Teste de obtenção de saldo real"""
        logger.info("🧪 Testando obtenção de saldo...")

        # Conectar primeiro
        await self.test_real_connection()

        # Aguardar atualização do saldo
        await asyncio.sleep(3)

        balance = await asyncio.wait_for(
            self.api.get_balance(),
            timeout=10.0
        )

        assert balance is not None, "Saldo não disponível"
        assert isinstance(balance, (int, float)), "Saldo deve ser numérico"
        assert balance >= 0, "Saldo deve ser não-negativo"

        logger.info(f"✅ Saldo obtido: ${balance:.2f}")

    @pytest.mark.asyncio
    async def test_get_payout_real(self):
        """Teste de obtenção de payout real"""
        logger.info("🧪 Testando obtenção de payout...")

        # Conectar primeiro
        await self.test_real_connection()

        # Aguardar dados de payout
        await asyncio.sleep(5)

        payout = await asyncio.wait_for(
            self.api.GetPayout("EURUSD_otc"),
            timeout=10.0
        )

        if payout is not None:
            assert isinstance(payout, (int, float)), "Payout deve ser numérico"
            assert payout > 0, "Payout deve ser positivo"
            assert payout <= 100, "Payout deve ser <= 100%"
            logger.info(f"✅ Payout obtido: {payout}%")
        else:
            logger.warning("⚠️ Payout não disponível")

    @pytest.mark.asyncio
    async def test_get_candles_real(self):
        """Teste de obtenção de candles reais"""
        logger.info("🧪 Testando obtenção de candles...")

        # Conectar primeiro
        await self.test_real_connection()

        candles = await asyncio.wait_for(
            self.api.get_candles("EURUSD_otc", 60, count=5),
            timeout=15.0
        )

        if candles:
            assert isinstance(candles, list), "Candles deve ser uma lista"
            assert len(candles) > 0, "Deve haver pelo menos um candle"

            # Verificar estrutura do primeiro candle
            first_candle = candles[0]
            required_fields = ["time", "open", "high", "low", "close"]
            for field in required_fields:
                assert field in first_candle, f"Campo '{field}' faltando no candle"

            logger.info(f"✅ {len(candles)} candles obtidos")
        else:
            logger.warning("⚠️ Nenhum candle obtido")

    @pytest.mark.asyncio
    async def test_buy_operation_real(self):
        """Teste de operação de compra real (CUIDADO!)"""
        logger.warning("🔥 TESTANDO OPERAÇÃO REAL - USE COM EXTREMO CUIDADO!")

        # Este teste só deve ser executado manualmente
        if not os.getenv('ALLOW_REAL_TRADES', '').lower() == 'true':
            pytest.skip("Operações reais desabilitadas. Configure ALLOW_REAL_TRADES=true para habilitar")

        # Conectar primeiro
        await self.test_real_connection()

        # Verificar saldo antes da operação
        balance_before = await self.api.get_balance()
        assert balance_before is not None, "Saldo inicial não disponível"
        assert balance_before >= 1.0, "Saldo insuficiente para teste"

        logger.info(f"💰 Saldo antes: ${balance_before:.2f}")

        # Executar operação pequena
        success, order_id = await asyncio.wait_for(
            self.api.buy(
                amount=1.0,  # Valor mínimo
                active="EURUSD_otc",
                action="call",
                expirations=60  # 1 minuto
            ),
            timeout=10.0
        )

        assert success, "Operação deve ser bem-sucedida"
        assert order_id is not None, "Order ID deve ser retornado"

        logger.info(f"✅ Operação realizada: ID {order_id}")

        # Aguardar resultado (tempo de expiração + buffer)
        await asyncio.sleep(70)

        profit, status = await asyncio.wait_for(
            self.api.check_win(order_id),
            timeout=10.0
        )

        assert profit is not None, "Profit deve ser obtido"
        assert status in ["ganhou", "perdeu"], f"Status inválido: {status}"

        logger.info(f"📊 Resultado: {status} - Profit: ${profit:.2f}")

        # Verificar saldo após operação
        balance_after = await self.api.get_balance()
        assert balance_after is not None, "Saldo final não disponível"

        logger.info(f"💰 Saldo depois: ${balance_after:.2f}")
        logger.info(f"📊 Diferença: ${balance_after - balance_before:.2f}")


@pytest.mark.integration
@pytest.mark.slow
class TestPocketOptionStress:
    """
    Testes de estresse da API
    """

    SSID_REAL = os.getenv('POCKETOPTION_SSID')
    DEMO_MODE = os.getenv('POCKETOPTION_DEMO', 'true').lower() == 'true'

    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Configuração para cada teste"""
        if not self.SSID_REAL:
            pytest.skip("SSID_REAL não configurado")

        self.api = PocketOption(self.SSID_REAL, self.DEMO_MODE)

    @pytest.fixture(autouse=True)
    def teardown_method(self):
        """Limpeza após cada teste"""
        if hasattr(self, 'api'):
            try:
                asyncio.run(self.api.disconnect())
            except:
                pass

    @pytest.mark.asyncio
    async def test_multiple_connections(self):
        """Teste de múltiplas conexões consecutivas"""
        logger.info("🧪 Testando múltiplas conexões...")

        for i in range(3):
            logger.info(f"🔄 Conexão {i+1}/3")

            connected = await asyncio.wait_for(
                self.api.connect(),
                timeout=15.0
            )
            assert connected, f"Falha na conexão {i+1}"

            # Aguardar um pouco
            await asyncio.sleep(2)

            # Desconectar
            await self.api.disconnect()
            assert not global_value.websocket_is_connected, f"WebSocket ainda conectado após desconexão {i+1}"

        logger.info("✅ Múltiplas conexões bem-sucedidas")

    @pytest.mark.asyncio
    async def test_rapid_candles_requests(self):
        """Teste de múltiplas requisições de candles rápidas"""
        logger.info("🧪 Testando múltiplas requisições de candles...")

        await self.api.connect()

        # Fazer múltiplas requisições
        for i in range(5):
            logger.info(f"📊 Requisição {i+1}/5")

            candles = await asyncio.wait_for(
                self.api.get_candles("EURUSD_otc", 60, count=10),
                timeout=10.0
            )

            if candles:
                assert len(candles) > 0, f"Requisição {i+1} falhou"

            # Pequena pausa entre requisições
            await asyncio.sleep(0.5)

        logger.info("✅ Múltiplas requisições de candles bem-sucedidas")


if __name__ == '__main__':
    # Executar apenas testes unitários por padrão
    pytest.main([__file__, "-m", "not integration", "-v"])
