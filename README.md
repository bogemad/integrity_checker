# IntegrityChecker

## Overview

`IntegrityChecker` is a Python package offering a command-line utility to verify the integrity of files based on their MD5 checksums. It facilitates comparisons between local and remote files, either individually or within directories. 

## Installation

To install `IntegrityChecker`, use pip:

```bash
pip install integrity_checker
```

For those who prefer a direct source installation:

```
git clone https://github.com/yourusername/integrity_checker.git
cd integrity_checker
pip install .
```

## Usage
### Single File Comparison
To compare an individual file on your local system with a counterpart on a remote host, utilize the file command:

```
integrity_checker file localfile.txt remotehost:/path/to/remotefile.txt

```

This command relays if the two designated files are identical or divergent based on their MD5 checksums.

### Directory-Based File Comparison
For a more comprehensive assessment involving all files within a specified directory on a remote machine (and their corresponding local files), employ the dir command:

```
integrity_checker dir /path/to/local/directory remotehost:/path/to/remote/directory summary.tsv
```

The resulting summary, in TSV (Tab-Separated Values) format, contains two columns: Filename and Status. The Status column can have values: Identical, Different, or Not Found Locally.

## Contributing
We warmly welcome contributions! Feel free to initiate a Pull Request or discuss potential enhancements in the issues section.

## License
IntegrityChecker is governed under the MIT License. For more details, refer to the LICENSE.md file.
