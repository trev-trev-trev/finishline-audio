# Manual export loop (current MVP)

## Goal
Iterate Utility gain until `verify-audio` returns PASS.

## One iteration
1) In Ableton, export Master to: `output/master.wav`
   - Use: `flaas export-guide`

2) In Terminal:
```bash
flaas verify-audio output/master.wav
```

3. If FAIL on LUFS:
```bash
flaas loop output/master.wav
```

4. Repeat from step 1.

## Safety
* `flaas loop` stops if Utility gain is near max.
* `flaas apply` refuses if Live fingerprint changed since planning.

## Reset
```bash
flaas reset
```
