# Text comparing algorithms

#1 levenshtein distance metric
#--> finds the distance between 2 statements

def levenshtein_distance(text1,text2):
    """
        Compare two statements based on the Levenshtein distance
        of each statement's text.

        For example, there is a 65% similarity between the statements
        "where is the post office?" and "looking for the post office"
        based on the Levenshtein distance algorithm.

        :return: The percent of similarity between the text of the statements.
        :rtype: float
        """
    try:
        from Levenshtein.StringMatcher import StringMatcher as SequenceMatcher
    except ImportError:
        from difflib import SequenceMatcher

    if not text1.text or not text2.text:
        return 0

    text1_text=str(text1.text.lower())
    text2_text = str(text2.text.lower())

    similarity=SequenceMatcher(None,text1_text,text2_text)

    # Calculate a decimal percent of the similarity
    percent = round(similarity.ratio(), 2)

    return percent



#2 synset distance

def synset_distance(text1,text2):
    """
    Calculate the similarity of two statements.
    This is based on the total maximum synset similarity between each word in each sentence.

    This algorithm uses the `wordnet`_ functionality of `NLTK`_ to determine the similarity
    of two statements based on the path similarity between each token of each statement.
    This is essentially an evaluation of the closeness of synonyms.

    :return: The percent of similarity between the closest synset distance.
    :rtype: float

    .. _wordnet: http://www.nltk.org/howto/wordnet.html
    .. _NLTK: http://www.nltk.org/
    """

    from nltk.corpus import wordnet
    from nltk import word_tokenize
    import itertools

    text1_tokens=word_tokenize(text1.text.lower())
    text2_tokens=word_tokenize(text2.text.lower())

    def remove_stopwords(tokens, language):
        """
        Takes a language (i.e. 'english'), and a set of word tokens.
        Returns the tokenized text with any stopwords removed.
        Stop words are words like "is, the, a, ..."
        """
        from nltk.corpus import stopwords

        # Get the stopwords for the specified language
        stop_words = stopwords.words(language)

        # Remove the stop words from the set of word tokens
        tokens = set(tokens) - set(stop_words)

        return tokens

    # Remove all stop words from the list of word tokens
    text1_tokens = remove_stopwords(text1_tokens, language='english')
    text2_tokens = remove_stopwords(text2_tokens, language='english')

    # The maximum possible similarity is an exact match
    # Because path_similarity returns a value between 0 and 1,
    # max_possible_similarity is the number of words in the longer
    # of the two input statements.
    max_possible_similarity = max(
        len(text1.text.split()),
        len(text2.text.split())
    )
    max_similarity = 0.0

    for tup in itertools.product(*[text1_tokens,text2_tokens]):
        synset1=wordnet.synsets(tup[0])
        synset2 = wordnet.synsets(tup[1])

        if synset1 and synset2:

            for synset in itertools.product(*[synset1,synset2]):
                similarity = synset[0].path_similarity(synset[1])

                if similarity and (similarity > max_similarity):
                    max_similarity = similarity

        if max_possible_similarity == 0:
            return 0

        return max_similarity / max_possible_similarity


def sentiment_comparison(text1 , text2):
    """
    Calculate the similarity of two statements based on the closeness of
    the sentiment value calculated for each statement.

    :return: The percent of similarity between the sentiment value.
    :rtype: float
    """

    from nltk.sentiment.vader import SentimentIntensityAnalyzer
    sentiment_analyzer=SentimentIntensityAnalyzer()

    text1_polarity=sentiment_analyzer.polarity_scores(text1.text.lower())
    text2_polarity=sentiment_analyzer.polarity_scores(text2.text.lower())

    statement_greatest_polarity = 'neu'
    statement_greatest_score = -1
    for polarity in sorted(text1_polarity):
        if text1_polarity[polarity] > statement_greatest_score:
            statement_greatest_polarity = polarity
            statement_greatest_score = text1_polarity[polarity]

    statement2_greatest_polarity = 'neu'
    statement2_greatest_score = -1
    for polarity in sorted(text2_polarity):
        if text2_polarity[polarity] > statement2_greatest_score:
            statement2_greatest_polarity = polarity
            statement2_greatest_score = text2_polarity[polarity]

    # Check if the polarity if of a different type
    if statement_greatest_polarity != statement2_greatest_polarity:
        return 0

    values = [statement_greatest_score, statement2_greatest_score]
    difference = max(values) - min(values)

    return 1.0 - difference



def jaccard_similarity(text1, text2, threshold=0.5):
    """
    Calculates the similarity of two statements based on the Jaccard index.

    The Jaccard index is composed of a numerator and denominator.
    In the numerator, we count the number of items that are shared between the sets.
    In the denominator, we count the total number of items across both sets.
    Let's say we define sentences to be equivalent if 50% or more of their tokens are equivalent.
    Here are two sample sentences:

        The young cat is hungry.
        The cat is very hungry.

    When we parse these sentences to remove stopwords, we end up with the following two sets:

        {young, cat, hungry}
        {cat, very, hungry}

    In our example above, our intersection is {cat, hungry}, which has count of two.
    The union of the sets is {young, cat, very, hungry}, which has a count of four.
    Therefore, our `Jaccard similarity index`_ is two divided by four, or 50%.
    Given our threshold above, we would consider this to be a match.

    .. _`Jaccard similarity index`: https://en.wikipedia.org/wiki/Jaccard_index
    """
    from nltk.corpus import wordnet
    import nltk
    import string

    text1_text=text1.text.lower()
    text2_text=text2.text.lower()

    # Get default English stopwords and extend with punctuation
    stopwords = nltk.corpus.stopwords.words('english')
    stopwords.extend(string.punctuation)
    stopwords.append('')
    lemmatizer = nltk.stem.wordnet.WordNetLemmatizer()

    def get_wordnet_pos(pos_tag):
        if pos_tag[1].startswith('J'):
            return (pos_tag[0], wordnet.ADJ)
        elif pos_tag[1].startswith('V'):
            return (pos_tag[0], wordnet.VERB)
        elif pos_tag[1].startswith('N'):
            return (pos_tag[0], wordnet.NOUN)
        elif pos_tag[1].startswith('R'):
            return (pos_tag[0], wordnet.ADV)
        else:
            return (pos_tag[0], wordnet.NOUN)

    ratio = 0
    pos_a = map(get_wordnet_pos, nltk.pos_tag(nltk.tokenize.word_tokenize(text1_text)))
    pos_b = map(get_wordnet_pos, nltk.pos_tag(nltk.tokenize.word_tokenize(text2_text)))

    lemma_a = [lemmatizer.lemmatize(token.strip(string.punctuation), pos) for token, pos in pos_a
               if pos == wordnet.NOUN and token.strip(string.punctuation) not in stopwords]
    lemma_b = [lemmatizer.lemmatize(token.strip(string.punctuation), pos) for token, pos in pos_b
               if pos == wordnet.NOUN and token.strip(string.punctuation) not in stopwords]

    # Calculate Jaccard similarity
    try:
        ratio = len(set(lemma_a).intersection(lemma_b)) / float(len(set(lemma_a).union(lemma_b)))
    except Exception as e:
        print('Error', e)
    return ratio >= threshold

