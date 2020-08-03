#! /usr/bin/env python

import sys
import os.path

should_have_quote_set = set(['u_id', 't_id', 're_t_tid', 're_u_id',
                             'qu_t_id', 'qu_u_id'])
might_have_quote_set = set(['qu_n_qu', 'qu_n_re',  'qu_n_rt', 'qu_n_fav',
                            'rt_n_qu', 'rt_n_re',
                            're_t_id', 'rt_t_tid', 'rt_n_rt',
                            'rt_u_id', 'rt_n_fav'])

fname = sys.argv[1]
assert fname.endswith('.tsv')

def maybe_rm_quote(word, label):
    if label in should_have_quote_set and word:
        assert word.startswith('\''), ('%s %s has no single quote'
                                       % (label, word))
        try:
            ignored = int(word[1:])
        except ValueError:
            raise RuntimeError('%s %s not parseable as int'
                               % (label, word[1:]))
        return word[1:]
    elif label in might_have_quote_set and word:
        if word.startswith('\''):
            try: 
                ignored = int(word[1:])
            except ValueError:
                raise RuntimeError('%s %s not parseable as int'
                                   % (label, word[1:]))
            return word[1:]
        else:
            return word
    else:
        return word

with open(fname, 'rU') as f:
    line = f.readline()
    line = line.strip('\n')
    labels = line.split('\t')
    sys.stdout.write('%s\n' % '\t'.join(labels))
    for line in f.readlines():
        line = line.strip('\n')
        words = line.split('\t')
        out_words = [maybe_rm_quote(wd, lbl)
                     for wd, lbl in zip(words, labels)]
        sys.stdout.write('%s\n' % '\t'.join(out_words))




