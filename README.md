# 🚀 PocketOption API

[![GitHub](https://img.shields.io/badge/GitHub-AdminhuDev-blue?style=flat-square&logo=github)](https://github.com/AdminhuDev)
[![Website](https://img.shields.io/badge/Website-Portfolio-green?style=flat-square&logo=google-chrome)](https://adminhudev.github.io)
[![Telegram](https://img.shields.io/badge/Telegram-@devAdminhu-blue?style=flat-square&logo=telegram)](https://t.me/Analista_Adminhu)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](https://opensource.org/licenses/MIT)
[![Python 3.6+](https://img.shields.io/badge/python-3.6+-blue.svg?style=flat-square)](https://www.python.org/downloads/)
[![Version](https://img.shields.io/badge/version-1.0.0-orange?style=flat-square)](https://github.com/AdminhuDev/pocketoptionapi)

> Uma API Python robusta e moderna para integração com a PocketOption, oferecendo uma interface limpa e eficiente para automação de operações de trading.

![Preview da API](pocketoption.png)

## ✨ Destaques

- 🔐 **Autenticação Segura**: Login via SSID com validação robusta e processamento automático
- 💹 **Trading Automatizado**: Operações de compra/venda programáticas com suporte completo
- 📊 **Dados em Tempo Real**: WebSocket otimizado para cotações e operações instantâneas
- 📈 **Análise Técnica**: Acesso a dados históricos de velas (candles) e indicadores
- 🛡️ **Estabilidade**: Reconexão automática, tratamento de erros e locks thread-safe
- 🔄 **Versátil**: Suporte completo a contas demo e real
- ⚡ **Performance**: Implementação assíncrona com asyncio para máxima performance
- 📝 **Logs Detalhados**: Sistema de logging avançado com Loguru para debugging

## 🛠️ Instalação

### Via pip (recomendado):
```bash
pip install git+https://github.com/AdminhuDev/pocketoptionapi.git
```

### Para desenvolvimento:
```bash
git clone https://github.com/AdminhuDev/pocketoptionapi.git
cd pocketoptionapi
pip install -e .
```

### Dependências do Sistema:
- Python 3.6 ou superior
- pip (gerenciador de pacotes Python)

### Verificação da Instalação:
```bash
python -c "import pocketoptionapi; print('✅ PocketOption API instalada com sucesso!')"
```

## 📖 Uso Básico

```python
import asyncio
from pocketoptionapi.stable_api import PocketOption
import logging

# Configurar logging (opcional)
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')

# Configuração da sessão - formato completo obrigatório
ssid = '42["auth",{"session":"sua_sessao_aqui","isDemo":1,"uid":seu_uid_aqui,"platform":2}]'
demo = True  # True para conta demo, False para conta real

async def main():
    # Inicializar API
    api = PocketOption(ssid, demo)

    # Conectar
    conectado = await api.connect()
    if conectado:
        print("✅ Conectado com sucesso!")

        # Consultar saldo
        saldo = await api.get_balance()
        print(f"💰 Saldo: ${saldo:.2f}")

        # Realizar operação
        sucesso, order_id = await api.buy(
            amount=10,           # Valor em $
            active="EURUSD_otc", # Par de moedas (note o sufixo _otc)
            action="call",       # "call" (Alta) ou "put" (Baixa)
            expirations=60       # Expiração em segundos
        )

        if sucesso:
            print(f"✅ Operação realizada: ID {order_id}")

            # Verificar resultado após alguns segundos
            await asyncio.sleep(5)
            profit, status = await api.check_win(order_id)
            print(f"📊 Resultado: {status} - Profit: ${profit:.2f}")

        # Desconectar
        await api.disconnect()
    else:
        print("❌ Falha na conexão")

# Executar
asyncio.run(main())
```

## 🎯 Recursos Avançados

### Obtenção de Dados Históricos (Candles)
```python
import asyncio
from pocketoptionapi.stable_api import PocketOption

async def get_historical_data():
    api = PocketOption(ssid, demo)
    await api.connect()

    # Obter histórico de candles
    candles = await api.get_candles(
        active="EURUSD_otc",    # Ativo com sufixo _otc
        period=60,              # Período em segundos (1min, 5min, etc.)
        count=100,              # Quantidade de candles
        start_time=None         # Timestamp inicial (None = mais recente)
    )

    if candles:
        print(f"📊 Obtidos {len(candles)} candles")
        for candle in candles[:5]:  # Mostrar primeiros 5
            print(f"⏰ {candle['time']} - O:{candle['open']} H:{candle['high']} L:{candle['low']} C:{candle['close']}")

    await api.disconnect()

asyncio.run(get_historical_data())
```

### Obtenção de Payout (Retorno Percentual)
```python
async def get_payout_info():
    api = PocketOption(ssid, demo)
    await api.connect()

    # Aguardar dados de payout serem carregados
    await asyncio.sleep(3)

    # Obter payout para um par específico
    payout = await api.GetPayout("EURUSD_otc")
    if payout:
        print(f"📈 Payout EURUSD_otc: {payout}%")
    else:
        print("⚠️ Payout não disponível")

    await api.disconnect()

asyncio.run(get_payout_info())
```

### Monitoramento de Ordens em Tempo Real
```python
async def monitor_orders():
    api = PocketOption(ssid, demo)
    await api.connect()

    # Realizar várias operações
    orders = []
    for i in range(3):
        success, order_id = await api.buy(10, "EURUSD_otc", "call", 60)
        if success:
            orders.append(order_id)
            print(f"✅ Ordem {i+1} criada: {order_id}")

    # Monitorar resultados
    for order_id in orders:
        await asyncio.sleep(65)  # Aguardar expiração + buffer
        profit, status = await api.check_win(order_id)
        print(f"📊 Ordem {order_id}: {status} - Profit: ${profit:.2f}")

    await api.disconnect()

asyncio.run(monitor_orders())
```

## 🔧 Configuração

### Dependências Principais
```txt
websocket-client>=1.6.1
requests>=2.31.0
python-dateutil>=2.8.2
websockets>=12.0
tzlocal>=5.1
loguru>=0.7.0
pandas>=2.1.3
colorama>=0.4.6
```

### Configurações de Logging
```python
import logging
from loguru import logger

# Configuração básica
logging.basicConfig(level=logging.INFO)

# Ou configuração avançada com Loguru
logger.add("logs/pocketoption_{time}.log", rotation="1 day", retention="7 days")
```

### Obtendo o SSID
Para obter o SSID necessário para autenticação:

#### Método Manual:
1. Faça login na plataforma PocketOption pelo navegador
2. Abra as Ferramentas do Desenvolvedor (F12)
3. Vá para a aba "Network" (Rede)
4. Procure por conexões WebSocket (filtro: WS)
5. Encontre uma mensagem que começa com `42["auth"`
6. Copie o SSID completo no formato:
   ```
   42["auth",{"session":"session_string_aqui","isDemo":1,"uid":123456,"platform":2}]
   ```

#### Método Automático (Recomendado):
```python
# Usar o parser automático da API
from pocketoptionapi.ssid_parser import process_ssid_input

# Seu SSID bruto
ssid_bruto = '42["auth",{"session":"minha_session","isDemo":1,"uid":123,"platform":2}]'
demo = True

# Processar automaticamente
ssid_formatado, dados_parseados = process_ssid_input(ssid_bruto, force_demo=demo)
```

#### Formatos Suportados:
- ✅ **Formato Completo** (recomendado): `42["auth",{...}]`
- ✅ **JSON Puro**: `{"session":"...",...}`
- ✅ **Session ID Puro**: `session_string_aqui`
- ❌ **Outros formatos**: Não suportados

## 📚 Documentação da API

### Classes Principais

#### `PocketOption`
Classe principal para interação com a PocketOption.

**Métodos Principais:**
- `__init__(ssid, demo)`: Inicializa a API
- `connect()`: Conecta ao WebSocket
- `disconnect()`: Desconecta graciosamente
- `buy(amount, active, action, expirations)`: Realiza uma operação
- `check_win(order_id)`: Verifica resultado de uma operação
- `get_balance()`: Obtém saldo atual
- `get_candles(active, period, count)`: Obtém dados históricos
- `GetPayout(pair)`: Obtém payout de um ativo

**Parâmetros:**
- `ssid`: String de autenticação no formato `42["auth",{...}]`
- `demo`: Boolean (True para conta demo, False para real)

#### `PocketOptionAPI`
Classe de baixo nível para comunicação WebSocket.

**Atributos Importantes:**
- `websocket`: Cliente WebSocket
- `time_sync`: Sincronização de tempo
- `get_balances`: Gerenciamento de saldos
- `buyv3`: Canal de operações
- `getcandles`: Canal de dados históricos

### Constantes Importantes

#### Ativos Disponíveis
```python
from pocketoptionapi.constants import ACTIVES

# Exemplos de ativos
print(ACTIVES["EURUSD_otc"])    # 66
print(ACTIVES["BTCUSD_otc"])    # 484
print(ACTIVES["#AAPL_otc"])     # 170
```

#### Timeframes
```python
TIMEFRAMES = {
    "1m": 60,
    "5m": 300,
    "15m": 900,
    "1h": 3600,
    "4h": 14400,
    "1d": 86400
}
```

#### Regiões WebSocket
```python
from pocketoptionapi.constants import REGION

# Regiões disponíveis
print(REGION.get_all_regions())
```

### Tratamento de Erros

A API utiliza tratamento robusto de erros:

- **Conexão**: Reconexão automática com fallback entre servidores
- **Autenticação**: Validação de SSID e reautenticação automática
- **Operações**: Retry automático para operações falhadas
- **Timeout**: Timeouts configuráveis para todas as operações

### Logs e Debug

```python
import logging
from loguru import logger

# Configurar logs detalhados
logger.add("debug.log", level="DEBUG")

# Ou usar logging padrão
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("pocketoption.log"),
        logging.StreamHandler()
    ]
)
```

## 🤝 Contribuindo

Sua contribuição é muito bem-vinda! Siga estes passos:

1. 🍴 Fork este repositório
2. 🔄 Crie uma branch para sua feature
   ```bash
   git checkout -b feature/MinhaFeature
   ```
3. 💻 Faça suas alterações seguindo as melhores práticas:
   - Mantenha compatibilidade com Python 3.6+
   - Adicione testes para novas funcionalidades
   - Atualize a documentação
   - Use commits convencionais
4. ✅ Commit usando mensagens convencionais
   ```bash
   git commit -m "feat: Adiciona nova funcionalidade"
   ```
5. 📤 Push para sua branch
   ```bash
   git push origin feature/MinhaFeature
   ```
6. 🔍 Abra um Pull Request com descrição detalhada

### Diretrizes para Contribuição
- 🐛 **Bugs**: Abra uma issue detalhada
- ✨ **Features**: Discuta primeiro em uma issue
- 📝 **Documentação**: Melhorias sempre bem-vindas
- 🧪 **Testes**: Adicione testes para suas alterações

## 📜 Licença

Este projeto está licenciado sob a MIT License - veja o arquivo [LICENSE](LICENSE) para detalhes.

## ⚠️ Aviso Legal

**IMPORTANTE**: Este projeto é uma implementação não oficial e não possui vínculo com a PocketOption ou suas afiliadas.

- 🚫 **Uso comercial**: Não recomendado sem consulta jurídica
- ⚠️ **Riscos**: Trading envolve riscos financeiros significativos
- 🔞 **Idade**: Apenas para maiores de 18 anos
- 💰 **Perdas**: Você pode perder todo seu capital investido
- 📊 **Resultados**: Passados não garantem resultados futuros

**Use por sua conta e risco. Não nos responsabilizamos por perdas financeiras.**

## 📞 Suporte

- 💬 Telegram: [@devAdminhu](https://t.me/devAdminhu)
- 🌐 Website: [adminhudev.site](https://adminhudev.github.io)
- 🐛 Issues: [GitHub Issues](https://github.com/AdminhuDev/pocketoptionapi/issues)

## 🙏 Agradecimentos

- PocketOption pela plataforma
- Comunidade open source
- Todos os contribuidores

---

<p align="center">
  Desenvolvido com ❤️ por <a href="https://github.com/AdminhuDev">AdminhuDev</a>
</p> 
