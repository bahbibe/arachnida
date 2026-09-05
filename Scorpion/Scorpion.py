#!/usr/bin/env python3
import os
import time
import curses
import argparse
from colorama import Fore, Style
from PIL import Image, ExifTags

DEFAULT_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.gif', '.bmp')
EXIF_NAME_TO_TAG = {name: tag_id for tag_id, name in ExifTags.TAGS.items()}

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
    parser = argparse.ArgumentParser(prog="./Scorpion", description="Scorpion allows you to extract, modify, and delete EXIF and metadata from images.")
    parser.add_argument("--all", action="store_true", help="Accept all file extensions")
    parser.add_argument("-e", "--extensions", type=str, help="Comma-separated extensions to accept (e.g. '.jpg,.png,.webp')")
    parser.add_argument("-s", "--set", action="append", metavar="TAG=VALUE", help="Set/modify an EXIF tag (e.g. -s Artist=John). Can be repeated.")
    parser.add_argument("-d", "--delete", action="append", metavar="TAG", help="Delete an EXIF tag by name. Can be repeated.")
    parser.add_argument("--delete-all-exif", action="store_true", help="Delete all EXIF tags from the file(s).")
    parser.add_argument("-i", "--tui", action="store_true", help="Launch an interactive terminal UI to view and manage metadata. If no FILE is given, browses image files in the current directory.")
    parser.add_argument("FILE", nargs='*', help="Path to the image file(s). Optional with -i (defaults to the current directory).")
    args = parser.parse_args()
    if not args.FILE and not args.tui:
        parser.error("the following arguments are required: FILE (or pass -i alone to browse the current directory)")
    return args

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

def resolve_tag_id(tag_name):
    tag_id = EXIF_NAME_TO_TAG.get(tag_name)
    if tag_id is not None:
        return tag_id
    if tag_name.isdigit():
        return int(tag_name)
    raise ValueError(f"Unknown EXIF tag '{tag_name}'")

def set_exif_tag(exif, tag_name, value):
    tag_id = resolve_tag_id(tag_name)
    if value.lstrip('-').isdigit():
        value = int(value)
    exif[tag_id] = value

def delete_exif_tag(exif, tag_name):
    tag_id = resolve_tag_id(tag_name)
    if tag_id not in exif:
        raise ValueError(f"Tag '{tag_name}' not set on this file")
    del exif[tag_id]

def save_exif(file, image, exif):
    image.save(file, exif=exif.tobytes())

def edit_file(file, set_list, delete_list, delete_all):
    with Image.open(file) as image:
        image.load()
        exif = image.getexif()
        changed = False
        if delete_all:
            for tag_id in list(exif.keys()):
                del exif[tag_id]
            changed = True
        for tag_name in delete_list or []:
            try:
                delete_exif_tag(exif, tag_name)
                changed = True
            except ValueError as e:
                print(Fore.YELLOW + f"[!] {file}: {e}" + Style.RESET_ALL)
        for pair in set_list or []:
            if '=' not in pair:
                print(Fore.YELLOW + f"[!] {file}: invalid --set value '{pair}', expected TAG=VALUE" + Style.RESET_ALL)
                continue
            tag_name, value = pair.split('=', 1)
            try:
                set_exif_tag(exif, tag_name, value)
                changed = True
            except ValueError as e:
                print(Fore.YELLOW + f"[!] {file}: {e}" + Style.RESET_ALL)
        if changed:
            save_exif(file, image, exif)
            print(Fore.GREEN + f"[+] Updated metadata for {file}" + Style.RESET_ALL)
        else:
            print(Fore.YELLOW + f"[!] No changes applied to {file}" + Style.RESET_ALL)

C_TITLE, C_SELECTED, C_LABEL, C_TAG, C_SUCCESS, C_ERROR, C_HINT = range(1, 8)

