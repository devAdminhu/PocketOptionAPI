# 📚 Documentação Técnica - PocketOption API

## Visão Geral

A PocketOption API é uma biblioteca Python moderna e robusta para integração com a plataforma PocketOption, oferecendo uma interface limpa e eficiente para automação de operações de trading.

## Arquitetura

### Estrutura de Diretórios

```
pocketoptionapi/
├── __init__.py           # Inicialização do pacote
├── api.py                # Classe principal de comunicação WebSocket
├── stable_api.py         # Interface de alto nível para usuários
├── ssid_parser.py        # Parser e validador de SSID
├── constants.py          # Constantes da API (ativos, regiões, etc.)
├── global_value.py       # Estado global da aplicação
├── session_manager.py    # Gerenciamento de sessão
├── assets_parser.py      # Parser de dados de ativos
├── ws/                   # Módulo WebSocket
│   ├── __init__.py
│   ├── client.py         # Cliente WebSocket
│   ├── channels/         # Canais WebSocket específicos
│   └── objects/          # Objetos de dados WebSocket
├── tests/                # Suíte de testes
└── examples/             # Exemplos de uso
```

### Componentes Principais

#### 1. `PocketOption` (stable_api.py)
Classe principal para interação com a API:

- **Responsabilidades**:
  - Gerenciamento de conexão WebSocket
  - Parsing e validação de SSID
  - Operações de trading (buy/check_win)
  - Obtenção de dados de mercado
  - Gerenciamento de sessão

- **Métodos Principais**:
  - `connect()`: Estabelece conexão WebSocket
  - `disconnect()`: Fecha conexão graciosamente
  - `buy()`: Executa operações de compra
  - `check_win()`: Verifica resultado de operações
  - `get_balance()`: Obtém saldo da conta
  - `get_candles()`: Obtém dados históricos

#### 2. `PocketOptionAPI` (api.py)
Classe de baixo nível para comunicação WebSocket:

- **Responsabilidades**:
  - Comunicação direta com WebSocket
  - Gerenciamento de mensagens
  - Sincronização de tempo
  - Reconexão automática

#### 3. `WebsocketClient` (ws/client.py)
Cliente WebSocket otimizado:

- **Características**:
  - Reconexão automática com fallback
  - Gerenciamento de locks async-safe
  - Parsing de mensagens em tempo real
  - Ping/pong para manter conexão ativa

## Fluxo de Funcionamento

### 1. Inicialização
```python
from pocketoptionapi.stable_api import PocketOption

# SSID obrigatório no formato completo
ssid = '42["auth",{"session":"...","isDemo":1,"uid":123,"platform":2}]'
api = PocketOption(ssid, demo=True)
```

### 2. Conexão
```python
# Conexão assíncrona com timeout
connected = await api.connect()
if connected:
    print("Conectado com sucesso")
```

### 3. Operações
```python
# Compra
success, order_id = await api.buy(10, "EURUSD_otc", "call", 60)

# Verificação de resultado
profit, status = await api.check_win(order_id)
```

### 4. Dados de Mercado
```python
# Candles históricos
candles = await api.get_candles("EURUSD_otc", 60, count=100)

# Payout
payout = await api.GetPayout("EURUSD_otc")
```

## Protocolo WebSocket

### Formato de Mensagens

#### Mensagem de Autenticação
```json
42["auth", {
  "session": "session_string",
  "isDemo": 1,
  "uid": 123456,
  "platform": 2,
  "isFastHistory": true
}]
```

#### Mensagem de Operação
```json
42["openOrder", {
  "asset": "EURUSD_otc",
  "amount": 10,
  "action": "call",
  "isDemo": 1,
  "requestId": "buy_123",
  "optionType": 100,
  "time": 60
}]
```

### Estados da Conexão

1. **Desconectado**: Estado inicial
2. **Conectando**: Tentativa de conexão
3. **Conectado**: Autenticação pendente
4. **Autenticado**: Pronto para operações
5. **Erro**: Falha na conexão

### Reconexão Automática

O sistema implementa fallback entre múltiplos servidores:

1. **Europa** (primário)
2. **Seychelles** (secundário)
3. **França** (terciário)
4. **EUA** (quaternário)

## Parsing de SSID

### Formatos Suportados

#### 1. Formato Completo (Recomendado)
```json
42["auth", {"session":"abc123","isDemo":1,"uid":123,"platform":2}]
```

#### 2. JSON Puro
```json
{"session":"abc123","isDemo":1,"uid":123,"platform":2}
```

#### 3. Session ID Puro
```
abc123
```

### Processo de Parsing

1. **Validação**: Verifica formato básico
2. **Extração**: Remove prefixo `42` se presente
3. **Parse JSON**: Converte string para objeto
4. **Validação de Campos**: Verifica campos obrigatórios
5. **Override de Configurações**: Aplica configurações de demo/UID

## Tratamento de Erros

### Categorias de Erro

#### 1. Erros de Conexão
- **Timeout**: Servidor não responde
- **DNS**: Falha de resolução
- **SSL**: Problemas de certificado
- **Proxy**: Configuração incorreta

