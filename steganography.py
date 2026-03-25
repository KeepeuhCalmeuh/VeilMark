import hashlib
import struct
import os
from PIL import Image

MAGIC_HEADER = b"VEILMARK"

def generate_fingerprint(text: str) -> str:
    """Generate a SHA-256 fingerprint for the given text."""
    return hashlib.sha256(text.encode('utf-8')).hexdigest()

def _bytes_to_bits(data: bytes):
    """Convert bytes to a generator of bits (0s and 1s)."""
    for byte in data:
        for i in range(7, -1, -1):
            yield (byte >> i) & 1

def _bits_to_bytes(bit_list: list) -> bytes:
    """Convert a list of bits to bytes."""
    byte_array = bytearray()
    for i in range(0, len(bit_list), 8):
        byte_val = 0
        for bit in bit_list[i:i+8]:
            byte_val = (byte_val << 1) | bit
        byte_array.append(byte_val)
    return bytes(byte_array)

def encode_data(image_path: str, text: str, output_path: str):
    """
    Encode text and its fingerprint into the given image using LSB.
    It does not change the image resolution and changes are visually imperceptible.
    """
    img = Image.open(image_path)
    
    # Store original mode and convert to RGBA for consistency in pixel manipulation
    original_mode = img.mode
    if img.mode not in ('RGB', 'RGBA'):
        img = img.convert('RGBA')

    # Prepare payload
    fingerprint = generate_fingerprint(text)
    fingerprint_bytes = fingerprint.encode('utf-8')
    text_bytes = text.encode('utf-8')
    
    # Payload format: MAGIC(8) + FINGERPRINT(64) + LENGTH(4) + TEXT(...)
    payload_length = struct.pack(">I", len(text_bytes))
    payload = MAGIC_HEADER + fingerprint_bytes + payload_length + text_bytes
    
    pixels = list(img.getdata())
    total_pixels = len(pixels)
    channels = len(pixels[0])
    max_bits = total_pixels * channels
    payload_bits = len(payload) * 8
    
    if payload_bits > max_bits:
        raise ValueError(f"Image is too small to hold the provided text. Required bits: {payload_bits}, Available: {max_bits}")
        
    bit_gen = _bytes_to_bits(payload)
    
    encoded_pixels = []
    bit_exhausted = False
    
    for pixel in pixels:
        if bit_exhausted:
            encoded_pixels.append(pixel)
            continue
            
        new_pixel = list(pixel)
        for i in range(channels):
            try:
                bit = next(bit_gen)
                # Modify LSB: clear the last bit, then set it to our payload bit
                new_pixel[i] = (new_pixel[i] & ~1) | bit
            except StopIteration:
                bit_exhausted = True
                break
        encoded_pixels.append(tuple(new_pixel))
        
    encoded_img = Image.new(img.mode, img.size)
    encoded_img.putdata(encoded_pixels)
    
    # In order to preserve LSBs, the image should be saved ideally as PNG. 
    # Calling code determines the output extension.
    if original_mode == 'P':
        # Don't revert to P mode if originally P, because palette modifications via LSB don't work the same way.
        # Keeping it RGBA is safer for fidelity. But the user might notice color mode changed.
        pass

    encoded_img.save(output_path)
    return fingerprint

def decode_data(image_path: str) -> tuple:
    """
    Decode fingerprint and text from the given image using LSB.
    """
    img = Image.open(image_path)
    if img.mode not in ('RGB', 'RGBA'):
        img = img.convert('RGBA')
        
    pixels = list(img.getdata())
    channels = len(pixels[0])
    
    def extract_bits():
        """Generator to infinitely extract bits from the image."""
        for pixel in pixels:
            for i in range(channels):
                yield pixel[i] & 1
                
    bit_gen = extract_bits()
    
    def read_bytes(n: int) -> bytes:
        bits = []
        for _ in range(n * 8):
            try:
                bits.append(next(bit_gen))
            except StopIteration:
                raise ValueError("Unexpected end of image data. Not a valid VeilMark image.")
        return _bits_to_bytes(bits)
        
    # Read Magic Header
    magic = read_bytes(len(MAGIC_HEADER))
    if magic != MAGIC_HEADER:
        raise ValueError("No valid VeilMark signature found in the image. The image is either not encoded, or uses lossy compression that corrupted the data.")
        
    # Read Fingerprint (64 bytes hex string)
    fingerprint = read_bytes(64).decode('utf-8')
    
    # Read Payload Length (4 bytes)
    length_bytes = read_bytes(4)
    text_length = struct.unpack(">I", length_bytes)[0]
    
    # Read Text
    text_bytes = read_bytes(text_length)
    text = text_bytes.decode('utf-8')
    
    # Optional fingerprint verification
    expected_fingerprint = generate_fingerprint(text)
    if fingerprint != expected_fingerprint:
        print("WARNING: Fingerprint mismatch. The text may have been tampered with or corrupted.")
        
    return fingerprint, text
