import re


class Tokenize:

    dict = {"\n": " ", ' percentage': '%', " percent": "%", "①": ''}

    def dict_replacment(self, text):
        for key in self.dict.keys():
            text = text.replace(key, self.dict[key])
        return text

    def handle_hashtag(self, hashtag):
        """
        This function takes a string representing a hashtag and breaks it into tokens
        :param hashtag: a string starting with '#'
        :return: the parsed hashtag as a list
        """
        hashtag_len = len(hashtag)
        if hashtag_len == 1:
            return []
        elif hashtag_len == 2:
            if not hashtag[1].isnumeric():
                return [hashtag[1]]
            return []

        without_hashtag = hashtag[1:]
        if "_" in hashtag:
            tokens = without_hashtag.split('_')
        else:
            tokens = [chunk for chunk in re.split(r"([A-Z][a-z]+)", without_hashtag) if chunk]
        return tokens

    def handle_url(self, text):
        """
        This function takes a string representing a utl and breaks it into tokens
        :param text: string - url
        :return: tokenized url
        """
        text = re.sub(r'[^\w]', ' ', text)
        web_tokens = text.split(' ')
        web_tokens = list(filter(None, web_tokens))
        # web_tokens = re.split('://|[.?]|/|=', text)
        return web_tokens

    def deEmojify(self, text):
        regrex_pattern = re.compile(pattern="["
                                            u"\U0001F600-\U0001F64F"  # emoticons
                                            u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                                            u"\U0001F680-\U0001F6FF"  # transport & map symbols
                                            u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                                            "]+", flags=re.UNICODE)
        return regrex_pattern.sub(r'', text)





