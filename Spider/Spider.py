#!/usr/bin/env python3


import os
import argparse
import requests
import validators
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from colorama import Fore,Style

def banner():
        print(Fore.RED + Style.DIM + """
                                 ▄▄▄ ▄▄▄▄  ▄    ▐▌▗▞▀▚▖ ▄▄▄ 
                                ▀▄▄  █   █ ▄    ▐▌▐▛▀▀▘█    
                                ▄▄▄▀ █▄▄▄▀ █ ▗▞▀▜▌▝▚▄▄▖█    
                                     █     █ ▝▚▄▟▌          
                                     ▀                      
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

def collect_links(url, level):
    print(f"Collecting links from {url} at level {level}")
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
    if not os.path.exists(path):
        os.makedirs(path)
    for link in links:
        try:
            response = requests.get(link)
            if response.status_code == 200:
                filename = os.path.join(path, os.path.basename(link))
                with open(filename, 'wb') as f:
                    f.write(response.content)
                log_info(f"Downloaded: {filename}")
            else:
                log_error(f"Failed to download {link}: {response.status_code}")
        except requests.RequestException as e:
            log_error(f"Error downloading {link}: {e}")


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
            print(args.level)
            links = collect_links(args.url, args.level)
            log_info(f"Found {len(links)} links.")
            # download_images(links, args.path)
        # else:
        #     response = requests.get(args.url)
        #     soup = BeautifulSoup(response.text, 'html.parser')
        #     images = [img['src'] for img in soup.find_all('img', src=True)]
        #     log_info(f"Found {len(images)} images.")
            # download_images(images, args.path)
            
    except Exception as e:
        log_error(f"Error: {e}")
        exit(1)
    # except KeyboardInterrupt:
    #     log_error("\nProcess interrupted by user.")
    #     exit(1)
    # except SystemExit:
    #     log_error("\nExiting...")
    #     exit(1)
    # except:
    #     log_error("\nAn unexpected error occurred.")
    #     exit(1)

