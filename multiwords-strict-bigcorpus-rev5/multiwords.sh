#! /bin/bash
# -*- coding: utf-8, vim: expandtab:ts=4 -*-
#        Multi-Word Units (MWUs) Extractor based on (Silva and Lopes, 1999)
#                     Luís Gomes <luismsgomes@gmail.com>
#
# Bibliography:
#
# Joaquim Ferreira da Silva and Gabriel Pereira Lopes. A Local Maxima method
#   and a Fair Dispersion Normalization for extracting multi-word units from
#   corpora. In Sixth Meeting on Mathematics of Language, pages 369–381,
#   Orlando, USA, 1999.
#
#
# In the description of the algorithm that follows, I use "CHECKPOINT N"
# to refer to some point in the code that is marked at the right margin
# with # N #.
# When I mention "table", I mean a sequence of lines, each line containing
# one or more columns separated by tabs.
#
#
#                     Algorithm/Strategy Description
#
# This is a toplevel description.  Look at the source of the individual
# programs that are invoqued from here to learn about them.
#
# To compute the "glue" of each ngram we need to know the frequency of all
# prefixes and suffixes of that ngram.
# We start by creating a table of ngram frequencies.
# At CHECKPOINT 1 we have a table with two columns:
#   <ngram> <freq>
#
# Next, we want to append to each line a list (in JSON format) containing
# the frequency of each prefix of the ngram in that line.
# Because the table is sorted by ngram, we know that the (n-1)gram prefix
# of one ngram appears in the line immediately above it.  Thus, We just
# have to cascade the frequency of an N-gram Xi to all subsequent ngrams Xj
# as long as Xi is prefix of Xj.
# At CHECKPOINT 2 we have a table with three columns:
#   <ngram> <freq> <prefix_freqs>
# The third column is a JSON list.
#
# Next we do the same for suffixes.
# At CHECKPOINT 3 the ngrams are sorted according to their suffixes.
#
# At CHECKPOINT 4 we have a table with four columns:
#   <ngram> <freq> <prefix_freqs> <suffix_freqs>
# The third and fourth columns are JSON lists.
#
# At CHECKPOINT 5 the unigrams have been discarded because their frequencies
# were cascaded into the other ngrams.
#
# At CHECKPOINT 6 we have computed the "glue" of each ngram. We keep only
# three columns:
#   <ngram> <freq> <glue>
#
# At CHECKPOINT 7 we have marked all ngrams as accepted by appending to
# each line one column consisting of the symbol plus (+):
#   <ngram> <freq> <glue> <+>
#
# Remember that the ngrams are currently sorted by suffix.
# This means that the (n-1)suffix of any ngram comes in the line immediately
# before it.
# Next we compare the glue of each ngram with the glue of the previous one
# (if the previous is a sufix of the current) and we reject the ngram
# having the lowest glue of those two.
# At CHECKPOINT 8 we have marked as rejected all local minima by replacing
# the plus symbol (+) in the last column by a minus (-).
#
# Next we sort the ngrams by prefix and we mark as rejected all local minima
# like the previous step.
# At CHECKPOINT 9 we have rejected local minima from both sides (prefix and
# suffix).
#
# Finally, at CHECKPOINT 10, we have removed from the table:
#   * all the ngrams that were marked as local minima
#   * hapax legomena (ngrams with frequency 1)
#   * the ngrams that were not compared against larger ones, ie, those
#     with n = MAXN+1
#

BIN=$(dirname $0)

if [ $# != 3 ]; then
    echo "usage: $0 (dice|scp) MAXN SORTBUF(there will be two sorts!)" >&2
    exit 1
fi
GFUN=$1
MAXN=$2
MEM=$3

$BIN/ngrams.py $((MAXN + 1)) |
    LANG=C sort -S $MEM | LANG=C uniq -c |
    mawk -v OFS="\t" '{for (i=2; i<NF; i++)
                           printf("%s ", $i); print $NF,$1 }'       # 1 #
    $BIN/cascadefreqs.py |                                          # 2 #
    mawk -F'\t' -v OFS='\t' \
         '{n=split($1, ngram, " "); $1=""      # Split, delete field
           for (i=n; i>1; i--)                 # print REVERSE N-GRAM...
               printf("%s ",ngram[i])          # ...minus the first
           printf("%s%s%s", ngram[1], $0, ORS) # Print the rest
          }' | # "a b c" => "c b a"
    LANG=C sort -t $'\t' -k 1 -S $MEM |                             # 3 #
    $BIN/cascadefreqs.py |                                          # 4 #
    LANG=C grep -v $'^[^ ]*\t' | # drop unigrams                    # 5 #
    $BIN/glue.py $GFUN |
    cut -f 1,2,5 | # keep only three columns: <ngram> <freq> <glue> # 6 #
    mawk -v OFS="\t" '{  # mark all ngrams as accepted
                       print $0,"+"}' |   # (append '\t+')          # 7 #
    $BIN/rejlocalmin.py |                                           # 8 #
    mawk -F'\t' -v OFS='\t' \
         '{n=split($1, ngram, " "); $1=""      # Split, delete field
           for (i=n; i>1; i--)                 # print REVERSE N-GRAM...
               printf("%s ",ngram[i])          # ...minus the first
           printf("%s%s%s", ngram[1], $0, ORS) # Print the rest
          }' | # put the ngrams in the original form
    LANG=C sort -t $'\t' -k 1 -S $MEM | # sort by prefix
    $BIN/rejlocalmin.py |                                           # 9 #
    grep -v  $'^[^\t]*\t1\t.*\t-$' | # drop the rejected ones and hapax legomena (freq = 1)
    cut -f -3 | # drop the last column (accepted/rejected)
    $BIN/dropn.py $((MAXN+1))                                       # 10 #


