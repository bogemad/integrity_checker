from .compute import import_local_files, compute_md5_local, compute_md5_remote
from .sql import create_table, create_table_statement, create_calc_md5_task, check_entry_exists
import subprocess
import pandas as pd
from collections import defaultdict
from progressbar import progressbar

def build_local_md5_db(args, conn):
    if conn:
        create_table(conn, create_table_statement('calc_md5', args.table_name))
    else:
        d = defaultdict(list)
    
    lfiles = []
    for ldir in args.local_dir:
        print(f"Identifying local files in {ldir}...")
        lfiles += import_local_files(ldir)
    print("Calculating md5 for local files...")
    for path in progressbar(lfiles):
        if conn:
            if check_entry_exists(conn, args.table_name, 'path', path):
                continue
        md5 = compute_md5_local(path)
        if conn:
            create_calc_md5_task(conn, (path, md5), args.table_name)
        else:
            d['Path'] = path
            d['md5'] = md5
    if conn:
        conn.close()
    else:
        df = pd.Dataframe(d)
        df.to_csv(args.summary_file, sep='\t', index=False)


def build_remote_md5_db(args, conn):
    if conn:
        create_table(conn, create_table_statement('calc_md5', args.table_name))
    else:
        d = defaultdict(list)
    for rdir in args.remote_dir:
        remote_host, remote_dir = rdir.split(':', 1)
        print(f"Identifying remote files in {rdir}...")
        remote_files = subprocess.run(['ssh', remote_host, 'find', remote_dir, '-type', 'f'], stdout=subprocess.PIPE)
        remote_files = remote_files.stdout.decode('utf-8').strip().split('\n')
    for path in progressbar(remote_files):
        if conn:
            if check_entry_exists(conn, args.table_name, 'path', path):
                continue
        md5 = compute_md5_remote(remote_host, path)
        if conn:
            create_calc_md5_task(conn, (f"{remote_host}:{path}", md5), args.table_name)
        else:
            d['Path'] = f"{remote_host}:{path}"
            d['md5'] = md5
    if conn:
        conn.close()
    else:
        df = pd.Dataframe(d)
        df.to_csv(args.summary_file, sep='\t', index=False)
