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

# The Main difference between the gluing methods:
# 1) sum: In Dice: reversed summing, In SCP: reversed multiplication
# 2) freq: In Dice: 2*freq, In SCP: freq^2
# The rest is the same.

# Dice gluing method:
# Note (1): len(pref_freqs) == len(suff_freqs) is always true, so the code is simplified
# Note (2): For numerical stability avg is splitted: 2*freq *len(pref_freqs) / sum(...)
# 1) Split the prefix and suffix freqs to an array (separated by space no need of JSON)
# 2) Apply the glue function: 2*freq / avg(pref_freqs) + avg(suff_freqs))
dice="mawk -F$'\t' -v OFS=$'\t' '{len = split(\$3, pref_freqs, \" \");
                                        split(\$4, suff_freqs, \" \");
                                  sum = 0;
                                  for (i=1; i <= len; i++) sum += pref_freqs[i] + suff_freqs[len+1-i];
                                  print \$0, 2*\$2 *len / sum
                                 }'"

# SCP gluing method:
# Note (1): len(pref_freqs) == len(suff_freqs) is always true, so the code is simplified
# Note (2): For numerical stability avg is splitted: freq^2 *len(pref_freqs) / sum(...)
# 1) Split the prefix and suffix freqs to an array (separated by space no need of JSON)
# 2) Apply the glue function: freq^2 / avg([pref_freq * suff_freq] for ... in zip(pref_freqs, suff_freqs)])
scp="mawk -F$'\t' -v OFS=$'\t' '{len = split(\$3, pref_freqs, \" \");
                                       split(\$4, suff_freqs, \" \");
                                 sum = 0;
                                 for (i=1; i <= len; i++) sum += (pref_freqs[i] *suff_freqs[len+1-i]);
                                 print \$0, \$2^2 *len / sum
                                }'"

# Cascade frequencies (onesided version, as it will be run twice):
# 1) Store the prefixes of current element by joining them (prefix = [(ngram, freq) for in prefix if ...]
# 2) Print the current n-gram with the computed prefix frequencies
# 3) Add the current n-gram to the "prefix array" with an additional space for full word match
# 4) Make a new prefix array and maintain the length (counter loop is faster, than iterating)
cascadefreqs="mawk -F$'\t' -v OFS=$'\t' 'BEGIN {p_len = 0}
                                        {sep_p = \"\";
                                         sep_f = \"\";
                                         joined_p = \"\";
                                         joined_f = \"\";
                                         for (p_cur=1;  p_cur <= p_len; p_cur++) {
                                             if (index(\$1, prefixes_p[p_cur]) == 1) {
                                                 joined_p = joined_p sep_p prefixes_p[p_cur];
                                                 joined_f = joined_f sep_f prefixes_f[p_cur];
                                                 sep_p = FS;
                                                 sep_f = \" \"
                                             }
                                         }
                                         print \$0, joined_f;
                                         joined_p = joined_p sep_p \$1 \" \";
                                         joined_f = joined_f sep_f \$2;
                                         p_len = split(joined_p, prefixes_p, FS);
                                                 split(joined_f, prefixes_f, \" \")
                                        }'"

# Reject local minima (Strict, onesided version, as it will be run twice):
# Note (1): The Relaxed version can not be separated by sides, therefore must implemented in an other way
# 1) Simulate stack: while (stack and stack[-1].isprefixof(ngram)) print(stack.pop())
# 2) Do the rejection: if ... elif ...
# 3) Append the new elem on stack: stack.append(line)
# 4) Finally print the stack
rejlocalmin="mawk -F$'\t' -v OFS=$'\t' 'BEGIN {s_len = 0}
                                       {sep_p = \"\";
                                        sep_f = \"\";
                                        joined_p = \"\";
                                        joined_f = \"\";
                                        while (s_len > 0 && index(\$1, stack_n[s_len] \" \") != 1){
                                            print stack_n[s_len], stack_f[s_len], stack_g[s_len], stack_s[s_len];
                                            s_len--
                                        }
                                        if (s_len > 0){
                                            if (stack_g[s_len] < \$3)
                                                stack_s[s_len] = \"-\";
                                            else if (stack_g[s_len] > \$3)
                                                \$4 = \"-\"
                                        }
                                        s_len++;
                                        stack_n[s_len] = \$1;
                                        stack_f[s_len] = \$2;
                                        stack_g[s_len] = \$3;
                                        stack_s[s_len] = \$4
                                        }
                                        END {for (s_curr=s_len; s_curr > 0; s_curr--)
                                                 print stack_n[s_curr], stack_f[s_curr], stack_g[s_curr], stack_s[s_curr]
                                        }'"

# Reverse the first field (n-gram):
# 1) Split the first field and delete it form the original string
# 2) Print reverse minus the last one (beause the separator) == ' '.join(reversed(...))
# 2) Print the last elem of the n-gram and the rest of the fields
revngrams="mawk -F$'\t' -v OFS=$'\t' '{n=split(\$1, ngram, \" \"); \$1=\"\";
                                       for (i=n; i>1; i--) printf(\"%s \",ngram[i]);
                                       printf(\"%s%s%s\", ngram[1], \$0, ORS)
                                       }'"

if [ $# != 3 ]; then
    echo "usage: $0 (dice|scp) MAXN SORTBUF(there will be four sorts)!" >&2
    exit 1
elif [ "$1" == "dice" ]; then
    GFUN=$dice
elif [ "$1" == "scp" ]; then
    GFUN=$scp
else
    echo "Wrong function name ($1) chose from dice or scp!" >&2
    exit 1
fi

MAXN=$2
MEM=$3

mawk -v maxn=$((MAXN + 1)) '{min = maxn < NF ? maxn : NF; m = NF + 1
                             for (n=1; n <= min; n++)
                                 for (i=1; i <= m - n; i++) {
                                     for (j = i; j <= (i + n - 2); j++)
                                         printf("%s%s", $j, OFS)
                                     print $(i + n - 1)
                                 }
                             }' |
    LANG=C sort -S $MEM | LANG=C uniq -c |
    mawk -v OFS=$'\t' '{for (i=2; i<NF; i++)
                           printf("%s ", $i); print $NF,$1 }' |      # 1 #
    eval $cascadefreqs |                                             # 2 #
    eval $revngrams |  # "a b c" => "c b a"
    LANG=C sort -t $'\t' -k 1 -S $MEM |                              # 3 #
    eval $cascadefreqs |                                             # 4 #
    LANG=C grep -v $'^[^ ]*\t' |  # drop unigrams                    # 5 #
    eval $GFUN |  # There is no significant speedup on integrating cut and the next mawk...
    cut -f 1,2,5 |  # keep only three columns: <ngram> <freq> <glue> # 6 #
    mawk -v OFS="\t" '{  # mark all ngrams as accepted
                       print $0,"+"}' |  # (append '\t+')            # 7 #
    eval $rejlocalmin |                                              # 8 #
    eval $revngrams |  # put the ngrams in the original form
    LANG=C sort -t $'\t' -k 1 -S $MEM |  # sort by prefix
    eval $rejlocalmin |                                              # 9 #
    LANG=C grep -Fv $'\t1\t' |  # drop hapax legomena (freq = 1)
    LANG=C grep -v $'\t-$' |  # drop the rejected ones and
    cut -f -3 |  # drop the last column (accepted/rejected)
    mawk -F$'\t' -v OFS=$'\t'\
                -v n=$((MAXN+1)) '{len=split($1, a, " ")  # cut and grep is faster then MAWK!
                                   if (n != len) print $0}' |        # 10 #
    LANG=C sort -S $MEM -t$'\t' -k3gr