import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from scipy.cluster.hierarchy import dendrogram, linkage, fcluster
import matplotlib.pyplot as plt
import numpy as np
from database import DB
import credentials
from sklearn.cluster import DBSCAN
from llmInterface import LLM



db = DB(credentials.db_config)

embedding = LLM(db)

query = "SELECT id,sentence,sentence_v, (sentence_v <=> %s::vector) as similarity FROM interviews_sentences where project=%s AND (sentence_v <=> %s::vector) < 0.20" 
#the vector column
vector_define = embedding.getEmbedding('Hopes and aspirations','azure')
#params = (vector_define,'3e85686d-2380-47c1-a953-978069002775', vector_define)
rows = db.query_database_all(query,params)
data_frame = pd.DataFrame(rows, columns=['id', 'content', 'content_v','similarity'])



#data_frame['content_v'] = data_frame['content_v'].apply(lambda x: np.fromstring(x.strip('[]'), sep=','))


vectors = np.stack(data_frame['content_v'].values)

range_n_clusters = list(range(2, 20)) 
silhouette_avg_scores = []

for num_clusters in range_n_clusters:
    kmeans = KMeans(n_clusters=num_clusters, random_state=42, n_init='auto')
    cluster_labels = kmeans.fit_predict(vectors)
    silhouette_avg = silhouette_score(vectors, cluster_labels)
    silhouette_avg_scores.append(silhouette_avg)
    print(f"Number of clusters: {num_clusters}, Silhouette score: {silhouette_avg}")


plt.plot(range_n_clusters, silhouette_avg_scores)
plt.xlabel('Number of Clusters')
plt.ylabel('Silhouette Score')
plt.show()


optimal_clusters = range_n_clusters[np.argmax(silhouette_avg_scores)]
print(f"Optimal number of clusters: {optimal_clusters}")


kmeans = KMeans(n_clusters=optimal_clusters, random_state=42, n_init='auto')
kmeans.fit(vectors)


print(kmeans.labels_)

Z = linkage(vectors, method='ward')  # 'ward' is one option for the method
number_of_clusters = np.count_nonzero(Z[:, 2] > 1)
print(f"Number of cluster according to the dendogram: {number_of_clusters}")
# Plot the dendrogram
plt.figure(figsize=(20, 14))
plt.title('Hierarchical Clustering Dendrogram Kilo')
dendrogram(Z)
plt.show()

clusters = fcluster(Z, t=optimal_clusters, criterion='maxclust')
data_frame['cluster_label'] = kmeans.labels_
sorted_df = data_frame.sort_values(by='cluster_label')

sorted_df.to_csv('sorted_clusters.csv', index=False)

#for index, row in data_frame.iterrows():
#	print(f"Updating {int(row['id'])}")
#	db.query_database_insert("UPDATE interviews_sentences set sub_cluster=%s where id=%s",(int(row['cluster_label']), int(row['id'])))


# dbscan = DBSCAN(eps=0.5, min_samples=5)  # Adjust the eps and min_samples parameters as needed
# dbScanClusters = dbscan.fit_predict(vectors)

# print(dbScanClusters)
