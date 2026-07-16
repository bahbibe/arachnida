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

### Scorpion

```bash
# Read metadata from a single image
python Scorpion/Scorpion.py image.jpg

# Read metadata from multiple images
python Scorpion/Scorpion.py image1.jpg image2.png image3.jpeg
```

Supported formats: `.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`

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
- Only image files with valid extensions are downloaded
- Images are saved with their original filenames (query params stripped)
