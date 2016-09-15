#! /usr/bin/env python3
"""
        Multi-Word Units (MWUs) Extractor based on (Silva and Lopes, 1999)
                    Luís Gomes <luismsgomes@gmail.com>

Bibliography:

Joaquim Ferreira da Silva and Gabriel Pereira Lopes. A Local Maxima method
  and a Fair Dispersion Normalization for extracting multi-word units from
  corpora. In Sixth Meeting on Mathematics of Language, pages 369–381,
  Orlando, USA, 1999.
"""
import collections
import sys


def _avg(ls):
    return sum(ls) / len(ls)


def _dice(frequency, split_freqs):
    return 2 * frequency / sum(map(_avg, zip(*split_freqs)))


def _scp(freqency, split_freqs):
    multiplied_freqs = [pref_freq * suff_freq for pref_freq, suff_freq in split_freqs]
    return freqency ** 2 / (sum(multiplied_freqs) / len(multiplied_freqs))


def get_ngrams(inp, max_n):
    for line in inp:
        tokens = line.rstrip().split()
        for curr_n in range(1, max_n + 1):
            # For len(grams) < n including empty line the line is skipped
            for i in range(len(tokens) - curr_n + 1):
                yield tuple(tokens[i:i + curr_n])


def _localmaxs_relaxed(max_n, gtab):
    submax = collections.defaultdict(float)  # default 0.0
    supmax = collections.defaultdict(float)
    for n_gram, c in gtab.items():
        if len(n_gram) > 2:
            l, r = n_gram[1:], n_gram[:-1]
            submax[n_gram] = max(gtab[l], gtab[r])
            if c > supmax[l]:
                supmax[l] = c
            if c > supmax[r]:
                supmax[r] = c
    for n_gram, c in gtab.items():
        n = len(n_gram)
        if n == 2 and c > supmax[n_gram] or 2 < n <= max_n and c > (submax[n_gram] + supmax[n_gram]) / 2.0:
            yield n_gram


def _localmaxs_strict(max_n, gtab):
    rej = set()
    for n_gram, c in gtab.items():
        n = len(n_gram)
        if n == 1:
            rej.add(n_gram)
        elif n > 2:
            l, r = n_gram[1:], n_gram[:-1]
            gl = gtab[l]
            gr = gtab[r]
            if n > max_n or c < gl or c < gr:
                rej.add(n_gram)
            else:
                if c > gl:
                    rej.add(l)
                if c > gr:
                    rej.add(r)
    return set(gtab) - rej


def multiwords(inp, g_fun, maxima_fname, max_n):
    """Extract Multi-Word Units (MWUs) from raw text

    Parameters:
        input is a sequence of lines of text
        gfun is the name of the glue measure: either 'dice' or 'scp'
        maxn is the maximum number of tokens in extracted expressions
    """
    gfuns = {'dice': _dice, 'scp': _scp}
    maximas = {'strict': _localmaxs_strict, 'relaxed': _localmaxs_relaxed}
    assert(max_n >= 2)
    assert(g_fun in gfuns)
    assert(maxima_fname in maximas)
    glue_f = gfuns[g_fun]
    maxima_f = maximas[maxima_fname]
    # Creating frequency table
    ftab = collections.Counter(get_ngrams(inp, max_n + 1))
    # Creating glue table
    gtab = {n_gram: glue_f(freqency, [(ftab[n_gram[:i]], ftab[n_gram[i:]]) for i in range(1, len(n_gram))])
            for n_gram, freqency in ftab.items() if len(n_gram) > 1}
    # Computing maximas from glue table
    for n_gram in maxima_f(max_n, gtab):
        yield n_gram, ftab[n_gram], gtab[n_gram]

if '__main__' == __name__:
    if 4 != len(sys.argv) or (sys.argv[1] not in ('dice', 'scp') and sys.argv[2] not in ('strict', 'relaxed')):
        print('usage: multiwords (dice|scp) (strict|relaxed) MAXN', file=sys.stderr)
        sys.exit(1)
    gfun, maxima, maxn = sys.argv[1], sys.argv[2], int(sys.argv[3])
    sys.stdout.writelines('{0}\t{1}\t{2:.4f}\n'.format(' '.join(ngram), freq, glue)
                          for ngram, freq, glue in multiwords(sys.stdin, gfun, maxima, maxn))
