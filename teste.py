"""
Teste Básico da PocketOption API
Autor: AdminhuDev
Versão: 1.0.0
Data: 2024
"""

import asyncio
import time
import logging
from pocketoptionapi.stable_api import PocketOption
from loguru import logger

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger.add("logs/teste_{time}.log", rotation="1 day", retention="7 days")

# Configuração da sessão (EXEMPLO - substitua pelos seus dados reais)
SSID_EXEMPLO = '42["auth",{"session":"lmarivud8uivsahpc3lbl09plk","isDemo":1,"uid":86113915,"platform":3,"isFastHistory":true,"isOptimized":true}]'

async def teste_basico():
    """
    Teste básico da API PocketOption
    """
    print("🚀 Iniciando teste básico da PocketOption API")
    print("=" * 50)

    try:
        # 1. Inicialização da API
        print("📋 1. Inicializando API...")
        api = PocketOption(SSID_EXEMPLO)
        print("✅ API inicializada com sucesso")

        # 2. Conexão WebSocket
        print("🔗 2. Conectando ao WebSocket...")
        conectado = await api.connect()

        if not conectado:
            print("❌ Falha na conexão WebSocket")
            print("💡 Verifique seu SSID e conexão com internet")
            return

        print("✅ Conectado com sucesso ao WebSocket")

        # 3. Aguardar estabilização
        print("⏳ 3. Aguardando estabilização da conexão...")
        await asyncio.sleep(3)

        # 4. Teste de saldo
        print("💰 4. Testando obtenção de saldo...")
        try:
            saldo = await api.get_balance()
            if saldo is not None:
                print(f"✅ Saldo obtido: ${saldo:.2f}")
            else:
                print("⚠️ Saldo não disponível (pode estar carregando)")
        except Exception as e:
            print(f"❌ Erro ao obter saldo: {e}")

        # 5. Aguardar dados de payout
        print("📊 5. Aguardando dados de payout...")
        await asyncio.sleep(5)

        # 6. Teste de payout
        print("📈 6. Testando obtenção de payout...")
        try:
            payout = await api.GetPayout("EURUSD_otc")
            if payout:
                print(f"✅ Payout EURUSD_otc: {payout}%")
            else:
                print("⚠️ Payout não disponível")
        except Exception as e:
            print(f"❌ Erro ao obter payout: {e}")

        # 7. Teste de candles (dados históricos)
        print("📊 7. Testando obtenção de candles...")
        try:
            candles = await api.get_candles("EURUSD_otc", 60, count=10)
            if candles and len(candles) > 0:
                print(f"✅ Obtidos {len(candles)} candles")
                print("📋 Primeiras 3 velas:")
                for i, candle in enumerate(candles[:3]):
                    print(f"   {i+1}. {candle['time']} - O:{candle['open']:.5f} C:{candle['close']:.5f}")
            else:
                print("⚠️ Nenhum candle obtido")
        except Exception as e:
            print(f"❌ Erro ao obter candles: {e}")

        # 8. Teste de operação
        print("💹 8. Teste de operação...")
        
        # Exemplo de operação (descomente para testar)
        """
        print("🎮 TESTANDO OPERAÇÃO")
        try:
            sucesso, order_id = await api.buy(
                amount=1,
                active="EURUSD_otc",
                action="call",
                expirations=60
            )

            if sucesso and order_id:
                print(f"✅ Operação realizada: ID {order_id}")

                # Aguardar resultado
                await asyncio.sleep(65)
                profit, status = await api.check_win(order_id)
                print(f"📊 Resultado: {status} - Profit: ${profit:.2f}")
            else:
                print("❌ Falha na operação")
        except Exception as e:
            print(f"❌ Erro na operação: {e}")
        """

        # 9. Desconexão
        print("🔌 9. Desconectando...")
        await api.disconnect()
        print("✅ Desconectado com sucesso")

    except Exception as e:
        print(f"❌ Erro geral no teste: {e}")
        print(f"🔍 Detalhes: {str(e)}")

    print("=" * 50)
    print("🏁 Teste básico concluído")

def main():
    """
    Função principal
    """
    print("🎯 PocketOption API - Teste Básico")
    print("💡 Este teste verifica as funcionalidades básicas da API")
    print()

    # Verificar se o SSID foi configurado
    if SSID_EXEMPLO == '42["auth",{"session":"sua_session_aqui","isDemo":1,"uid":123456,"platform":2}]':
        print("⚠️ ATENÇÃO: Você precisa configurar seu SSID real!")
        print("📝 Edite a variável SSID_EXEMPLO no arquivo teste.py")
        print()
        print("Para obter seu SSID:")
        print("1. Faça login na PocketOption")
        print("2. Abra DevTools (F12)")
        print("3. Vá para Network > WS")
        print("4. Copie a mensagem que começa com 42[\"auth\"")
        print()
        return

    # Executar teste
    asyncio.run(teste_basico())

if __name__ == "__main__":
    main()
