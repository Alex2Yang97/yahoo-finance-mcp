import json
import os
import urllib.parse
import urllib.request
from enum import Enum

import pandas as pd
import yfinance as yf
from mcp.server import MCPServer


# Define an enum for the type of financial statement
class FinancialType(str, Enum):
    income_stmt = "income_stmt"
    quarterly_income_stmt = "quarterly_income_stmt"
    balance_sheet = "balance_sheet"
    quarterly_balance_sheet = "quarterly_balance_sheet"
    cashflow = "cashflow"
    quarterly_cashflow = "quarterly_cashflow"


class HolderType(str, Enum):
    major_holders = "major_holders"
    institutional_holders = "institutional_holders"
    mutualfund_holders = "mutualfund_holders"
    insider_transactions = "insider_transactions"
    insider_purchases = "insider_purchases"
    insider_roster_holders = "insider_roster_holders"


class RecommendationType(str, Enum):
    recommendations = "recommendations"
    upgrades_downgrades = "upgrades_downgrades"


# Initialize MCP server
yfinance_server = MCPServer(
    "yfinance",
    instructions="""
# Yahoo Finance MCP Server

This server is used to get information about a given ticker symbol from yahoo finance.

Available tools:
- get_historical_stock_prices: Get historical stock prices for a given ticker symbol from yahoo finance. Include the following information: Date, Open, High, Low, Close, Volume, Adj Close.
- get_stock_info: Get stock information for a given ticker symbol from yahoo finance. Include the following information: Stock Price & Trading Info, Company Information, Financial Metrics, Earnings & Revenue, Margins & Returns, Dividends, Balance Sheet, Ownership, Analyst Coverage, Risk Metrics, Other.
- get_yahoo_finance_news: Get news for a given ticker symbol from yahoo finance.
- get_stock_actions: Get stock dividends and stock splits for a given ticker symbol from yahoo finance.
- get_financial_statement: Get financial statement for a given ticker symbol from yahoo finance. You can choose from the following financial statement types: income_stmt, quarterly_income_stmt, balance_sheet, quarterly_balance_sheet, cashflow, quarterly_cashflow.
- get_holder_info: Get holder information for a given ticker symbol from yahoo finance. You can choose from the following holder types: major_holders, institutional_holders, mutualfund_holders, insider_transactions, insider_purchases, insider_roster_holders.
- get_option_expiration_dates: Fetch the available options expiration dates for a given ticker symbol.
- get_option_chain: Fetch the option chain for a given ticker symbol, expiration date, and option type.
- get_recommendations: Get recommendations or upgrades/downgrades for a given ticker symbol from yahoo finance. You can also specify the number of months back to get upgrades/downgrades for, default is 12.
- get_fxmacrodata_catalogue: Get FXMacroData's supported macro indicators and endpoint coverage for a currency.
- get_fxmacrodata_calendar: Get macroeconomic release calendar rows for a currency.
- get_fxmacrodata_latest_announcements: Get the latest macroeconomic announcement rows for a currency.
""",
)


FXMACRODATA_BASE_URL = "https://api.fxmacrodata.com"


def _fxmacrodata_get(path: str, params: dict[str, str | None] | None = None) -> str:
    """Fetch a read-only FXMacroData endpoint and return the raw JSON response."""
    query_params = {key: value for key, value in (params or {}).items() if value}
    api_key = os.getenv("FXMD_API_KEY")
    if api_key:
        query_params["api_key"] = api_key

    query = urllib.parse.urlencode(query_params)
    url = f"{FXMACRODATA_BASE_URL}{path}"
    if query:
        url = f"{url}?{query}"

    try:
        with urllib.request.urlopen(url, timeout=30) as response:
            return response.read().decode("utf-8")
    except Exception as e:
        return f"Error: getting FXMacroData endpoint {path}: {e}"


