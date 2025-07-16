# app/context/embedding.py
from pathlib import Path
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from dotenv import load_dotenv
load_dotenv()  # loads OPENAI_API_KEY from .env

# ────────────────────────────────


CHROMA_DIR = Path(__file__).parent.parent.parent / "chroma"
EMBED_MODEL = OpenAIEmbeddings(model="text-embedding-3-small")

def _load_repo_files() -> list[str]:
    roots = ["app/prompts", "app/agents/schema.py"]
    exts  = {".txt", ".md", ".py"}
    files = [p for r in roots for p in Path(r).rglob("*") if p.suffix in exts]
    return [p.read_text() for p in files]

def build_index() -> None:
    docs = _load_repo_files()
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=512, chunk_overlap=64
    )
    Chroma.from_documents(
        splitter.create_documents(docs),
        EMBED_MODEL,
        persist_directory=str(CHROMA_DIR)
    ).persist()

def get_retriever(k: int = 4):
    store = Chroma(
        embedding_function=EMBED_MODEL,
        persist_directory=str(CHROMA_DIR)
    )
    return store.as_retriever(search_kwargs={"k": k})

if __name__ == "__main__":
    import sys
    if "build_index" in sys.argv:
        build_index()
        print("✅ Chroma index rebuilt at", CHROMA_DIR)
