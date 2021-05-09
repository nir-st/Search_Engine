from nltk.corpus import wordnet as wn


def get_all_synonyms_for_a_sentence(sentence: str):
    final = []
    for word in sentence.split(' '):
        final.extend(get_all_synonyms_for_a_word(word))
    return ' '.join(list(set(final)))


def get_all_synonyms_for_a_word(word: str):
    all_synonyms = []
    for d in wn.synsets(word):
        all_synonyms.extend(d.lemma_names())
    return list(set(all_synonyms)) + [word]