@yfinance_server.tool(
    name="get_historical_stock_prices",
    description="""Get historical stock prices for a given ticker symbol from yahoo finance. Include the following information: Date, Open, High, Low, Close, Volume, Adj Close.
Args:
    ticker: str
        The ticker symbol of the stock to get historical prices for, e.g. "AAPL"
    period : str
        Valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
        Either Use period parameter or use start and end
        Default is "1mo"
    interval : str
        Valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
        Intraday data cannot extend last 60 days
        Default is "1d"
""",
)
async def get_historical_stock_prices(
    ticker: str, period: str = "1mo", interval: str = "1d"
) -> str:
    """Get historical stock prices for a given ticker symbol

    Args:
        ticker: str
            The ticker symbol of the stock to get historical prices for, e.g. "AAPL"
        period : str
            Valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
            Either Use period parameter or use start and end
            Default is "1mo"
        interval : str
            Valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
            Intraday data cannot extend last 60 days
            Default is "1d"
    """
    try:
        company = yf.Ticker(ticker)
        # Get the historical data directly (isin check is slow and unreliable)
        hist_data = company.history(period=period, interval=interval)
        hist_data = hist_data.reset_index(names="Date")
        hist_data = hist_data.to_json(orient="records", date_format="iso")
        return hist_data
    except Exception as e:
        print(f"Error: getting historical stock prices for {ticker}: {e}")
        return f"Error: getting historical stock prices for {ticker}: {e}"


@yfinance_server.tool(
    name="get_stock_info",
    description="""Get stock information for a given ticker symbol from yahoo finance. Include the following information:
Stock Price & Trading Info, Company Information, Financial Metrics, Earnings & Revenue, Margins & Returns, Dividends, Balance Sheet, Ownership, Analyst Coverage, Risk Metrics, Other.

Args:
    ticker: str
        The ticker symbol of the stock to get information for, e.g. "AAPL"
""",
)
async def get_stock_info(ticker: str) -> str:
    """Get stock information for a given ticker symbol"""
    try:
        company = yf.Ticker(ticker)
        # Get info directly (isin check is slow and unreliable)
        info = company.info
        # Check for fundamental properties that valid tickers should have
        if not info or 'symbol' not in info or 'quoteType' not in info:
            print(f"No stock info found for ticker {ticker}.")
            return f"No stock info found for ticker {ticker}."
        return json.dumps(info)
    except Exception as e:
        print(f"Error: getting stock information for {ticker}: {e}")
        return f"Error: getting stock information for {ticker}: {e}"


@yfinance_server.tool(
    name="get_yahoo_finance_news",
    description="""Get news for a given ticker symbol from yahoo finance.

Args:
    ticker: str
        The ticker symbol of the stock to get news for, e.g. "AAPL"
""",
)
async def get_yahoo_finance_news(ticker: str) -> str:
    """Get news for a given ticker symbol

    Args:
        ticker: str
            The ticker symbol of the stock to get news for, e.g. "AAPL"
    """
    try:
        company = yf.Ticker(ticker)
        # Get news directly (isin check is slow and unreliable)
        news_data = company.news
        if not news_data:
            print(f"No news found for ticker {ticker}.")
            return f"No news found for ticker {ticker}."

        news_list = []
        for news in news_data:
            if news.get("content", {}).get("contentType", "") == "STORY":
                title = news.get("content", {}).get("title", "")
                summary = news.get("content", {}).get("summary", "")
                description = news.get("content", {}).get("description", "")
                url = news.get("content", {}).get("canonicalUrl", {}).get("url", "")
                news_list.append(
                    f"Title: {title}\nSummary: {summary}\nDescription: {description}\nURL: {url}"
                )
        if not news_list:
            print(f"No news found for company that searched with {ticker} ticker.")
            return f"No news found for company that searched with {ticker} ticker."
        return "\n\n".join(news_list)
    except Exception as e:
        print(f"Error: getting news for {ticker}: {e}")
        return f"Error: getting news for {ticker}: {e}"


