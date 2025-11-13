"""
Bot de Trading Simples
Exemplo básico para um ativo
"""

import asyncio
from pocketoptionapi import PocketOption


class SimpleBot:
    """Bot simples para trading em um ativo"""

    def __init__(self, ssid: str):
        self.api = PocketOption(ssid)
        self.asset = "EURUSD_otc"
        self.amount = 1
        self.duration = 60

    async def connect(self):
        """Conectar à API"""
        return await self.api.connect()

    async def trade_call(self):
        """Fazer operação CALL"""
        success, order_id = await self.api.buy(
            amount=self.amount,
            active=self.asset,
            action="call",
            expirations=self.duration
        )
        return success, order_id

    async def check_result(self, order_id):
        """Verificar resultado"""
        await asyncio.sleep(self.duration + 5)
        return await self.api.check_win(order_id)

    async def run_once(self):
        """Executar uma operação"""
        if not await self.connect():
            print("Erro de conexão")
            return

        # Aguardar dados
        await asyncio.sleep(3)

        # Obter informações
        balance = await self.api.get_balance()
        payout = await self.api.GetPayout(self.asset)
        print(f"Saldo: ${balance} | Payout: {payout}%")

        # Fazer operação
        success, order_id = await self.trade_call()
        if success:
            print(f"Operação executada: {order_id}")
            profit, status = await self.check_result(order_id)
            print(f"Resultado: {status} | Profit: ${profit}")
        else:
            print("Falha na operação")

        await self.api.disconnect()


async def main():
    """Exemplo de uso"""
    SSID = '42["auth",{"session":"sua_session_aqui","isDemo":1,"uid":123456,"platform":2}]'
    
    if 'sua_session_aqui' in SSID:
        print("Configure seu SSID real")
        return
    
    bot = SimpleBot(SSID)
    await bot.run_once()


if __name__ == "__main__":
    asyncio.run(main())
