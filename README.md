# Arachnida

A Python web image scraper and image metadata extractor.

## Tools

### Spider
Scrapes images from a website with optional recursive crawling.

### Scorpion
Extracts EXIF data and metadata from local image files.

---

## Setup

### 1. Clone the repo

```bash
git clone https://github.com/your-username/arachnida.git
cd arachnida
```

### 2. Create and activate virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## Usage

### Spider

```bash
# Scrape images from a single page
python Spider/Spider.py <URL>

# Recursively scrape images (default depth: 5)
python Spider/Spider.py -r <URL>

# Set recursion depth
python Spider/Spider.py -r -l 3 <URL>

# Specify output directory
python Spider/Spider.py -p ./my_images/ <URL>

# Download all file extensions (not just defaults)
python Spider/Spider.py --all <URL>

# Download only specific extensions
python Spider/Spider.py -e ".jpg,.png,.webp" <URL>

# Show verbose progress output
python Spider/Spider.py -v <URL>

# Full options
python Spider/Spider.py -r -l 3 -p ./data/ https://example.com
```

**Options:**

| Flag | Description |
|------|-------------|
| `URL` | Target URL (required) |
| `-r, --recursive` | Enable recursive crawling |
| `-l, --level` | Recursion depth (default: 5) |
| `-p, --path` | Output directory (default: `./data/`) |
| `--all` | Download all file extensions |
| `-e, --extensions` | Comma-separated extensions (e.g. `.jpg,.png,.webp`) |
| `-v, --verbose` | Show detailed progress output |

**Validation:** the target URL must be a valid URL, `--all` and `-e` cannot be used together, and `-l` must be a non-negative integer — invalid input prints an error and exits with a non-zero status.

### Scorpion

```bash
# Read metadata from a single image
python Scorpion/Scorpion.py image.jpg

# Read metadata from multiple images
python Scorpion/Scorpion.py image1.jpg image2.png image3.jpeg

# Accept all file extensions
python Scorpion/Scorpion.py --all image.webp image.tiff

# Accept only specific extensions
python Scorpion/Scorpion.py -e ".jpg,.png,.webp" image.jpg
```

**Options:**

| Flag | Description |
|------|-------------|
| `FILE` | Image file(s) to process (required) |
| `--all` | Accept all file extensions |
| `-e, --extensions` | Comma-separated extensions (e.g. `.jpg,.png,.webp`) |

**Default supported formats:** `.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`

**Output includes:** format, mode, size, filename, changed/modified/accessed timestamps, file size, EXIF data (when available), and a per-file success/error status line.

**Validation:** `--all` and `-e` cannot be used together, and each file must exist and have a supported extension — invalid files are skipped with an error message rather than aborting the run.

---

## Dependencies

| Package | Purpose |
|---------|---------|
| requests | HTTP requests |
| beautifulsoup4 | HTML parsing |
| validators | URL validation |
| fake-useragent | Random user-agent rotation |
| colorama | Colored terminal output |
| pillow | Image EXIF/metadata extraction |

---

## Notes

- All HTTP requests include a random user-agent header to avoid being blocked
- Requests have a timeout of 3s (connect) and 10s (read) to prevent hanging
- Only image files with valid extensions are downloaded by default (`.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`)
- Use `--all` to download any file extension, or `-e` to specify custom ones
- Images are saved with their original filenames (query params stripped)
- Duplicate URLs and duplicate output filenames are tracked to prevent redundant/overwriting downloads
