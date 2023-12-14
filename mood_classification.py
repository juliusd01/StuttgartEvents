import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import nltk

# Download German language resources for NLTK
nltk.download('stopwords')
nltk.download('punkt')

# Read your DataFrame with event descriptions
df = pd.read_csv('data/all_events.csv')  # Replace 'your_dataframe.csv' with your actual file path or URL




# Get German stop words from NLTK
german_stop_words = set(stopwords.words('german'))

# Convert event descriptions to document-term matrix
vectorizer = CountVectorizer(stop_words=list(german_stop_words), max_features=1000, max_df=0.85)

event_descriptions = []
for index, row in df.iterrows():
    event_description = row['description']
    if isinstance(event_description, str):
        event_descriptions.append(event_description)
    else:
        event_descriptions.append('Anderes')

X = vectorizer.fit_transform(event_descriptions)

# Apply Latent Dirichlet Allocation (LDA)
num_topics = 5  # Adjust based on the desired number of categories
lda = LatentDirichletAllocation(n_components=num_topics, random_state=42)
document_topics = lda.fit_transform(X)

# Get the most probable topic for each document (event)
predicted_labels = document_topics.argmax(axis=1)

# Map the topic labels to your predefined categories
topic_labels_mapping = {
    0: 'Kulturell',
    1: 'Gesellig',
    2: 'Musikalisch',
    3: 'Kreativ',
    4: 'Anderes'
}

# Map the predicted labels to category names
predicted_category_labels = [topic_labels_mapping[label] for label in predicted_labels]

# Add the predicted category labels to the DataFrame
df['stimmung'] = predicted_category_labels

# Print or further analyze the predicted category labels
print(df[['description', 'stimmung']])

df.to_csv('data/all_events.csv', index=False)
