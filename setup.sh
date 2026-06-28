#!/usr/bin/env bash
# One-command setup for C.H.R.I.S. on Linux / macOS.
#
# It installs everything from scratch: the uv package manager, the pinned
# Python 3.12 interpreter, the project virtualenv, and all dependencies. After
# it finishes, you only need to drop your API key into .env and run the app.
#
# Usage:   ./setup.sh        (run `chmod +x setup.sh` first if needed)

set -euo pipefail

# Always operate from the repository root (where this script lives), so the
# script works no matter the current directory.
cd "$(dirname "$0")"

echo "==> C.H.R.I.S. setup (Linux/macOS)"

# 1. Ensure uv is installed (no sudo; it lands in ~/.local/bin).
if ! command -v uv >/dev/null 2>&1; then
  echo "==> Installing uv (Python & dependency manager)..."
  curl -LsSf https://astral.sh/uv/install.sh | sh
  # Make uv visible in this same shell session.
  export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"
fi
if ! command -v uv >/dev/null 2>&1; then
  echo "ERROR: uv is not available. See https://docs.astral.sh/uv/ and re-run." >&2
  exit 1
fi

# 2. Install the exact Python the project is pinned to.
echo "==> Installing Python 3.12..."
uv python install 3.12

# 3. Create the virtualenv (skip if it already exists).
if [ ! -d venv ]; then
  echo "==> Creating virtualenv (venv)..."
  uv venv venv --python 3.12
fi

# 4. Install all dependencies into the venv.
echo "==> Installing dependencies (first run can take a few minutes)..."
uv pip install --python venv/bin/python -r requirements.txt

# 5. Create .env from the template if it doesn't exist yet.
if [ ! -f .env ]; then
  cp .env.example .env
  echo "==> Created .env from template (.env.example)."
fi

# 6. (Optional) Install the fish auto-activation hook, if fish is in use.
if command -v fish >/dev/null 2>&1; then
  hook="$HOME/.config/fish/conf.d/auto_venv.fish"
  if [ -f scripts/auto_venv.fish ] && [ ! -f "$hook" ]; then
    mkdir -p "$(dirname "$hook")"
    cp scripts/auto_venv.fish "$hook"
    echo "==> Installed fish auto-venv hook (activates the venv on cd into the project)."
  fi
fi

cat <<'DONE'

============================================================
 Setup complete.

 Next steps:
   1. Edit .env and set your key:   OPENAI_API_KEY=sk-...
      (HF_TOKEN is optional; the speech model is public.)
   2. Activate the venv:            source venv/bin/activate
   3. Run the app:                  streamlit run app.py

 The first run downloads the speech + voice models (~3.3 GB)
 and caches them; later runs start in seconds.
============================================================
DONE
