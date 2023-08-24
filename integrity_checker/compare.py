import subprocess, os
import pandas as pd
import numpy as np
from collections import defaultdict

def compute_md5_local(path_df, threads):
    path_df.to_csv('/tmp/tmpmd5.lcokelif', index=False, header=False)
    result = subprocess.run(['parallel', '--bar', '-a', '/tmp/tmpmd5.lcokelif', '-j', threads, '-k', 'md5sum', '{}'], stdout=subprocess.PIPE)
    md5 = [ x.split(' ')[0] for x in result.stdout.decode('utf-8').splitlines() ]
    os.remove('/tmp/tmpmd5.lcokelif')
    return md5

def compute_md5_remote(remote_host, path_df, threads):
    path_df.to_csv('/tmp/tmpmd5.rcokelif', index=False, header=False)
    remote_md5 = subprocess.run(['parallel', '--bar', '-a', '/tmp/tmpmd5.rcokelif', '-j', threads, '-k', 'ssh', remote_host, 'md5sum', '{}'], stdout=subprocess.PIPE)
    remote_md5 = [ x.split(' ')[0] for x in remote_md5.stdout.decode('utf-8').splitlines() ] 
    os.remove('/tmp/tmpmd5.rcokelif')
    return remote_md5

def import_local_files(local_dir):
    d = defaultdict(list)
    for root, dirs, files in os.walk(local_dir):
        for file in files:
            file_path=os.path.join(root, file)
            d['Filename'].append(file)
            d['roots'].append(root)
            d['Filepath'] = file_path
    return pd.DataFrame(d)

def id_best_file(remote_file, filename, df):
    match_df = df[df['Filename'] == filename]
    dirname = os.path.dirname(remote_file)
    while True:
        if len(match_df) == 1:
            return os.path.join(str(match_df['roots'].iloc[0]), str(match_df['Filename'].iloc[0])), str(match_df['Local md5'].iloc[0])
        if len(match_df) == 0:
            return np.nan, np.nan
        if len(match_df) > 1:
            dir = os.path.basename(dirname)
            match_df = match_df[match_df['roots'].str.contains(dir, case=True)]
            dirname = os.path.dirname(dirname)
            if dirname == '/':
                return np.nan, np.nan

def import_remote_files(remote_files, local_files):
    d = defaultdict(list)
    for remote_file in remote_files:
        d['Filename'] = os.path.basename(remote_file)
        d['Remote Path'] = remote_file
        if local_files:
            d['Local path'], d['Local md5'] = id_best_file(remote_file, d['Filename'], local_files)
    return pd.DataFrame(d)


def compare_directory_files(local_dir, remote_host_and_dir, summary_file, threads):
    remote_host, remote_dir = remote_host_and_dir.split(':', 1)
    print("Identifying local files...")
    lfile_deets = import_local_files(local_dir)
    print(f"Found {len(lfile_deets)} local files...")
    print("Calculating md5 for local files...")
    lfile_deets['Local md5'] = compute_md5_local(lfile_deets['Filepath'], threads)
    print("Identifying remote files...")
    remote_files = subprocess.run(['ssh', remote_host, 'find', remote_dir, '-type', 'f'], stdout=subprocess.PIPE)
    remote_files = remote_files.stdout.decode('utf-8').strip().split('\n')
    print(f"Found {len(remote_files)} remote files...")
    print("Comparing remote and local files...")
    df = import_remote_files(remote_files, remote_host, lfile_deets)
    df['Remote md5'] = compute_md5_remote(remote_host, df['Remote Path'], threads)
    df['Status'] = np.where(df['Local md5'] == df['Remote md5'], 'Identical', 'Different')
    df.loc[df['Local md5'].isna(), 'Status'] = 'Local file not found'
    df.to_csv(summary_file, sep='\t', index=False)

def build_local_md5_db(local_dir, summary_file, threads):
    print("Identifying local files...")
    lfile_deets = import_local_files(local_dir)
    print(f"Found {len(lfile_deets)} local files...")
    print("Calculating md5 for local files...")
    lfile_deets['Local md5'] = compute_md5_local(lfile_deets['Filepath'], threads)
    lfile_deets = lfile_deets.drop('roots', axis=1)
    lfile_deets.to_csv(summary_file, sep='\t', index=False)


def build_remote_md5_db(remote_host_and_dir, summary_file, threads):
    remote_host, remote_dir = remote_host_and_dir.split(':', 1)
    print("Identifying remote files...")
    remote_files = subprocess.run(['ssh', remote_host, 'find', remote_dir, '-type', 'f'], stdout=subprocess.PIPE)
    remote_files = remote_files.stdout.decode('utf-8').strip().split('\n')
    print(f"Found {len(remote_files)} remote files...")
    df = import_remote_files(remote_files, None)
    df['Remote md5'] = compute_md5_remote(remote_host, df['Remote Path'], threads)
    df.to_csv(summary_file, sep='\t', index=False)