@yfinance_server.tool(
    name="get_stock_actions",
    description="""Get stock dividends and stock splits for a given ticker symbol from yahoo finance.

Args:
    ticker: str
        The ticker symbol of the stock to get stock actions for, e.g. "AAPL"
""",
)
async def get_stock_actions(ticker: str) -> str:
    """Get stock dividends and stock splits for a given ticker symbol"""
    try:
        company = yf.Ticker(ticker)
        actions_df = company.actions
        actions_df = actions_df.reset_index(names="Date")
        return actions_df.to_json(orient="records", date_format="iso")
    except Exception as e:
        print(f"Error: getting stock actions for {ticker}: {e}")
        return f"Error: getting stock actions for {ticker}: {e}"


@yfinance_server.tool(
    name="get_financial_statement",
    description="""Get financial statement for a given ticker symbol from yahoo finance. You can choose from the following financial statement types: income_stmt, quarterly_income_stmt, balance_sheet, quarterly_balance_sheet, cashflow, quarterly_cashflow.

Args:
    ticker: str
        The ticker symbol of the stock to get financial statement for, e.g. "AAPL"
    financial_type: str
        The type of financial statement to get. You can choose from the following financial statement types: income_stmt, quarterly_income_stmt, balance_sheet, quarterly_balance_sheet, cashflow, quarterly_cashflow.
""",
)
async def get_financial_statement(ticker: str, financial_type: str) -> str:
    """Get financial statement for a given ticker symbol"""
    try:
        company = yf.Ticker(ticker)
        # Get financial statement directly (isin check is slow and unreliable)
        if financial_type == FinancialType.income_stmt:
            financial_statement = company.income_stmt
        elif financial_type == FinancialType.quarterly_income_stmt:
            financial_statement = company.quarterly_income_stmt
        elif financial_type == FinancialType.balance_sheet:
            financial_statement = company.balance_sheet
        elif financial_type == FinancialType.quarterly_balance_sheet:
            financial_statement = company.quarterly_balance_sheet
        elif financial_type == FinancialType.cashflow:
            financial_statement = company.cashflow
        elif financial_type == FinancialType.quarterly_cashflow:
            financial_statement = company.quarterly_cashflow
        else:
            return f"Error: invalid financial type {financial_type}. Please use one of the following: {FinancialType.income_stmt}, {FinancialType.quarterly_income_stmt}, {FinancialType.balance_sheet}, {FinancialType.quarterly_balance_sheet}, {FinancialType.cashflow}, {FinancialType.quarterly_cashflow}."

        if financial_statement.empty:
            print(f"No financial statement data found for ticker {ticker}.")
            return f"No financial statement data found for ticker {ticker}."

        # Create a list to store all the json objects
        result = []

        # Loop through each column (date)
        for column in financial_statement.columns:
            if isinstance(column, pd.Timestamp):
                date_str = column.strftime("%Y-%m-%d")  # Format as YYYY-MM-DD
            else:
                date_str = str(column)

            # Create a dictionary for each date
            date_obj = {"date": date_str}

            # Add each metric as a key-value pair
            for index, value in financial_statement[column].items():
                # Add the value, handling NaN values
                date_obj[index] = None if pd.isna(value) else value

            result.append(date_obj)

        return json.dumps(result)
    except Exception as e:
        print(f"Error: getting financial statement for {ticker}: {e}")
        return f"Error: getting financial statement for {ticker}: {e}"


