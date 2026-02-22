.PHONY: smoke write-fast write

# FLAAS Smoke Test Lanes
# Lane 1: READ-ONLY (fast sanity check)
smoke:
	./scripts/run_smoke_tests.sh

# Lane 2: WRITE-FAST (dev loop gate, ~9s)
write-fast:
	./scripts/run_smoke_tests.sh --write-fast

# Lane 3: WRITE (pre-commit gate, ~32s)
write:
	./scripts/run_smoke_tests.sh --write
