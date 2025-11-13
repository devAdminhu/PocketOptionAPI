# 🚀 PocketOption API (Open Source)

[![GitHub](https://img.shields.io/badge/GitHub-devAdminhu-blue?style=flat-square&logo=github)](https://github.com/devAdminhu)
[![Website](https://img.shields.io/badge/Website-dev.adminhu.site-green?style=flat-square&logo=google-chrome)](https://dev.adminhu.site)
[![Telegram](https://img.shields.io/badge/Telegram-@devAdminhu-blue?style=flat-square&logo=telegram)](https://t.me/devAdminhu)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](https://opensource.org/licenses/MIT)
[![Python 3.6+](https://img.shields.io/badge/python-3.6+-blue.svg?style=flat-square)](https://www.python.org/downloads/)
[![Version](https://img.shields.io/badge/version-1.0.0-orange?style=flat-square)](https://github.com/devAdminhu/pocketoptionapi)

> API Python robusta para integração com PocketOption

![Preview da API](pocketoption.png)

## ✨ Recursos

- 🔐 Autenticação via SSID
- 💹 Trading automatizado (Buy/Sell)
- 📊 Dados em tempo real via WebSocket
- 📈 Dados históricos (candles)
- 🛡️ Reconexão automática
- 🔄 Suporte a conta Demo e Real
- ⚡ Implementação assíncrona
- 📝 Logs com Loguru

## 🛠️ Instalação

```bash
pip install git+https://github.com/devAdminhu/pocketoptionapi.git
```

## 📖 Uso Básico

```python
import asyncio
from pocketoptionapi.stable_api import PocketOption

ssid = '42["auth",{"session":"sua_sessao","isDemo":1,"uid":123456,"platform":2}]'
demo = True

async def main():
    api = PocketOption(ssid, demo)

    if await api.connect():
        print(f"💰 Saldo: ${await api.get_balance():.2f}")

        success, order_id = await api.buy(10, "EURUSD_otc", "call", 60)
        if success:
            await asyncio.sleep(65)
            profit, status = await api.check_win(order_id)
            print(f"📊 {status} - Profit: ${profit:.2f}")

        await api.disconnect()

asyncio.run(main())
```

## 📚 Documentação

### Métodos Principais
- `connect()` - Conecta ao WebSocket
- `buy(amount, active, action, expirations)` - Realiza operação
- `check_win(order_id)` - Verifica resultado
- `get_balance()` - Obtém saldo
- `get_candles(active, period, count)` - Dados históricos
- `get_payout(pair)` - Obtém payout

**[Ver documentação completa →](docs/)**

## 📜 Licença

MIT License - Uso livre

## ⚠️ Aviso

Projeto não oficial. Trading envolve riscos. Use por sua conta e risco.

## 📞 Suporte

- 🐛 Issues: [GitHub](https://github.com/devAdminhu/pocketoptionapi/issues)
- 💬 Telegram: [@devAdminhu](https://t.me/devAdminhu)

---

<p align="center">
  Desenvolvido por <a href="https://github.com/devAdminhu">devAdminhu</a>
</p>