@yfinance_server.tool(
    name="get_holder_info",
    description="""Get holder information for a given ticker symbol from yahoo finance. You can choose from the following holder types: major_holders, institutional_holders, mutualfund_holders, insider_transactions, insider_purchases, insider_roster_holders.

Args:
    ticker: str
        The ticker symbol of the stock to get holder information for, e.g. "AAPL"
    holder_type: str
        The type of holder information to get. You can choose from the following holder types: major_holders, institutional_holders, mutualfund_holders, insider_transactions, insider_purchases, insider_roster_holders.
""",
)
async def get_holder_info(ticker: str, holder_type: str) -> str:
    """Get holder information for a given ticker symbol"""
    try:
        company = yf.Ticker(ticker)
        # Get holder info directly (isin check is slow and unreliable)
        if holder_type == HolderType.major_holders:
            return company.major_holders.reset_index(names="metric").to_json(orient="records")
        elif holder_type == HolderType.institutional_holders:
            return company.institutional_holders.to_json(orient="records")
        elif holder_type == HolderType.mutualfund_holders:
            return company.mutualfund_holders.to_json(orient="records", date_format="iso")
        elif holder_type == HolderType.insider_transactions:
            return company.insider_transactions.to_json(orient="records", date_format="iso")
        elif holder_type == HolderType.insider_purchases:
            return company.insider_purchases.to_json(orient="records", date_format="iso")
        elif holder_type == HolderType.insider_roster_holders:
            return company.insider_roster_holders.to_json(orient="records", date_format="iso")
        else:
            return f"Error: invalid holder type {holder_type}. Please use one of the following: {HolderType.major_holders}, {HolderType.institutional_holders}, {HolderType.mutualfund_holders}, {HolderType.insider_transactions}, {HolderType.insider_purchases}, {HolderType.insider_roster_holders}."
    except Exception as e:
        print(f"Error: getting holder info for {ticker}: {e}")
        return f"Error: getting holder info for {ticker}: {e}"


@yfinance_server.tool(
    name="get_option_expiration_dates",
    description="""Fetch the available options expiration dates for a given ticker symbol.

Args:
    ticker: str
        The ticker symbol of the stock to get option expiration dates for, e.g. "AAPL"
""",
)
async def get_option_expiration_dates(ticker: str) -> str:
    """Fetch the available options expiration dates for a given ticker symbol."""
    try:
        company = yf.Ticker(ticker)
        # Get options directly (isin check is slow and unreliable)
        options = company.options
        if not options:
            print(f"No options expiration dates found for ticker {ticker}.")
            return f"No options expiration dates found for ticker {ticker}."
        return json.dumps(options)
    except Exception as e:
        print(f"Error: getting option expiration dates for {ticker}: {e}")
        return f"Error: getting option expiration dates for {ticker}: {e}"


def _spot_price(company: yf.Ticker) -> float | None:
    """Resolve the current underlying price, or None when unavailable.

    Tries `fast_info` first (cheap, no full `.info` fetch) and falls back to the
    most recent daily close. Returns None rather than raising so an unresolvable
    spot degrades to "no strike filtering" instead of failing the request.
    """
    try:
        price = company.fast_info.get("lastPrice")
        if price is not None and float(price) > 0:
            return float(price)
    except Exception:
        pass

    try:
        hist = company.history(period="1d", interval="1d")
        if hist is not None and not hist.empty and "Close" in hist.columns:
            closes = hist["Close"].dropna()
            if len(closes) > 0 and float(closes.iloc[-1]) > 0:
                return float(closes.iloc[-1])
    except Exception:
        pass

    return None


def _window_strikes(
    company: yf.Ticker, chain: pd.DataFrame, strike_window_pct: float | None
) -> pd.DataFrame:
    """Restrict `chain` to strikes within +/- `strike_window_pct` of spot.

    Returns the chain unchanged when no window is requested, the window is not a
    positive number, spot cannot be resolved, or the window would select nothing
    — a caller asking for a narrower view must never receive an empty chain when
    a wider one exists.
    """
    if strike_window_pct is None or "strike" not in chain.columns:
        return chain

    try:
        window = float(strike_window_pct)
    except (TypeError, ValueError):
        return chain
    if window <= 0:
        return chain

    spot = _spot_price(company)
    if spot is None:
        return chain

    windowed = chain[
        (chain["strike"] >= spot * (1 - window))
        & (chain["strike"] <= spot * (1 + window))
    ]
    return windowed if not windowed.empty else chain


def _project_fields(chain: pd.DataFrame, fields: list[str] | None) -> pd.DataFrame:
    """Restrict `chain` to `fields`, always retaining `strike`.

    Projection is all-or-nothing: if *any* requested name is not a real column,
    the full chain is returned unchanged.

    A partial match is the dangerous case. Dropping just the unrecognized names
    yields a chain that parses as valid data while silently missing a column the
    caller asked for and believes it has — e.g. requesting
    ``["bid", "implied volatility"]`` would hand back bids with no volatility at
    all. Returning everything is wasteful but never wrong, and the caller can
    see its projection did not apply.
    """
    if not fields:
        return chain

    available = set(chain.columns)
    if any(field not in available for field in fields):
        return chain

    keep = [column for column in chain.columns if column in set(fields)]
    if "strike" in chain.columns and "strike" not in keep:
        keep.insert(0, "strike")
    return chain[keep]


