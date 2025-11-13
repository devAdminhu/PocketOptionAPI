# 🧪 Testes da PocketOption API

Este diretório contém a suíte completa de testes para a PocketOption API.

## 📋 Estrutura dos Testes

```
tests/
├── __init__.py              # Inicialização do módulo de testes
├── conftest.py              # Configuração global do pytest
├── test_pocketoption.py     # Testes unitários da classe principal
├── test_ssid_parser.py      # Testes do parser de SSID
├── test_constants.py        # Testes das constantes da API
├── test_integration.py      # Testes de integração (requer configuração)
└── README.md               # Esta documentação
```

## 🚀 Como Executar os Testes

### Pré-requisitos

```bash
pip install pytest pytest-asyncio
```

### Executar Todos os Testes Unitários

```bash
# Do diretório raiz do projeto
pytest tests/ -v
```

### Executar Apenas Testes Rápidos

```bash
pytest tests/ -m "not slow" -v
```

### Executar Apenas Testes de Integração (Avançado)

⚠️ **ATENÇÃO**: Os testes de integração requerem configuração real da API!

```bash
# Configurar variáveis de ambiente
export POCKETOPTION_SSID='42["auth",{"session":"sua_session","isDemo":1,"uid":123,"platform":2}]'
export POCKETOPTION_DEMO=true
export ALLOW_REAL_TRADES=false  # Para segurança

# Executar testes de integração
pytest tests/ -m integration -v -s
```

## 📝 Tipos de Testes

### 🧩 Testes Unitários (`test_*.py`)

- **Propósito**: Testar componentes individuais em isolamento
- **Características**:
  - Não requerem conexão real com a API
  - Usam mocks e fixtures para simular dependências
  - Executam rapidamente
  - Cobrem funcionalidades críticas

### 🔗 Testes de Integração (`test_integration.py`)

- **Propósito**: Testar integração com a API real
- **Características**:
  - Requerem SSID válido e conexão com internet
  - Testam cenários reais de uso
  - Mais lentos para executar
  - Podem envolver custos reais (operações)

### ⚡ Testes de Estresse (`test_integration.py::TestPocketOptionStress`)

- **Propósito**: Testar performance e estabilidade
- **Características**:
  - Testam múltiplas conexões consecutivas
  - Verificam resistência a falhas
  - Avaliam performance sob carga

## 🛠️ Configuração do Ambiente de Teste

### Variáveis de Ambiente

```bash
# SSID para testes de integração
export POCKETOPTION_SSID='42["auth",{"session":"...","isDemo":1,"uid":123,"platform":2}]'

# Modo demo ou real
export POCKETOPTION_DEMO=true

# Permitir operações reais (CUIDADO!)
export ALLOW_REAL_TRADES=false
```

### Instalação em Ambiente Virtual

```bash
# Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# Instalar dependências
pip install -e .
pip install pytest pytest-asyncio

# Executar testes
pytest tests/ -v
```

## 📊 Cobertura dos Testes

### Funcionalidades Testadas

- ✅ **Parser de SSID**: Validação, parsing e formatação
- ✅ **Classe PocketOption**: Inicialização, conexão, operações
- ✅ **Constantes**: Ativos, regiões, timeframes
- ✅ **WebSocket**: Conexão, comunicação, tratamento de mensagens
- ✅ **Operações**: Compra, venda, verificação de resultados
- ✅ **Dados Históricos**: Obtenção de candles
- ✅ **Saldo e Payout**: Consulta de informações da conta

### Cenários de Teste

#### Parser de SSID
- ✅ SSID válido completo
- ✅ SSID JSON simples
- ✅ SSID session ID puro
- ✅ SSID mal formado
- ✅ SSID vazio/nulo
- ✅ Sessions complexas (PHP serialized)
- ✅ Sessions com caracteres especiais

