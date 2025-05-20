#!/usr/bin/env python3
import os
import argparse
import requests
import validators
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from colorama import Fore,Style

def banner():
        print(Fore.RED + Style.BRIGHT + r"""
               .__    .___            
  ____________ |__| __| _/___________ 
 /  ___/\____ \|  |/ __ |/ __ \_  __ \
 \___ \ |  |_> >  / /_/ \  ___/|  | \/
/____  >|   __/|__\____ |\___  >__|   
     \/ |__|           \/    \/       
""" + Style.RESET_ALL)
        
def log_error(message):
    print(Fore.RED + message + Style.RESET_ALL)
def log_info(message):
    print(Fore.GREEN + message + Style.RESET_ALL)
def log_warning(message):
    print(Fore.YELLOW + message + Style.RESET_ALL)
def log_success(message):
    print(Fore.BLUE + message + Style.RESET_ALL)

def parse_args():
    parser = argparse.ArgumentParser(prog="./Spider", description="Spider allows you to scrape images from a website.")
    parser.add_argument("-r", "--recursive", action="store_true", help="Recursively scrape images")
    parser.add_argument("-l", "--level", type=int, default=5, help="Recursion level (default: 5)")
    parser.add_argument("-p", "--path", type=str, default="./data/", help="Directory to save images (default: './data/')")
    parser.add_argument("url", help="URL to scrape images from")
    return parser.parse_args()

def save_image(filename, img_data):
    try:
        with open(filename, 'wb') as f:
            for chunk in img_data.iter_content(1024):
                f.write(chunk)
        log_success(f"Downloaded {filename}")
    except Exception as e:
        log_error(f"Error saving image {filename}: {e}")
        exit(1)
    

def collect_links(url, level):
    if level == 0:
        return []
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        links = []
        for link in soup.find_all('a', href=True):
            full_url = urljoin(url, link['href'])
            if validators.url(full_url):
                links.append(full_url)
                links.extend(collect_links(full_url, level - 1))
        return links
    except requests.RequestException as e:
        log_error(f"Error fetching {url}: {e}")
        return []
    
def download_images(links, path):
    try:
        for link in links:
            response = requests.get(link)
            soup = BeautifulSoup(response.text, 'html.parser')
            images = soup.find_all('img')
            for img in images:
                if 'src' not in img.attrs:
                    continue
                img_url = urljoin(link, img['src'])
                if validators.url(img_url):
                    basename = os.path.basename(img_url).split("?")[0]
                    if not os.path.splitext(basename)[1].lower() in ('.jpg', '.jpeg', '.png', '.gif', '.bmp'):
                        continue
                    filename = os.path.join(path, basename)
                    save_image(filename, requests.get(img_url, stream=True))
    except requests.RequestException as e:
        log_error(f"Error fetching images from {link}: {e}")
        exit(1)

if __name__ == "__main__":
    banner()
    args = parse_args()
    try:
        if not validators.url(args.url):
            raise ValueError("Invalid URL")
        if not os.path.exists(args.path):
            os.makedirs(args.path)
        if args.recursive and args.level < 0:
            raise ValueError("Recursion level must be non-negative")
        if args.recursive:
            links = collect_links(args.url, args.level)
            download_images(links, args.path)
        else:
            download_images([args.url], args.path)
    except Exception as e:
        log_error(f"Error: {e}")
        exit(1)
    except KeyboardInterrupt:
        log_warning("Process interrupted by user.")
        exit(0)
