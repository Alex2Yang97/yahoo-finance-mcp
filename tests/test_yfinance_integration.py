import json
import pytest
from server import (
    get_historical_stock_prices,
    get_stock_info,
    get_financial_statement,
    get_holder_info,
    get_recommendations,
    get_yahoo_finance_news,
    get_stock_actions,
    get_option_expiration_dates,
    get_option_chain,
)

# Use a stable ticker for testing
TEST_TICKER = "AAPL"
# Use an invalid ticker for error case testing
INVALID_TICKER = "INVALIDTICKER123XYZ"


# =============================================================================
# get_historical_stock_prices tests
# =============================================================================


@pytest.mark.asyncio
async def test_get_historical_stock_prices():
    """Test fetching historical stock prices with explicit params."""
    result = await get_historical_stock_prices(TEST_TICKER, period="5d", interval="1d")

    # Verify result is a string (JSON)
    assert isinstance(result, str)

    # Parse JSON and verify structure
    data = json.loads(result)
    assert isinstance(data, list)
    assert len(data) > 0

    # Check for expected columns from yfinance history()
    first_row = data[0]
    expected_cols = ["Date", "Open", "High", "Low", "Close", "Volume"]
    for col in expected_cols:
        assert col in first_row, f"Missing expected column: {col}"


@pytest.mark.asyncio
async def test_get_historical_stock_prices_default_params():
    """Test fetching historical stock prices with default parameters (period=1mo, interval=1d)."""
    result = await get_historical_stock_prices(TEST_TICKER)

    assert isinstance(result, str)
    data = json.loads(result)
    assert isinstance(data, list)
    # Default period is 1mo, should have multiple data points
    assert len(data) > 0


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "period,interval",
    [
        ("1d", "1m"),
        ("5d", "5m"),
        ("1mo", "1h"),
        ("3mo", "1d"),
        ("1y", "1wk"),
    ],
)
async def test_get_historical_stock_prices_various_periods(period, interval):
    """Test fetching historical stock prices with various period/interval combinations."""
    result = await get_historical_stock_prices(TEST_TICKER, period=period, interval=interval)

    assert isinstance(result, str)
    # Should return valid JSON (either data or empty list)
    data = json.loads(result)
    assert isinstance(data, list)


# =============================================================================
# get_stock_info tests
# =============================================================================


@pytest.mark.asyncio
async def test_get_stock_info():
    """Test fetching stock information."""
    result = await get_stock_info(TEST_TICKER)

    assert isinstance(result, str)
    assert "No stock info found" not in result
    assert "Error" not in result

    data = json.loads(result)
    assert isinstance(data, dict)

    # Check for critical keys that server validates
    assert "symbol" in data
    assert data["symbol"] == TEST_TICKER
    assert "quoteType" in data  # Server checks for this
    assert "currentPrice" in data or "regularMarketPrice" in data


@pytest.mark.asyncio
async def test_get_stock_info_invalid_ticker():
    """Test fetching stock info for an invalid ticker."""
    result = await get_stock_info(INVALID_TICKER)

    assert isinstance(result, str)
    # Server returns this exact message when symbol/quoteType missing
    assert "No stock info found" in result or "Error" in result


# =============================================================================
# get_financial_statement tests
# Using string inputs to match MCP client behavior (not Python enums)
# =============================================================================


@pytest.mark.asyncio
async def test_get_financial_statement_income_stmt():
    """Test fetching income statement using string input (MCP client behavior)."""
    result = await get_financial_statement(TEST_TICKER, "income_stmt")

    assert isinstance(result, str)
    assert "Error" not in result

    data = json.loads(result)
    assert isinstance(data, list)
    assert len(data) > 0
    # Each entry should have 'date' and financial metrics
    assert "date" in data[0]
    # Check for common income statement metrics
    first_entry_keys = set(data[0].keys())
    assert "date" in first_entry_keys
    # Should have more than just 'date' - actual financial data
    assert len(first_entry_keys) > 1


@pytest.mark.asyncio
async def test_get_financial_statement_quarterly_income_stmt():
    """Test fetching quarterly income statement."""
    result = await get_financial_statement(TEST_TICKER, "quarterly_income_stmt")

    assert isinstance(result, str)
    assert "Error" not in result

    data = json.loads(result)
    assert isinstance(data, list)
    assert len(data) > 0
    assert "date" in data[0]


