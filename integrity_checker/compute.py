import pandas as pd
import numpy as np
import os, subprocess
from collections import defaultdict
from progressbar import progressbar
import sys


def id_best_file(remote_file, l):
    filename = os.path.basename(remote_file)
    dirname = os.path.dirname(remote_file)

    while True:
        if len(l) == 1:
            return os.path.join(l[0])
        if len(l) == 0:
            return 'File not found'
        if len(l) > 1:
            dir = os.path.basename(dirname)
            l = [ p for p in l if dir in p]
            dirname = os.path.dirname(dirname)
            if dirname == '/' or dirname == '':
                return 'File not found'

def compute_md5_local(path):
    result = subprocess.run(['md5sum', path], stdout=subprocess.PIPE)
    return result.stdout.decode('utf-8').split(' ')[0]

def compute_md5_remote(remote_host, path):
    result = subprocess.run(['ssh', remote_host, 'md5sum', path], stdout=subprocess.PIPE)
    return result.stdout.decode('utf-8').split(' ')[0]

def import_local_files(local_dir):
    file_paths = []
    for root, dirs, files in os.walk(local_dir):
        for file in files:
            file_paths.append(os.path.join(root, file))
    return file_paths

def consolidate_paths(paths):
    d = defaultdict(list)
    for path in paths:
        d[os.path.basename(path)].append(path)
    return d

def find_singles(r, l):
    singles = []
    rl = list(r)
    s = set(list(l))
    for key in progressbar(rl):
        if not key in s:
            singles.append((r[key][0], 'File not found'))
    return singles

def match_easy_pairs(r, l, singles):
    nd1 = {}
    s = set([a[0] for a in singles])
    print("Finding unique remote filenames...")
    for k,v in progressbar(r.items()):
        if len(v) == 1 and not v[0] in s:
            nd1[k] = v[0]
    print(f"{len(nd1)} found.")
    print("Finding unique local filenames...")
    nd2 = {}
    for k,v in progressbar(l.items()):
        if len(v) == 1:
            nd2[k] = v[0]
    print(f"{len(nd2)} found.")
    print("Saving unique filename pairs...")
    easy_pairs = []
    for k, v in progressbar(nd1.items()):
        easy_pairs.append((v,nd2[k]))
    return easy_pairs

def head(l, i):
    print(l[:i])