#### 2. Erros de Autenticação
- **SSID Inválido**: Formato incorreto
- **Sessão Expirada**: Login necessário
- **Conta Banida**: Acesso negado
- **IP Bloqueado**: Restrição geográfica

#### 3. Erros de Operação
- **Saldo Insuficiente**: Fundos inadequados
- **Ativo Indisponível**: Mercado fechado
- **Valor Inválido**: Parâmetros fora do limite
- **Rate Limit**: Muitas operações

### Estratégias de Recuperação

1. **Reconexão**: Tentativa automática com backoff
2. **Retry**: Reenvio de operações falhadas
3. **Fallback**: Uso de servidores alternativos
4. **Logging**: Registro detalhado para debugging

## Performance

### Otimizações Implementadas

#### 1. Asyncio
- Operações não-bloqueantes
- Paralelização de tarefas
- Gerenciamento eficiente de recursos

#### 2. Locks Thread-Safe
- Controle de concorrência
- Prevenção de race conditions
- Sincronização de estado global

#### 3. Pool de Conexões
- Reutilização de conexões
- Gerenciamento de estado
- Cleanup automático

### Benchmarks

- **Conexão**: < 3 segundos (média)
- **Operação**: < 500ms (média)
- **Candles**: < 2 segundos para 1000 registros
- **Memória**: ~50MB em uso normal

## Segurança

### Medidas Implementadas

#### 1. Validação de Entrada
- SSID obrigatório no formato correto
- Parâmetros validados antes do envio
- Sanitização de dados

#### 2. Gerenciamento de Sessão
- Timeout automático
- Renovação de sessão
- Logout forçado

#### 3. Comunicação Segura
- WebSocket SSL/TLS
- Certificados verificados
- Headers de segurança

### Recomendações

1. **Nunca commite SSIDs** no código
2. **Use sempre HTTPS** para transmissão
3. **Implemente rate limiting** na aplicação
4. **Monitore logs** de segurança
5. **Use contas demo** para desenvolvimento

## Monitoramento

### Métricas Disponíveis

#### 1. Performance
- Latência de conexão
- Tempo de resposta das operações
- Taxa de sucesso de requisições

#### 2. Estado da Conta
- Saldo atual
- Operações abertas
- Histórico de resultados

#### 3. Sistema
- Uso de memória
- Conexões ativas
- Taxa de erros

### Logging

O sistema utiliza Loguru para logging avançado:

```python
from loguru import logger

# Configuração
logger.add("logs/api.log", rotation="1 day", retention="7 days")

# Uso
logger.info("Operação executada com sucesso")
logger.error("Erro na conexão WebSocket")
```

## Testes

### Estrutura de Testes

```
tests/
├── test_pocketoption.py      # Testes da classe principal
├── test_ssid_parser.py       # Testes do parser
├── test_constants.py         # Testes das constantes
├── test_integration.py       # Testes de integração
└── conftest.py              # Configuração pytest
```

### Execução de Testes

```bash
# Todos os testes unitários
pytest tests/ -v

# Apenas testes rápidos
pytest tests/ -m "not slow" -v

# Com cobertura
pytest tests/ --cov=pocketoptionapi --cov-report=html
```

### Tipos de Teste

1. **Unitários**: Testam componentes isoladamente
2. **Integração**: Testam interação com API real
3. **Performance**: Verificam métricas de performance
4. **Estresse**: Testam limites do sistema

## Exemplos de Uso

### Básico
```python
import asyncio
from pocketoptionapi.stable_api import PocketOption

async def main():
    api = PocketOption(ssid, demo=True)
    await api.connect()

    # Operação simples
    success, order_id = await api.buy(10, "EURUSD_otc", "call", 60)
    profit, status = await api.check_win(order_id)

    await api.disconnect()

asyncio.run(main())
```

### Avançado com Análise Técnica
```python
# Ver exemplos em examples/
```

## Troubleshooting

### Problemas Comuns

#### 1. Erro de Conexão
```
Erro: Timeout na conexão WebSocket
Solução: Verificar conexão internet e tentar novamente
```

#### 2. SSID Inválido
```
Erro: User not Authorized
Solução: Obter novo SSID da plataforma
```

#### 3. Operação Rejeitada
```
Erro: Saldo insuficiente
Solução: Verificar saldo disponível
```

### Debug

1. **Habilitar logs detalhados**:
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

2. **Executar testes de conectividade**:
   ```bash
   python -c "import pocketoptionapi; print('OK')"
   ```

3. **Verificar versão**:
   ```python
   import pocketoptionapi
   print(pocketoptionapi.__version__)
   ```

## Suporte

- **GitHub Issues**: Para bugs e solicitações
- **Telegram**: @devAdminhu para suporte rápido
- **Email**: adminhudev@gmail.com para questões técnicas

## Contribuição

Ver [CONTRIBUTING.md](../CONTRIBUTING.md) para diretrizes de contribuição.

## Licença

Este projeto está sob a licença MIT. Ver [LICENSE](../LICENSE) para detalhes.

---

<p align="center">
  Desenvolvido com ❤️ por <a href="https://github.com/AdminhuDev">AdminhuDev</a>
</p>
