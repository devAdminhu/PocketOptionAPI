"""
Bot de Trading Simples - PocketOption API
Exemplo básico de operação em 1 ativo apenas
"""

import asyncio
from pocketoptionapi import PocketOption

# Configuração básica
SSID = '42["auth",{"session":"sua_session_aqui","isDemo":1,"uid":123456,"platform":2}]'
ASSET = "EURUSD_otc"
AMOUNT = 1
DURATION = 60  # segundos


async def simple_trade():
    """Operação simples em um ativo"""
    
    # Conectar à API
    api = PocketOption(SSID)
    connected = await api.connect()
    
    if not connected:
        print("Erro: Não foi possível conectar")
        return
    
    print("Conectado com sucesso!")
    
    # Aguardar dados
    await asyncio.sleep(3)
    
    # Obter saldo
    balance = await api.get_balance()
    print(f"Saldo: ${balance}")
    
    # Obter payout
    payout = await api.GetPayout(ASSET)
    print(f"Payout {ASSET}: {payout}%")
    
    # Fazer operação CALL
    print(f"Fazendo operação CALL em {ASSET}...")
    success, order_id = await api.buy(
        amount=AMOUNT,
        active=ASSET,
        action="call",
        expirations=DURATION
    )
    
    if success and order_id:
        print(f"Operação realizada: ID {order_id}")
        
        # Aguardar resultado
        print("Aguardando resultado...")
        await asyncio.sleep(DURATION + 5)
        
        # Verificar resultado
        profit, status = await api.check_win(order_id)
        print(f"Resultado: {status}")
        if profit:
            print(f"Profit: ${profit:.2f}")
    else:
        print("Falha na operação")
    
    # Desconectar
    await api.disconnect()
    print("Desconectado")


async def main():
    """Função principal"""
    print("=== Bot Trading Simples ===")
    print(f"Ativo: {ASSET}")
    print(f"Valor: ${AMOUNT}")
    print(f"Duração: {DURATION}s")
    print()
    
    if 'sua_session_aqui' in SSID:
        print("⚠️ Configure seu SSID real antes de usar!")
        return
    
    await simple_trade()


if __name__ == "__main__":
    asyncio.run(main())