@pytest.mark.asyncio
async def test_get_financial_statement_balance_sheet():
    """Test fetching balance sheet."""
    result = await get_financial_statement(TEST_TICKER, "balance_sheet")

    assert isinstance(result, str)
    assert "Error" not in result

    data = json.loads(result)
    assert isinstance(data, list)
    assert len(data) > 0
    assert "date" in data[0]


@pytest.mark.asyncio
async def test_get_financial_statement_quarterly_balance_sheet():
    """Test fetching quarterly balance sheet."""
    result = await get_financial_statement(TEST_TICKER, "quarterly_balance_sheet")

    assert isinstance(result, str)
    assert "Error" not in result

    data = json.loads(result)
    assert isinstance(data, list)
    assert len(data) > 0
    assert "date" in data[0]


@pytest.mark.asyncio
async def test_get_financial_statement_cashflow():
    """Test fetching cash flow statement."""
    result = await get_financial_statement(TEST_TICKER, "cashflow")

    assert isinstance(result, str)
    assert "Error" not in result

    data = json.loads(result)
    assert isinstance(data, list)
    assert len(data) > 0
    assert "date" in data[0]


@pytest.mark.asyncio
async def test_get_financial_statement_quarterly_cashflow():
    """Test fetching quarterly cash flow statement."""
    result = await get_financial_statement(TEST_TICKER, "quarterly_cashflow")

    assert isinstance(result, str)
    assert "Error" not in result

    data = json.loads(result)
    assert isinstance(data, list)
    assert len(data) > 0
    assert "date" in data[0]


@pytest.mark.asyncio
async def test_get_financial_statement_invalid_type():
    """Test fetching financial statement with invalid type."""
    error_result = await get_financial_statement(TEST_TICKER, "invalid_type")
    # Server returns: "Error: invalid financial type {type}. Please use one of the following: ..."
    assert "Error: invalid financial type" in error_result
    assert "invalid_type" in error_result


# =============================================================================
# get_holder_info tests
# Using string inputs to match MCP client behavior
# =============================================================================


@pytest.mark.asyncio
async def test_get_holder_info_major_holders():
    """Test fetching major holders information."""
    result = await get_holder_info(TEST_TICKER, "major_holders")

    assert isinstance(result, str)
    data = json.loads(result)
    assert isinstance(data, list)
    # major_holders uses reset_index(names="metric") so should have 'metric' column
    if len(data) > 0:
        assert "metric" in data[0], "major_holders should have 'metric' column from reset_index"


@pytest.mark.asyncio
async def test_get_holder_info_institutional_holders():
    """Test fetching institutional holders information."""
    result = await get_holder_info(TEST_TICKER, "institutional_holders")

    assert isinstance(result, str)
    data = json.loads(result)
    assert isinstance(data, list)
    # Should have holder data
    if len(data) > 0:
        assert "Holder" in data[0] or "holder" in str(data[0].keys()).lower()


@pytest.mark.asyncio
async def test_get_holder_info_mutualfund_holders():
    """Test fetching mutual fund holders information."""
    result = await get_holder_info(TEST_TICKER, "mutualfund_holders")

    assert isinstance(result, str)
    data = json.loads(result)
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_get_holder_info_insider_transactions():
    """Test fetching insider transactions information."""
    result = await get_holder_info(TEST_TICKER, "insider_transactions")

    assert isinstance(result, str)
    data = json.loads(result)
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_get_holder_info_insider_purchases():
    """Test fetching insider purchases information."""
    result = await get_holder_info(TEST_TICKER, "insider_purchases")

    assert isinstance(result, str)
    data = json.loads(result)
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_get_holder_info_insider_roster_holders():
    """Test fetching insider roster holders information."""
    result = await get_holder_info(TEST_TICKER, "insider_roster_holders")

    assert isinstance(result, str)
    data = json.loads(result)
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_get_holder_info_invalid_type():
    """Test fetching holder info with invalid type."""
    error_result = await get_holder_info(TEST_TICKER, "invalid_type")
    # Server returns: "Error: invalid holder type {type}. Please use one of the following: ..."
    assert "Error: invalid holder type" in error_result
    assert "invalid_type" in error_result


