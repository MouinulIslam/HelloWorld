import json
import pprint
import sys
from operator import itemgetter
from copy import deepcopy
import ast
import os


from table_distance import distance

VERBOSE = False
current_dir = os.getcwd()

def get_corpus(filename):
    '''
    Load corpus file located at `filename` into a list of dicts
    '''
    with open(filename, 'r') as f:
        corpus = json.load(f)

    if VERBOSE:
        print(corpus)
    return corpus

def get_words(corpus):
    '''
    From a `corpus` object, build a dict whose keys are 'Eng' and 'Ban',
    and whose values are sets. Each dict[language] set contains every
    word in that language which appears in the corpus
    '''
    def source_words(lang):
        for pair in corpus:
            for word in pair[lang].split():
                yield word
    return {lang: set(source_words(lang)) for lang in ('Eng', 'Ban')}


def init_translation_probabilities(corpus):
    '''
    Given a `corpus` generate the first set of translation probabilities,
    which can be accessed as
    p(e|s) <=> translation_probabilities[e][s]
    we first assume that for an `e` and set of `s`s, it is equally likely
    that e will translate to any s in `s`s
    '''
    words = get_words(corpus)
    return {
        word_en: {word_fr: 1.0/len(words['Eng'])
                  for word_fr in words['Ban']}
        for word_en in words['Eng']}


def train_iteration(corpus, words, total_s, prev_translation_probabilities):
    '''
    Perform one iteration of the EM-Algorithm

    corpus: corpus object to train from
    words: {language: {word}} mapping

    total_s: counts of the destination words, weighted according to
             their translation probabilities t(e|s)

    prev_translation_probabilities: the translation_probabilities from the
                                    last iteration of the EM algorithm
    '''
    translation_probabilities = deepcopy(prev_translation_probabilities)

    counts = {word_en: {word_fr: 0 for word_fr in words['Ban']}
              for word_en in words['Eng']}

    totals = {word_fr: 0 for word_fr in words['Ban']}

    for (es, fs) in [(pair['Eng'].split(), pair['Ban'].split())
                     for pair in corpus]:
        for e in es:
            total_s[e] = 0

            for f in fs:
                total_s[e] += translation_probabilities[e][f]

        for e in es:
            for f in fs:
                counts[e][f] += (translation_probabilities[e][f] /
                                 total_s[e])
                totals[f] += translation_probabilities[e][f] / total_s[e]

    for f in words['Ban']:
        for e in words['Eng']:
            translation_probabilities[e][f] = counts[e][f] / totals[f]

    return translation_probabilities


def is_converged(probabilties_prev, probabilties_curr, epsilon):
    '''
    Decide when the model whose final two iterations are
    `probabilties_prev` and `probabilties_curr` has converged
    '''
    delta = distance(probabilties_prev, probabilties_curr)
    if VERBOSE:
        print(delta)

    return delta < epsilon


def train_model(corpus, epsilon):
    '''
    Given a `corpus` and `epsilon`, train a translation model on that corpus
    '''
    words = get_words(corpus)

    total_s = {word_en: 0 for word_en in words['Eng']}
    prev_translation_probabilities = init_translation_probabilities(corpus)

    converged = False
    iterations = 0
    while not converged:
        translation_probabilities = train_iteration(
                                        # this is a disgusting way
                                        # to indent code
                                        corpus, words, total_s,
                                        prev_translation_probabilities
                                    )

        converged = is_converged(prev_translation_probabilities,
                                 translation_probabilities, epsilon)
        prev_translation_probabilities = translation_probabilities
        iterations += 1
    return translation_probabilities, iterations


def summarize_results(translation_probabilities):
    '''
    from a dict of source: {target: p(source|target}, return
    a list of mappings from source words to the most probable target word
    '''
    return {
        # for each english word
        # sort the words it could translate to; most probable first
        k: sorted(v.items(), key=itemgetter(1), reverse=True)
        # then grab the head of that == `(most_probable, p(k|most probable)`
        [0]
        # and the first of that pair (the actual word!)
        [0]
        for (k, v) in translation_probabilities.items()
    }


def main():
    '''
    IBM Model 1 SMT Training Example

    infile: path to JSON file containing English-French sentence pairs
            in the form [ {"Eng": <sentence>, "Ban": <sentence>}, ... ]

    outfile: path to output file (defaults to stdout)

    epsilon: Acceptable euclidean distance between translation probability
             vectors across iterations

    verbose: print running info to stderr
    '''
    global VERBOSE
    epsilon = 0.01
    verbose = False
    VERBOSE = verbose
    infile = current_dir + '/data/sentences.json'
    outfile = current_dir + '/data/output.json'

    if infile == '-':
        corpus = get_corpus(sys.stdin)
    else:
        corpus = get_corpus(infile)

    probabilities, iterations = train_model(corpus, epsilon)
    #print probabilities
    result_table = summarize_results(probabilities)
    if outfile:
        with open(outfile, 'w') as f:
            f.write('{')
            first = 0
            for k,v in result_table.iteritems():
                k = k.encode('utf-8')
                v = v.encode('utf-8')
                if first == 0:
                    f.write('\"' + k +'\": \"' + v + '\"')
                    first = 1
                else:
                    f.write(', \"' + k + '\": \"' + v + '\"')
            f.write('}')
    else:
        json.dump(result_table, sys.stdout)

    if VERBOSE:
        print('Performed {} iterations'.format(iterations))

if __name__ == '__main__':
    main()