#### Classe Principal
- ✅ Inicialização válida
- ✅ Inicialização inválida
- ✅ Conexão WebSocket
- ✅ Desconexão
- ✅ Obtenção de saldo
- ✅ Obtenção de payout
- ✅ Obtenção de candles
- ✅ Operações de compra
- ✅ Verificação de resultados

#### Constantes
- ✅ Estrutura de ativos
- ✅ Formatos OTC
- ✅ Categorias de ativos
- ✅ Regiões WebSocket
- ✅ Timeframes
- ✅ Configurações de conexão
- ✅ Limites da API

## 🔧 Desenvolvimento de Testes

### Adicionando Novos Testes

1. **Criar arquivo de teste**:
   ```python
   # tests/test_novo_modulo.py
   import unittest
   from pocketoptionapi.novo_modulo import NovaClasse

   class TestNovaClasse(unittest.TestCase):
       def test_metodo_exemplo(self):
           instancia = NovaClasse()
           resultado = instancia.metodo_exemplo()
           self.assertEqual(resultado, "esperado")
   ```

2. **Para testes assíncronos**:
   ```python
   import pytest

   @pytest.mark.asyncio
   async def test_metodo_assincrono():
       api = PocketOption(ssid, demo)
       resultado = await api.metodo_assincrono()
       assert resultado is not None
   ```

3. **Para testes de integração**:
   ```python
   @pytest.mark.integration
   @pytest.mark.slow
   def test_integracao_real():
       # Teste que requer API real
       pass
   ```

### Boas Práticas

- ✅ Usar `pytest` como framework principal
- ✅ Nomear arquivos com `test_*.py`
- ✅ Nomear classes com `Test*`
- ✅ Nomear métodos com `test_*`
- ✅ Usar fixtures para configuração comum
- ✅ Marcar testes especiais com `@pytest.mark`
- ✅ Documentar testes complexos
- ✅ Usar asserções descritivas

## 📈 Relatórios de Cobertura

Para gerar relatório de cobertura:

```bash
# Instalar pytest-cov
pip install pytest-cov

# Executar com cobertura
pytest tests/ --cov=pocketoptionapi --cov-report=html

# Abrir relatório
open htmlcov/index.html
```

## 🚨 Avisos Importantes

### Segurança
- 🔒 **Nunca** commite SSIDs reais no código
- 🚫 **Nunca** habilite `ALLOW_REAL_TRADES=true` em produção
- ⚠️ **Sempre** use contas demo para testes automáticos

### Performance
- 🐌 Testes de integração são lentos por natureza
- ⏰ Configure timeouts adequados para sua conexão
- 🔄 Use fixtures para reutilizar conexões quando possível

### Custos
- 💰 Operações reais consomem saldo da conta
- 📊 Monitore uso de dados em conexões móveis
- ⚡ Prefira testes unitários para desenvolvimento diário

## 🐛 Debugging de Testes

### Testes Falhando

1. **Verificar logs**:
   ```bash
   pytest tests/ -v -s --log-cli-level=INFO
   ```

2. **Executar teste específico**:
   ```bash
   pytest tests/test_pocketoption.py::TestPocketOption::test_init_valid_ssid -v -s
   ```

3. **Debug interativo**:
   ```bash
   pytest tests/ --pdb
   ```

### Problemas Comuns

#### `ModuleNotFoundError`
```bash
# Solução: instalar dependências
pip install -e .
```

#### `ConnectionError`
```bash
# Solução: verificar conexão com internet
ping google.com
```

#### `AssertionError` em testes de integração
```bash
# Solução: verificar SSID e configuração
export POCKETOPTION_SSID='42["auth",{"session":"..."}]'
```

## 📞 Suporte

- 🐛 **Issues**: [GitHub Issues](https://github.com/AdminhuDev/pocketoptionapi/issues)
- 📧 **Email**: adminhudev@gmail.com
- 💬 **Telegram**: [@devAdminhu](https://t.me/devAdminhu)

---

<p align="center">
  Desenvolvido com ❤️ por <a href="https://github.com/AdminhuDev">AdminhuDev</a>
</p>
