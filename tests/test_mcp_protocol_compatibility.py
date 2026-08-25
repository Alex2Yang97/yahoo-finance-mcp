import asyncio
import json
import sys
from pathlib import Path

import pytest

REPOSITORY_ROOT = Path(__file__).parent.parent
LEGACY_PROTOCOL_VERSION = "2024-11-05"

EXPECTED_TOOL_SCHEMAS = {
    "get_historical_stock_prices": {
        "required": ["ticker"],
        "properties": ["ticker", "period", "interval"],
        "defaults": {"period": "1mo", "interval": "1d"},
    },
    "get_stock_info": {"required": ["ticker"], "properties": ["ticker"]},
    "get_yahoo_finance_news": {"required": ["ticker"], "properties": ["ticker"]},
    "get_stock_actions": {"required": ["ticker"], "properties": ["ticker"]},
    "get_financial_statement": {
        "required": ["ticker", "financial_type"],
        "properties": ["ticker", "financial_type"],
    },
    "get_holder_info": {
        "required": ["ticker", "holder_type"],
        "properties": ["ticker", "holder_type"],
    },
    "get_option_expiration_dates": {
        "required": ["ticker"],
        "properties": ["ticker"],
    },
    "get_option_chain": {
        "required": ["ticker", "expiration_date", "option_type"],
        "properties": [
            "ticker",
            "expiration_date",
            "option_type",
            "strike_window_pct",
            "fields",
        ],
    },
    "get_recommendations": {
        "required": ["ticker", "recommendation_type"],
        "properties": ["ticker", "recommendation_type", "months_back"],
        "defaults": {"months_back": 12},
    },
}


async def _read_json_line(process: asyncio.subprocess.Process) -> dict:
    line = await asyncio.wait_for(process.stdout.readline(), timeout=10)
    assert line, "MCP server closed stdout before returning a response"
    return json.loads(line)


async def _send_json_line(process: asyncio.subprocess.Process, message: dict) -> None:
    process.stdin.write((json.dumps(message) + "\n").encode())
    await process.stdin.drain()


@pytest.mark.asyncio
async def test_stdio_preserves_legacy_initialize_and_tool_schemas():
    process = await asyncio.create_subprocess_exec(
        sys.executable,
        str(REPOSITORY_ROOT / "server.py"),
        cwd=REPOSITORY_ROOT,
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    try:
        await _send_json_line(
            process,
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": LEGACY_PROTOCOL_VERSION,
                    "capabilities": {},
                    "clientInfo": {"name": "compatibility-test", "version": "1"},
                },
            },
        )
        initialize_response = await _read_json_line(process)
        initialize_result = initialize_response["result"]

        assert initialize_response["id"] == 1
        assert initialize_result["protocolVersion"] == LEGACY_PROTOCOL_VERSION
        assert initialize_result["serverInfo"]["name"] == "yfinance"

        await _send_json_line(
            process,
            {"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}},
        )
        await _send_json_line(
            process,
            {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}},
        )
        tools_response = await _read_json_line(process)
        tools = {tool["name"]: tool for tool in tools_response["result"]["tools"]}

        assert tools_response["id"] == 2
        assert set(tools) == set(EXPECTED_TOOL_SCHEMAS)

        for tool_name, expected in EXPECTED_TOOL_SCHEMAS.items():
            schema = tools[tool_name]["inputSchema"]
            assert schema["required"] == expected["required"]
            assert set(schema["properties"]) == set(expected["properties"])
            for property_name, default in expected.get("defaults", {}).items():
                assert schema["properties"][property_name]["default"] == default

        await _send_json_line(
            process,
            {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {
                    "name": "get_recommendations",
                    "arguments": {"ticker": "AAPL", "recommendation_type": "invalid_type"},
                },
            },
        )
        call_response = await _read_json_line(process)
        call_text = call_response["result"]["content"][0]["text"]

        assert call_response["id"] == 3
        assert "Error: invalid recommendation type" in call_text
        assert "invalid_type" in call_text
    finally:
        process.stdin.close()
        await process.stdin.wait_closed()
        try:
            await asyncio.wait_for(process.wait(), timeout=5)
        except asyncio.TimeoutError:
            process.kill()
            await process.wait()

    assert process.returncode == 0
