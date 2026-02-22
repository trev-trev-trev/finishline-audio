#!/usr/bin/env python3
"""
Generate unique line ledger for FLAAS codebase.

Extracts all unique code lines, tracks their locations,
and groups them by category for transparency.
"""

from pathlib import Path
from collections import defaultdict
import re
import json

REPO_ROOT = Path(__file__).parent.parent
SRC_DIR = REPO_ROOT / "src" / "flaas"
OUTPUT_DIR = REPO_ROOT / "docs" / "reference" / "unique-lines"


def normalize_line(line: str) -> str:
    """Normalize a line by stripping whitespace."""
    return line.strip()


def categorize_line(line: str) -> str:
    """Categorize a line of code."""
    if not line or line.startswith("#"):
        return "comments"
    
    if line.startswith("from ") or line.startswith("import "):
        return "imports"
    
    if re.match(r'^[A-Z_][A-Z0-9_]*\s*=', line):
        return "constants"
    
    if "request_once(" in line or "send_message(" in line or "send_ping(" in line:
        return "osc_calls"
    
    if any(x in line for x in ["Path(", ".write_text(", ".read_text(", "open(", "sf.read", "sf.write"]):
        return "file_io"
    
    if any(x in line for x in ["plan_", "analyze_", "check_"]):
        return "planning"
    
    if any(x in line for x in ["clamp", "max(", "min(", "assert", "raise", "RuntimeError", "ValueError"]):
        return "safety"
    
    if any(x in line for x in ["argparse", "add_parser", "add_argument", "parse_args"]):
        return "cli_wiring"
    
    if line.startswith("def ") or line.startswith("class "):
        return "definitions"
    
    if line.startswith("@"):
        return "decorators"
    
    return "logic"


def extract_lines(file_path: Path) -> list[tuple[int, str, str]]:
    """Extract lines from a Python file.
    
    Returns: list of (line_number, normalized_line, category)
    """
    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception as e:
        print(f"Warning: Could not read {file_path}: {e}")
        return []
    
    lines = []
    for line_num, line in enumerate(content.splitlines(), start=1):
        normalized = normalize_line(line)
        if normalized:  # Skip empty lines
            category = categorize_line(normalized)
            lines.append((line_num, normalized, category))
    
    return lines


def generate_ledger():
    """Generate the unique line ledger."""
    
    # Track all unique lines and their locations
    line_locations = defaultdict(list)  # normalized_line -> [(file, line_num, category)]
    
    # Process all Python files
    py_files = sorted(SRC_DIR.glob("*.py"))
    
    print(f"Processing {len(py_files)} files...")
    
    for py_file in py_files:
        rel_path = py_file.relative_to(REPO_ROOT)
        lines = extract_lines(py_file)
        
        for line_num, normalized, category in lines:
            line_locations[normalized].append((str(rel_path), line_num, category))
    
    print(f"Found {len(line_locations)} unique lines")
    
    # Group by category
    category_lines = defaultdict(list)
    for normalized, locations in line_locations.items():
        # Use the most common category for this line
        categories = [cat for _, _, cat in locations]
        primary_category = max(set(categories), key=categories.count)
        category_lines[primary_category].append((normalized, locations))
    
    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Write category files
    for category in sorted(category_lines.keys()):
        lines = sorted(category_lines[category], key=lambda x: x[0])
        
        output_file = OUTPUT_DIR / f"{category}.md"
        with output_file.open("w", encoding="utf-8") as f:
            f.write(f"# Unique Lines: {category.replace('_', ' ').title()}\n\n")
            f.write(f"**Total unique lines**: {len(lines)}\n\n")
            f.write("---\n\n")
            
            for normalized, locations in lines:
                f.write(f"## Line: `{normalized}`\n\n")
                f.write(f"**Occurrences**: {len(locations)}\n\n")
                
                # Group by file
                by_file = defaultdict(list)
                for file_path, line_num, _ in locations:
                    by_file[file_path].append(line_num)
                
                for file_path in sorted(by_file.keys()):
                    line_nums = sorted(by_file[file_path])
                    if len(line_nums) == 1:
                        f.write(f"- `{file_path}:{line_nums[0]}`\n")
                    else:
                        ranges = []
                        start = line_nums[0]
                        prev = start
                        for num in line_nums[1:]:
                            if num == prev + 1:
                                prev = num
                            else:
                                if start == prev:
                                    ranges.append(str(start))
                                else:
                                    ranges.append(f"{start}-{prev}")
                                start = num
                                prev = num
                        if start == prev:
                            ranges.append(str(start))
                        else:
                            ranges.append(f"{start}-{prev}")
                        f.write(f"- `{file_path}`: lines {', '.join(ranges)}\n")
                
                f.write("\n")
        
        print(f"Wrote {output_file}")
    
    # Write index
    index_file = OUTPUT_DIR / "INDEX.md"
    with index_file.open("w", encoding="utf-8") as f:
        f.write("# Unique Line Ledger - Index\n\n")
        f.write("**Generated from**: `src/flaas/*.py`\n\n")
        f.write("This ledger tracks every unique line of code in the FLAAS codebase,\n")
        f.write("showing all locations where each line appears.\n\n")
        f.write("## Purpose\n\n")
        f.write("- **Transparency**: See exactly what code exists and where\n")
        f.write("- **Deduplication analysis**: Identify repeated patterns\n")
        f.write("- **Refactoring aid**: Find all instances of a pattern\n")
        f.write("- **Audit trail**: Track every line's usage\n\n")
        f.write("## Categories\n\n")
        
        for category in sorted(category_lines.keys()):
            count = len(category_lines[category])
            f.write(f"- **[{category}.md]({category}.md)**: {count} unique lines\n")
        
        f.write("\n## Regeneration\n\n")
        f.write("To regenerate this ledger:\n\n")
        f.write("```bash\n")
        f.write("python3 scripts/generate_unique_lines.py\n")
        f.write("```\n\n")
        f.write("## Statistics\n\n")
        f.write(f"- **Total unique lines**: {len(line_locations)}\n")
        f.write(f"- **Total occurrences**: {sum(len(locs) for locs in line_locations.values())}\n")
        f.write(f"- **Files processed**: {len(py_files)}\n")
        f.write(f"- **Categories**: {len(category_lines)}\n")
    
    print(f"Wrote {index_file}")
    
    # Write summary stats
    stats_file = OUTPUT_DIR / "stats.json"
    stats = {
        "total_unique_lines": len(line_locations),
        "total_occurrences": sum(len(locs) for locs in line_locations.values()),
        "files_processed": len(py_files),
        "categories": {cat: len(lines) for cat, lines in category_lines.items()},
        "most_repeated": sorted(
            [(line, len(locs)) for line, locs in line_locations.items()],
            key=lambda x: x[1],
            reverse=True
        )[:10]
    }
    
    stats_file.write_text(json.dumps(stats, indent=2))
    print(f"Wrote {stats_file}")


if __name__ == "__main__":
    generate_ledger()
    print("\nUnique line ledger generated successfully!")
