import argparse
from .compare import compare_directory_files, build_local_md5_db, build_remote_md5_db

def main():
    parser = argparse.ArgumentParser(description='Compare MD5 checksums of files within local and remote directories.')
    parser.add_argument('-l', '--local_dir', default=None, help='Path to the local directory')
    parser.add_argument('-r', '--remote_dir', default=None, help='SSH-compatible remote host and directory string, e.g. "remotehost:/path/to/remote/directory"')
    parser.add_argument('-s', '--summary_file', required=True, help='Path to the output summary TSV file')
    parser.add_argument('-t', '--threads', default=1, help='Number of threads for md5 calculation')
    
    args = parser.parse_args()
    
    if args.local_dir and args.remote_dir:
        compare_directory_files(args.local_dir, args.remote_dir, args.summary_file, args.threads)
    if args.local_dir:
        build_local_md5_db(args.local_dir, args.summary_file, args.threads)
    if args.remote_dir:
        build_remote_md5_db(args.remote_dir, args.summary_file, args.threads)


if __name__ == '__main__':
    main()
