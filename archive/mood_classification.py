import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import nltk
import pyLDAvis
import pyLDAvis.lda_model

# Download German language resources for NLTK
nltk.download('stopwords')
nltk.download('punkt')

# Read DataFrame with event descriptions
df = pd.read_csv('data/2000_events_sample.csv')  # Replace 'your_dataframe.csv' with your actual file path or URL

# Get German stop words from NLTK
german_stop_words = set(stopwords.words('german'))
english_stop_words = set(stopwords.words('english'))
self_defined_stop_words = ['stuttgart', 'de', 'www', 'uhr', '00', '30', '19', '20', '21', '22', '23', '00', '10', '11', '12', '13', '14', '1', 'http', 'com', 'br', 'https']

combined_stop_words = german_stop_words.union(english_stop_words).union(self_defined_stop_words)

# Convert event descriptions to document-term matrix
vectorizer = CountVectorizer(stop_words=list(combined_stop_words), max_features=1000, max_df=0.85)

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

def print_top_words(model, feature_names, n_top_words):
    for topic_idx, topic in enumerate(model.components_):
        message = f"Topic #{topic_idx}: "
        message += " ".join([feature_names[i]
                             for i in topic.argsort()[:-n_top_words - 1:-1]])
        print(message)

n_top_words = 20
tf_feature_names = vectorizer.get_feature_names_out()
print_top_words(lda, tf_feature_names, n_top_words)

# top words for sample of 2000 events
# Topic #0: yoga kurs stuttgart leben mehr menschen geht immer anmeldung innen
# Topic #1: the of and to for is at you on we
# Topic #2: stuttgart de anmeldung sowie www fragen veranstaltung bitte baden württemberg
# Topic #3: musik live band tour www mal album up ganz jazz
# Topic #4: uhr stuttgart 00 de www mittwoch 30 ab 19 20

# Map the topic labels to your predefined categories
topic_labels_mapping = {
    0: 'Lebhaft',
    1: 'International',
    2: 'Kultik',
    3: 'Energiegeladen',
    4: 'hello'
}

# Map the predicted labels to category names
predicted_category_labels = [topic_labels_mapping[label] for label in predicted_labels]

# Add the predicted category labels to the DataFrame
df['stimmung'] = predicted_category_labels

# Print or further analyze the predicted category labels
print(df[['description', 'stimmung']])

df.to_csv('2000_events_sample.csv', index=False)
