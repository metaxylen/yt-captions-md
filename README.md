# YT Captions MD

A small CLI that turns YouTube video captions into **Markdown** files in one command.

No API key required. Captions come from [youtube-transcript-api](https://github.com/jdepoix/youtube-transcript-api); title and channel metadata from [yt-dlp](https://github.com/yt-dlp/yt-dlp) (metadata only — no video download).

## Features

- **URL formats:** `youtube.com/watch`, `youtu.be`, `shorts`, extra query params (`&t=`, `&list=`, …)
- **Caption selection:** Manual captions first, then auto-generated; optional `--lang` preference order
- **Readable text:** Merges caption fragments and deduplicates common auto-caption overlaps
- **Markdown output:** Title, URL, channel, language, and caption type in the header
- **Safe filenames:** Derived from the video title; on collision, the video ID is appended (no silent overwrite)
- **Resilience:** Skips bad URLs and missing captions; retries network errors up to 3 times with exponential backoff

## Requirements

- Python **3.10+**
- Network access

## Install

### Global CLI (any directory, any terminal)

Install once so agents and shells can call `yt-captions-md` without opening this repo:

```bash
pip install --user /path/to/yt-captions-md
# or from GitHub:
pip install --user git+https://github.com/metaxylen/yt-captions-md.git
```

Ensure your user scripts directory is on `PATH` (macOS/Linux), e.g. `~/.local/bin` or `~/Library/Python/3.x/bin`.

Optional: default output folder everywhere (instead of `./output` in the current directory):

```bash
export YT_CAPTIONS_OUT="$HOME/yt-transcripts"
```

### Development (repo checkout)

```bash
git clone https://github.com/metaxylen/yt-captions-md.git
cd yt-captions-md
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -e .
```

## Usage

```bash
# After global install (from anywhere)
yt-captions-md "https://www.youtube.com/watch?v=VIDEO_ID"
python -m youtube_transcript URL

# From a repo checkout
python main.py URL

# Multiple videos
yt-captions-md URL1 URL2

# From a file (one URL per line; blank lines and # comments ignored)
yt-captions-md --file urls.txt

# Language preference, paragraph timestamps, output directory
yt-captions-md --lang tr,en --timestamps --out ~/yt-transcripts URL
```

### Options

| Flag | Description |
|------|-------------|
| `--lang tr,en` | Comma-separated language codes; manual captions preferred over auto-generated |
| `--timestamps` | Prefix each paragraph with `[mm:ss]` |
| `--out <dir>` | Output directory (default: `./output`, or `YT_CAPTIONS_OUT` if set) |
| `--file`, `-f` | Path to a URL list file |

## Example output

```markdown
# Video Title

- URL: https://www.youtube.com/watch?v=...
- Channel: Channel Name
- Language: en
- Type: manual

---

Transcript body here, one paragraph per line without blank lines between them...
```

## Project layout

```
├── main.py                 # CLI entrypoint
├── youtube_transcript/
│   ├── urls.py             # Video ID parsing
│   ├── transcript.py       # Fetch captions and retries
│   ├── metadata.py         # Title / channel via yt-dlp
│   ├── markdown.py         # Merge logic and document format
│   ├── files.py            # Filename sanitization and writes
│   └── cli.py              # CLI implementation
├── tests/
├── pyproject.toml
└── requirements.txt
```

## Tests

```bash
python -m unittest discover -s tests -v
```

## License

[MIT](LICENSE)

## Note

This tool only uses publicly available YouTube caption data. You are responsible for complying with copyright and YouTube’s terms of use.