def _tui_init_colors():
    curses.use_default_colors()
    curses.init_pair(C_TITLE, curses.COLOR_CYAN, -1)
    curses.init_pair(C_SELECTED, curses.COLOR_BLACK, curses.COLOR_CYAN)
    curses.init_pair(C_LABEL, curses.COLOR_YELLOW, -1)
    curses.init_pair(C_TAG, curses.COLOR_MAGENTA, -1)
    curses.init_pair(C_SUCCESS, curses.COLOR_GREEN, -1)
    curses.init_pair(C_ERROR, curses.COLOR_RED, -1)
    curses.init_pair(C_HINT, curses.COLOR_BLUE, -1)

def _tui_message(stdscr, text, color=C_SUCCESS):
    h, w = stdscr.getmaxyx()
    stdscr.move(h - 1, 0)
    stdscr.clrtoeol()
    stdscr.addstr(h - 1, 0, text[:w - 1], curses.color_pair(color) | curses.A_BOLD)
    stdscr.refresh()
    stdscr.getch()

def _tui_prompt(stdscr, label):
    """Returns the entered text, or None if the user cancelled with Esc."""
    h, w = stdscr.getmaxyx()
    hint = "Esc to cancel"
    text = ""
    curses.curs_set(1)
    try:
        while True:
            stdscr.move(h - 1, 0)
            stdscr.clrtoeol()
            hint_col = max(0, w - len(hint) - 1)
            stdscr.addstr(h - 1, hint_col, hint, curses.color_pair(C_HINT) | curses.A_DIM)
            entry = (label + text)[:max(0, hint_col - 1)]
            stdscr.addstr(h - 1, 0, entry, curses.color_pair(C_LABEL))
            stdscr.move(h - 1, min(len(entry), hint_col - 1))
            stdscr.refresh()
            key = stdscr.getch()
            if key == 27:
                return None
            elif key in (curses.KEY_ENTER, ord('\n'), ord('\r')):
                return text.strip()
            elif key in (curses.KEY_BACKSPACE, 127, 8):
                text = text[:-1]
            elif 32 <= key <= 126 and len(label) + len(text) < hint_col - 2:
                text += chr(key)
    finally:
        curses.curs_set(0)

def _tui_detail(stdscr, file):
    while True:
        info_lines = []
        exif_lines = []
        try:
            with Image.open(file) as image:
                image.load()
                info_lines.append(f"Format: {image.format}   Mode: {image.mode}   Size: {image.size}")
                exif = image.getexif()
                for tag_id, value in exif.items():
                    tag = ExifTags.TAGS.get(tag_id, tag_id)
                    exif_lines.append((str(tag), str(value)))
        except Exception as e:
            info_lines.append(f"Error reading file: {e}")

        stdscr.clear()
        stdscr.addstr(0, 0, f"{file}"[:curses.COLS - 1], curses.color_pair(C_TITLE) | curses.A_BOLD)
        stdscr.addstr(1, 0, "s: set tag   d: delete tag   x: delete all EXIF   b: back", curses.color_pair(C_HINT))
        row = 3
        for line in info_lines:
            stdscr.addstr(row, 0, line[:curses.COLS - 1])
            row += 1
        stdscr.addstr(row, 0, "EXIF:", curses.color_pair(C_SUCCESS) | curses.A_BOLD | curses.A_UNDERLINE)
        row += 1
        if not exif_lines:
            stdscr.addstr(row, 2, "(none)", curses.color_pair(C_HINT))
            row += 1
        else:
            for tag, value in exif_lines:
                stdscr.addstr(row, 2, f"{tag:25}"[:curses.COLS - 3], curses.color_pair(C_TAG) | curses.A_BOLD)
                stdscr.addstr(row, min(28, curses.COLS - 2), f": {value}"[:max(0, curses.COLS - 30)])
                row += 1
        stdscr.refresh()

        key = stdscr.getch()
        if key in (ord('b'), 27):
            break
        elif key == ord('s'):
            tag_name = _tui_prompt(stdscr, "Tag name: ")
            if not tag_name:
                continue
            value = _tui_prompt(stdscr, "Value: ")
            if value is None:
                continue
            try:
                with Image.open(file) as image:
                    image.load()
                    exif = image.getexif()
                    set_exif_tag(exif, tag_name, value)
                    save_exif(file, image, exif)
                _tui_message(stdscr, f"Set {tag_name}. Press any key.", C_SUCCESS)
            except Exception as e:
                _tui_message(stdscr, f"Error: {e}. Press any key.", C_ERROR)
        elif key == ord('d'):
            tag_name = _tui_prompt(stdscr, "Tag name to delete: ")
            if not tag_name:
                continue
            try:
                with Image.open(file) as image:
                    image.load()
                    exif = image.getexif()
                    delete_exif_tag(exif, tag_name)
                    save_exif(file, image, exif)
                _tui_message(stdscr, f"Deleted {tag_name}. Press any key.", C_SUCCESS)
            except Exception as e:
                _tui_message(stdscr, f"Error: {e}. Press any key.", C_ERROR)
        elif key == ord('x'):
            try:
                with Image.open(file) as image:
                    image.load()
                    exif = image.getexif()
                    for tag_id in list(exif.keys()):
                        del exif[tag_id]
                    save_exif(file, image, exif)
                _tui_message(stdscr, "Deleted all EXIF tags. Press any key.", C_SUCCESS)
            except Exception as e:
                _tui_message(stdscr, f"Error: {e}. Press any key.", C_ERROR)

