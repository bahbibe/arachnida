#!/usr/bin/env python3
import os
import argparse
import requests
import validators
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from colorama import Fore,Style

ua = UserAgent()

def random_headers():
    return {"User-Agent": ua.random}

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
    print(Fore.CYAN + message + Style.RESET_ALL)
def log_warning(message):
    print(Fore.YELLOW + message + Style.RESET_ALL)
def log_success(message):
    print(Fore.GREEN + message + Style.RESET_ALL)
def log_verbose(message, verbose):
    if verbose:
        log_info(message)

DEFAULT_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.gif', '.bmp')

def parse_args():
    parser = argparse.ArgumentParser(prog="./Spider", description="Spider allows you to scrape images from a website.")
    parser.add_argument("-r", "--recursive", action="store_true", help="Recursively scrape images")
    parser.add_argument("-l", "--level", type=int, default=5, help="Recursion level (default: 5)")
    parser.add_argument("-p", "--path", type=str, default="./data/", help="Directory to save images (default: './data/')")
    parser.add_argument("--all", action="store_true", help="Download all file extensions")
    parser.add_argument("-e", "--extensions", type=str, help="Comma-separated extensions to download (e.g. '.jpg,.png,.webp')")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose progress output")
    parser.add_argument("url", help="URL to scrape images from")
    return parser.parse_args()

def save_image(filename, img_data):
    try:
        with open(filename, 'wb') as f:
            for chunk in img_data.iter_content(1024):
                f.write(chunk)
        log_success(f"Downloaded {filename}")
        return True
    except Exception as e:
        log_error(f"Error saving image {filename}: {e}")
        return False
    

def collect_links(url, level, seen=None, verbose=False):
    if seen is None:
        seen = set()
    if level == 0 or url in seen:
        return []
    seen.add(url)
    try:
        log_verbose(f"Crawling {url} (level {level})", verbose)
        response = requests.get(url, headers=random_headers(), timeout=(3, 10))
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        links = []
        for link in soup.find_all('a', href=True):
            full_url = urljoin(url, link['href'])
            if validators.url(full_url) and full_url not in seen:
                links.append(full_url)
                links.extend(collect_links(full_url, level - 1, seen, verbose))
        return links
    except requests.RequestException as e:
        log_error(f"Error fetching {url}: {e}")
        return []
    
def download_images(links, path, extensions=DEFAULT_EXTENSIONS, verbose=False):
    downloaded_urls = set()
    downloaded_names = set()
    for index, link in enumerate(links, start=1):
        log_info(f"Processing page {index}/{len(links)}")
        log_verbose(f"Page URL: {link}", verbose)
        try:
            response = requests.get(link, headers=random_headers(), timeout=(3, 10))
            response.raise_for_status()
        except requests.RequestException as e:
            log_error(f"Error fetching {link}: {e}")
            continue
        soup = BeautifulSoup(response.text, 'html.parser')
        images = soup.find_all('img')
        log_verbose(f"Found {len(images)} image tag(s)", verbose)
        for img in images:
            if 'src' not in img.attrs:
                continue
            img_url = urljoin(link, img['src'])
            if not validators.url(img_url) or img_url in downloaded_urls:
                continue
            basename = os.path.basename(img_url).split("?")[0]
            if not basename or basename in ('.', '..') or basename in downloaded_names:
                continue
            ext = os.path.splitext(basename)[1].lower()
            if extensions and ext not in extensions:
                continue
            filename = os.path.join(path, basename)
            try:
                img_response = requests.get(img_url, headers=random_headers(), timeout=(3, 10), stream=True)
                img_response.raise_for_status()
            except requests.RequestException as e:
                log_error(f"Error fetching image {img_url}: {e}")
                continue
            if save_image(filename, img_response):
                downloaded_urls.add(img_url)
                downloaded_names.add(basename)
    return len(downloaded_urls)

if __name__ == "__main__":
    banner()
    args = parse_args()
    try:
        if not validators.url(args.url):
            raise ValueError("Invalid URL")
        if args.all and args.extensions:
            raise ValueError("--all and -e are mutually exclusive")
        if args.all:
            extensions = None
        elif args.extensions:
            extensions = tuple(e.strip().lower() if e.strip().startswith('.') else f'.{e.strip().lower()}' for e in args.extensions.split(','))
        else:
            extensions = DEFAULT_EXTENSIONS
        if not os.path.exists(args.path):
            os.makedirs(args.path)
        if args.recursive and args.level < 0:
            raise ValueError("Recursion level must be non-negative")
        if args.recursive:
            log_info("Collecting links...")
            links = collect_links(args.url, args.level, verbose=args.verbose)
            log_info(f"Collected {len(links)} link(s)")
            pages = [args.url] + links
        else:
            pages = [args.url]
        downloaded = download_images(pages, args.path, extensions, args.verbose)
        log_success(f"Finished. Downloaded {downloaded} image(s).")
    except Exception as e:
        log_error(f"Error: {e}")
        exit(1)
    except KeyboardInterrupt:
        log_warning("Process interrupted by user.")
        exit(0)
