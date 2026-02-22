#!/usr/bin/env bash
# Print the new chat bootstrap message for pasting into fresh ChatGPT threads

cat "$(dirname "$0")/../docs/status/TEMPLATES/NEW_CHAT_MESSAGE.md"
