#!/bin/zsh
cd "$(dirname "$0")"

if ! command -v python3 >/dev/null 2>&1; then
  echo "Python 3 not found."
  if ! command -v brew >/dev/null 2>&1; then
    echo "Homebrew not found — installing it first (you may be asked for your Mac password)..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    if [ -x /opt/homebrew/bin/brew ]; then
      eval "$(/opt/homebrew/bin/brew shellenv)"
    elif [ -x /usr/local/bin/brew ]; then
      eval "$(/usr/local/bin/brew shellenv)"
    fi
  fi
  echo "Installing Python 3 via Homebrew..."
  brew install python3
fi

if [ ! -d ".venv" ]; then
  echo "Setting up Life Tracker (first run only, this takes a minute)..."
  python3 -m venv .venv
fi

.venv/bin/python -m pip install --upgrade pip --quiet
.venv/bin/python -m pip install -r requirements.txt --quiet

exec .venv/bin/python -m streamlit run app.py --server.address 127.0.0.1 --browser.gatherUsageStats false
