from sklearn.cluster import KMeans
import random


class ClusterService(object):
    num_clusters = 5

    def __init__(self, num_clusters, *args):
        self.num_clusters = num_clusters
        super(ClusterService, self).__init__(*args)

    def cluster(self, corpus_embeddings, documents):
        clustering_model = KMeans(n_clusters=self.num_clusters)
        clustering_model.fit(corpus_embeddings)
        cluster_assignment = clustering_model.labels_

        clustered_sentences = [[] for i in range(self.num_clusters)]
        clustered_sample = []

        for sentence_id, cluster_id in enumerate(cluster_assignment):
            clustered_sentences[cluster_id].append(documents[sentence_id])

        for i, cluster in enumerate(clustered_sentences):
            clustered_sample.append(random.choice(cluster))

        return clustered_sample
