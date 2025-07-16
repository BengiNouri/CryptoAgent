import os
import json
import logging
from typing import Any, Union

from langchain_openai import ChatOpenAI
from app.context.embedding import get_retriever
from app.agents.schema import ALLOWED_FUNCTIONS
from .tools import get_top_movers, plot_price
from app.prompts.insight_prompt import INSIGHT_PROMPT as SYSTEM_PROMPT

# Initialize the LLM client
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

def _parse_call(raw: str) -> Union[dict[str, Any], None]:
    try:
        data = json.loads(raw)
        fn = data["function"]
        args = data["parameters"]
        # Validate against allowed functions and their schemas
        if fn not in ALLOWED_FUNCTIONS:
            return None
        schema = ALLOWED_FUNCTIONS[fn]
        for k, typ in schema.__annotations__.items():
            if k not in args:
                raise ValueError(f"Missing parameter '{k}' for function '{fn}'")
            if typ == int and not isinstance(args[k], int):
                raise TypeError(f"Parameter '{k}' expected int, got {type(args[k]).__name__}")
        return data
    except Exception:
        return None


def ask(question: str) -> Union[dict[str, Any], str]:
    # ─── 1. Logging setup ──────────────────────────────────────────────────────────
    logger = logging.getLogger("crypto_agent")
    for h in logger.handlers[:]:
        logger.removeHandler(h)
    log_path = os.path.join(os.getcwd(), "agent.log")
    fh = logging.FileHandler(log_path, encoding="utf8")
    fh.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(fh)
    logger.setLevel(logging.INFO)

    # ─── 2. Retrieve context ───────────────────────────────────────────────────────
    retriever = get_retriever(k=4)
    docs = retriever.get_relevant_documents(question)
    rag_block = "\n\n".join(f"- {d.page_content}" for d in docs)

    # ─── 3. Build & call LLM ──────────────────────────────────────────────────────
    prompt = (
        SYSTEM_PROMPT
        + f"\n\n---\nContext (top {len(docs)} snippets):\n{rag_block}\n\n"
        + f"User: {question}"
    )
    resp = llm.invoke(prompt).content.strip()
    call = _parse_call(resp)

    # ─── 4. Emit JSON‐line ─────────────────────────────────────────────────────────
    log_entry = {
        "query": question,
        "context_count": len(docs),
        "prompt": prompt,
        "response": resp,
        "tool_call": call,
    }
    logger.info(json.dumps(log_entry))

    # Clean up handler
    logger.removeHandler(fh)
    fh.close()

    # ─── 5. Dispatch (return spec instead of executing) ────────────────────────────
    if call:
        return call

    # No function call parsed: return raw assistant response
    return resp
