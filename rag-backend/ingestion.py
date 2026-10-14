import os
import duckdb
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer

# Initialize local embedding model
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
print("Loading local embedding model...")
embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)

DB_FILE = "rag.duckdb"


def extract_text_from_pdf(pdf_path: str) -> list[dict]:
  """Extracts text page by page from a PDF file with page number metadata."""
  reader = PdfReader(pdf_path)
  document_pages = []

  for page_num, page in enumerate(reader.pages):
    text = page.extract_text()
    if text:
      cleaned_text = " ".join(text.split())
      document_pages.append({"page": page_num + 1, "text": cleaned_text})

  return document_pages


def chunk_documents(document_pages: list[dict]) -> list[dict]:
  """Splits page text into overlapping chunks while preserving metadata."""
  text_splitter = RecursiveCharacterTextSplitter(
      chunk_size=500, chunk_overlap=100, length_function=len
  )

  chunked_docs = []
  for doc in document_pages:
    chunks = text_splitter.split_text(doc["text"])
    for i, chunk in enumerate(chunks):
      chunked_docs.append({
          "id": f"page_{doc['page']}_chunk_{i}",
          "vector": embedding_model.encode(chunk).tolist(),
          "text": chunk,
          "page": doc["page"],
      })

  return chunked_docs


def ingest_pdf_to_duckdb(pdf_path: str):
  """Full ingestion pipeline: Load -> Chunk -> Embed -> DuckDB Store."""
  if not os.path.exists(pdf_path):
    raise FileNotFoundError(f"PDF file not found at {pdf_path}")

  print(f"Loading and extracting text from {pdf_path}...")
  pages = extract_text_from_pdf(pdf_path)

  print("Chunking text and generating embeddings...")
  chunks = chunk_documents(pages)

  print(f"Storing {len(chunks)} rows in DuckDB...")
  con = duckdb.connect(DB_FILE)

  # Create table with a float array vector column
  con.execute("DROP TABLE IF EXISTS documents;")
  con.execute("""
        CREATE TABLE documents (
            id VARCHAR,
            vector FLOAT[384],
            text VARCHAR,
            page INTEGER
        );
    """)

  # Insert chunks batch by batch
  for chunk in chunks:
    con.execute(
        "INSERT INTO documents VALUES (?, ?, ?, ?)",
        (chunk["id"], chunk["vector"], chunk["text"], chunk["page"]),
    )

  con.close()
  print("DuckDB Ingestion complete successfully!")
  return len(chunks)


if __name__ == "__main__":
  ingest_pdf_to_duckdb("data/Onboarding_FAQ.pdf")