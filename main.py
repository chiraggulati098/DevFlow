import sys
from PyQt5.QtWidgets import QApplication

from backend.vector_store import VectorStore
from frontend.ui import UI

if __name__ == "__main__":
    store = VectorStore()

    print("Syncing ChromaDB with ./docs/ directory")
    store.sync_with_docs_directory()
    print("Sync complete")
    
    app = QApplication([])
    window = UI(store)  
    window.show()
    sys.exit(app.exec_())