@yfinance_server.tool(
    name="get_option_chain",
    description="""Fetch the option chain for a given ticker symbol, expiration date, and option type.

A full chain is large (a liquid US name runs 40-90 strikes and ~17KB of JSON per
expiration). Prefer `strike_window_pct` and `fields` to request only the strikes
and columns you actually need — pulling several full chains into one analysis is
the main driver of oversized requests.

Args:
    ticker: str
        The ticker symbol of the stock to get option chain for, e.g. "AAPL"
    expiration_date: str
        The expiration date for the options chain (format: 'YYYY-MM-DD')
    option_type: str
        The type of option to fetch ('calls' or 'puts')
    strike_window_pct: float | None
        Keep only strikes within +/- this fraction of the current spot price
        (e.g. 0.15 keeps strikes from 85% to 115% of spot). Omit for every strike.
    fields: list[str] | None
        Only return these columns. `strike` is always included. Omit for every column.
        Names must match these columns EXACTLY (they are case-sensitive, and none
        contain spaces or underscores):
            contractSymbol, lastTradeDate, strike, lastPrice, bid, ask, change,
            percentChange, volume, openInterest, impliedVolatility, inTheMoney,
            contractSize, currency
        Note "lastPrice" (not "last"), "impliedVolatility" (not "implied volatility"),
        "openInterest" (not "open interest"). If ANY name is not in that list the
        projection is dropped and the full chain is returned, so a typo costs
        payload rather than silently omitting a column you asked for.
        A good pricing set: ["strike", "bid", "ask", "lastPrice",
        "impliedVolatility", "openInterest", "volume"].
""",
)
async def get_option_chain(
    ticker: str,
    expiration_date: str,
    option_type: str,
    strike_window_pct: float | None = None,
    fields: list[str] | None = None,
) -> str:
    """Fetch the option chain for a given ticker symbol, expiration date, and option type.

    Args:
        ticker: The ticker symbol of the stock
        expiration_date: The expiration date for the options chain (format: 'YYYY-MM-DD')
        option_type: The type of option to fetch ('calls' or 'puts')
        strike_window_pct: Keep only strikes within +/- this fraction of spot.
            None returns every strike (the historical behavior).
        fields: Only return these columns, matched exactly against the chain's
            own column names. None returns every column (the historical
            behavior). `strike` is always retained so rows stay identifiable.
            If any name is unrecognized the projection is dropped entirely —
            see :func:`_project_fields`.

    Returns:
        str: JSON string containing the option chain data
    """
    try:
        company = yf.Ticker(ticker)
        # Get options directly (isin check is slow and unreliable)

        # Check if the expiration date is valid
        if expiration_date not in company.options:
            return f"Error: No options available for the date {expiration_date}. You can use `get_option_expiration_dates` to get the available expiration dates."

        # Check if the option type is valid
        if option_type not in ["calls", "puts"]:
            return "Error: Invalid option type. Please use 'calls' or 'puts'."

        # Get the option chain
        option_chain = company.option_chain(expiration_date)
        chain = option_chain.calls if option_type == "calls" else option_chain.puts

        chain = _window_strikes(company, chain, strike_window_pct)
        chain = _project_fields(chain, fields)

        return chain.to_json(orient="records", date_format="iso")
    except Exception as e:
        print(f"Error: getting option chain for {ticker}: {e}")
        return f"Error: getting option chain for {ticker}: {e}"


