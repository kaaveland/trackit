#!/usr/bin/env bash

# Provide contineous testing while working - runs tests when a file change
# is detected in a subdirectory.

# This requires watchdog and pytest to be installed:
# pip install watchdog pytest
# If combined with pytest-osxnotify:
# pip install pytest-osxnotify
# Will provide a notification with the number of failures and successes
# when run every time you save a file.

watchmedo shell-command --patterns='*.py' --recursive --command='py.test -v -l'
