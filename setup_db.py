from app.services.vector_store import VectorStoreService
import os

def main():
    print("Initializing Vector Database...")
    vs = VectorStoreService()
    data_path = os.path.join(os.getcwd(), "data", "stripe")
    
    if not os.path.exists(data_path):
        print(f"Error: Data path {data_path} does not exist.")
        return

    vs.index_documents(data_path)
    print("Database initialization complete.")

if __name__ == "__main__":
    main()
