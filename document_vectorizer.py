from word_to_vec import *
import numpy as np


class DocumentVectorizer:

    doc_to_vec = {}
    zero_vec = np.zeros(300)

    def __init__(self, model):
        self.w2v = W2V(model)

    def generate_document_vector(self, doc_terms_dict, doc_id, to_include_term_weights):
        """

        :param doc_terms_dict: dictionary {term: [int TF, boolean was_capitalized, string type]}
        :param doc_id: tweet id
        :param include_term_weights: boolean
        :param tfidf_dict: {doc_id: tf-idf weight}
        :return: vector
        """
        term_vectors = []
        for term in doc_terms_dict.keys():
            term_type = doc_terms_dict[term][2]
            if term_type == 'hashtag' or term_type == 'tag' or term_type == 'url':
                continue
            else:
                term_vec = self.w2v.get_terms_vector(term)
                if term_vec != [] and term_type == 'entity' or doc_terms_dict[term][1]:  # entity or capitalized word
                    term_vec = np.asarray(term_vec) * 2  # GIVING DOUBLE WEIGHT TO VECTORS OF ENTITIES OR CAPITALIZED WORDS
            if term_vec != []:  # is a vector
                if to_include_term_weights:
                    term_doc_weight = doc_terms_dict[term][3]
                    term_vec = np.asarray(term_vec) * term_doc_weight
                term_vectors += [np.asarray(term_vec)]
        if not term_vectors:
            doc_vec = DocumentVectorizer.zero_vec
            DocumentVectorizer.doc_to_vec[doc_id] = doc_vec
        else:
            # doc_vec = np.mean(np.asarray(term_vectors), 0)  # avg
            doc_vec = sum(term_vectors)                       # sum
            DocumentVectorizer.doc_to_vec[doc_id] = doc_vec
        return doc_vec

    def generate_all_document_vectors(self, document_posting, to_include_term_weights):
        """

        :param document_posting: dictionary {doc_id: document_object}
        :param to_include_term_weights: boolean
        :return:
        """
        for doc_id in document_posting:
            doc_terms_dict = document_posting[doc_id].term_doc_dictionary
            self.generate_document_vector(doc_terms_dict, doc_id, to_include_term_weights)
