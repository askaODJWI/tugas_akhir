import pandas as pd
import spacy
from spacy.pipeline import EntityRuler
from rapidfuzz import fuzz
from pathlib import Path

# 1. Load your dataset
df = pd.read_csv(r'C:\Users\madea\OneDrive\Documents\Kuliah\Semester 8\Tugas Akhir\Coding\Data Preprocessing\updated_jabodetabeksur_olx_housing_dataset_.csv')
df['description'] = df['description'].fillna('').str.lower()

# 2. Define entity patterns
entity_patterns = {
    "SCHOOL": ["sd", "smp", "sma", "sekolah", "tk", "playgroup"],
    "UNIVERSITY": ["universitas", "kampus", "perguruan tinggi"],
    "HOSPITAL": ["rumah sakit", "rs"],
    "MALL": ["mall", "plaza", "supermall", "pusat perbelanjaan"],
    "MARKET": ["pasar", "market", "traditional market"],
    "TRANSPORT": ["terminal", "stasiun", "halte", "tol", "bandara"],
    "WORSHIP": ["masjid", "gereja", "pura"]
}

# 3. Initialize spaCy with a blank Indonesian model
nlp = spacy.blank('id')
ruler = nlp.add_pipe('entity_ruler')

# 4. Add patterns to EntityRuler
patterns = []
for label, keywords in entity_patterns.items():
    for word in keywords:
        patterns.append({"label": label, "pattern": word})
ruler.add_patterns(patterns)

# 5. Fuzzy matcher fallback
def fuzzy_match(text, keywords, threshold=85):
    return any(fuzz.partial_ratio(text, k) >= threshold for k in keywords)

# 6. Entity extraction function
def extract_entities(description):
    doc = nlp(description)
    found_entities = {label: 0 for label in entity_patterns.keys()}

    # Exact rule-based matches
    for ent in doc.ents:
        found_entities[ent.label_] = 1

    # Fuzzy fallback check
    for label, keywords in entity_patterns.items():
        if found_entities[label] == 0:
            if fuzzy_match(description, keywords):
                found_entities[label] = 1

    return found_entities

# 7. Apply to dataset and expand columns
entity_df = df['description'].apply(extract_entities).apply(pd.Series)
df = pd.concat([df, entity_df], axis=1)


# Export results to CSV
filepath_csv = Path('INER/dataset_with_entities.csv')  
filepath_csv.parent.mkdir(parents=True, exist_ok=True)  
df.to_csv(filepath_csv, index=False, encoding='utf-8-sig')

# Export results to JSON
filepath_json = Path('INER/dataset_with_entities.json')  
filepath_json.parent.mkdir(parents=True, exist_ok=True)  
df.to_json(filepath_json, orient='records', force_ascii=False, indent=2)