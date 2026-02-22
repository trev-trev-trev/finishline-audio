# Finish Line Audio Automation (Backend MVP)

This repo is the backend skeleton for controlling Ableton Live via **AbletonOSC** and running the first acceptance tests.

## Prereqs
- Ableton Live running with AbletonOSC enabled as a Control Surface.
- AbletonOSC default ports:
  - Live listens on UDP **11000**
  - Live replies on UDP **11001**

## Setup
```bash
python -m venv .venv
source .venv/bin/activate   # mac/linux
# .venv\Scripts\activate  # windows
pip install -r requirements.txt
```

## Configure
Edit `config.yaml` if needed (host/ports/timeouts).

## Run
### 1) Ping AbletonOSC
```bash
python -m finishline_audio.cli ping
```

### 2) Print track names
```bash
python -m finishline_audio.cli tracks
```

If `ping` fails, fix AbletonOSC installation first.
