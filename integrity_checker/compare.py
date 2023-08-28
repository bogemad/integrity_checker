import pandas as pd
from progressbar import progressbar
from collections import defaultdict
from .compute import import_local_files, id_best_file, consolidate_paths, find_singles, match_easy_pairs, compute_md5_remote, compute_md5_local
from .sql import create_table, create_table_statement, create_compare_task
from .mp import compute_md5_in_parallel
import subprocess, os

def compare_directory_files(args, conn):
    if conn:
        create_table(conn, create_table_statement('compare', args.table_name))
    else:
        d = defaultdict(list)
    lfiles = []
    remote_files = []
    for ldir in args.local_dir:
        print(f"Identifying local files in {ldir}...")
        lfiles += import_local_files(ldir)
    ld = consolidate_paths(lfiles)
    remote_files = []
    for rdir in args.remote_dir:
        print(f"Identifying remote files in {rdir}...")
        remote_host, remote_dir = rdir.split(':', 1)
        remote_data = subprocess.run(['ssh', remote_host, 'find', remote_dir, '-type', 'f'], stdout=subprocess.PIPE)
        remote_files += remote_data.stdout.decode('utf-8').strip().split('\n')
    rd = consolidate_paths(remote_files)
    print("Pairing remote and local files...")
    singles = find_singles(rd, ld)
    print(f"Found {len(singles)} remote files not found locally.")
    pairs = match_easy_pairs(rd, ld, singles)
    print(f"Found {len(pairs)} remote and local files with unique filenames")
    print(f"Matching duplicated filenames with different paths")
    easy_remotes = set([s[0] for s in singles] + [ p[0] for p in pairs])
    hard_remotes = []
    for k,v in rd.items():
        for p in v:
            if not p in easy_remotes:
                hard_remotes.append(p)
    for p in progressbar(hard_remotes):
        pairs.append((p, id_best_file(p, ld[os.path.basename(p)])))
    print("Calculating md5 for remote and local files...")
    df = pd.DataFrame(columns=['Remote Path', "Local Path", 'Remote md5', 'Local md5', 'Status'])
    for remote_path, local_path in progressbar(pairs):
        try:
            md5_1 = compute_md5_remote(remote_host, remote_path)
            if local_path == 'File not found':
                md5_2 = 'NA'
                is_equal = 'Local file not found'
            else:
                md5_2 = compute_md5_local(local_path)
                if md5_1 == md5_2:
                    is_equal = 'Identical'
                else:
                    is_equal = 'Different'
            if conn:
                create_compare_task(conn, (f"{remote_host}:{remote_path}", local_path, md5_1, md5_2, is_equal), args.table_name)
            else:
                df.append(pd.Series((f"{remote_host}:{remote_path}", local_path, md5_1, md5_2, is_equal), index=['Remote Path', "Local Path", 'Remote md5', 'Local md5', 'Status']), ignore_index=True)
        except Exception as e:
            # Handle exceptions so that one failure doesn't kill the entire process
            print(e)
            if conn:
                create_compare_task(conn, (f"{remote_host}:{remote_path}", local_path, None, None, e), args.table_name)
            else:
                df.append(pd.Series((f"{remote_host}:{remote_path}", local_path, None, None, e), index=['Remote Path', "Local Path", 'Remote md5', 'Local md5', 'Status']), ignore_index=True)    
    if not conn:    
        df.to_csv(args.summary_file, sep='\t', index=False)

