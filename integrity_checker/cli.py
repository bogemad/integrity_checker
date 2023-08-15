import argparse
from .compare import compare_files, compare_directory_files

def main():
    parser = argparse.ArgumentParser(description='Compare MD5 checksums of local and remote files.')
    subparsers = parser.add_subparsers(dest='command')
    
    # Single file comparison command
    file_parser = subparsers.add_parser('file', help='Compare a single pair of files.')
    file_parser.add_argument('local_file', help='Path to the local file')
    file_parser.add_argument('remote', help='SSH-compatible remote host string, e.g. "remotehost:/path/to/remote/file"')
    
    # Directory comparison command
    dir_parser = subparsers.add_parser('dir', help='Compare all files in a remote directory with local files.')
    dir_parser.add_argument('local_dir', help='Path to the local directory')
    dir_parser.add_argument('remote_dir', help='SSH-compatible remote host and directory string, e.g. "remotehost:/path/to/remote/directory"')
    dir_parser.add_argument('summary_file', help='Path to the output summary TSV file')
    
    args = parser.parse_args()
    
    if args.command == 'file':
        remote_host, remote_file = args.remote.split(':', 1)
        if compare_files(args.local_file, remote_host, remote_file):
            print("The files are identical.")
        else:
            print("The files are different.")
    elif args.command == 'dir':
        compare_directory_files(args.local_dir, args.remote_dir, args.summary_file)

if __name__ == '__main__':
    main()
