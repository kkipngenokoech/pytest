#!/usr/bin/env python3

import sys
import argparse
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description='Process some files')
    parser.add_argument('files', nargs='*', help='Files to process')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    if args.verbose:
        print(f"Processing {len(args.files)} files")
    
    for file_path in args.files:
        path = Path(file_path)
        if path.exists():
            print(f"Processing: {path}")
        else:
            print(f"File not found: {path}", file=sys.stderr)
            return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
