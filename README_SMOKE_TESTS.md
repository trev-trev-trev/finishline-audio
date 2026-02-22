# FLAAS Smoke Tests: Three Lanes Model

**Version**: 2026-02-22.1

## Quick Reference

```bash
make smoke       # Lane 1: Read-only (7s)  - Fast sanity check
make write-fast  # Lane 2: Write-fast (9s) - Dev loop gate
make write       # Lane 3: Write (32s)     - Pre-commit gate
```

## The Three Lanes

### Lane 1: `smoke` (READ-ONLY)
- **Command**: `make smoke` or `./scripts/run_smoke_tests.sh`
- **Duration**: ~7s
- **Tests**: 8 read-only checks (remote-version, ping, inspect, scan, device-map)
- **Purpose**: Fast sanity check to verify Live is running and responsive
- **When to use**: 
  - After any code change
  - Before starting work on a new feature
  - Quick verification that AbletonOSC is loaded

### Lane 2: `write-fast` (DEV LOOP GATE)
- **Command**: `make write-fast` or `./scripts/run_smoke_tests.sh --write-fast`
- **Duration**: ~9s
- **Tests**: 4 tests (remote-version, ping, eq8-set-gain with revert, map warm)
- **Purpose**: Fast validation with minimal write operations
- **When to use**:
  - After implementing a feature
  - During iterative development
  - Before running full validation

### Lane 3: `write` (PRE-COMMIT GATE)
- **Command**: `make write` or `./scripts/run_smoke_tests.sh --write`
- **Duration**: ~32s
- **Tests**: 12 tests (all read + all write tests with reverts)
- **Purpose**: Full validation before committing code
- **When to use**:
  - Before committing changes
  - Before pushing to remote
  - In CI/CD pipelines

## Exit Codes (CI-friendly)

| Code | Meaning | Description |
|------|---------|-------------|
| `0` | PASS | All tests passed (or only soft-skips with at least 1 pass) |
| `10` | SOFT-SKIP ONLY | All tests skipped, none passed |
| `20` | READ FAILURE | ping, remote-version, scan, or inspect failed |
| `30` | WRITE FAILURE | eq8-set-gain or eq8-set-freq failed |

## Version Checking

### Single Source of Truth

The smoke tests enforce version compatibility between:
- **AbletonOSC**: `ABLETONOSC_VERSION` in `abletonosc/constants.py`
- **FLAAS repo**: `ABLETONOSC_VERSION_EXPECTED` in `src/flaas/version.py`

### How It Works

1. `flaas remote-version` queries AbletonOSC for its version
2. Compares remote version against `ABLETONOSC_VERSION_EXPECTED`
3. Fails with exit code `20` if versions don't match

### Checking Versions

```bash
# Check local FLAAS version and expected AbletonOSC version
flaas --version

# Check remote AbletonOSC version (requires Live running)
flaas remote-version
```

**Current versions**: `2026-02-22.1`

## Output and Reports

### Console Output (5-line summary)
```
Passed: 8  Failed: 0  Skipped: 2
Report: data/reports/smoke_latest.txt
JSON: data/reports/smoke_latest.json

Run with --write or --write-fast flag to include write tests
```

### Report Files
- **Text**: `data/reports/smoke_latest.txt` (human-readable detailed report)
- **JSON**: `data/reports/smoke_latest.json` (structured data for tooling)

### Copy Summary to Clipboard (macOS)
```bash
./scripts/smoke_copy_summary.sh
```

## Workflow Integration

### Development Workflow
```bash
# 1. Start work - verify Live is running
make smoke

# 2. Implement feature
# (edit code, test manually in Live)

# 3. Quick validation during dev loop
make write-fast

# 4. Full validation before commit
make write
git add .
git commit -m "Feature: Add XYZ"
```

### CI/CD Integration
```yaml
# Example GitHub Actions workflow
- name: Run smoke tests
  run: make write
  
- name: Check exit code
  if: failure()
  run: |
    if [ $? -eq 20 ]; then
      echo "Read failure - check Live connection"
    elif [ $? -eq 30 ]; then
      echo "Write failure - check device control"
    fi
```

## Performance

| Mode | Duration | Tests | Write Ops | Efficiency Gain |
|------|----------|-------|-----------|-----------------|
| smoke | 7s | 8 | 0 | 13x faster than initial |
| write-fast | 9s | 4 | 2 | 10x faster than initial |
| write | 32s | 12 | 6 | 3x faster than initial |

**Optimizations applied**:
- Direct RPC calls for EQ8 map (no scan dependency)
- Targeted scan (`--tracks` flag) for specific track inspection
- Reduced RPC timeouts (read: 1.5s, write: 3.0s)
- Single retry on timeout
- No sleep delays between tests
- Fast mode skips: inspect, scan, device-map, freq tests

## Test Configuration

Test targets are defined in `data/targets/default.json`:
```json
{
  "track_id": 41,
  "eq8_device_id": 0,
  "other_device_ids": [1, 2]
}
```

Modify this file to test different tracks/devices.

## Troubleshooting

### Version Mismatch Error
```
WARNING: Version mismatch!
  Remote: 2026-02-22.0
  Expected: 2026-02-22.1
```

**Solution**: Restart Ableton Live to reload the updated AbletonOSC script.

### Timeout Errors
```
ERROR: Timed out waiting for reply
```

**Solution**: 
1. Verify Ableton Live is running
2. Check that AbletonOSC is loaded (check Live's Log.txt)
3. Ensure no firewall is blocking OSC ports (11000/11001)

### Stale Python Cache
If code changes don't take effect after restarting Live:
```bash
# Clear Python bytecode cache
find "/Users/trev/Music/Ableton/User Library/Remote Scripts/AbletonOSC" \
  -name "*.pyc" -delete
find "/Users/trev/Music/Ableton/User Library/Remote Scripts/AbletonOSC" \
  -name "__pycache__" -type d -exec rm -rf {} +

# Then restart Ableton Live
```

## File Locations

### Scripts
- `./scripts/run_smoke_tests.sh` - Main smoke test runner
- `./scripts/smoke_copy_summary.sh` - Copy summary to clipboard
- `Makefile` - Shortcut targets

### Version Sources
- `src/flaas/version.py` - FLAAS version and expected AbletonOSC version
- `[AbletonOSC]/abletonosc/constants.py` - AbletonOSC version

### Reports
- `data/reports/smoke_latest.txt` - Text report
- `data/reports/smoke_latest.json` - JSON report

### Config
- `data/targets/default.json` - Test target configuration

## Development Notes

### Adding New Tests

1. Add test logic to `scripts/run_smoke_tests.sh`
2. Use `log_test` function to record results
3. Choose appropriate exit code for failures
4. Consider which lane(s) should include the test

### Modifying Timeouts

Edit these variables in `run_smoke_tests.sh`:
```bash
TIMEOUT_READ=1.5     # Read operations (ping, scan, inspect)
TIMEOUT_WRITE=3.0    # Write operations (eq8-set)
MAX_RETRIES=1        # Number of retries on timeout
```

### Cache Management

Scan cache is reused for 30 seconds (TTL):
```bash
CACHE_FILE="data/caches/model_cache.json"
CACHE_MAX_AGE_SEC=30
```

## License

Part of the FLAAS (Finishline Audio Automated System) project.

---

**Last updated**: 2026-02-22  
**Documentation version**: 1.0
