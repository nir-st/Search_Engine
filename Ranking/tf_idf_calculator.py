from utils import *
import os
import shutil
import math

dir_path = "TFIDF_Posting/"


def calc_query_terms_tfidf(inverted_index, term_dict, number_of_documents):
    """

    :param inverted_index: dictionary: {term: [#docs, #in_corpus]}
    :param term_dict: dictionary: term: [TF, is_capitalized, type]
    :return:
    """
    for term in term_dict:
        normalized_tf = term_dict[term][0] / len(term_dict)
        if term in inverted_index:
            idf = math.log(number_of_documents / inverted_index[term][0])
        elif term.lower() in inverted_index:
            idf = math.log(number_of_documents / inverted_index[term.lower()][0])
        else:
            idf = math.log(1+number_of_documents / number_of_documents)  #1 / number_of_documents  term not in inverted index and needs IDF #TODO:check if wether a better value should be here
        tfidf = normalized_tf * idf
        term_dict[term].append(tfidf)


def calc_docs_terms_tfidf(inverted_index, document_dict):
    """

    :param inverted_index: dictionary: {term: [#docs, #in_corpus]}
    :param document_dict: dictionary: {tweet_id: [document_object, vector]}
    :return: updated document_dict. each document's term dict will contain its TF-IDF values
    """
    number_of_documents = len(document_dict)
    for tweet_id in document_dict:
        cur_doc = document_dict[tweet_id]  # document object
        doc_terms_dict = cur_doc.term_doc_dictionary  # {term: [tf, is_capitalized, type]
        for term in doc_terms_dict:
            normalized_tf = doc_terms_dict[term][0] / cur_doc.doc_length
            if term in inverted_index:
                idf = math.log(number_of_documents / inverted_index[term][0])
            elif term.lower() in inverted_index:
                idf = math.log(number_of_documents / inverted_index[term.lower()][0])
            else:
                idf = math.log(1+number_of_documents / number_of_documents)  # term not in inverted index and needs IDF #TODO:check if wether a better value should be here

            tfidf = normalized_tf * idf

            doc_terms_dict[term].append(tfidf)
