import os
import json
import logging
from typing import Any, Union

from langchain_openai import ChatOpenAI
from app.context.embedding import get_retriever
from app.agents.schema import ALLOWED_FUNCTIONS
from .tools import get_top_movers, plot_price, forecast_price
from app.prompts.insight_prompt import INSIGHT_PROMPT as SYSTEM_PROMPT

# Model fallback configuration
MODELS = [
    "gpt-4o-mini",      # Primary choice - fastest and cheapest GPT-4 class
    "gpt-3.5-turbo",    # Fallback 1 - reliable and fast
    "gpt-4o",           # Fallback 2 - most capable but slower
]

def get_llm_with_fallback():
    """Try models in order until one works"""
    for model in MODELS:
        try:
            llm = ChatOpenAI(model=model, temperature=0, timeout=10)
            # Test the model with a simple call
            test_response = llm.invoke("Test")
            return llm, model
        except Exception as e:
            print(f"Model {model} failed: {str(e)}")
            continue
    
    # If all models fail, return the first one and let it error
    return ChatOpenAI(model=MODELS[0], temperature=0), MODELS[0]

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

    # ─── 2. Get LLM with fallback ──────────────────────────────────────────────────
    llm, model_used = get_llm_with_fallback()
    logger.info(f"Using model: {model_used}")

    # ─── 3. Retrieve context ───────────────────────────────────────────────────────
    retriever = get_retriever(k=4)
    docs = retriever.get_relevant_documents(question)
    rag_block = "\n\n".join(f"- {d.page_content}" for d in docs)

    # ─── 4. Build & call LLM ──────────────────────────────────────────────────────
    prompt = (
        SYSTEM_PROMPT
        + f"\n\n---\nContext (top {len(docs)} snippets):\n{rag_block}\n\n"
        + f"User: {question}"
    )
    
    try:
        resp = llm.invoke(prompt).content.strip()
    except Exception as e:
        logger.error(f"LLM call failed with {model_used}: {str(e)}")
        # Try one more fallback
        try:
            fallback_llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
            resp = fallback_llm.invoke(prompt).content.strip()
            model_used = "gpt-3.5-turbo (emergency fallback)"
        except Exception as e2:
            logger.error(f"All models failed: {str(e2)}")
            return f"Sorry, I'm experiencing technical difficulties. Please try again in a moment."
    
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
