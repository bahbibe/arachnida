#!/usr/bin/env python3
import os
import time
import argparse
from colorama import Fore, Style
from PIL import Image, ExifTags

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
    parser.add_argument("FILE",nargs='+', help="Path to the image file.")
    return parser.parse_args()

def read_exif(file):
    try:
        image = Image.open(file)
        exif_data = image._getexif()
        if exif_data is not None:
            print(Fore.GREEN + f"[+] EXIF data for {file}:" + Style.RESET_ALL)
            for tag_id, value in exif_data.items():
                tag = ExifTags.TAGS.get(tag_id, tag_id)
                print(f"{tag:25}: {value}")
        else:
            print(Fore.YELLOW + f"[!] No EXIF data found in {file}" + Style.RESET_ALL)
    except Exception as e:
        print(Fore.RED + f"[-] Error processing {file}: {e}" + Style.RESET_ALL)



def read_data(file):
    try:
        img = Image.open(file)
        if img.info:
            print(Fore.GREEN + f"[+] Metadata for {file}:" + Style.RESET_ALL)
            for key, value in img.info.items():
                print(f"{key:25}: {value}")
            print(f"{'Format':25}: {img.format}")
            print(f"{'Mode':25}: {img.mode}")
            print(f"{'Size':25}: {img.size}")
            print(f"{'Filename':25}: {img.filename}")
            print(f"{'Created':25}: {time.ctime(os.path.getctime(file))}")
            print(f"{'Modified':25}: {time.ctime(os.path.getmtime(file))}")
            print(f"{'Accessed':25}: {time.ctime(os.path.getatime(file))}")
            print(f"{'File Size':25}: {os.path.getsize(file)} bytes")
        else:
            print(Fore.YELLOW + f"[!] No metadata found in {file}" + Style.RESET_ALL)
    except Exception as e:
        print(Fore.RED + f"[-] Error processing {file}: {e}" + Style.RESET_ALL)


if __name__ == "__main__":
    banner()
    args = parse_args()
    files = args.FILE
    for file in files:
        validate = os.path.isfile(file)
        if not validate:
            print(Fore.RED + f"[-] {file} is not a valid file." + Style.RESET_ALL)
            continue
        if file.lower().endswith(('.jpg', '.jpeg','.png', '.gif', '.bmp')):
            read_data(file)
            if file.lower().endswith(('.jpg', '.jpeg')):
                read_exif(file)
        else:
            print(Fore.RED + f"[-] {file} is not a valid image file." + Style.RESET_ALL)
            continue
    print(Fore.GREEN + f"[+] Successfully processed {file}" + Style.RESET_ALL)