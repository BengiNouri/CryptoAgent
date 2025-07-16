# app/prompts/insight_prompt.py
import pathlib
INSIGHT_PROMPT = pathlib.Path(__file__).parent / "insight_prompt.txt"
INSIGHT_PROMPT = INSIGHT_PROMPT.read_text(encoding="utf8")
