# YouTube transcript archive

The Eric de Jesús Rodríguez Mendoza archive keeps its inventory and provider
status in the repository. Full transcript text stays in ignored local storage
until its redistribution rights are clarified.

## Repository layout

- `data/inventories/ericdejes.json`: 893-video inventory.
- `private/transcripts/ericdejes/`: full Markdown transcripts, intentionally not committed.
- `data/status/`: append-only provider results and failures.
- `scripts/supadata_transcripts.py`: Supadata native-caption provider.
- `scripts/channel_archive.py`: yt-dlp/YouTube fallback provider.

The Supadata provider uses `mode=native` and `text=false`: it retrieves existing
timestamped captions and does not request paid AI generation. Videos without
native captions remain in the status file for the VPS fallback.

## Credentials

Do not put API keys in the repository. Create this file on each machine:

```bash
mkdir -p ~/.config/shaul
vim ~/.config/shaul/supadata.env
chmod 600 ~/.config/shaul/supadata.env
```

The file should contain:

```bash
SUPADATA_API_KEY=your_key_here
```

Before running a provider:

```bash
set -a
source ~/.config/shaul/supadata.env
set +a
```

## Supadata pass

Run a small pilot first:

```bash
python3 scripts/supadata_transcripts.py \
  data/inventories/ericdejes.json \
  --limit 10 \
  --workers 4
```

Resume the full native-caption pass later with the same command without
`--limit`; existing files under `private/transcripts/` are skipped.

Supadata also provides a paid asynchronous batch endpoint. After confirming
that the account has batch access, process the remaining videos with:

```bash
python3 scripts/supadata_batch.py data/inventories/ericdejes.json
```

## VPS fallback

On an Ubuntu VPS:

```bash
sudo apt update
sudo apt install -y python3-venv ffmpeg
python3 -m venv ~/.venvs/transcripts
~/.venvs/transcripts/bin/pip install -U yt-dlp
```

Clone or pull this repository, load the key file, and run the fallback against
the private transcript output directory:

```bash
~/.venvs/transcripts/bin/python scripts/channel_archive.py transcripts \
  data/inventories/ericdejes.json \
  --transcript-dir private/transcripts/ericdejes \
  --status-file data/status/ericdejes.ytdlp.jsonl \
  --workers 2
```

The fallback skips transcripts already written by Supadata and records each
remaining result in the status file.

## Local source search

After a transcript pass, rebuild the local query index from the archive:

```bash
npm run sources:db:reindex
npm run sources:db:search -- "cordero"
```

The database at `private/sources/index.sqlite3` is disposable and ignored by
Git. Its default source directory is `private/transcripts/`, so it indexes the
whole channel archive rather than an empty `private/sources/` folder.
