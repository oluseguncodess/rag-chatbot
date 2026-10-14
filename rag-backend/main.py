import os
import duckdb
import ollama
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer

app = FastAPI(title="RAG Backend API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_FILE = "rag.duckdb"
OLLAMA_MODEL = "qwen2:1.5b" 

print("Initializing embedding model...")
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")


class QueryRequest(BaseModel):
  question: str


@app.post("/api/chat")
def chat_endpoint(payload: QueryRequest):
  if not os.path.exists(DB_FILE):
    raise HTTPException(
        status_code=500, detail="DuckDB database file not found. Run ingestion first."
    )

  question = payload.question.strip()
  if not question:
    raise HTTPException(status_code=400, detail="Question cannot be empty.")

  # Embed user's question
  q_embedding = embedding_model.encode(question).tolist()

  # Query DuckDB using vector distance calculation
  con = duckdb.connect(DB_FILE, read_only=True)
  query_sql = """
        SELECT text, page, array_distance(vector, ?::FLOAT[384]) as distance
        FROM documents
        ORDER BY distance ASC
        LIMIT 3;
    """
  results = con.execute(query_sql, [q_embedding]).fetchall()
  con.close()

  if not results:
    raise HTTPException(
        status_code=404, detail="No relevant context found in the database."
    )

  formatted_sources = []
  context_builder = []

  for row in results:
    text, page, distance = row
    formatted_sources.append({
        "text": text,
        "page": page,
        "distance": float(distance),
    })
    context_builder.append(f"[Page {page}]: {text}")

  context_text = "\n\n".join(context_builder)
 
  prompt = f"""You are a helpful, friendly, and natural customer support assistant. 
   Answer the user's question based on the provided context below. 
   You can paraphrase and explain the information in your own conversational words, but do not invent or add outside facts. 
   If the answer cannot be found in the context, state that you cannot find it in the document.

   Context:
   {context_text}

   User Question: {question}
   Answer:"""

  try:
    response = ollama.chat(
        model=OLLAMA_MODEL,
        messages=[{"role": "user", "content": prompt}],
        options={"temperature": 0.5},
    )
    answer = response["message"]["content"]
  except Exception as e:
    raise HTTPException(
        status_code=500,
        detail=f"Failed to generate response from Ollama. Is it running? Error: {str(e)}",
    )

  return {"question": question, "answer": answer, "sources": formatted_sources, "role": "agent"}


@app.get("/")
def health_check():
  return {"status": "Ollama RAG Backend is up and running!"}