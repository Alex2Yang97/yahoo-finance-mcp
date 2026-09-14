# Yahoo Finance MCP Server

<div align="right">
  <a href="README.md">English</a> | <a href="README.zh.md">中文</a>
</div>

This is a Model Context Protocol (MCP) server that provides comprehensive financial data from Yahoo Finance. It allows you to retrieve detailed information about stocks, including historical prices, company information, financial statements, options data, and market news.

![GitHub last commit](https://img.shields.io/github/last-commit/modesty/pdf2json?color=olive)

## Demo

![MCP Demo](assets/demo.gif)

## MCP Tools

The server exposes the following tools through the Model Context Protocol:

### Stock Information

| Tool | Description |
|------|-------------|
| `get_historical_stock_prices` | Get historical OHLCV data for a stock with customizable period and interval |
| `get_stock_info` | Get comprehensive stock data including price, metrics, and company details |
| `get_yahoo_finance_news` | Get latest news articles for a stock |
| `get_stock_actions` | Get stock dividends and splits history |

### Financial Statements

| Tool | Description |
|------|-------------|
| `get_financial_statement` | Get income statement, balance sheet, or cash flow statement (annual/quarterly) |
| `get_holder_info` | Get major holders, institutional holders, mutual funds, or insider transactions |

### Options Data

| Tool | Description |
|------|-------------|
| `get_option_expiration_dates` | Get available options expiration dates |
| `get_option_chain` | Get options chain for a specific expiration date and type (calls/puts) |

### Analyst Information

| Tool | Description |
|------|-------------|
| `get_recommendations` | Get analyst recommendations or upgrades/downgrades history |

### Macro Events

| Tool | Description |
|------|-------------|
| `get_fxmacrodata_catalogue` | Get supported FXMacroData macro indicators and endpoint coverage for a currency |
| `get_fxmacrodata_calendar` | Get macroeconomic release calendar rows for a currency |
| `get_fxmacrodata_latest_announcements` | Get the latest macroeconomic announcement rows for a currency |

## Real-World Use Cases

With this MCP server, you can use Claude to:

### Stock Analysis

- **Price Analysis**: "Show me the historical stock prices for NOW over the last 6 months with daily intervals."
- **Financial Health**: "Get the quarterly balance sheet for Intuit."
- **Performance Metrics**: "What are the key financial metrics for Intuit from the stock info?"
- **Trend Analysis**: "Compare the quarterly income statements of ServiceNow and Intuit."
- **Cash Flow Analysis**: "Show me the annual cash flow statement for ServiceNow."

### Market Research

- **News Analysis**: "Get the latest news articles about Intuit."
- **Institutional Activity**: "Show me the institutional holders of NOW stock."
- **Insider Trading**: "What are the recent insider transactions for ServiceNow?"
- **Options Analysis**: "Get the options chain for INTU with expiration date 2026-01-30 for calls."
- **Analyst Coverage**: "What are the analyst recommendations for Intuit over the last 3 months?"

### Investment Research

- "Create a comprehensive analysis of Intuit's financial health using their latest quarterly financial statements."
- "Compare the dividend history and stock splits of Coca-Cola and PepsiCo."
- "Analyze the institutional ownership changes in ServiceNow over the past year."
- "Generate a report on the options market activity for Intuit stock with expiration in 30 days."
- "Summarize the latest analyst upgrades and downgrades in the tech sector over the last 6 months."
- "Show upcoming USD macroeconomic releases that may affect SPY this week."
- "Get the latest JPY macro announcements before reviewing Toyota."

## Requirements

- Python 3.14.6 or higher
- Dependencies as listed in `pyproject.toml`, including:
  - mcp
  - yfinance
  - pandas
  - pydantic
  - and other packages for data processing

Optional:

- `FXMD_API_KEY` enables protected FXMacroData currencies and endpoint families.
  Public USD examples work without an API key.

## Setup

### Recommended: run with `uvx`

Run the server directly from the repository without creating a local virtual environment:

```bash
uvx --from git+https://github.com/Alex2Yang97/yahoo-finance-mcp yahoo-finance-mcp
```

### Local development

1. Clone this repository:

   ```bash
   git clone https://github.com/Alex2Yang97/yahoo-finance-mcp.git
   cd yahoo-finance-mcp
   ```

2. Create and activate a virtual environment and install dependencies:

   ```bash
   uv sync
   ```

## Usage

### Quick Start

Run the packaged entrypoint with:

```bash
uvx --from git+https://github.com/Alex2Yang97/yahoo-finance-mcp yahoo-finance-mcp
```

For local changes in this checkout, use:

```bash
uvx --from . yahoo-finance-mcp
```

### Development Mode

If you are working inside a local clone and want to run the source tree directly:

```bash
uv run server.py
```

### Integration with Claude for Desktop

To integrate this server with Claude for Desktop:

1. Install Claude for Desktop to your local machine.
2. Install VS Code to your local machine. Then run the following command to open the `claude_desktop_config.json` file:
   - MacOS: `code ~/Library/Application\ Support/Claude/claude_desktop_config.json`
   - Windows: `code $env:AppData\Claude\claude_desktop_config.json`

3. Edit the Claude for Desktop config file, located at:
   - macOS:

     ```json
     {
       "mcpServers": {
         "yfinance": {
           "command": "uvx",
           "args": [
             "--from",
             "git+https://github.com/Alex2Yang97/yahoo-finance-mcp",
             "yahoo-finance-mcp"
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
           "command": "uvx",
           "args": [
             "--from",
             "git+https://github.com/Alex2Yang97/yahoo-finance-mcp",
             "yahoo-finance-mcp"
           ]
         }
       }
     }
     ```

   - **Note**: You may need to put the full path to the uv executable in the command field. You can get this by running `which uv` on MacOS/Linux or `where uv` on Windows.

4. Restart Claude for Desktop

## License

MIT