@yfinance_server.tool(
    name="get_recommendations",
    description="""Get recommendations or upgrades/downgrades for a given ticker symbol from yahoo finance. You can also specify the number of months back to get upgrades/downgrades for, default is 12.

Args:
    ticker: str
        The ticker symbol of the stock to get recommendations for, e.g. "AAPL"
    recommendation_type: str
        The type of recommendation to get. You can choose from the following recommendation types: recommendations, upgrades_downgrades.
    months_back: int
        The number of months back to get upgrades/downgrades for, default is 12.
""",
)
async def get_recommendations(ticker: str, recommendation_type: str, months_back: int = 12) -> str:
    """Get recommendations or upgrades/downgrades for a given ticker symbol"""
    try:
        company = yf.Ticker(ticker)
        # Get recommendations directly (isin check is slow and unreliable)
        if recommendation_type == RecommendationType.recommendations:
            recommendations = company.recommendations  # type: ignore
            if recommendations.empty:  # type: ignore
                return "[]"
            return recommendations.to_json(orient="records")  # type: ignore
        elif recommendation_type == RecommendationType.upgrades_downgrades:
            # Get the upgrades/downgrades based on the cutoff date
            upgrades_downgrades = company.upgrades_downgrades  # type: ignore
            if upgrades_downgrades.empty:  # type: ignore
                return "[]"
            upgrades_downgrades = upgrades_downgrades.reset_index()  # type: ignore
            cutoff_date = pd.Timestamp.now() - pd.DateOffset(months=months_back)
            upgrades_downgrades = upgrades_downgrades[
                upgrades_downgrades["GradeDate"] >= cutoff_date
            ]
            upgrades_downgrades = upgrades_downgrades.sort_values("GradeDate", ascending=False)
            # Get the first occurrence (most recent) for each firm
            latest_by_firm = upgrades_downgrades.drop_duplicates(subset=["Firm"])
            return latest_by_firm.to_json(orient="records", date_format="iso")
        else:
            return f"Error: invalid recommendation type {recommendation_type}. Please use one of the following: {RecommendationType.recommendations}, {RecommendationType.upgrades_downgrades}."
    except Exception as e:
        print(f"Error: getting recommendations for {ticker}: {e}")
        return f"Error: getting recommendations for {ticker}: {e}"


@yfinance_server.tool(
    name="get_fxmacrodata_catalogue",
    description="""Get FXMacroData's supported macro indicators and endpoint coverage for a currency.

Args:
    currency: str
        Three-letter currency code such as "usd", "jpy", "eur", "gbp", or "aud".
        Defaults to "usd".
""",
)
async def get_fxmacrodata_catalogue(currency: str = "usd") -> str:
    """Get FXMacroData's supported macro indicators and endpoint coverage."""
    return _fxmacrodata_get(f"/v1/data_catalogue/{currency.lower()}")


@yfinance_server.tool(
    name="get_fxmacrodata_calendar",
    description="""Get macroeconomic release calendar rows from FXMacroData.

Args:
    currency: str
        Three-letter currency code such as "usd", "jpy", "eur", "gbp", or "aud".
        Defaults to "usd".
    start_date: str
        Optional start date in YYYY-MM-DD format.
    end_date: str
        Optional end date in YYYY-MM-DD format.
""",
)
async def get_fxmacrodata_calendar(
    currency: str = "usd", start_date: str | None = None, end_date: str | None = None
) -> str:
    """Get macroeconomic release calendar rows from FXMacroData."""
    return _fxmacrodata_get(
        f"/v1/calendar/{currency.lower()}",
        {"start_date": start_date, "end_date": end_date},
    )


@yfinance_server.tool(
    name="get_fxmacrodata_latest_announcements",
    description="""Get the latest macroeconomic announcements from FXMacroData.

Args:
    currency: str
        Three-letter currency code such as "usd", "jpy", "eur", "gbp", or "aud".
        Defaults to "usd".
""",
)
async def get_fxmacrodata_latest_announcements(currency: str = "usd") -> str:
    """Get the latest macroeconomic announcement rows from FXMacroData."""
    return _fxmacrodata_get(f"/v1/announcements/{currency.lower()}/latest")


def main() -> None:
    # Initialize and run the server
    print("Starting Yahoo Finance MCP server...")
    yfinance_server.run(transport="stdio")


if __name__ == "__main__":
    main()
