"""
-------------------------------------------------------------
--- THIS MODULE IS USING WORD2VEC AND SPELLING CORRECTION ---
-------------------------------------------------------------
"""
import pandas as pd
from Ranking import tf_idf_calculator
from Parsing.document_vectorizer import *
from Parsing.reader import ReadFile
from configuration import ConfigClass
from Parsing.parser_module import Parse
from Parsing.indexer import Indexer
from Ranking.searcher import Searcher
import utils
from Parsing import spell_correction


# DO NOT CHANGE THE CLASS NAME
class SearchEngine:

    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation, but you must have a parser and an indexer.
    def __init__(self, config=None):
        self._config = config
        self._parser = Parse()
        self._indexer = Indexer(config)
        # self._model = gensim.models.KeyedVectors.load_word2vec_format('GoogleNews-vectors-negative300.bin', binary=True)
        self._model = gensim.models.KeyedVectors.load_word2vec_format('../../../../GoogleNews-vectors-negative300.bin', binary=True)
        self.document_vectorizer = DocumentVectorizer(self._model)

    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    def build_index_from_parquet(self, fn):
        """
        Reads parquet file and passes it to the parser, then indexer.
        Input:
            fn - path to parquet file
        Output:
            No output, just modifies the internal _indexer object.
        """
        df = pd.read_parquet(fn, engine="pyarrow")
        documents_list = df.values.tolist()
        # Iterate over every document in the file
        number_of_documents = 0
        for idx, document in enumerate(documents_list):
            # parse the document
            parsed_document = self._parser.parse_doc(document, self._config.toStem)
            number_of_documents += 1
            # index the document data
            parsed_document = self._indexer.add_new_doc(parsed_document)
            if self._config.calculateDocumentVectorsWhileIndexing:
                doc_id = parsed_document.tweet_id
                self.document_vectorizer.generate_document_vector(parsed_document.term_doc_dictionary, doc_id, to_include_term_weights=False)
        self._indexer.remove_single_terms()
        self._indexer.total_num_of_docs = number_of_documents
        if self._config.toWeighVectors or self._config.toWeighQuery:
            tf_idf_calculator.calc_docs_terms_tfidf(self._indexer.inverted_idx, self._indexer.document_posting)

        if not self._config.toCalcVecsAfterQuery and not self._config.calculateDocumentVectorsWhileIndexing:
            self.document_vectorizer.generate_all_document_vectors(self._indexer.document_posting, self._config.toWeighVectors)

    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    def load_index(self, fn):
        """
        Loads a pre-computed index (or indices) so we can answer queries.
        Input:
            fn - file name of pickled index.
        """
        return self._indexer.load_index(fn)

    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    def load_precomputed_model(self, model_dir=None):
        """
        Loads a pre-computed model (or models) so we can answer queries.
        This is where you would load models like word2vec, LSI, LDA, etc. and
        assign to self._model, which is passed on to the searcher at query time.
        """
        pass

    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    def search(self, query):
        """
        Executes a query over an existing index and returns the number of
        relevant docs and an ordered list of search results.
        Input:
            query - string.
        Output:
            A tuple containing the number of relevant search results, and
            a list of tweet_ids where the first element is the most relavant
            and the last is the least relevant result.
        """
        searcher = Searcher(self._parser, self._indexer, model=self._model)
        query_with_corrected_spelling = spell_correction.correct_spelling(query)
        return searcher.search(query_with_corrected_spelling)
