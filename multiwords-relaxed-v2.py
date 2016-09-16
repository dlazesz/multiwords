#!/usr/bin/env python3
# -*- coding: utf-8, vim: expandtab:ts=4 -*-

"""
        Multi-Word Units (MWUs) Extractor based on (Silva and Lopes, 1999)
                    Luís Gomes <luismsgomes@gmail.com>

Bibliography:

Joaquim Ferreira da Silva and Gabriel Pereira Lopes. A Local Maxima method
  and a Fair Dispersion Normalization for extracting multi-word units from
  corpora. In Sixth Meeting on Mathematics of Language, pages 369–381,
  Orlando, USA, 1999.
"""

from typing import Iterable
import collections
import os
import sys


def dice(freq, pref_freqs, suff_freqs):
    pref_freqs = list(pref_freqs)
    suff_freqs = list(suff_freqs)
    return 2 * freq / (sum(pref_freqs) / len(pref_freqs) + sum(suff_freqs) / len(suff_freqs))


def scp(freq, pref_freqs, suff_freqs):
    multiplied_freqs = [pref_freq * suff_freq for pref_freq, suff_freq in zip(pref_freqs, suff_freqs)]
    # freq^2 / sum(avg(multiplied)) = (freq^2 * len(multiplied)) / sum(multiplied) (Latter is more stable numerically)
    return freq ** 2 * len(multiplied_freqs) / sum(multiplied_freqs)


def compute_ngram_glues(glue_f, ngram_freqs_fname, ngram_glues_fname, ngram_glues_fname_tmp):
    with open(ngram_glues_fname_tmp, 'w') as output:
        output.writelines('{0}\t{1}\t0\t0\n'.format(' '.join(ngram), str(glue_f(int(freq),
                                                                                map(int, pref_freqs),
                                                                                map(int, suff_freqs))))
                          for ngram, freq, pref_freqs, suff_freqs in read_ngram_freqs(ngram_freqs_fname))
    os.rename(ngram_glues_fname_tmp, ngram_glues_fname)


def get_ngrams(curr_n, textfilename) -> Iterable[str]:
    with open(textfilename) as lines:
        for line in lines:
            tokens = line.rstrip().split()
            for i in range(len(tokens) - curr_n + 1):  # A BUG IN THE ORIGINAL CODE (FIXED): Last n-gram is not printed
                yield ' '.join(tokens[i:i+curr_n])  # It will be joined on write...


def compute_ngram_freqs(curr_n, textfilename, ngram_freqs_fname, ngram_freqs_fname_tmp):
    with open(ngram_freqs_fname_tmp, 'w') as output:
        output.writelines('{0}\t{1}\t\t\n'.format(ngram, freq)
                          for ngram, freq in collections.Counter(get_ngrams(curr_n, textfilename)).items())
    os.rename(ngram_freqs_fname_tmp, ngram_freqs_fname)


def cascade_ngram_freqs(subngram_freqs, sub_n, ngram_freqs_fname, ngram_freqs_fname_tmp):
    with open(ngram_freqs_fname_tmp, 'w') as output:
        for ngram, freq, pref_freqs, suff_freqs in read_ngram_freqs(ngram_freqs_fname):
            pref_freqs.append(str(subngram_freqs.get(ngram[:sub_n], '1')))
            suff_freqs.append(str(subngram_freqs.get(ngram[-sub_n:], '1')))  # will be prepended by reverse
            print(' '.join(ngram), freq, ' '.join(pref_freqs),
                  ' '.join(reversed(suff_freqs)), sep='\t', file=output)
    os.rename(ngram_freqs_fname_tmp, ngram_freqs_fname)


def cascade_ngram_glues(ngram_glues_fname, ngram_glues_fname_tmp, subngram_glues_fname, subngram_glues_fname_tmp):
    subngram_glues = {ngram: [glue, max_subngram_glue, max_supngram_glue]
                      for ngram, glue, max_subngram_glue, max_supngram_glue in read_ngram_glues(subngram_glues_fname)}

    with open(ngram_glues_fname_tmp, 'w') as output:
        for ngram, glue, _, max_superngram_glue in read_ngram_glues(ngram_glues_fname):
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
    os.rename(ngram_glues_fname_tmp, ngram_glues_fname)

    with open(subngram_glues_fname_tmp, 'w') as output:
        output.writelines('{0}\t{1}\t{2}\t{3}\n'.format(' '.join(ngram), glue, max_subngram_glue, max_superngram_glue)
                          for ngram, (glue, max_subngram_glue, max_superngram_glue) in subngram_glues.items())
    os.rename(subngram_glues_fname_tmp, subngram_glues_fname)


