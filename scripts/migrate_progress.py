"""
Migration Script: JSON progress to YAML chapter states
Migrates from single-file JSON (novel-progress.txt) to per-chapter YAML files
"""

import os
import sys
import json
import shutil
import argparse
from datetime import datetime
from typing import Dict, List, Any, Optional

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML is required. Install with: pip install pyyaml")
    sys.exit(1)

from core.chapter_state_store import ChapterStateStore, ChapterState


def load_json_progress(progress_file: str) -> Optional[Dict[str, Any]]:
    """Load progress from JSON file"""
    if not os.path.exists(progress_file):
        return None

    try:
        with open(progress_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Failed to load JSON progress: {e}")
        return None


def migrate_project(project_dir: str, dry_run: bool = False) -> Dict[str, Any]:
    """
    Migrate a single project from JSON to YAML

    Args:
        project_dir: Path to the project directory
        dry_run: If True, only simulate migration without writing files

    Returns:
        Dictionary with migration results
    """
    progress_file = os.path.join(project_dir, "novel-progress.txt")
    chapters_dir = os.path.join(project_dir, "chapters")
    states_dir = os.path.join(chapters_dir, "states")

    results = {
        "project_dir": project_dir,
        "migrated": False,
        "chapters_migrated": 0,
        "errors": [],
        "warnings": [],
    }

    # Load JSON progress
    json_progress = load_json_progress(progress_file)

    if not json_progress:
        results["errors"].append("No JSON progress file found")
        return results

    # Create states directory
    if not dry_run:
        os.makedirs(states_dir, exist_ok=True)

    # Initialize store for atomic writes
    store = ChapterStateStore(project_dir)

    # Migrate each chapter
    chapters_data = json_progress.get("chapters", [])

    if not chapters_data:
        results["warnings"].append("No chapters found in progress file")

    for ch_data in chapters_data:
        chapter_num = ch_data.get("chapter_number")
        if not chapter_num:
            results["warnings"].append(f"Skipping chapter without number: {ch_data}")
            continue

        # Create ChapterState from JSON data
        chapter_state = ChapterState(
            chapter_number=chapter_num,
            title=ch_data.get("title", f"第{chapter_num}章"),
            status=ch_data.get("status", "pending"),
            word_count=ch_data.get("word_count", 0),
            quality_score=ch_data.get("quality_score", 0.0),
            created_at=ch_data.get("created_at", datetime.now().isoformat()),
            updated_at=ch_data.get("completed_at")
            or ch_data.get("updated_at")
            or datetime.now().isoformat(),
            notes=ch_data.get("notes", ""),
        )

        if not dry_run:
            # Write YAML file
            file_path = store._get_state_file_path(chapter_num)
            content = yaml.dump(
                chapter_state.to_yaml_dict(),
                allow_unicode=True,
                default_flow_style=False,
                sort_keys=False,
            )
            store._atomic_write(file_path, content)

        results["chapters_migrated"] += 1

    # Create index file (backward compatibility)
    index_data = {
        "title": json_progress.get("title", "Unknown"),
        "genre": json_progress.get("genre", "general"),
        "total_chapters": json_progress.get(
            "total_chapters", results["chapters_migrated"]
        ),
        "completed_chapters": sum(
            1 for ch in chapters_data if ch.get("status") == "completed"
        ),
        "migration_date": datetime.now().isoformat(),
        "migration_version": "1.0.0",
        "storage_format": "yaml",
    }

    index_file = os.path.join(project_dir, "novel-progress.txt")

    if not dry_run:
        with open(index_file, "w", encoding="utf-8") as f:
            json.dump(index_data, f, ensure_ascii=False, indent=2)

    results["migrated"] = True
    results["index_file"] = index_file

    return results


def migrate_multiple_projects(
    projects_dir: str, dry_run: bool = False
) -> List[Dict[str, Any]]:
    """
    Migrate all projects in a directory

    Args:
        projects_dir: Directory containing novel projects
        dry_run: If True, only simulate migration

    Returns:
        List of migration results for each project
    """
    results = []

    if not os.path.exists(projects_dir):
        print(f"Projects directory not found: {projects_dir}")
        return results

    for project_name in os.listdir(projects_dir):
        project_dir = os.path.join(projects_dir, project_name)

        if not os.path.isdir(project_dir):
            continue

        progress_file = os.path.join(project_dir, "novel-progress.txt")

        if not os.path.exists(progress_file):
            continue

        print(f"Migrating: {project_name}...")

        result = migrate_project(project_dir, dry_run=dry_run)
        results.append(result)

        if result["migrated"]:
            print(f"  ✓ Migrated {result['chapters_migrated']} chapters")
        else:
            print(f"  ✗ Failed: {result['errors']}")

    return results


def rollback_migration(project_dir: str) -> bool:
    """
    Rollback a migration by removing YAML files

    Args:
        project_dir: Path to the project directory

    Returns:
        True if successful
    """
    states_dir = os.path.join(project_dir, "chapters", "states")

    if not os.path.exists(states_dir):
        print("No YAML states directory found")
        return False

    # Remove YAML files
    removed = 0
    for filename in os.listdir(states_dir):
        if filename.endswith(".yaml"):
            os.unlink(os.path.join(states_dir, filename))
            removed += 1

    print(f"Removed {removed} YAML state files")
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Migrate novel progress from JSON to YAML"
    )
    parser.add_argument(
        "project_dir",
        nargs="?",
        help="Path to project directory (or novels/ directory for batch)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate migration without writing files",
    )
    parser.add_argument(
        "--rollback", action="store_true", help="Rollback migration (remove YAML files)"
    )
    parser.add_argument(
        "--batch", action="store_true", help="Batch migrate all projects in directory"
    )

    args = parser.parse_args()

    if args.rollback:
        if not args.project_dir:
            print("Error: --rollback requires project_dir")
            sys.exit(1)
        rollback_migration(args.project_dir)
        return

    if not args.project_dir:
        parser.print_help()
        return

    # Determine if project_dir is a single project or a novels directory
    progress_file = os.path.join(args.project_dir, "novel-progress.txt")

    if args.batch or not os.path.exists(progress_file):
        # Batch mode
        results = migrate_multiple_projects(args.project_dir, dry_run=args.dry_run)

        print("\n" + "=" * 60)
        print("Migration Summary")
        print("=" * 60)

        total = len(results)
        successful = sum(1 for r in results if r["migrated"])

        print(f"Total projects: {total}")
        print(f"Successful: {successful}")
        print(f"Failed: {total - successful}")

        if args.dry_run:
            print("\n(Dry run - no files were actually written)")
    else:
        # Single project mode
        print(f"Migrating: {args.project_dir}")

        result = migrate_project(args.project_dir, dry_run=args.dry_run)

        if result["migrated"]:
            print(f"✓ Migrated {result['chapters_migrated']} chapters")

            if args.dry_run:
                print("\n(Dry run - no files were actually written)")
        else:
            print(f"✗ Failed: {result['errors']}")


if __name__ == "__main__":
    main()