# =============================================================================
# get_recommendations tests
# Using string inputs to match MCP client behavior
# =============================================================================


@pytest.mark.asyncio
async def test_get_recommendations():
    """Test fetching analyst recommendations."""
    result = await get_recommendations(TEST_TICKER, "recommendations")
    assert isinstance(result, str)
    # Result can be "[]" if no data, which is valid JSON
    data = json.loads(result)
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_get_recommendations_upgrades_downgrades():
    """Test fetching upgrades/downgrades with output structure validation."""
    result = await get_recommendations(TEST_TICKER, "upgrades_downgrades")
    assert isinstance(result, str)
    data = json.loads(result)
    assert isinstance(data, list)

    # If data exists, validate expected columns from server code
    if len(data) > 0:
        first_entry = data[0]
        # Server uses reset_index() which adds GradeDate, and filters/sorts by GradeDate
        assert "GradeDate" in first_entry, "upgrades_downgrades should have 'GradeDate' column"
        assert "Firm" in first_entry, "upgrades_downgrades should have 'Firm' column"


@pytest.mark.asyncio
async def test_get_recommendations_with_months_back():
    """Test fetching upgrades/downgrades with custom months_back parameter."""
    # Test with 6 months back
    result_6m = await get_recommendations(TEST_TICKER, "upgrades_downgrades", months_back=6)
    assert isinstance(result_6m, str)
    data_6m = json.loads(result_6m)
    assert isinstance(data_6m, list)

    # Test with 24 months back
    result_24m = await get_recommendations(TEST_TICKER, "upgrades_downgrades", months_back=24)
    assert isinstance(result_24m, str)
    data_24m = json.loads(result_24m)
    assert isinstance(data_24m, list)


@pytest.mark.asyncio
async def test_get_recommendations_invalid_type():
    """Test fetching recommendations with invalid type."""
    error_result = await get_recommendations(TEST_TICKER, "invalid_type")
    # Server returns: "Error: invalid recommendation type {type}. Please use one of the following: ..."
    assert "Error: invalid recommendation type" in error_result
    assert "invalid_type" in error_result


# =============================================================================
# get_yahoo_finance_news tests
# =============================================================================


@pytest.mark.asyncio
async def test_get_yahoo_finance_news():
    """Test fetching news returns formatted text (not JSON)."""
    result = await get_yahoo_finance_news(TEST_TICKER)
    assert isinstance(result, str)
    assert len(result) > 0

    # News is returned as formatted text, not JSON
    # Server formats as: "Title: {title}\nSummary: {summary}\nDescription: {description}\nURL: {url}"
    if "No news found" not in result:
        assert "Title:" in result


@pytest.mark.asyncio
async def test_get_yahoo_finance_news_structure():
    """Test that news output contains expected formatted structure."""
    result = await get_yahoo_finance_news(TEST_TICKER)
    assert isinstance(result, str)

    # Check for expected fields in the formatted output
    if "No news found" not in result:
        assert "Title:" in result
        assert "Summary:" in result
        assert "Description:" in result
        assert "URL:" in result


# =============================================================================
# get_stock_actions tests
# =============================================================================


@pytest.mark.asyncio
async def test_get_stock_actions():
    """Test fetching stock actions (dividends/splits)."""
    result = await get_stock_actions(TEST_TICKER)
    assert isinstance(result, str)
    data = json.loads(result)
    assert isinstance(data, list)

    # Server uses reset_index(names="Date") so Date column should exist
    if len(data) > 0:
        assert "Date" in data[0]


@pytest.mark.asyncio
async def test_get_stock_actions_columns():
    """Test that stock actions has expected columns (Dividends, Stock Splits)."""
    result = await get_stock_actions(TEST_TICKER)
    data = json.loads(result)

    # AAPL has dividend history
    assert len(data) > 0
    first_row = data[0]
    # yfinance actions DataFrame has these columns
    assert "Dividends" in first_row or "Stock Splits" in first_row


# =============================================================================
# get_option_expiration_dates tests
# =============================================================================


