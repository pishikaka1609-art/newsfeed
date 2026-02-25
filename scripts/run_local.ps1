param(
  [string]$PageUrl = ""
)

if (-not (Test-Path ".venv")) {
  python -m venv .venv
}

. .\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install .

if ($PageUrl -eq "") {
  $PageUrl = "http://localhost/"
}

newsfeed pull-feedback
newsfeed run --page-url $PageUrl

