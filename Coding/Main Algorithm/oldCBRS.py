import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Load the old dataset
old_df = pd.read_csv(r'C:\Users\madea\OneDrive\Documents\Kuliah\Semester 8\Tugas Akhir\Coding\Data Preprocessing\updated_jabodetabeksur_olx_housing_dataset_.csv')

# Preprocessing function
def preprocess(df):
    df['description'] = df['description'].fillna('').str.lower()
    df['facilities'] = df['facilities'].fillna('').str.lower()
    df['combined_text'] = df['description'] + ' ' + df['facilities']
    return df

# Apply preprocessing
old_df = preprocess(old_df)

# TF-IDF vectorization
vectorizer = TfidfVectorizer(max_features=5000)
old_tfidf = vectorizer.fit_transform(old_df['combined_text'])

# Compute cosine similarity matrix
old_sim_matrix = cosine_similarity(old_tfidf)

# Recommendation function
def compare_old_recommendations(property_index, top_n=5):
    print(f"\nProperty Index: {property_index}\n")

    # Compute similarity scores
    scores = list(enumerate(old_sim_matrix[property_index]))

    # Sort and remove the property itself
    top_matches = sorted(scores, key=lambda x: x[1], reverse=True)[1:top_n+1]

    # Create result DataFrame
    target = old_df.iloc[[property_index]].copy()
    target['similarity_score'] = 'TARGET'

    recommendations = old_df.iloc[[i for i, _ in top_matches]].copy()
    recommendations['similarity_score'] = [score for _, score in top_matches]

    # Combine target and recommendations
    result = pd.concat([target, recommendations], ignore_index=True)

    # Export to CSV
    filename = f"cbrs_recommendations_olddata_{property_index}.csv"
    result.to_csv(filename, index=False)

    print(f"Recommendations saved to: {filename}")
    return result

# Example usage
compare_old_recommendations(property_index=384, top_n=5)
