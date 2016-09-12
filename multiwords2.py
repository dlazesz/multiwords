#! /usr/bin/env python3
'''
        Multi-Word Units (MWUs) Extractor based on (Silva and Lopes, 1999)
                    Luís Gomes <luismsgomes@gmail.com>

Bibliography:

Joaquim Ferreira da Silva and Gabriel Pereira Lopes. A Local Maxima method
  and a Fair Dispersion Normalization for extracting multi-word units from
  corpora. In Sixth Meeting on Mathematics of Language, pages 369–381,
  Orlando, USA, 1999.
'''
import collections, os, sys


def avg(ls):
    return sum(ls) / len(ls)

def dice(freq, pref_freqs, suff_freqs):
    return 2 * freq / (avg(pref_freqs) + avg(suff_freqs))

def scp(freq, pref_freqs, suff_freqs):
    return freq ** 2 / avg([pref_freq * suff_freq for pref_freq, suff_freq in zip(pref_freqs, suff_freqs)])

def compute_ngram_glues(n):
    ngram_glues_filename = get_ngram_glues_filename(n)
    with open(ngram_glues_filename + '.tmp', 'w') as output:
        for ngram, freq, pref_freqs, suff_freqs in read_ngram_freqs(n):
            glue = glue_fun(freq, pref_freqs, suff_freqs)
            print(' '.join(ngram), glue, 0, 0, sep='\t', file=output)
    os.rename(ngram_glues_filename + '.tmp', ngram_glues_filename)   

def compute_glues_for_all_ngrams():
    print('computing glues for all ngrams...', end=' ')
    sys.stdout.flush()
    for n in range(2, maxn+2):
        print(n, end=' ')
        sys.stdout.flush()
        compute_ngram_glues(n)
    print('done')

def get_ngrams_in_line(n, line):
    tokens = line.split()
    for i in range(len(tokens) - n):
        yield tuple(tokens[i:i+n])

def get_ngrams(n):
    global text_filename
    with open(text_filename, 'r') as lines:
        for line in lines:
            for ngram in get_ngrams_in_line(n, line):
                yield ngram

def compute_ngram_freqs(n):
    freqs = collections.Counter(get_ngrams(n))
    ngram_freqs_filename = get_ngram_freqs_filename(n)
    with open(ngram_freqs_filename + '.tmp', 'w') as output:
        for ngram, freq in freqs.items():
            print(' '.join(ngram), freq, '', '', sep='\t', file=output)
    os.rename(ngram_freqs_filename + '.tmp', ngram_freqs_filename)

def compute_freqs_for_all_ngrams():
    print('computing frequencies for all ngrams...', end=' ')
    sys.stdout.flush()
    for n in range(1, maxn+2):
        print(n, end=' ')
        sys.stdout.flush()
        compute_ngram_freqs(n)
    print('done')

def cascade_ngram_freqs(subngram_freqs, subn, n):
    ngram_freqs_filename = get_ngram_freqs_filename(n)
    with open(ngram_freqs_filename + '.tmp', 'w') as output:
        for ngram, freq, pref_freqs, suff_freqs in read_ngram_freqs(n):
            pref_freqs.append(subngram_freqs.get(ngram[:subn], 1))
            suff_freqs.insert(0, subngram_freqs.get(ngram[-subn:], 1)) # prepend
            print(' '.join(ngram), freq, ' '.join(map(str, pref_freqs)), ' '.join(map(str, suff_freqs)), sep='\t', file=output)
    os.rename(ngram_freqs_filename + '.tmp', ngram_freqs_filename)

def cascade_freqs_for_all_ngrams():
    global maxn
    print('cascading frequencies for all ngrams...', end=' ')
    sys.stdout.flush()
    for subn in range(1, maxn+1):
        freqs = load_ngram_freqs(subn)
        for n in range(subn + 1, maxn+2):
            print('{}=>{}'.format(subn, n), end=' ')
            sys.stdout.flush()
            cascade_ngram_freqs(freqs, subn, n)
    print('done')

