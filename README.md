# CLI File Organizer & Log Parser

A lightweight command-line utility built in Core Python that automatically categorizes files into folders by extension, handles duplicate filenames safely, and logs all operations to a CSV file with summary reporting.

## Features
- Categorizes files into Documents, Images, Videos, Audio, Archives, Code, and Others
- Safe duplicate filename resolution (appends numeric suffixes instead of overwriting)
- `--dry-run` mode to preview file movements before modifying disk
- CSV audit logging and `--summary` report parser

## Usage
```bash
# Preview file organization without moving files
python organizer.py ./target_folder --dry-run

# Organize files and generate organizer_log.csv
python organizer.py ./target_folder

# View summary report from the CSV log
python organizer.py ./target_folder --summary
