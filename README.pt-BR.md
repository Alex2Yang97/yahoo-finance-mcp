# Servidor Yahoo Finance MCP

<div align="right">
  <a href="README.md">English</a> | <a href="README.zh.md">中文</a> | <a href="README.pt-BR.md">Português (BR)</a>
</div>

Este é um servidor baseado no Model Context Protocol (MCP) que fornece dados financeiros do Yahoo Finance. Ele permite obter informações detalhadas sobre ações, incluindo preços históricos, dados da empresa, demonstrações financeiras, dados de opções e notícias do mercado.

[![smithery badge](https://smithery.ai/badge/@Alex2Yang97/yahoo-finance-mcp)](https://smithery.ai/server/@Alex2Yang97/yahoo-finance-mcp)

## Demonstração

![Demonstração MCP](assets/demo.gif)

## Ferramentas MCP

O servidor expõe as seguintes ferramentas através do Model Context Protocol:

### Informações de ações

| Ferramenta | Descrição |
|------|-------------|
| `get_historical_stock_prices` | Obtém dados históricos OHLCV de uma ação com período e intervalo personalizáveis |
| `get_stock_info` | Obtém dados completos da ação, incluindo preço, métricas e detalhes da empresa |
| `get_yahoo_finance_news` | Obtém as últimas notícias sobre uma ação |
| `get_stock_actions` | Obtém histórico de dividendos e desdobramentos da ação |

### Demonstrações financeiras

| Ferramenta | Descrição |
|------|-------------|
| `get_financial_statement` | Obtém DRE, balanço patrimonial ou fluxo de caixa (anual/trimestral) |
| `get_holder_info` | Obtém principais acionistas, acionistas institucionais, fundos mútuos ou transações de insider |

### Dados de opções

| Ferramenta | Descrição |
|------|-------------|
| `get_option_expiration_dates` | Obtém datas de vencimento de opções disponíveis |
| `get_option_chain` | Obtém a cadeia de opções para uma data de vencimento e tipo (calls/puts) |

### Informações de analistas

| Ferramenta | Descrição |
|------|-------------|
| `get_recommendations` | Obtém recomendações de analistas ou histórico de upgrades/downgrades |

## Casos de uso

Com este servidor MCP, você pode usar o Claude para:

### Análise de ações

- **Análise de preços**: "Mostre os preços históricos da ação AAPL dos últimos 6 meses com intervalos diários."
- **Saúde financeira**: "Obtenha o balanço patrimonial trimestral da Microsoft."
- **Métricas de desempenho**: "Quais são as principais métricas financeiras da Tesla a partir das informações da ação?"
- **Análise de tendência**: "Compare as DREs trimestrais da Amazon e do Google."
- **Análise de fluxo de caixa**: "Mostre a demonstração de fluxo de caixa anual da NVIDIA."

### Pesquisa de mercado

- **Análise de notícias**: "Obtenha as últimas notícias sobre a Meta Platforms."
- **Atividade institucional**: "Mostre os acionistas institucionais da Apple."
- **Transações de insider**: "Quais são as transações recentes de insider da Tesla?"
- **Análise de opções**: "Obtenha a cadeia de opções do SPY com vencimento em 2024-06-21 para calls."
- **Cobertura de analistas**: "Quais são as recomendações de analistas para a Amazon nos últimos 3 meses?"

### Pesquisa de investimentos

- "Crie uma análise completa da saúde financeira da Microsoft usando suas últimas demonstrações financeiras trimestrais."
- "Compare o histórico de dividendos e desdobramentos da Coca-Cola e da PepsiCo."
- "Analise as mudanças na propriedade institucional da Tesla no último ano."
- "Gere um relatório sobre a atividade do mercado de opções da Apple com vencimento em 30 dias."
- "Resuma os últimos upgrades e downgrades de analistas no setor de tecnologia nos últimos 6 meses."

## Requisitos

- Python 3.11 ou superior
- Dependências listadas no `pyproject.toml`, incluindo:
  - mcp
  - yfinance
  - pandas
  - pydantic
  - e outros pacotes para processamento de dados

## Instalação

1. Clone este repositório:
   ```bash
   git clone https://github.com/Alex2Yang97/yahoo-finance-mcp.git
   cd yahoo-finance-mcp
   ```

2. Crie e ative um ambiente virtual e instale as dependências:
   ```bash
   uv venv
   source .venv/bin/activate  # No Windows: .venv\Scripts\activate
   uv pip install -e .
   ```

## Uso

### Modo de desenvolvimento

Você pode testar o servidor com o MCP Inspector executando:

```bash
uv run server.py
```

Isso iniciará o servidor e permitirá testar as ferramentas disponíveis.

### Integração com Claude for Desktop

Para integrar este servidor ao Claude for Desktop:

1. Instale o Claude for Desktop na sua máquina.
2. Instale o VS Code na sua máquina. Em seguida, execute o comando abaixo para abrir o arquivo `claude_desktop_config.json`:
   - MacOS: `code ~/Library/Application\ Support/Claude/claude_desktop_config.json`
   - Windows: `code $env:AppData\Claude\claude_desktop_config.json`

3. Edite o arquivo de configuração do Claude for Desktop, localizado em:
   - macOS:
     ```json
     {
       "mcpServers": {
         "yfinance": {
           "command": "uv",
           "args": [
             "--directory",
             "/CAMINHO/ABSOLUTO/PARA/PASTA/yahoo-finance-mcp",
             "run",
             "server.py"
           ]
         }
       }
     }
     ```
   - Windows:
     ```json
     {
       "mcpServers": {
         "yfinance": {
           "command": "uv",
           "args": [
             "--directory",
             "C:\\CAMINHO\\ABSOLUTO\\PARA\\PASTA\\yahoo-finance-mcp",
             "run",
             "server.py"
           ]
         }
       }
     }
     ```

   - **Nota**: Pode ser necessário colocar o caminho completo do executável uv no campo command. Execute `which uv` no MacOS/Linux ou `where uv` no Windows para obter o caminho.

4. Reinicie o Claude for Desktop

## Licença

MIT
