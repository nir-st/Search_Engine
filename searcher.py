from document_vectorizer import DocumentVectorizer
from ranker import Ranker
import utils
import configuration
import tf_idf_calculator


# DO NOT MODIFY CLASS NAME
class Searcher:
    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit. The model 
    # parameter allows you to pass in a precomputed model that is already in 
    # memory for the searcher to use such as LSI, LDA, Word2vec models. 
    # MAKE SURE YOU DON'T LOAD A MODEL INTO MEMORY HERE AS THIS IS RUN AT QUERY TIME.
    def __init__(self, parser, indexer, model=None):
        self._parser = parser
        self._indexer = indexer
        self._ranker = Ranker()
        self._model = model
        self.config = configuration.ConfigClass()
        self.doc_vectorizer = DocumentVectorizer(model)

    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    def search(self, query, k=None):
        """ 
        Executes a query over an existing index and returns the number of 
        relevant docs and an ordered list of search results (tweet ids).
        Input:
            query - string.
            k - number of top results to return, default to everything.
        Output:
            A tuple containing the number of relevant search results, and 
            a list of tweet_ids where the first element is the most relavant 
            and the last is the least relevant result.
        """
        query_as_dict = self._parser.parse_sentence(query, '', self.config.toStem)
        if self.config.toWeighQuery:
            tf_idf_calculator.calc_query_terms_tfidf(self._indexer.inverted_idx, query_as_dict, self._indexer.total_num_of_docs)
        relevant_docs = self._relevant_docs_from_posting(query_as_dict)
        if self.config.toCalcVecsAfterQuery:
            for document_id in relevant_docs.keys():
                doc_terms_dict = self._indexer.document_posting[document_id].term_doc_dictionary
                self.doc_vectorizer.generate_document_vector(doc_terms_dict, document_id, self.config.toWeighVectors)

        query_vector = self.doc_vectorizer.generate_document_vector(doc_terms_dict=query_as_dict, doc_id=0,
                                                                    to_include_term_weights=self.config.toWeighQuery)

        ranked_doc_ids = Ranker.rank_relevant_docs(relevant_docs, query_vector)
        n_relevant = len(ranked_doc_ids)
        return n_relevant, ranked_doc_ids

    # feel free to change the signature and/or implementation of this function 
    # or drop altogether.
    def _relevant_docs_from_posting(self, query_as_dict):
        """
        This function loads the posting list and count the amount of relevant documents per term.
        :param query_as_list: parsed query tokens
        :return: dictionary of relevant documents mapping doc_id to document frequency.
        """
        relevant_docs = {}
        for term in query_as_dict:
            posting_dict = self._indexer.get_term_posting_dict(term)
            for doc_id in posting_dict:
                count_term_in_tweet = posting_dict[doc_id]
                if doc_id in relevant_docs:
                    relevant_docs[doc_id].append((term, count_term_in_tweet))
                else:
                    relevant_docs[doc_id] = [(term, count_term_in_tweet)]
        return relevant_docs
