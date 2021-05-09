from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from document import Document
from document import Document
from number_handler import NumberHandle
from tokenizer import Tokenize
from nltk.stem import PorterStemmer


class Parse:

    def __init__(self):
        our_stop_words = ['rt', 'http', 'https', 'com', 'www', 'co', 'my', 'so', 'if', 'like', 'amp', 'get', 'one', "it’s", "don’t", 'dont', 'its']
        self.stop_words = {w: '' for w in our_stop_words + stopwords.words('english')}
        self.ps = PorterStemmer()

    def parse_sentence(self, text, url, stemming=False):
        """
        This function tokenize, remove stop words and apply lower case for every word within the text
        :param stemming:
        :param text:
        :param url:
        :param: stemming
        :return:
        """
        sentence_term_dict = {}
        t = Tokenize()
        text = t.dict_replacment(text)
        text_tokens = text.split(' ')
        nh = NumberHandle()
        text_tokens = nh.handle_numbers(text_tokens)
        tokens_to_add = []
        entities_in_sentence = []
        hashtags_in_sentence = []
        urls_in_sentence = []
        i = 0
        j = 0
        for token in text_tokens:
            if token.lower() in self.stop_words:
                text_tokens.remove(token)
            # if len(token) <= 1:
            #     text_tokens.remove(token)
            if token == '':
                continue
            if len(token) > 0 and token[0] == '#':  # hashtags
                tokens_to_add.extend(t.handle_hashtag(token))
                hashtags_in_sentence.append(token)
            elif token.startswith("http"):  # urls
                new_url = token.replace(token, url)
                tokens_to_add.extend(t.handle_url(new_url))
                # text_tokens.remove(token)
                urls_in_sentence.append(new_url)
            elif '/' in token:
                tokens_to_add.extend(token.split('/'))
                text_tokens.remove(token)

            elif i >= j and len(token) > 1 and token[0].isupper() and token[1].islower():
                cur_entity = token
                j = i
                text_token_len = len(text_tokens)
                while j < i+3:
                    j += 1
                    if j <= text_token_len - 1 and len(text_tokens[j]) > 1 and text_tokens[j][0].isupper() and text_tokens[j][1].islower:
                        cur_entity += " " + text_tokens[j]

                    else:
                        break
                if " " in cur_entity:
                    entities_in_sentence.append(cur_entity)
            i += 1
        text_tokens.extend(tokens_to_add)
        text_tokens_without_stopwords = []
        for token in text_tokens:
            if token == '':
                continue
            lower_token = token.lower()
            if token[0] != '#' and ('corona' in lower_token or 'covid' in lower_token):  # corona terms
                token = 'covid19'
            token = t.deEmojify(token)  # remove emojis
            token = self.clean_token(token)

            if len(token) <= 1:
                continue

            if stemming:
                was_upper = False
                if token[0].isupper():
                    was_upper = True
                token = self.ps.stem(token)
                if was_upper:
                    token = token.upper()

            if token.lower() not in self.stop_words:
                text_tokens_without_stopwords.append(token)

        self.update_sentence_term_dict(text_tokens_without_stopwords, sentence_term_dict)
        self.add_special_tokens_to_sentence_dict(entities_in_sentence, 'entity', sentence_term_dict)
        self.add_special_tokens_to_sentence_dict(hashtags_in_sentence, 'hashtag', sentence_term_dict)
        self.add_special_tokens_to_sentence_dict(urls_in_sentence, 'url', sentence_term_dict)

        return sentence_term_dict

    def update_sentence_term_dict(self, terms, sentence_term_dict):
        for term in terms:
            if term.islower():
                if term.upper() in sentence_term_dict:
                    sentence_term_dict[term] = sentence_term_dict.pop(term.upper())
                    sentence_term_dict[term][0] += 1
                else:
                    if term.startswith('@'):
                        sentence_term_dict[term] = [1, False, 'tag']
                    else:
                        sentence_term_dict[term] = [1, False, 0]
            else:
                if term.lower() in sentence_term_dict:
                    sentence_term_dict[term.lower()][0] += 1
                    sentence_term_dict[term.lower()][1] = True
                else:
                    if term in sentence_term_dict:
                        sentence_term_dict[term][0] += 1
                    else:
                        if term.startswith('@'):
                            sentence_term_dict[term] = [1, False, 'tag']
                        else:
                            sentence_term_dict[term] = [1, True, 0]


    def add_special_tokens_to_sentence_dict(self, terms, term_type, sentence_term_dict):
        for term in terms:
            if term in sentence_term_dict:
                sentence_term_dict[term][0] += 1
            else:
                sentence_term_dict[term] = [1, False, type]


    def parse_doc(self, doc_as_list, toStem):
        """
        This function takes a tweet document as list and break it into different fields
        :param doc_as_list: list re-presenting the tweet.
        :return: Document object with corresponding fields.
        """
        tweet_id = doc_as_list[0]
        tweet_date = doc_as_list[1]
        full_text = doc_as_list[2]
        url = doc_as_list[3]
        retweet_text = doc_as_list[4]
        retweet_url = doc_as_list[5]
        quote_text = doc_as_list[6]
        quote_url = doc_as_list[7]
        term_dict = {}
        tokenized_text = self.parse_sentence(full_text, url, toStem)

        doc_length = 0
        max_tf = 0
        unique_terms = 0

        for term in tokenized_text.keys():
            occurrences_in_doc = tokenized_text[term][0]
            if occurrences_in_doc == 1:
                unique_terms += 1
            if occurrences_in_doc > max_tf:
                max_tf = tokenized_text[term][0]
            doc_length += occurrences_in_doc

        document = Document(tweet_id, tweet_date, full_text, url, retweet_text, retweet_url, quote_text,
                            quote_url, tokenized_text, doc_length)
        return document




    def clean_token(self, token):
        """

        :param token: string
        :return: remove any special character from the string, except @/# at the beginning.
        """
        token_len = len(token)
        if token_len < 1:
            return ''
        first_char = token[0]
        if first_char == '@' and token[-1] == ':':
            return token[:token_len - 1]
        elif first_char != '@' and first_char != '#' and first_char in garbage_symbols:
            token = token[1:]
        token_len = len(token)
        if token_len < 1:
            return ''
        i = 0
        if first_char == '@' or first_char == '#':
            i = 1
        while i < token_len:
            if token[i] in garbage_symbols:
                token = token[:i] + token[i + 1:]
                token_len -= 1
            else:
                i += 1

        return token

garbage_symbols_lst = ['[', ']', '(', ')', '{', '}', ',', '.', ':', '?', '!', '@', '#', '$', '+', '=', '*', '&', '^',
                       "\'",
                       '\"', "\\", "/", '-', ";", '`', '“']

garbage_symbols = {x: '' for x in garbage_symbols_lst}