def _tui_main(stdscr, files):
    curses.curs_set(0)
    _tui_init_colors()
    idx = 0
    while True:
        stdscr.clear()
        stdscr.addstr(0, 0, "Scorpion metadata viewer", curses.color_pair(C_TITLE) | curses.A_BOLD)
        stdscr.addstr(1, 0, "up/down to move, enter to open, q to quit", curses.color_pair(C_HINT))
        for i, f in enumerate(files):
            marker = "> " if i == idx else "  "
            attr = curses.color_pair(C_SELECTED) | curses.A_BOLD if i == idx else curses.A_NORMAL
            stdscr.addstr(i + 3, 0, f"{marker}{f}"[:curses.COLS - 1], attr)
        stdscr.refresh()

        key = stdscr.getch()
        if key in (curses.KEY_UP, ord('k')):
            idx = (idx - 1) % len(files)
        elif key in (curses.KEY_DOWN, ord('j')):
            idx = (idx + 1) % len(files)
        elif key in (curses.KEY_ENTER, ord('\n'), ord('\r')):
            _tui_detail(stdscr, files[idx])
        elif key in (ord('q'), 27):
            break

def _tui_single(stdscr, file):
    curses.curs_set(0)
    _tui_init_colors()
    _tui_detail(stdscr, file)

def run_tui(files):
    if not files:
        print(Fore.RED + "[-] No valid files to display." + Style.RESET_ALL)
        return
    if len(files) == 1:
        curses.wrapper(_tui_single, files[0])
    else:
        curses.wrapper(_tui_main, files)

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

    if args.tui and not args.FILE:
        candidates = sorted(f for f in os.listdir('.') if os.path.isfile(f))
    else:
        candidates = args.FILE

    valid_files = []
    for file in candidates:
        if not os.path.isfile(file):
            print(Fore.RED + f"[-] {file} is not a valid file." + Style.RESET_ALL)
            continue
        if extensions and not file.lower().endswith(extensions):
            if args.FILE:
                print(Fore.RED + f"[-] {file} is not a valid image file." + Style.RESET_ALL)
            continue
        valid_files.append(file)

    if args.tui:
        run_tui(valid_files)
        exit(0)

    edit_mode = bool(args.set or args.delete or args.delete_all_exif)
    for file in valid_files:
        if edit_mode:
            try:
                edit_file(file, args.set, args.delete, args.delete_all_exif)
            except Exception as e:
                print(Fore.RED + f"[-] Error editing {file}: {e}" + Style.RESET_ALL)
            continue
        try:
            with Image.open(file) as image:
                read_data(file, image)
                read_exif(file, image)
            print(Fore.GREEN + f"[+] Successfully processed {file}" + Style.RESET_ALL)
        except Exception as e:
            print(Fore.RED + f"[-] Error opening {file}: {e}" + Style.RESET_ALL)
