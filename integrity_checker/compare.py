import subprocess, os

def compute_md5(file_path):
    result = subprocess.run(['md5sum', file_path], stdout=subprocess.PIPE)
    md5 = result.stdout.decode('utf-8').split(' ')[0]
    return md5

def compare_files(local_file, remote_host, remote_file):
    local_md5 = compute_md5(local_file)
    remote_md5 = subprocess.run(['ssh', remote_host, 'md5sum', remote_file], stdout=subprocess.PIPE)
    remote_md5 = remote_md5.stdout.decode('utf-8').split(' ')[0]
    
    return local_md5 == remote_md5

def compare_directory_files(local_dir, remote_host_and_dir, summary_file):
    remote_host, remote_dir = remote_host_and_dir.split(':', 1)
    
    with open(summary_file, 'w') as f:
        f.write("Filename\tLocal Path\tRemote Path\tStatus\n")
        
        remote_files = subprocess.run(['ssh', remote_host, 'find', remote_dir, '-type', 'f'], stdout=subprocess.PIPE)
        remote_files = remote_files.stdout.decode('utf-8').strip().split('\n')
        
        for remote_file in remote_files:
            filename = remote_file.split('/')[-1]
            local_file = subprocess.run(['find', local_dir, '-type', 'f', '-name', filename, '-print', '-quit'], stdout=subprocess.PIPE)
            local_file = local_file.stdout.decode('utf-8').strip()
            
            if local_file:
                identical = compare_files(local_file, remote_host, remote_file)
                status = 'Identical' if identical else 'Different'
            else:
                status = 'Not Found Locally'
            
            f.write(f"{filename}\t{local_file}\t{remote_file}\t{status}\n")
