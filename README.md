# Multiwords
Implementation for the LocalMaxs algorithm for extracting multiword units (MWUs) from plain text, described in (Silva and Lopes, 1999)

## Description

These programs implement the LocalMaxs algorithm for extracting multiword units (MWUs) from plain text, described in ([Silva and Lopes, 1999](http://research.variancia.com/multiwords/#silva99)).
There are two versions of the algorithm: strict and relaxed. (The paper describes the strict version.)

There are two implementations of strict LocalMaxs:
If your corpus is large then it is possible that only bigcorpus version is able to cope with it.
Otherwise, you may choose the relaxed version for its greater recall or the strict version for its greater precision.

## Versions

Originally there were four versions available, which were incorporated into three as seen below:

- Simple version: _multiwords 1.2_ strict and relaxed versions (This implementation is not suitable for large corpora because it requires lots of memory.)
- Strict-bigcorpus version: _multiwords 1.5 bigcorpus-rev5_ strict version (This can handle huge corpora. See details above.).)
- Relaxed version: _multiwords 2.0_ relaxed version (Uses somewhat lesser memory works on disk, slow.)

## Usage

### Simple version

Command syntax:

Requirements: Python 3

> ./multiwords.py dice|scp strict|relaxed MAXN
For example this command will extract bigrams and trigrams from the given corpus, using scp as the "glue" function:

> ./multiwords.py scp strict 3 < corpus.txt > mwus.txt

### Relaxed version

Note: A bug fixed since the original version.  See source code for details.

Requirements: Python 3

> ./multiwords2.py dice|scp MAXN TEXTFILE OUTPUTDIR

MAXN is an integer ≥ 2

TEXTFILE is the corpus file, previously tokenized and lowercased

OUTPUTDIR is the name of a directory (it will be created if it doesn't exist) where the program writes temporary and output files. The output files will be named OUTPUTDIR/Nmwus.txt, N being 2, 3, ..., MAXN.

For example this command will extract bigrams and trigrams from the given corpus, using scp as the "glue" function:

> ./multiwords2.py scp 3 corpus.txt results

The output files will be results/2mwus.txt and results/3mwus.txt

### Strict-bigcorpus version

Note: This version is highly optimised for speed, and the handling of big corpora. This repository contains the original version (in a previous commit). That version need perl, sed and Python 3 to work.

Requirements:
- [MAWK](http://invisible-island.net/mawk/) as [it is the fastest AWK implementation available!](https://brenocon.com/blog/2009/09/dont-mawk-awk-the-fastest-and-most-elegant-big-data-munging-language/)
- Standard Unix tools: grep, cut, sort, uniq
- Nothing else...

> ./multiwords-strict-bigcorpus-rev5/multiwords.sh dice|scp MAXN SORTBUF < input.txt > output.txt

SORTBUF: __There is four sorts in the pipeline__, so you should not add more than 90% of your system's memory!

You should __export TEMPDIR=/much_space/__ because the big temporary files!



For example:

> ./multiwords-strict-bigcorpus-rev5/multiwords.sh dice 3 90% < input.txt > output.txt

## License

This modified code is made available under the GNU Lesser General Public License v3.0:
The original code available from [here](http://research.variancia.com/multiwords/) and [here](http://research.variancia.com/multiwords2/) (also available in this repository) are under the [Creative Commons Attribution 3.0 Unported License](http://creativecommons.org/licenses/by/3.0/) by the authors authors Joaquim Ferreira da Silva and José Gabriel Pereira Lopes.
My modifications are licensed under the [GNU GPL v3.0](https://www.gnu.org/licenses/gpl-3.0.en.html) license (CC-BY-3.0 -> CC-BY-SA 3.0 -> CC-BY-SA 4.0 -> GNU GPL v3.0).

## Reference

If you use this implementation of the original Local Maxima algorithm please cite the following paper:

A Local Maxima method and a Fair Dispersion Normalization for extracting multi-word units from corpora.
Joaquim Ferreira da Silva, and José Gabriel Pereira Lopes.
In Proceedings of the Sixth Meeting on Mathematics of Language (MOL6), Orlando, Florida July 23-25, 1999. pp. 369-381.
([pdf](http://hlt.di.fct.unl.pt/jfs/MOL99.pdf))

    @inproceedings{da1999local,
      title={A local maxima method and a fair dispersion normalization for extracting multi-word units from corpora},
      author={Silva, Joaquim Ferreira da and Lopes, José Gabriel Pereira},
      booktitle={Sixth Meeting on Mathematics of Language},
      pages={369--381},
      year={1999}
    }
