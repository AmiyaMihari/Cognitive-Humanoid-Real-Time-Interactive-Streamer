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

# 2. Ensure the optional SoX command-line tool exists. Qwen3-TTS can import
#    without it, but installing it avoids warnings and keeps audio tooling ready.
install_sox() {
  if command -v sox >/dev/null 2>&1; then
    echo "==> SoX found: $(command -v sox)"
    return
  fi

  echo "==> SoX was not found; trying a best-effort system install..."
  if command -v pacman >/dev/null 2>&1; then
    sudo pacman -S --needed --noconfirm sox || true
  elif command -v apt-get >/dev/null 2>&1; then
    sudo apt-get update && sudo apt-get install -y sox || true
  elif command -v dnf >/dev/null 2>&1; then
    sudo dnf install -y sox || true
  elif command -v brew >/dev/null 2>&1; then
    brew install sox || true
  else
    echo "==> No supported package manager found for SoX; continuing."
  fi

  if command -v sox >/dev/null 2>&1; then
    echo "==> SoX installed: $(command -v sox)"
  else
    echo "==> SoX is still missing. Install it manually if Qwen3-TTS warns about it."
  fi
}

install_sox

# 3. Install the exact Python the project is pinned to.
echo "==> Installing Python 3.12..."
uv python install 3.12

# 4. Create the virtualenv (skip if it already exists).
if [ ! -d venv ]; then
  echo "==> Creating virtualenv (venv)..."
  uv venv venv --python 3.12
fi

# Safety: never install without the venv. Everything below targets the venv's
# own interpreter explicitly, so nothing can ever leak into the system Python.
if [ ! -x venv/bin/python ]; then
  echo "ERROR: the virtualenv was not created (venv/bin/python is missing)." >&2
  echo "       Aborting before installing anything, to keep your system clean." >&2
  exit 1
fi

# 5. Install all dependencies into the venv (note: --python venv/bin/python).
echo "==> Installing dependencies into the venv (first run can take a few minutes)..."
uv pip install --python venv/bin/python -r requirements.txt

# 6. Create .env from the template if it doesn't exist yet.
if [ ! -f .env ]; then
  cp .env.example .env
  echo "==> Created .env from template (.env.example)."
fi

# 7. (Optional) Install the venv auto-activation hook for the shells in use, so
#    the venv activates by itself when you cd into the project. Both are
#    idempotent and only ever added once.
repo="$(pwd)"

# fish: drop a conf.d snippet (fish loads it automatically).
if command -v fish >/dev/null 2>&1; then
  hook="$HOME/.config/fish/conf.d/auto_venv.fish"
  if [ -f scripts/auto_venv.fish ] && [ ! -f "$hook" ]; then
    mkdir -p "$(dirname "$hook")"
    cp scripts/auto_venv.fish "$hook"
    echo "==> Installed fish auto-venv hook."
  fi
fi

# bash: source the bash hook from ~/.bashrc.
if [ -f "$HOME/.bashrc" ] && [ -f scripts/auto_venv.sh ]; then
  if ! grep -q "C.H.R.I.S. venv auto-activation" "$HOME/.bashrc"; then
    {
      echo ""
      echo "# C.H.R.I.S. venv auto-activation (installed by setup.sh)"
      echo "[ -f \"$repo/scripts/auto_venv.sh\" ] && source \"$repo/scripts/auto_venv.sh\""
    } >> "$HOME/.bashrc"
    echo "==> Added bash auto-venv hook to ~/.bashrc."
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

 The first run downloads Whisper (~3 GB), Qwen3-TTS 1.7B
 VoiceDesign (~4.3 GB), and PyTorch/CUDA wheels. They are
 cached; later runs reuse them.
============================================================
DONE
