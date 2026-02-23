# FLAAS Testing Framework

**Automated unit tests with background CI.**

---

## Quick Run

```bash
cd /Users/trev/Repos/finishline_audio_repo
source .venv/bin/activate
python -m pytest tests/ -v
```

**Current status:** 51 tests passing ✅

---

## Test Modules

| File | Coverage | Tests |
|------|----------|-------|
| `test_analyze.py` | Audio analysis (LUFS/True Peak) | 14 |
| `test_osc_rpc.py` | OSC communication | 6 |
| `test_preflight.py` | Pre-flight checks | 12 |
| `test_targets.py` | Constants & device resolution | 10 |
| `test_util.py` | Utility functions | 9 |

---

## Automated Background Testing

**Status:** ✅ **ACTIVE** - Tests run automatically every 30 minutes

### How It Works

**macOS LaunchAgent** (`com.finishline.flaas.tests`):
- Runs `scripts/run_tests_background.sh` every 30 minutes
- Logs to `logs/tests/test_run_YYYYMMDD_HHMMSS.log`
- Keeps last 100 test runs
- Creates `logs/tests/latest.log` symlink to most recent run

### Check Status

```bash
# View latest test results
cat logs/tests/latest.log

# List recent test runs
ls -lt logs/tests/test_run_*.log | head -5

# Check launchd agent status
launchctl list | grep flaas
```

### Manual Control

```bash
# Stop automated testing
launchctl unload ~/Library/LaunchAgents/com.finishline.flaas.tests.plist

# Start automated testing
launchctl load ~/Library/LaunchAgents/com.finishline.flaas.tests.plist

# Trigger test run now (doesn't wait 30 min)
launchctl start com.finishline.flaas.tests

# View agent config
cat ~/Library/LaunchAgents/com.finishline.flaas.tests.plist
```

---

## Test Coverage

Run with coverage report:

```bash
python -m pytest tests/ --cov=src/flaas --cov-report=html
open htmlcov/index.html
```

**Target**: 80%+ coverage on core modules

---

## Writing New Tests

### Structure

```python
"""Unit tests for module_name.py - Description."""
import pytest
from unittest.mock import patch, MagicMock
from flaas.module_name import function_to_test


class TestFunctionName:
    """Test specific function."""
    
    @pytest.fixture
    def setup_data(self):
        """Setup test data."""
        return {"key": "value"}
    
    def test_basic_case(self, setup_data):
        """Test basic functionality."""
        result = function_to_test(setup_data)
        assert result == expected
    
    @patch("flaas.module_name.external_dependency")
    def test_with_mock(self, mock_dep):
        """Test with mocked dependency."""
        mock_dep.return_value = "mocked"
        result = function_to_test()
        assert mock_dep.called
```

### Best Practices

1. **One class per function** - `TestFunctionName` tests `function_name`
2. **Descriptive names** - `test_function_name_specific_case`
3. **Mock external deps** - OSC calls, file I/O, subprocess calls
4. **Use fixtures** - For setup/teardown and shared test data
5. **Test edge cases** - Empty inputs, timeouts, errors, boundary values
6. **Fast tests** - Mock slow operations (OSC, exports, analysis)

---

## CI Integration

**Background testing logs** are automatically:
- Generated every 30 minutes
- Timestamped and archived
- Accessible via `logs/tests/latest.log`
- Cleaned up (only last 100 runs kept)

**Benefits:**
- Catches regressions early
- No manual intervention needed
- Historical record of test stability
- Runs even when you're not actively coding

---

## Test Metrics

**Current stats:**
- Total tests: 51
- Pass rate: 100%
- Coverage: TBD (run with `--cov`)
- Runtime: <1 second

**Goals:**
- Maintain 100% pass rate
- Add tests for new features immediately
- Increase coverage to 80%+
- Keep runtime under 5 seconds

---

## Troubleshooting

### Tests fail locally but pass in CI
- Check Python version (`python --version`)
- Reinstall dependencies (`pip install -r requirements.txt`)

### Automated tests not running
```bash
# Check launchd agent
launchctl list | grep flaas

# Check logs
tail -f logs/tests/launchd_stderr.log

# Manually trigger
launchctl start com.finishline.flaas.tests
```

### Permission errors in logs
- Ensure script is executable: `chmod +x scripts/run_tests_background.sh`
- Check log directory exists: `mkdir -p logs/tests`

---

**Tests run automatically. No action needed.** 🎯
