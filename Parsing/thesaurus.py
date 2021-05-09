from nltk.corpus import lin_thesaurus as thesaurus


def get_all_synonyms_for_a_sentence(sentence: str):
    final = []
    for word in sentence.split(' '):
        final.extend(get_all_synonyms_for_a_word(word))
    return ' '.join(list(set(final)))


def get_all_synonyms_for_a_word(word: str):
    all_synonyms = []
    for sim in thesaurus.synonyms(word):
        all_synonyms.extend(list(sim[1])[:2])
    return list(set(all_synonyms)) + [word]
