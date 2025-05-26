import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler
from scipy.sparse import csr_matrix, hstack
import numpy as np

# Load new dataset
new_df = pd.read_csv("housing_with_entities.csv")

# Preprocessing function
def preprocess(df):
    df['description'] = df['description'].fillna('').str.lower()
    df['facilities'] = df['facilities'].fillna('').str.lower()
    df['combined_text'] = df['description'] + ' ' + df['facilities']
    return df

# Apply preprocessing
new_df = preprocess(new_df)

# TF-IDF Vectorization on new dataset
vectorizer = TfidfVectorizer(max_features=5000)
new_tfidf = vectorizer.fit_transform(new_df['combined_text'])

# Structured features (entity counts)
entity_features = ['SCHOOL', 'UNIVERSITY', 'HOSPITAL', 'MALL', 'MARKET', 'TRANSPORT', 'WORSHIP']
new_structured = new_df[entity_features].fillna(0).astype(int)

# Normalize structured features
scaler = MinMaxScaler()
new_structured_scaled = scaler.fit_transform(new_structured)

# Combine text and structured features
combined_matrix = hstack([new_tfidf, csr_matrix(new_structured_scaled)])

# Compute similarity matrix
new_sim_matrix = cosine_similarity(combined_matrix)

# Recommendation function
def compare_recommendations(property_index, top_n=5):
    print(f"\nProperty Index: {property_index}\n")
    
    # Get similarity scores
    scores = list(enumerate(new_sim_matrix[property_index]))

    # Sort scores, exclude the property itself
    top_matches = sorted(scores, key=lambda x: x[1], reverse=True)[1:top_n+1]

    # Create output DataFrame
    target = new_df.iloc[[property_index]].copy()
    target['similarity_score'] = 'TARGET'

    recommendations = new_df.iloc[[i for i, _ in top_matches]].copy()
    recommendations['similarity_score'] = [score for _, score in top_matches]

    # Combine target and recommendations
    result = pd.concat([target, recommendations], ignore_index=True)

    # Export to CSV
    filename = f"cbrs_recommendations_newdata_{property_index}.csv"
    result.to_csv(filename, index=False)

    print(f"Recommendations saved to: {filename}")
    return result

# Example usage
compare_recommendations(property_index=384, top_n=5)