def cascade_ngram_glues(n):
    subngram_glues = load_ngram_glues(n-1)
    ngram_glues_filename = get_ngram_glues_filename(n)
    with open(ngram_glues_filename + '.tmp', 'w') as output:
        for ngram, glue, _, max_superngram_glue in read_ngram_glues(n):
            pref = ngram[:-1]
            suff = ngram[1:]
            pref_glue, _, pref_max_supergram_glue = subngram_glues[pref]
            suff_glue, _, suff_max_supergram_glue = subngram_glues[suff]
            max_subngram_glue = max(pref_glue, suff_glue)
            print(' '.join(ngram), glue, max_subngram_glue, max_superngram_glue, sep='\t', file=output)
            if glue > pref_max_supergram_glue:
                subngram_glues[pref][2] = glue
            if glue > suff_max_supergram_glue:
                subngram_glues[suff][2] = glue
    os.rename(ngram_glues_filename + '.tmp', ngram_glues_filename)
    subngram_glues_filename = get_ngram_glues_filename(n-1)
    with open(subngram_glues_filename + '.tmp', 'w') as output:
        for ngram, (glue, max_subngram_glue, max_superngram_glue) in subngram_glues.items():
            print(' '.join(ngram), glue, max_subngram_glue, max_superngram_glue, sep='\t', file=output)
    os.rename(subngram_glues_filename + '.tmp', subngram_glues_filename)

def cascade_glues_for_all_ngrams():
    global maxn
    print('cascading glues for all ngrams...', end=' ')
    sys.stdout.flush()
    for n in range(3, maxn+2):
        print('{}<=>{}'.format(n-1, n), end=' ')
        sys.stdout.flush()
        cascade_ngram_glues(n)
    print('done')

def select_local_maxima(n):
    output_filename = get_output_filename(n)
    with open(output_filename + '.tmp', 'w') as output:
        for ngram, glue, max_subgrams_glue, max_supergrams_glue in read_ngram_glues(n):
            if glue > (max_subgrams_glue + max_supergrams_glue) / 2:
                print(' '.join(ngram), file=output)
    os.rename(output_filename + '.tmp', output_filename)

def select_local_maxima_for_all_ngrams():
    global maxn
    print('selecting local maxima...', end=' ')
    sys.stdout.flush()
    for n in range(2, maxn+1):
        print(n, end=' ')
        sys.stdout.flush()
        select_local_maxima(n)
    print('done')

def load_ngram_glues(n):
    glues = dict()
    with open(get_ngram_glues_filename(n), 'r') as lines:
        for line in lines:
            cols = line.split('\t')
            if not cols:
                continue
            assert len(cols) == 4
            ngram = tuple(cols[0].split())
            glue, max_subngram_glue, max_supngram_glue = map(float, cols[1:])
            glues[ngram] = [glue, max_subngram_glue, max_supngram_glue]
    return glues

def read_ngram_glues(n):
    with open(get_ngram_glues_filename(n), 'r') as lines:
        for line in lines:
            cols = line.split('\t')
            if not cols:
                continue
            assert len(cols) == 4
            ngram = tuple(cols[0].split())
            glue, max_subngram_glue, max_supngram_glue = map(float, cols[1:])
            yield ngram, glue, max_subngram_glue, max_supngram_glue

def load_ngram_freqs(n):
    freqs = dict()
    with open(get_ngram_freqs_filename(n), 'r') as lines:
        for line in lines:
            cols = line.split('\t')
            if not cols:
                continue
            assert len(cols) == 4
            ngram, freq = cols[:2]
            freqs[tuple(ngram.split())] = int(freq)
    return freqs

def read_ngram_freqs(n):
    with open(get_ngram_freqs_filename(n), 'r') as lines:
        for line in lines:
            cols = line.split('\t')
            if not cols:
                continue
            assert len(cols) == 4
            ngram, freq, pref_freqs, suff_freqs = cols
            yield tuple(ngram.split()), int(freq), list(map(int, pref_freqs.split())), list(map(int, suff_freqs.split()))

def get_ngram_freqs_filename(n):
    global output_dir
    return os.path.join(output_dir, str(n) + 'gram_freqs.txt')

def get_ngram_glues_filename(n):
    global output_dir
    return os.path.join(output_dir, str(n) + 'gram_glues.txt')

def get_output_filename(n):
    global output_dir
    return os.path.join(output_dir, str(n) + 'mwus.txt')

if '__main__' == __name__:
    if 5 != len(sys.argv) or sys.argv[1] not in ('dice', 'scp'):
        print('usage: multiwords (dice|scp) MAXN TEXT OUTDIR', file=sys.stderr)
        sys.exit(1)
    glue_fun = scp if sys.argv[1] == 'scp' else dice
    maxn = int(sys.argv[2])
    text_filename, output_dir = sys.argv[3:]
    if not os.path.isdir(output_dir):
        os.mkdir(output_dir)
    assert os.path.isfile(text_filename)
    assert os.path.isdir(output_dir)
    compute_freqs_for_all_ngrams()
    cascade_freqs_for_all_ngrams()
    compute_glues_for_all_ngrams()
    cascade_glues_for_all_ngrams()
    select_local_maxima_for_all_ngrams()

