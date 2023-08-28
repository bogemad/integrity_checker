from multiprocessing import Pool, Queue
from .compute import compute_md5_local, compute_md5_remote
from .args import get_args

def compute_md5_in_parallel(file_tuples):
    args = get_args()
    num_processes = args.threads
    output_queue = Queue()
    
    with Pool(num_processes) as pool:
        pool.starmap_async(worker, [(file_tuple, output_queue) for file_tuple in file_tuples])

        # Count the processed files
        processed_count = 0
        while processed_count < len(file_tuples):
            yield output_queue.get()
            processed_count += 1


def worker(file_tuple, output_queue):
    args = get_args()
    remote_host, remote_dir = args.remote_dir.split(':', 1)
    path1, path2 = file_tuple
    try:
        md5_1 = compute_md5_remote(path1)
        if path2 == 'File not found':
            md5_2 = 'NA'
            is_equal = 'Local file not found'
        else:
            md5_2 = compute_md5_local(path2)
            if md5_1 == md5_2:
                is_equal = 'Identical'
            else:
                is_equal = 'Different'
        output_queue.put((f"{remote_host}:{path1}", path2, md5_1, md5_2, is_equal))
    except Exception as e:
        # Handle exceptions so that one failure doesn't kill the entire process
        output_queue.put((f"{remote_host}:{path1}", path2, None, None, e))

