#!/usr/bin/env python3
import os
import argparse
from colorama import Fore, Style


def banner():
    print(Fore.RED + Style.BRIGHT + r"""
                                 .__               
  ______ ____  _________________ |__| ____   ____  
 /  ___// ___\/  _ \_  __ \____ \|  |/  _ \ /    \ 
 \___ \\  \__(  <_> )  | \/  |_> >  (  <_> )   |  \
/____  >\___  >____/|__|  |   __/|__|\____/|___|  /
     \/     \/            |__|                  \/ 

""" + Style.RESET_ALL)

if __name__ == "__main__":
    banner()