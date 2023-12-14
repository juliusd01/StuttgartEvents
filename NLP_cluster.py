### Here we tried to build clusters for the event descriptions using K-Means clustering and visualize the clusters using TSNE and word clouds.
### However, the results were not very meaningful, so we decided not to use this approach.

import pandas as pd
import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt
from wordcloud import WordCloud

# Download German language resources for NLTK
nltk.download('stopwords')
nltk.download('punkt')

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# Assuming 'event_descriptions' is a list of German event descriptions

# Text preprocessing for German
stop_words = set(stopwords.words('german'))
custom_stopwords = {'http', 'br', 'href', 'de', 'https', 'div', 'https', 'bbcode', 'a', 'nofollow', 'clr', 'bbcode strong'}
stop_words = stop_words.union(custom_stopwords)

def preprocess_german_text(text):
    tokens = word_tokenize(text, language='german')
    filtered_tokens = [word.lower() for word in tokens if word.isalpha() and word.lower() not in stop_words]
    return ' '.join(filtered_tokens)

df = pd.read_csv('data/events_df.csv')

preprocessed_descriptions = []
for index, row in df.iterrows():
    event_description = row['description']
    try:
        preprocessed_description = preprocess_german_text(event_description)
        preprocessed_descriptions.append(preprocessed_description)
    except TypeError:
        continue
    
# Text vectorization
tfidf_vectorizer = TfidfVectorizer()
tfidf_matrix = tfidf_vectorizer.fit_transform(preprocessed_descriptions)

# Clustering with K-Means
num_clusters = 5  # Adjust based on the optimal number from analysis
kmeans = KMeans(n_clusters=num_clusters)
kmeans.fit(tfidf_matrix)

# Get cluster labels
cluster_labels = kmeans.labels_
print(cluster_labels)

# Get cluster centers
cluster_centers = kmeans.cluster_centers_
print(cluster_centers)

# Get top terms per cluster
terms = tfidf_vectorizer.get_feature_names_out()
for i in range(num_clusters):
    print("Cluster %d:" % i),
    for ind in cluster_centers[i].argsort()[-10:]:
        print(' %s' % terms[ind])


# Visualize clusters using TSNE
tsne_model = TSNE(n_components=2, random_state=42)
tsne_data = tsne_model.fit_transform(tfidf_matrix.toarray())

# Plot the clusters
plt.scatter(tsne_data[:, 0], tsne_data[:, 1], c=cluster_labels, cmap='viridis')
plt.title('Cluster Visualization using TSNE')
plt.show()


# Visualize word clouds for each cluster
for i in range(num_clusters):
    cluster_text = ' '.join([preprocessed_descriptions[j] for j in range(len(preprocessed_descriptions)) if cluster_labels[j] == i])
    
    wordcloud = WordCloud(width = 800, height = 800, 
                background_color ='white', 
                stopwords = stop_words, 
                min_font_size = 10).generate(cluster_text)

    plt.figure(figsize = (8, 8), facecolor = None) 
    plt.imshow(wordcloud) 
    plt.axis("off") 
    plt.title(f'Word Cloud for Cluster {i}')
    plt.show()