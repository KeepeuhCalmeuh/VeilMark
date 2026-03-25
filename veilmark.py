#!/usr/bin/env python3
import argparse
import sys
import os
from steganography import encode_data, decode_data

def main():
    parser = argparse.ArgumentParser(description="VeilMark: LSB Steganography Tool to embed text and fingerprint in images.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--encode', action='store_true', help="Encode text into an image")
    group.add_argument('--decode', action='store_true', help="Decode text and fingerprint from an image")
    
    parser.add_argument("file_path", type=str, help="Path to the image file")
    parser.add_argument("text", type=str, nargs='?', help="Text to encode (required if --encode is used)")
    
    args = parser.parse_args()
    
    if args.encode:
        if not args.text:
            print("Error: --encode requires <text> argument.")
            sys.exit(1)
            
        input_path = args.file_path
        if not os.path.exists(input_path):
            print(f"Error: File '{input_path}' not found.")
            sys.exit(1)
            
        dir_name = os.path.dirname(input_path)
        base_name = os.path.basename(input_path)
        output_name = f"FGP_{base_name}"
        
        # Check standard format
        _, ext = os.path.splitext(output_name)
        if ext.lower() in ['.jpg', '.jpeg']:
            print(f"Warning: JPEG is a lossy format. Saving to '{output_name}' might compress and corrupt the hidden data.")
            print("We strongly recommend using PNG images for steganography.")
            
        output_path = os.path.join(dir_name, output_name)
        
        try:
            fingerprint = encode_data(input_path, args.text, output_path)
            print(f"Successfully encoded data into '{output_path}'.")
            print(f"Associated Fingerprint (SHA-256): {fingerprint}")
        except ValueError as e:
            print(f"Error: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"Error during encoding: {e}")
            sys.exit(1)
            
    elif args.decode:
        input_path = args.file_path
        if not os.path.exists(input_path):
            print(f"Error: File '{input_path}' not found.")
            sys.exit(1)
            
        try:
            fingerprint, text = decode_data(input_path)
            print("--- VeilMark Decoding Successful ---")
            print(f"Fingerprint : {fingerprint}")
            print(f"Message     : {text}")
            print("------------------------------------")
        except ValueError as e:
            print(f"Error: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"Error during decoding: {e}")
            sys.exit(1)

if __name__ == "__main__":
    main()
