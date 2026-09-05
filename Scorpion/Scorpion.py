#!/usr/bin/env python3
import os
import time
import argparse
from colorama import Fore, Style
from PIL import Image, ExifTags

DEFAULT_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.gif', '.bmp')

def banner():
    print(Fore.RED + Style.BRIGHT + r"""
                                 .__
   ______ ____  _________________ |__| ____   ____
  /  ___// ___\/  _ \_  __ \____ \|  |/  _ \ /    \
  \___ \\  \__(  <_> )  | \/  |_> >  (  <_> )   |  \
 /____  >\___  >____/|__|  |   __/|__|\____/|___|  /
      \/     \/            |__|                  \/

""" + Style.RESET_ALL)

def parse_args():
    parser = argparse.ArgumentParser(prog="./Scorpion", description="Scorpion allows you to extract EXIF and metadata from images.")
    parser.add_argument("--all", action="store_true", help="Accept all file extensions")
    parser.add_argument("-e", "--extensions", type=str, help="Comma-separated extensions to accept (e.g. '.jpg,.png,.webp')")
    parser.add_argument("FILE", nargs='+', help="Path to the image file.")
    return parser.parse_args()

def read_exif(file, image):
    try:
        exif_data = image.getexif()
        if exif_data:
            print(Fore.GREEN + f"[+] EXIF data for {file}:" + Style.RESET_ALL)
            for tag_id, value in exif_data.items():
                tag = ExifTags.TAGS.get(tag_id, tag_id)
                print(f"{tag:25}: {value}")
        else:
            print(Fore.YELLOW + f"[!] No EXIF data found in {file}" + Style.RESET_ALL)
    except Exception as e:
        print(Fore.RED + f"[-] Error reading EXIF from {file}: {e}" + Style.RESET_ALL)

def read_data(file, image):
    try:
        print(Fore.GREEN + f"[+] Metadata for {file}:" + Style.RESET_ALL)
        print(f"{'Format':25}: {image.format}")
        print(f"{'Mode':25}: {image.mode}")
        print(f"{'Size':25}: {image.size}")
        print(f"{'Filename':25}: {image.filename}")
        print(f"{'Changed':25}: {time.ctime(os.path.getctime(file))}")
        print(f"{'Modified':25}: {time.ctime(os.path.getmtime(file))}")
        print(f"{'Accessed':25}: {time.ctime(os.path.getatime(file))}")
        print(f"{'File Size':25}: {os.path.getsize(file)} bytes")
        if image.info:
            for key, value in image.info.items():
                print(f"{key:25}: {value}")
        else:
            print(Fore.YELLOW + f"[!] No extra metadata found in {file}" + Style.RESET_ALL)
    except Exception as e:
        print(Fore.RED + f"[-] Error reading metadata from {file}: {e}" + Style.RESET_ALL)


if __name__ == "__main__":
    banner()
    args = parse_args()
    if args.all and args.extensions:
        print(Fore.RED + "[-] --all and -e are mutually exclusive" + Style.RESET_ALL)
        exit(1)
    if args.all:
        extensions = None
    elif args.extensions:
        extensions = tuple(e.strip().lower() if e.strip().startswith('.') else f'.{e.strip().lower()}' for e in args.extensions.split(','))
    else:
        extensions = DEFAULT_EXTENSIONS
    files = args.FILE
    for file in files:
        if not os.path.isfile(file):
            print(Fore.RED + f"[-] {file} is not a valid file." + Style.RESET_ALL)
            continue
        if extensions and not file.lower().endswith(extensions):
            print(Fore.RED + f"[-] {file} is not a valid image file." + Style.RESET_ALL)
            continue
        try:
            with Image.open(file) as image:
                read_data(file, image)
                read_exif(file, image)
            print(Fore.GREEN + f"[+] Successfully processed {file}" + Style.RESET_ALL)
        except Exception as e:
            print(Fore.RED + f"[-] Error opening {file}: {e}" + Style.RESET_ALL)
