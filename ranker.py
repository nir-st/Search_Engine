from numpy import dot
from numpy.linalg import norm
from document_vectorizer import *

# you can change whatever you want in this module, just make sure it doesn't
# break the searcher module
class Ranker:
    def __init__(self):
        pass

    @staticmethod
    def rank_relevant_docs(relevant_docs, query_vector, k=None):
        """
        This function provides rank for each relevant document and sorts them by their scores.
        The current score considers solely the number of terms shared by the tweet (full_text) and query.
        :param k: number of most relevant docs to return, default to everything.
        :param relevant_docs: dictionary of documents that contains at least one term from the query.
        :return: sorted list of documents by score
        """
        doc_id_score_list = []
        for doc_id in relevant_docs.keys():
            a = DocumentVectorizer.doc_to_vec[doc_id]
            b = query_vector
            cos_sim = float(dot(a, b) / (norm(a) * norm(b)))
            doc_id_score_list.append((doc_id, cos_sim))
        ranked_results = sorted(doc_id_score_list, key=lambda x: x[1], reverse=True)
        if k is not None:
            ranked_results = ranked_results[:k]
        return [d[0] for d in ranked_results[:4000]]

