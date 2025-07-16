import json
import pytest

# Define your expected behavior
EVAL_CASES = [
    {
        "query": "plot_price coin=ETH days=5",
        "expected_tool": "plot_price",
        "expected_params": {"coin": "ETH", "days": 5},
    },
    {
        "query": "get_top_movers period=1d limit=3",
        "expected_tool": "get_top_movers",
        "expected_params": {"period": "1d", "limit": 3},
    },
    # add more cases...
]

@pytest.mark.parametrize("case", EVAL_CASES)
def test_tool_calls(case, tmp_path):
    # 1. Clear or recreate agent.log
    log_file = tmp_path / "agent.log"
    # 2. Run the query via ask()
    from app.agents.insight_agent import ask
    ask(case["query"])
    # 3. Read last line of log
    entry = json.loads(log_file.read_text().splitlines()[-1])
    assert entry["tool_call"]["function"] == case["expected_tool"]
    assert entry["tool_call"]["parameters"] == case["expected_params"]
