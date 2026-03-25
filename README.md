# VeilMark

VeilMark is a command-line tool that allows you to hide a text message and a unique fingerprint inside an image using Least Significant Bit (LSB) steganography. This modifies the image's pixels so slightly that it is imperceptible to the human eye, without changing the image's resolution.

The hidden data includes a SHA-256 fingerprint (acting as a crypto-signature) that allows anyone decoding the image to verify the integrity and origin of the embedded text.

For now, the tool is only able to encode and decode messages in PNG images, and isn't really robust. It's more usable as a little security when sharing images if you need to trace the origin of the image or if you want to hide a message inside it.

## Requirements

- Python 3.6+
- Pillow (Python Imaging Library)

## Installation

Install the required dependencies using pip:

```bash
pip install -r requirements.txt
```

## Usage

You can use the tool to either encode a message into an image or decode a message from an already marked image.

### Encoding

To hide a text inside an image:

```bash
python veilmark.py --encode <file_path> "<text>"
```

Example:
```bash
python veilmark.py --encode photo.png "This is my secret message"
```

This will create a new file named `FGP_photo.png` in the same directory, containing the hidden message and its generated fingerprint.

**Note on Image Formats:** It is highly recommended to use lossless image formats (like PNG or BMP). Lossy formats like JPEG compress the image data and will destroy the carefully placed LSB hidden data. If you pass a JPEG image, it is recommended to convert it or accept that the signature could be lost.

### Decoding

To extract the fingerprint and the message from a marked image:

```bash
python veilmark.py --decode FGP_<file_path>
```

Example:
```bash
python veilmark.py --decode FGP_photo.png
```

The console will output the fingerprint (signature) and the associated text message.