@pytest.mark.asyncio
async def test_get_option_expiration_dates():
    """Test fetching option expiration dates."""
    result = await get_option_expiration_dates(TEST_TICKER)
    assert isinstance(result, str)

    # Should not be an error message
    assert "No options expiration dates found" not in result
    assert "Error" not in result

    data = json.loads(result)
    assert isinstance(data, list)
    assert len(data) > 0
    # Dates should be strings
    assert isinstance(data[0], str)


@pytest.mark.asyncio
async def test_get_option_expiration_dates_format():
    """Test that option expiration dates are in YYYY-MM-DD format."""
    result = await get_option_expiration_dates(TEST_TICKER)
    data = json.loads(result)

    assert len(data) > 0
    # Dates should be in YYYY-MM-DD format
    first_date = data[0]
    assert len(first_date) == 10
    assert first_date[4] == "-"
    assert first_date[7] == "-"


# =============================================================================
# get_option_chain tests
# =============================================================================


@pytest.mark.asyncio
async def test_get_option_chain_calls():
    """Test fetching option chain for calls."""
    # First get valid expiration dates
    exp_dates_result = await get_option_expiration_dates(TEST_TICKER)
    exp_dates = json.loads(exp_dates_result)
    assert len(exp_dates) > 0

    # Use the first available expiration date
    expiration_date = exp_dates[0]

    result = await get_option_chain(TEST_TICKER, expiration_date, "calls")
    assert isinstance(result, str)
    assert "Error" not in result

    data = json.loads(result)
    assert isinstance(data, list)
    assert len(data) > 0

    # Check for expected option chain columns from yfinance
    first_row = data[0]
    expected_cols = ["strike", "lastPrice", "bid", "ask", "volume", "openInterest"]
    for col in expected_cols:
        assert col in first_row, f"Missing expected column: {col}"


@pytest.mark.asyncio
async def test_get_option_chain_puts():
    """Test fetching option chain for puts."""
    # First get valid expiration dates
    exp_dates_result = await get_option_expiration_dates(TEST_TICKER)
    exp_dates = json.loads(exp_dates_result)
    assert len(exp_dates) > 0

    # Use the first available expiration date
    expiration_date = exp_dates[0]

    result = await get_option_chain(TEST_TICKER, expiration_date, "puts")
    assert isinstance(result, str)
    assert "Error" not in result

    data = json.loads(result)
    assert isinstance(data, list)
    assert len(data) > 0

    # Check for expected option chain columns from yfinance
    first_row = data[0]
    expected_cols = ["strike", "lastPrice", "bid", "ask", "volume", "openInterest"]
    for col in expected_cols:
        assert col in first_row, f"Missing expected column: {col}"


@pytest.mark.asyncio
async def test_get_option_chain_invalid_option_type():
    """Test fetching option chain with invalid option type."""
    # First get valid expiration dates
    exp_dates_result = await get_option_expiration_dates(TEST_TICKER)
    exp_dates = json.loads(exp_dates_result)
    expiration_date = exp_dates[0]

    result = await get_option_chain(TEST_TICKER, expiration_date, "invalid_type")
    # Server returns: "Error: Invalid option type. Please use 'calls' or 'puts'."
    assert "Error" in result
    assert "Invalid option type" in result


@pytest.mark.asyncio
async def test_get_option_chain_invalid_expiration_date():
    """Test fetching option chain with invalid expiration date."""
    result = await get_option_chain(TEST_TICKER, "1999-01-01", "calls")
    # Server returns: "Error: No options available for the date {date}..."
    assert "Error" in result
    assert "No options available" in result


# =============================================================================
# get_option_chain payload-reduction tests (strike_window_pct / fields)
# =============================================================================


@pytest.mark.asyncio
async def test_get_option_chain_strike_window_shrinks_payload():
    """A strike window returns a strict subset of the full chain."""
    exp_dates = json.loads(await get_option_expiration_dates(TEST_TICKER))
    expiration_date = exp_dates[0]

    full = json.loads(await get_option_chain(TEST_TICKER, expiration_date, "calls"))
    windowed = json.loads(
        await get_option_chain(
            TEST_TICKER, expiration_date, "calls", strike_window_pct=0.15
        )
    )

    assert 0 < len(windowed) <= len(full)
    full_strikes = {row["strike"] for row in full}
    assert {row["strike"] for row in windowed} <= full_strikes


