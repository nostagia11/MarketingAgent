import os
import time

def get_index(data, index_name):
    index = None
    if not os.path.exists(index_name):
      print("building index", index_name)
      index = VectorStoreIndex.from_documents(data, show_progress=True)
      index.storage_context.persist(persist_dir=index_name)
    else:
        index = load_index_from_storage(
            StorageContext.from_defaults(persist_dir=index_name)
        )
    return index


data_folder = "data"
last_check = time.time()

def get_new_pdfs_by_time(folder, last_check):
    new_files = []
    for f in os.listdir(folder):
        if f.endswith(".pdf"):
            full_path = os.path.join(folder, f)
            if os.path.getmtime(full_path) > last_check:
                new_files.append(full_path)
    return new_files

# Example usage
new_pdfs = get_new_pdfs_by_time(data_folder, last_check)
for pdf_path in new_pdfs:
    docs = PDFReader().load_data(file=pdf_path)
    pdf_index = get_index(docs, os.path.basename(pdf_path).replace(".pdf", ""))
    rag_engine = pdf_index.as_query_engine()
    print(f"Indexed new: {pdf_path}")

last_check = time.time()  # update checkpoint
