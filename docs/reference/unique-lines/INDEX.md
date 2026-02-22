# Unique Line Ledger - Index

**Generated from**: `src/flaas/*.py`

This ledger tracks every unique line of code in the FLAAS codebase,
showing all locations where each line appears.

## Purpose

- **Transparency**: See exactly what code exists and where
- **Deduplication analysis**: Identify repeated patterns
- **Refactoring aid**: Find all instances of a pattern
- **Audit trail**: Track every line's usage

## Categories

- **[cli_wiring.md](cli_wiring.md)**: 52 unique lines
- **[comments.md](comments.md)**: 4 unique lines
- **[constants.md](constants.md)**: 2 unique lines
- **[decorators.md](decorators.md)**: 2 unique lines
- **[definitions.md](definitions.md)**: 35 unique lines
- **[file_io.md](file_io.md)**: 7 unique lines
- **[imports.md](imports.md)**: 41 unique lines
- **[logic.md](logic.md)**: 278 unique lines
- **[osc_calls.md](osc_calls.md)**: 17 unique lines
- **[planning.md](planning.md)**: 12 unique lines
- **[safety.md](safety.md)**: 19 unique lines

## Regeneration

To regenerate this ledger:

```bash
python3 scripts/generate_unique_lines.py
```

## Statistics

- **Total unique lines**: 469
- **Total occurrences**: 619
- **Files processed**: 18
- **Categories**: 11
