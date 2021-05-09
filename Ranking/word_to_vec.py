import gensim
import time


class W2V:
    def __init__(self, model):
        self.model = model
        self.top_terms = ['covid19', 'mask', 'pandemic', 'wear', 'people', 'twitter', 'status', 'trump', 'masks', 'us', 'web',
             'virus', 'cases', 'new', 'wearing', 'like', '#COVID19', 'amp', 'one', 'get', 'lockdown', 'positive',
             'schools', '19', 'time', 'quarantine', 'it’s', 'news', 'deaths', 'face', 'go', 'health', 'would',
             'going', 'day', 'don’t', 'tested', 'today', 'social', 'need', 'still', 'know', 'please', 'home',
             'dont', 'back', 'even', 'think', 'vaccine', 'world', '2020', 'see', 'want', 'work', 'school', 'right',
             'reopen', 'president', 'i’m', 'florida', 'make', 'says', 'public', 'data', 'first', 'many', 'good',
             '@REALDONALDTRUMP', 'said', 'say', 'everyone', 'every', 'could', 'country', 'got', 'testing',
             'distancing', 'due', 'cdc', 'government', 'take', 'stop', 'died', 'im', 'months', 'test', 'really',
             'state', 'since', 'breaking', 'help', 'death', 'can’t', 'also', 'never', 'way', '#CORONAVIRUS', 'much',
             'states', 'kids']
        self.top_terms_dict = {}

    def get_terms_vector(self, term):
        global oov_count
        global oov
        """
        returns a vector matching the given term.
        :param term: string.
        :return: vector.
        """
        if term in self.top_terms_dict:
            return self.top_terms_dict[term]
        elif term in self.top_terms:
            if term not in self.top_terms_dict:
                if 'covid' in term.lower() or 'corona' in term.lower():
                    self.top_terms_dict[term] = self.model['pandemic']
                elif 'trump' in term:
                    self.top_terms_dict[term] = self.model['DONALD_TRUMP']
                elif term in self.model:
                    self.top_terms_dict[term] = self.model[term]
                else:
                    self.top_terms_dict[term] = []
            return self.top_terms_dict[term]
        elif term[0] == '@' or term[0] == '#':
            return []
        elif term in self.model:
            return self.model[term]
        term_lower = term.lower()
        term_upper = term.upper()
        if term_lower in self.model:
            return self.model[term_lower]
        elif term_upper in self.model:
            return self.model[term_upper]
        elif term.replace(' ', '_') in self.model:
            return self.model[term.replace(' ', '_')]
        elif term_upper.replace(' ', '_') in self.model:
            return self.model[term_upper.replace(' ', '_')]
        elif "corona" in term_lower or 'covid' in term_lower:
            return self.model['pandemic']
        return []