@pytest.mark.asyncio
async def test_get_option_chain_fields_projects_columns():
    """`fields` restricts columns and always retains `strike`."""
    exp_dates = json.loads(await get_option_expiration_dates(TEST_TICKER))
    expiration_date = exp_dates[0]

    result = json.loads(
        await get_option_chain(
            TEST_TICKER, expiration_date, "calls", fields=["bid", "ask"]
        )
    )
    assert len(result) > 0
    assert set(result[0].keys()) == {"strike", "bid", "ask"}


@pytest.mark.asyncio
async def test_get_option_chain_partial_field_typo_keeps_every_column():
    """A partially misspelled `fields` list must not silently drop columns.

    Keeping only the names that happened to match returns a chain that parses as
    valid data while missing a column the caller asked for and believes it has.
    Requesting bid + implied volatility with the natural-language spelling must
    never yield bids with no volatility.
    """
    exp_dates = json.loads(await get_option_expiration_dates(TEST_TICKER))
    expiration_date = exp_dates[0]

    full = json.loads(await get_option_chain(TEST_TICKER, expiration_date, "calls"))
    partial_typo = json.loads(
        await get_option_chain(
            TEST_TICKER,
            expiration_date,
            "calls",
            # "implied volatility" is not a column; "impliedVolatility" is.
            fields=["bid", "implied volatility"],
        )
    )

    assert partial_typo == full
    assert "impliedVolatility" in partial_typo[0]


@pytest.mark.asyncio
async def test_get_option_chain_documented_pricing_fields_all_resolve():
    """Every column name the docs and prompts hand out must really exist.

    If one of these drifts, the all-or-nothing projection silently degrades to
    the full chain on every call and the payload reduction quietly stops working.
    """
    exp_dates = json.loads(await get_option_expiration_dates(TEST_TICKER))
    expiration_date = exp_dates[0]

    pricing_fields = [
        "strike",
        "bid",
        "ask",
        "lastPrice",
        "impliedVolatility",
        "openInterest",
        "volume",
    ]
    result = json.loads(
        await get_option_chain(
            TEST_TICKER, expiration_date, "calls", fields=pricing_fields
        )
    )
    assert set(result[0].keys()) == set(pricing_fields)


@pytest.mark.asyncio
async def test_get_option_chain_defaults_are_unchanged():
    """Omitting both new args reproduces the historical full-chain response."""
    exp_dates = json.loads(await get_option_expiration_dates(TEST_TICKER))
    expiration_date = exp_dates[0]

    default = json.loads(await get_option_chain(TEST_TICKER, expiration_date, "calls"))
    explicit_none = json.loads(
        await get_option_chain(
            TEST_TICKER, expiration_date, "calls", strike_window_pct=None, fields=None
        )
    )
    assert default == explicit_none
    for col in ["strike", "lastPrice", "bid", "ask", "volume", "openInterest"]:
        assert col in default[0]


@pytest.mark.asyncio
async def test_get_option_chain_unusable_filters_degrade_to_full_chain():
    """Filters that would yield unusable data fall back to the full chain."""
    exp_dates = json.loads(await get_option_expiration_dates(TEST_TICKER))
    expiration_date = exp_dates[0]

    full = json.loads(await get_option_chain(TEST_TICKER, expiration_date, "calls"))

    # No requested field exists -> a strike-only chain would look valid but be
    # unusable, so the full chain is returned instead.
    all_unknown = json.loads(
        await get_option_chain(
            TEST_TICKER, expiration_date, "calls", fields=["not_a_column"]
        )
    )
    assert all_unknown == full

    # A window so narrow it selects nothing must not return an empty chain.
    empty_window = json.loads(
        await get_option_chain(
            TEST_TICKER, expiration_date, "calls", strike_window_pct=0.0001
        )
    )
    assert len(empty_window) == len(full)

    # A non-positive window is treated as "no filtering".
    zero_window = json.loads(
        await get_option_chain(
            TEST_TICKER, expiration_date, "calls", strike_window_pct=0
        )
    )
    assert len(zero_window) == len(full)
