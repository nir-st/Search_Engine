import utils

# DO NOT MODIFY CLASS NAME
class Indexer:
    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    def __init__(self, config):
        self.inverted_idx = {}
        self.postingDict = {}
        self.config = config
        self.words_to_change = {}  # key-file name, value-words that need an update because we found a word with lower case
        self.total_num_of_docs = 0
        self.document_posting = {}  # dictionary {document_id: document_object}

    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    def add_new_doc(self, document):
        """
        This function perform indexing process for a document object.
        Saved information is captures via two dictionaries ('inverted index' and 'posting')
        :param document: a document need to be indexed.
        :return: -
        """

        document_dictionary = document.term_doc_dictionary
        updated_dict = {}
        for term in document_dictionary.keys():
            tf = document_dictionary[term][0]
            if document_dictionary[term][2] == 'entity':  ## this is an entity
                self.add_the_term(term, tf, document.tweet_id)
                continue
            if len(term) > 0 and term[0].islower():  # first letter is lowercase-first
                if term.upper() in self.inverted_idx:  # same word with upper-case letters is in index
                    if self.inverted_idx[term.upper()][2] == 0:  # term's posting not stored on disk yet
                        self.inverted_idx[term.lower()] = self.inverted_idx.pop(
                            term.upper())  # update index key to lower case
                        self.postingDict[term.lower()] = self.postingDict.pop(
                            term.upper())  # update posting key to lower case
                        self.add_the_term(term.lower(), tf, document.tweet_id)
                    else:  # term is lower cased and its posting is already stored on disk
                        self.add_to_word_to_change(term)
                        self.add_the_term(term.upper(), tf, document.tweet_id)
                else:  # upper cased term is not in the index
                    self.add_the_term(term.lower(), tf, document.tweet_id)

                updated_dict[term.lower()] = document_dictionary[term]

            else:  # first letter is a capital letter
                if term.lower() in self.inverted_idx.keys():  # lower cased term is in index
                    updated_dict[term.lower()] = document_dictionary[term]
                    self.add_the_term(term.lower(), tf, document.tweet_id)
                else:  # lower cased term is not in index
                    updated_dict[term.upper()] = document_dictionary[term]
                    self.add_the_term(term.upper(), tf, document.tweet_id)
        document.term_doc_dictionary = updated_dict
        self.document_posting[document.tweet_id] = document
        return document

    def add_the_term(self, term, tf, document_id):
        """
        This function adds a term to the inverted index and the local posting dictionary
        :param term: string
        :param tf: term's term frequency in the document
        :param document_id: int, tweet id
        """
        if term not in self.inverted_idx.keys():  # term not in index
            self.inverted_idx[term] = [1, tf, 0]
        else:  # term is in index
            self.inverted_idx[term][0] += 1
            self.inverted_idx[term][1] += tf

        if term in self.postingDict:
            self.postingDict[term].update({document_id: tf})
        else:
            self.postingDict[term] = {document_id: tf}

    def add_to_word_to_change(self, term):
        term_file_name = self.inverted_idx[term.upper()][2]
        if self.inverted_idx[term.upper()][2] != 0 and term_file_name in self.words_to_change:  # check if file exists already
            if term.upper() not in self.words_to_change[term_file_name]:
                # add to the file the word in uppercase as it is now but will change when we update
                self.words_to_change[term_file_name].append(term.upper())
        else:
            self.words_to_change[term_file_name] = [term.upper()]  # add a new file name with the term

    def remove_single_terms(self):
        """
        remove all terms appeared in only 1 document in the corpus
        :param indexer:
        :return:
        """
        keys_to_be_removed = []
        for term in self.inverted_idx.keys():
            if self.inverted_idx[term][0] == 1:
                keys_to_be_removed.append(term)
        for k in keys_to_be_removed:
            del self.inverted_idx[k]

    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    def load_index(self, fn):
        """
        Loads a pre-computed index (or indices) so we can answer queries.
        Input:
            fn - file name of pickled index.
        """
        return utils.load_obj(fn)

    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    def save_index(self, fn):
        """
        Saves a pre-computed index (or indices) so we can save our work.
        Input:
              fn - file name of pickled index.
        """
        return utils.save_obj(fn)

    # feel free to change the signature and/or implementation of this function 
    # or drop altogether.
    def _is_term_exist(self, term):
        """
        Checks if a term exist in the dictionary.
        """
        return term in self.postingDict

    # feel free to change the signature and/or implementation of this function 
    # or drop altogether.
    def get_term_posting_dict(self, term):
        """
        Return the posting list from the index for a term.
        """
        return self.postingDict[term] if self._is_term_exist(term) else []
