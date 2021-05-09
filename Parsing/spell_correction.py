from spellchecker import SpellChecker


def correct_spelling(sentence: str):
    """
    this function gets a sentence as str and and returns a corrected sentence as str
    :param sentence:
    :return:
    """
    spell = SpellChecker()
    corrected_sentence = ''
    splited = sentence.split(' ')
    for word in splited:
        word = word.replace('.', '')
        corrected = spell.correction(word)
        corrected_sentence += corrected + ' '
    return corrected_sentence[:-1]


"""
run code below to check the spell checker on the queries
"""
# import pandas as pd
# import os
# queries = pd.read_csv(os.path.join('data', 'queries_train.tsv'), sep='\t')
# for i, row in queries.iterrows():
#     q_id = row['query_id']
#     q_keywords = row['keywords']
#     print(correct_spelling(q_keywords))
