import pandas as pd
from google.cloud import firestore
import os

# Authenticate with GCP (run `gcloud auth application-default login` in terminal first)
db = firestore.Client(project='tugasakhir2025')

# Load your local CSV
df = pd.read_csv(r'C:\Users\madea\OneDrive\Documents\Kuliah\Semester 8\Tugas Akhir\Coding\Property Recommender APP\dataset\kbrs_dataset_2.csv')

# Get a reference to the collection you want to create
collection_ref = db.collection('properties')

# Loop through the DataFrame and upload each row as a new document
for index, row in df.iterrows():
    # Convert row to a dictionary, handle potential NaN values
    doc_data = row.to_dict()
    # Firestore doesn't like NaN, convert to None (null)
    doc_data_clean = {k: (None if pd.isna(v) else v) for k, v in doc_data.items()}

    # You can use a specific column as the document ID, or let Firestore auto-generate one
    collection_ref.add(doc_data_clean)
    print(f"Added document for row {index}")

print("Data upload to Firestore complete.")