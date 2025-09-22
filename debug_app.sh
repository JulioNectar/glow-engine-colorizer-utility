#!/bin/bash
cd "$(dirname "$0")"
./dist/Glow\ Engine\ Colorizer\ Utility.app/Contents/MacOS/Glow\ Engine\ Colorizer\ Utility 2>&1 | tee app_log.txt