#!/usr/bin/env python3

import sys
import argparse
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description='Simple CLI application')
    parser.add_argument('--version', action='version', version='1.0.0')
    parser.add_argument('--input', '-i', help='Input file path')
    parser.add_argument('--output', '-o', help='Output file path')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    if args.verbose:
        print(f"Input: {args.input}")
        print(f"Output: {args.output}")
    
    if args.input:
        input_path = Path(args.input)
        if not input_path.exists():
            print(f"Error: Input file '{args.input}' does not exist", file=sys.stderr)
            return 1
        
        with open(input_path, 'r') as f:
            content = f.read()
        
        if args.output:
            output_path = Path(args.output)
            with open(output_path, 'w') as f:
                f.write(content.upper())
            print(f"Processed content written to {args.output}")
        else:
            print(content.upper())
    else:
        print("Hello, World!")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
