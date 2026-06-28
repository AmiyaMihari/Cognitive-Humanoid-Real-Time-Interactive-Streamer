# One-command setup for C.H.R.I.S. on Windows (PowerShell).
#
# It installs everything from scratch: the uv package manager, the pinned
# Python 3.12 interpreter, the project virtualenv, and all dependencies. After
# it finishes, you only need to drop your API key into .env and run the app.
#
# Usage (in PowerShell, from the repo folder):
#   ./setup.ps1
# If script execution is blocked, run it once as:
#   powershell -ExecutionPolicy Bypass -File .\setup.ps1

$ErrorActionPreference = "Stop"

# Always operate from the repository root (where this script lives).
Set-Location -Path $PSScriptRoot

Write-Host "==> C.H.R.I.S. setup (Windows)"

# 1. Ensure uv is installed.
if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Host "==> Installing uv (Python & dependency manager)..."
    powershell -ExecutionPolicy Bypass -Command "irm https://astral.sh/uv/install.ps1 | iex"
    # Make uv visible in this same session (covers both possible install dirs).
    $env:Path = "$env:USERPROFILE\.local\bin;$env:USERPROFILE\.cargo\bin;$env:Path"
}
if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Error "uv is not available. See https://docs.astral.sh/uv/ and re-run."
    exit 1
}

# 2. Ensure the optional SoX command-line tool exists. Qwen3-TTS can import
#    without it, but installing it avoids warnings and keeps audio tooling ready.
if (Get-Command sox -ErrorAction SilentlyContinue) {
    Write-Host "==> SoX found."
} else {
    Write-Host "==> SoX was not found; trying a best-effort system install..."
    if (Get-Command winget -ErrorAction SilentlyContinue) {
        winget install --id ChrisBagwell.SoX -e --accept-source-agreements --accept-package-agreements
    } elseif (Get-Command choco -ErrorAction SilentlyContinue) {
        choco install sox.portable -y
    } else {
        Write-Host "==> No supported package manager found for SoX; continuing."
    }

    if (Get-Command sox -ErrorAction SilentlyContinue) {
        Write-Host "==> SoX installed."
    } else {
        Write-Host "==> SoX is still missing. Install it manually if Qwen3-TTS warns about it."
    }
}

# 3. Install the exact Python the project is pinned to.
Write-Host "==> Installing Python 3.12..."
uv python install 3.12

# 4. Create the virtualenv (skip if it already exists).
if (-not (Test-Path "venv")) {
    Write-Host "==> Creating virtualenv (venv)..."
    uv venv venv --python 3.12
}

# Safety: never install without the venv. Everything below targets the venv's
# own interpreter explicitly, so nothing can ever leak into the system Python.
if (-not (Test-Path "venv\Scripts\python.exe")) {
    Write-Error "The virtualenv was not created (venv\Scripts\python.exe is missing). Aborting before installing anything."
    exit 1
}

# 5. Install all dependencies into the venv (note: --python venv\Scripts\python.exe).
Write-Host "==> Installing dependencies into the venv (first run can take a few minutes)..."
uv pip install --python "venv\Scripts\python.exe" -r requirements.txt

# 6. Create .env from the template if it doesn't exist yet.
if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "==> Created .env from template (.env.example)."
}

Write-Host ""
Write-Host "============================================================"
Write-Host " Setup complete."
Write-Host ""
Write-Host " Next steps:"
Write-Host "   1. Edit .env and set your key:   OPENAI_API_KEY=sk-..."
Write-Host "      (HF_TOKEN is optional; the speech model is public.)"
Write-Host "   2. Activate the venv:            venv\Scripts\Activate.ps1"
Write-Host "   3. Run the app:                  streamlit run app.py"
Write-Host ""
Write-Host " The first run downloads Whisper (~3 GB), Qwen3-TTS 1.7B"
Write-Host " VoiceDesign (~4.3 GB), and PyTorch/CUDA wheels. They are"
Write-Host " cached; later runs reuse them."
Write-Host "============================================================"
