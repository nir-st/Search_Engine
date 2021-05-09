import re


class NumberHandle:

    def handle_numbers(self, split_sentence):
        """
        :param split_sentence: a split sentence.
        :return: the split sentence with a uniform number structure.
        """
        for i in range(len(split_sentence) - 1):
            try:
                if i >= len(split_sentence):
                    break
                if re.match("^[0-9]{1,3}(,[0-9]{3}){1,3}$", split_sentence[i]):
                    split_sentence[i] = split_sentence[i].replace(',', '')
                if split_sentence[i] in Fractions:
                    split_sentence[i] = str(Fractions.get(split_sentence[i]))
                elif split_sentence[i].isnumeric():
                    if split_sentence[i][-1] in Fractions:
                        split_sentence[i] = str(float(split_sentence[i][:-1]) + Fractions[split_sentence[i][-1]])
                    num = normalized = float(split_sentence[i])
                    if 1000 <= num <= 999999:
                        normalized = str(round(num / 1000, 3)) + "K"
                        split_sentence[i] = str(normalized)
                    elif 1000000 <= num <= 999999999:
                        normalized = str(round(num / 1000000, 3)) + "M"
                        split_sentence[i] = str(normalized)
                    elif 1000000000 <= num <= 999999999999:
                        normalized = str(round(num / 1000000000, 3)) + "B"
                        split_sentence[i] = str(normalized)
                    else:
                        if i < len(split_sentence) - 1:
                            following_word = split_sentence[i + 1].lower()
                            if following_word == 'thousand':
                                split_sentence[i] += 'K'
                                del split_sentence[i + 1]
                            elif following_word == 'million':
                                split_sentence[i] += 'M'
                                del split_sentence[i + 1]
                            elif following_word == 'billion':
                                split_sentence[i] += 'B'
                                del split_sentence[i + 1]
            except:
                del split_sentence[i]

        return split_sentence


Fractions = {
    '½': 0.5,
    '⅓': 0.333,
    '¼': 0.25,
    '¾': 0.75,
    '⅔': 0.667,
    '⅕': 0.2
}
