#! /usr/bin/env python3.1
'''
        Multi-Word Units (MWUs) Extractor based on (Silva and Lopes, 1999)
                    Luís Gomes <luismsgomes@gmail.com>

Bibliography:

Joaquim Ferreira da Silva and Gabriel Pereira Lopes. A Local Maxima method
  and a Fair Dispersion Normalization for extracting multi-word units from
  corpora. In Sixth Meeting on Mathematics of Language, pages 369–381,
  Orlando, USA, 1999.
'''
import collections
import sys


def _ngrams(input, maxn):
    for line in input:
        grams = line.rstrip().split()
        if not grams: continue
        for n in range(1, maxn + 1):
            if n > len(grams): break
            for i in range(len(grams) - n + 1):
                yield tuple(grams[i:i + n])


def _splits(ngram):
    assert(len(ngram) > 1)
    for i in range(1, len(ngram)):
        yield ngram[:i], ngram[i:]


def _avg(ls):
    return sum(ls) / len(ls)


def _dice(freq, split_freqs):
    return 2 * freq / sum(map(_avg, zip(*split_freqs)))


def _scp(freq, split_freqs):
    return freq ** 2 / _avg([lfreq * rfreq for lfreq, rfreq in split_freqs])


def _glue(ftab, gfun):
    for ngram, freq in ftab.items():
        if len(ngram) > 1:
            split_freqs = [(ftab[l], ftab[r]) for l, r in _splits(ngram)]
            glue = gfun(freq, split_freqs)
            yield ngram, glue


def _localmaxs(maxn, gtab):
    rej = set()
    for ngram, c in gtab.items():
        n = len(ngram)
        if n == 1:
            rej.add(ngram)
        elif n > 2:
            l = ngram[1:]
            r = ngram[:-1]
            ldiff = c - gtab[l]
            rdiff = c - gtab[r]
            if n > maxn or ldiff < 0 or rdiff < 0:
                rej.add(ngram)
            if ldiff > 0:
                rej.add(l)
            if rdiff > 0:
                rej.add(r)
    return set(gtab) - rej


def multiwords(input, gfun, maxn):
    '''Extract Multi-Word Units (MWUs) from raw text

    Parameters:
        input is a sequence of lines of text
        gfun is the name of the glue measure: either 'dice' or 'scp'
        maxn is the maximum number of tokens in extracted expressions
    '''
    gfuns = {'dice': _dice, 'scp': _scp}
    assert(maxn >= 2)
    assert(gfun in gfuns)
    ftab = collections.Counter(_ngrams(input, maxn + 1))
    gtab = dict(_glue(ftab, gfuns[gfun]))
    for ngram in _localmaxs(maxn, gtab):
        yield ngram, ftab[ngram], gtab[ngram]


if '__main__' == __name__:
    if 3 != len(sys.argv) or sys.argv[1] not in ('dice', 'scp'):
        print('usage: multiwords (dice|scp) MAXN', file=sys.stderr)
        sys.exit(1)
    gfun, maxn = sys.argv[1], int(sys.argv[2])
    for ngram, freq, glue in multiwords(sys.stdin, gfun, maxn):
        print(' '.join(ngram), freq, format(glue, '.4f'), sep='\t')

