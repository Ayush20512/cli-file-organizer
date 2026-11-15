import argparse
import csv
import shutil
from datetime import datetime
from pathlib import Path

# Extension-to-folder mapping
CATEGORIES = {
    "Documents": {".pdf", ".docx", ".doc", ".txt", ".xlsx", ".pptx", ".csv"},
    "Images": {".jpg", ".jpeg", ".png", ".gif", ".svg", ".webp"},
    "Videos": {".mp4", ".mkv", ".mov", ".avi"},
    "Audio": {".mp3", ".wav", ".flac", ".aac"},
    "Archives": {".zip", ".rar", ".7z", ".tar", ".gz"},
    "Code": {".py", ".cpp", ".c", ".js", ".html", ".css", ".sql", ".json"},
}


def get_category(extension: str) -> str:
    ext = extension.lower()
    for category, extensions in CATEGORIES.items():
        if ext in extensions:
            return category
    return "Others"


def resolve_collision(dest_path: Path) -> Path:
    """Appends a numeric suffix if a file with the same name already exists."""
    if not dest_path.exists():
        return dest_path

    counter = 1
    while True:
        new_name = f"{dest_path.stem}_{counter}{dest_path.suffix}"
        candidate = dest_path.with_name(new_name)
        if not candidate.exists():
            return candidate
        counter += 1


def organize_directory(target_dir: Path, dry_run: bool = False) -> list[dict]:
    logs = []

    if not target_dir.exists() or not target_dir.is_dir():
        raise FileNotFoundError(f"Directory not found: {target_dir}")

    for item in target_dir.iterdir():
        # Skip subdirectories and hidden files
        if item.is_dir() or item.name.startswith("."):
            continue

        category = get_category(item.suffix)
        dest_folder = target_dir / category
        dest_path = resolve_collision(dest_folder / item.name)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        try:
            if not dry_run:
                dest_folder.mkdir(exist_ok=True)
                shutil.move(str(item), str(dest_path))

            logs.append({
                "timestamp": timestamp,
                "status": "DRY_RUN" if dry_run else "MOVED",
                "file_name": item.name,
                "category": category,
                "destination": str(dest_path),
            })
        except PermissionError:
            logs.append({
                "timestamp": timestamp,
                "status": "ERROR_PERMISSION",
                "file_name": item.name,
                "category": category,
                "destination": "SKIPPED",
            })

    return logs


def write_csv_log(logs: list[dict], log_file: Path) -> None:
    if not logs:
        print("No files found to organize.")
        return

    file_exists = log_file.exists()
    fieldnames = ["timestamp", "status", "file_name", "category", "destination"]

    with open(log_file, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerows(logs)


def parse_log_summary(log_file: Path) -> None:
    """Parses the CSV log file and prints summary metrics."""
    if not log_file.exists():
        print(f"No log file found at {log_file}")
        return

    category_counts = {}
    status_counts = {}

    with open(log_file, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            cat = row["category"]
            stat = row["status"]
            category_counts[cat] = category_counts.get(cat, 0) + 1
            status_counts[stat] = status_counts.get(stat, 0) + 1

    print("\n--- Log Summary Report ---")
    print("Operations by Status:", status_counts)
    print("Files by Category:", category_counts)


def main():
    parser = argparse.ArgumentParser(
        description="CLI File Organizer & Operation Log Parser"
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Target directory path to organize (default: current directory)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview file moves without modifying disk",
    )
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Parse and display summary from organizer_log.csv",
    )

    args = parser.parse_args()
    target_dir = Path(args.path).resolve()
    log_path = target_dir / "organizer_log.csv"

    if args.summary:
        parse_log_summary(log_path)
        return

    logs = organize_directory(target_dir, dry_run=args.dry_run)
    write_csv_log(logs, log_path)
    print(f"Processed {len(logs)} files. Log saved to {log_path.name}.")


if __name__ == "__main__":
    main()