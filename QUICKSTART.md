# QUICKSTART

**Repo**: `/Users/trev/Repos/finishline_audio_repo`

## Current Task

Troubleshoot Ableton export crash. See `STATE.md` for details.

## Key Files

- `STATE.md` - Operational state (read this)
- `docs/status/STATUS.md` - Operating procedures
- `NEW_CHAT_CONTEXT.md` - Extended context for new chats

## Commands

```bash
# Smoke tests
make smoke       # 7s, read-only
make write-fast  # 9s, dev gate
make write       # 39s, commit gate

# Master workflow
flaas verify              # Check gain
flaas plan-gain <wav>     # Calculate delta
flaas apply --actions <j> # Apply delta
```

## Next Action

In Ableton: Disable ValhallaSpaceModulator + StudioVerse → test 4-8 bar export.
