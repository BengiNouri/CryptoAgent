# test1.py
import os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from app.agents.insight_agent import ask

def main():
    # A few sample queries to test both direct answers and tool calls
    queries = [
        "What arguments does plot_price take?",
        "plot_price coin=ETH days=5",
        "get_top_movers period=1d limit=3",
        "Tell me something about Bitcoin."
    ]
    for q in queries:
        print(f">>> Query: {q!r}")
        try:
            resp = ask(q)
        except Exception as e:
            resp = f"ERROR: {e}"
        print(f"Response:\n{resp}\n")
    print("Done.")

if __name__ == "__main__":
    main()
