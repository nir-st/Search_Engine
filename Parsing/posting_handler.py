from utils import *
import os
import shutil


class PostingHandler:

    def __init__(self, output_path='output', terms_per_file=30000):
        self.number_of_files = 0
        self.terms_per_file = terms_per_file
        self.output_path = output_path + "/PostingFiles"
        if os.path.isdir("." + self.output_path):
            shutil.rmtree("." + self.output_path)
        os.mkdir(self.output_path)
        if not os.path.isfile(self.output_path + '/covid.pkl'):
            save_obj({'covid19': {}, '#COVID19': {}}, self.output_path + '/covid')
        if not os.path.isfile('PostingFiles/pop_terms.pkl'):
            save_obj({'mask': {}, 'wear': {}, 'pandemic': {}, 'people': {}}, self.output_path + '/pop_terms1')
        if not os.path.isfile('PostingFiles/pop_terms.pkl'):
            save_obj({'mask': {}, 'wear': {}, 'pandemic': {}, 'people': {},
                      'twitter': {}, 'status': {}, 'trump': {}, 'masks': {},
                      'us': {}, 'web': {}, 'virus': {}, 'cases': {}, 'new': {},
                      'wearing': {}}, self.output_path + '/pop_terms2')

    def save_posting_files(self, posting_dict, inverted_idx, words_to_change):
        """
        This function takes a posting dictionary and store it to the engine's local data base
        :param posting_dict: A posting dictionary of key: term, value: a list of (tweet_id, number_of_occurrences)
        :param inverted_idx: Main inverted index dictionary.
        :param words_to_change:
        :return: The main inverted index dictionary updated with the file names for updated terms.
        """
        if not os.path.isfile(self.output_path + '/pf0.pkl'):
            save_obj({}, self.output_path + '/pf0')

        file_term_dict = generate_file_term_dict(posting_dict.keys(), inverted_idx)

        for file_name in file_term_dict.keys():
            if file_name != 0:  # is a file
                dict_from_disc = load_obj(self.output_path + "/" + file_name)  # load posting file
                for term in file_term_dict[file_name]:  # iterate over terms stored on that posting file
                    if term not in dict_from_disc and term.upper() in posting_dict:
                        dict_from_disc[term.lower()].update(posting_dict[term.upper()])
                    else:
                        dict_from_disc[term].update(posting_dict[term])
                if file_name in words_to_change:  # terms on that file need be lower cased
                    lower_case_keys(words_to_change[file_name], dict_from_disc, inverted_idx)
                    words_to_change.pop(file_name)
                save_obj(dict_from_disc, self.output_path + '/' + file_name)

            else:  # not on a file yet
                file_name = 'pf' + str(self.number_of_files)
                dict_from_disc = load_obj(self.output_path + '/' + file_name)
                terms_on_dict = len(dict_from_disc)
                for term in file_term_dict[0]:
                    if terms_on_dict < self.terms_per_file:
                        dict_from_disc[term] = posting_dict[term]
                        terms_on_dict += 1
                    else:  # file is full, create a new one
                        save_obj(dict_from_disc, self.output_path + '/' + file_name)
                        self.number_of_files += 1
                        dict_from_disc = {
                            term: posting_dict[term]
                        }
                        file_name = 'pf' + str(self.number_of_files)
                        terms_on_dict = 1
                    inverted_idx[term][2] = file_name  # update index filename
                if file_name in words_to_change:  # terms on that file need be lower cased
                    lower_case_keys(words_to_change[file_name], dict_from_disc, inverted_idx)  ### save changes without return???
                    words_to_change.pop(file_name)
                save_obj(dict_from_disc, self.output_path + '/' + file_name)

        for file_name in words_to_change.keys():  # update all remaining terms that need to be lower cased
            dict_from_disc = load_obj(self.output_path + file_name)
            lower_case_keys(words_to_change[file_name, dict_from_disc, inverted_idx])
            save_obj(self.output_path + '/' + file_name)

        words_to_change.clear()

        return inverted_idx

    def sort_dict_doc_list_by_id(self, posting_dict):
        """
        This function sorts all lists of tweets by their ids
        :param posting_dict: A posting dict of key: term, value: a list of (tweet_id, number_of_occurrences).
        """
        for term in posting_dict.keys():
            posting_dict[term].sort()


def lower_case_keys(terms, dict_from_disc, inverted_index):
    """

    :param terms: list of terms
    :param dict_from_disc:sdfsdsdf
    :param inverted_index:
    :return:asdd
    """
    for t in terms:
        dict_from_disc[t.lower()] = dict_from_disc.pop(t)
        inverted_index[t.lower()] = inverted_index.pop(t)


def generate_file_term_dict(terms_list, inverted_idx):
    """
    This function creates a 'file_name' to 'term_list' dictionary for a given term list
    :param terms_list: A list of terms.
    :param inverted_idx: The main inverted index dictionary.
    :return: A dictinoary of key: file_name, value: a list of the terms stored on that file_name.
    """
    file_term_dict = {}
    for term in terms_list:
        if term in inverted_idx:
            if inverted_idx[term][2] in file_term_dict:
                file_term_dict[inverted_idx[term][2]].append(term)
            else:
                file_term_dict[inverted_idx[term][2]] = [term]
    return file_term_dict


def get_query_tweet_ids(term_lst, inverted_idx, output_path):
    """
    This function takes a list of terms generated from a query and returns all relevant tweet_id lists for the terms
    :param output_path:
    :param term_lst: A list of terms.
    :param inverted_idx: The main inverted index dictionary.
    :return: A dictionary of relevant tweets list. (key: term, value: relevant tweets tuple)
    """
    file_term_dict = generate_file_term_dict(term_lst, inverted_idx)
    relevant_docs = {}
    for file_name in file_term_dict.keys():
        dict_from_disc = load_obj(output_path + "/PostingFiles/" + file_name)
        for term in file_term_dict[file_name]:
            relevant_docs[term] = dict_from_disc[term]

    return relevant_docs
