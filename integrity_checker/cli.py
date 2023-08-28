import argparse, sys
from .compare import compare_directory_files
from .calc_md5 import build_local_md5_db, build_remote_md5_db
from .sql import create_connection
from .args import get_args

def main():
    args = get_args()
    if args.database:
        if not args.table_name:
            sys.exit("SQL Database table name option (-n/--table_name) is required with -d/--database.")
        if args.summary_file:
            sys.exit("Use either -s/--summary_file or -d/--database. Cannot use both.")
        sqlconn = create_connection(args.database)
    else:
        sqlconn = None

    if args.local_dir and args.remote_dir:
        compare_directory_files(args, sqlconn)
    if args.local_dir:
        build_local_md5_db(args, sqlconn)
    if args.remote_dir:
        build_remote_md5_db(args, sqlconn)

if __name__ == '__main__':
    main()
