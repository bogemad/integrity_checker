import argparse

def get_args():
    parser = argparse.ArgumentParser(description='Compare MD5 checksums of files within local and remote directories.')
    parser.add_argument('-l', '--local_dir', nargs='+', default=None, help='Path to the local directory')
    parser.add_argument('-r', '--remote_dir', nargs='+', default=None, help='SSH-compatible remote host and directory string, e.g. "remotehost:/path/to/remote/directory"')
    parser.add_argument('-s', '--summary_file', default=None, help='Path to the output summary TSV file')
    parser.add_argument('-t', '--threads', default=1, help='Number of threads for md5 calculation')
    parser.add_argument('-d', '--database', default=None, help='Optionally save output tables as a sqlite database. Include path to database file.')
    parser.add_argument('-n', '--table_name', default=None, help='Table name for sqlite database.')
    
    args = parser.parse_args()
    return args

