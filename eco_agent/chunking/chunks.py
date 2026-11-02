
from pathlib import Path
import re
import json
import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Specify directory path (use Path(r"C:\path\to\data") if running on Windows)
folder1 = Path("/home/yazid/backend/eco_agent/data")

print(f"Directory: {folder1}")
print(f"Directory Exists: {folder1.exists()}")  # Fixed method call

if not folder1.exists():
    raise FileNotFoundError(f"Directory does not exist: {folder1}")

documents = []

# Process all PDF files
for file in folder1.glob("*.pdf"):
    try:
        loader = PyPDFLoader(str(file))
        docs = loader.load()
    except Exception as e:
        print(f"Error loading {file.name}: {e}")
        continue
    
    for doc in docs:
        try:
            doc.metadata["source"] = os.fsdecode(file.name)
            cleaned_content = re.sub(r'\n{3,}', "\n\n", doc.page_content)
            doc.page_content = cleaned_content.strip()
        except Exception as e:
            print(f"Error cleaning {file.name}: {e}")
            
    documents.extend(docs)

# Split documents into chunks
splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=150,
    separators=["\n\n", "\n", ".", " ", ""]
)

chunks = splitter.split_documents(documents)
print(f"Total chunks: {len(chunks)}")

# Format output and sanitize metadata for JSON dumping
output = []
for i, chunk in enumerate(chunks):
    # Ensure all metadata values are JSON serializable
    safe_metadata = {
        k: (v if isinstance(v, (str, int, float, bool, type(None))) else str(v))
        for k, v in chunk.metadata.items()
    }
    updated_metadata = {**safe_metadata, "id": i}
    output.append({"Content": chunk.page_content, "metadata": updated_metadata})

output_file = folder1 / "complete_windows.json"

with open(output_file, "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"Saved to {output_file}")
