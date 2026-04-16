import os
from typing import List
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.core.config import config

class DocumentIngestor:
    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.CHUNK_SIZE,
            chunk_overlap=config.CHUNK_OVERLAP,
            separators=["\n\n", "\n", " ", ""]
        )

    def load_documents(self) -> List[dict]:
        documents = []
        if not os.path.exists(self.data_dir):
            print(f"Warning: Data directory {self.data_dir} not found.")
            return documents

        for filename in os.listdir(self.data_dir):
            if filename.endswith(".txt"):
                file_path = os.path.join(self.data_dir, filename)
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    chunks = self.splitter.split_text(content)
                    for i, chunk in enumerate(chunks):
                        documents.append({
                            "content": chunk,
                            "metadata": {
                                "source": filename,
                                "chunk_id": i
                            }
                        })
        return documents

if __name__ == "__main__":
    # Test ingestion
    ingestor = DocumentIngestor("data/stripe")
    docs = ingestor.load_documents()
    print(f"Loaded {len(docs)} chunks from Stripe documentation.")