def select_local_maxima(ngram_glues_fname, output_fname, output_fname_tmp):
    with open(output_fname_tmp, 'w') as output:
        output.writelines(' '.join(ngram) + '\n'
                          for ngram, glue, max_subgrams_glue, max_supergrams_glue in read_ngram_glues(ngram_glues_fname)
                          if glue > (max_subgrams_glue + max_supergrams_glue) / 2)
    os.rename(output_fname_tmp, output_fname)


def read_ngram_glues(ngram_glues_fname):
    with open(ngram_glues_fname) as lines:
        for line in lines:
            cols = line.strip().split('\t')
            if cols:
                assert len(cols) == 4
                ngram = tuple(cols[0].split())
                glue, max_subngram_glue, max_supngram_glue = map(float, cols[1:])
                yield ngram, glue, max_subngram_glue, max_supngram_glue


def read_ngram_freqs(ngram_freqs_fname):
    with open(ngram_freqs_fname) as lines:
        for line in lines:
            cols = line.strip('\n').split('\t')
            if cols:
                assert len(cols) == 4
                ngram, freq, pref_freqs, suff_freqs = cols
                # Do not need to map freqs to int as it will be converted to string later...
                yield (tuple(ngram.split()), freq, pref_freqs.split(), suff_freqs.split())

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
    # Create filename pattern for later use
    ngram_freqs_filename = os.path.join(output_dir,  'freqs_for_gram.')
    ngram_freqs_filename_tmp = os.path.join(output_dir,  'tmp_' + 'freqs_for_gram.')
    ngram_glues_filename = os.path.join(output_dir, 'glues_for_gram.')
    ngram_glues_filename_tmp = os.path.join(output_dir, 'tmp_' + 'glues_for_gram.')
    output_filename = os.path.join(output_dir, 'mwus.')
    output_filename_tmp = os.path.join(output_dir, 'tmp_' + 'mwus.')

    # compute freqs for all ngrams
    print('computing frequencies for all ngrams...', end=' ')
    sys.stdout.flush()
    for n in range(1, maxn+2):
        print(n, end=' ')
        sys.stdout.flush()
        compute_ngram_freqs(n, text_filename, ngram_freqs_filename + str(n), ngram_freqs_filename_tmp + str(n))
    print('done')

    # cascade freqs for all ngrams
    print('cascading frequencies for all ngrams...', end=' ')
    sys.stdout.flush()
    for subn in range(1, maxn+1):
        freqs = {ngram: freq for ngram, freq, _, __ in read_ngram_freqs(ngram_freqs_filename + str(subn))}
        for n in range(subn + 1, maxn+2):
            print('{}=>{}'.format(subn, n), end=' ')
            sys.stdout.flush()
            cascade_ngram_freqs(freqs, subn, ngram_freqs_filename + str(n), ngram_freqs_filename_tmp + str(n))
    print('done')

    # compute glues for all ngrams
    print('computing glues for all ngrams...', end=' ')
    sys.stdout.flush()
    for n in range(2, maxn+2):
        print(n, end=' ')
        sys.stdout.flush()
        compute_ngram_glues(glue_fun, ngram_freqs_filename + str(n),
                            ngram_glues_filename + str(n), ngram_glues_filename_tmp + str(n))
    print('done')

    # cascade glues for all ngrams
    print('cascading glues for all ngrams...', end=' ')
    sys.stdout.flush()
    for n in range(3, maxn+2):
        print('{}<=>{}'.format(n-1, n), end=' ')
        sys.stdout.flush()
        cascade_ngram_glues(ngram_glues_filename + str(n), ngram_glues_filename_tmp + str(n),
                            ngram_glues_filename + str(n-1), ngram_glues_filename_tmp + str(n-1))
    print('done')

    # select local maxima for all ngrams
    print('selecting local maxima...', end=' ')
    sys.stdout.flush()
    for n in range(2, maxn+1):
        print(n, end=' ')
        sys.stdout.flush()
        select_local_maxima(ngram_glues_filename + str(n), output_filename + str(n), output_filename_tmp + str(n))
    print('done')
