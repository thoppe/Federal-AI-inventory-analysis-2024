from pathlib import Path
import numpy as np
import json
from tqdm import tqdm
import pandas as pd

# Set this flag if we have new data
force = False

# Maximum fidelity we need
n_max_clusters = 30


def load_vectors(f_npy, n_dim=40):
    from sklearn.decomposition import IncrementalPCA

    # Loads in the vectors and highly compress them via SVD
    ipca = IncrementalPCA(n_components=n_dim)
    V = np.load(f_npy)

    Vt = ipca.fit_transform(V)
    return Vt


def umap_vectors(V):
    import umap

    # Compress data down to two dimensions for visualization
    # clf = umap.UMAP(n_neighbors=5, random_state=44, min_dist=0.055)
    clf = umap.UMAP(n_neighbors=5, n_jobs=-1, min_dist=0.055)

    clf.fit(V)
    embedding = clf.embedding_.copy()
    embedding -= embedding.mean(axis=0)
    embedding /= embedding.std(axis=0)

    return embedding


def cluster_data(embedding, num_text_labels=25):
    from sklearn.cluster import MiniBatchKMeans

    clf = MiniBatchKMeans(n_clusters=num_text_labels, batch_size=1000)
    return clf.fit_predict(embedding)


f_embedding = Path("processed_responses/GPT_embedding.npy")
f_umap = Path("processed_responses/GPT_umap.npy")
f_clusters = Path("processed_responses/GPT_clusters.npy")
f_keywords = Path("processed_responses/GPT_cluster_keywords.csv")
f_summary_text = Path("processed_responses/summary_text.csv")

if not f_umap.exists() or force:
    V = load_vectors(f_embedding)
    embedding = umap_vectors(V)
    np.save(f_umap, embedding)
    print(f"Saved {f_umap}")


if not f_clusters.exists() or force:
    embedding = np.load(f_umap)
    clusters = [cluster_data(embedding, k) for k in tqdm(range(1, n_max_clusters + 1))]
    clusters = np.array(clusters)
    np.save(f_clusters, clusters)
    print(f"Saved {f_clusters}")

if not f_keywords.exists() or force:
    from keybert import KeyBERT

    clusters = np.load(f_clusters)
    embedding = np.load(f_umap)

    df = pd.read_csv(f_summary_text)

    kw_model = KeyBERT(model="all-MiniLM-L6-v2")
    stop_words = ["dataset", "metadata", "cnn", "rnn", "nlp", "ai", "tensorflow"]
    args = {"keyphrase_ngram_range": (1, 2), "stop_words": stop_words}

    CUTOFF = 100_000
    data = []

    for k in range(1, n_max_clusters + 1):
        for i in range(0, k):
            idx = clusters[k - 1] == i

            doc = "\n".join(df["summary_text"].values[idx][:CUTOFF])
            Z = embedding[idx]
            ux, uy = Z.T
            kw = kw_model.extract_keywords(doc, **args)

            row = {
                "n_clusters": k,
                "cluster_k": i,
                "cluster_x": ux.mean(),
                "cluster_y": uy.mean(),
                "cluster_size": idx.sum(),
                "label_text": kw[0][0],
                "label_score": kw[0][1],
            }
            data.append(row)
            print(row)

    kws = pd.DataFrame(data)
    kws.to_csv(f_keywords, index=False)
    print(f"Saved {f_keywords}")
