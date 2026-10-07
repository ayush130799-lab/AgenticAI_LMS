import sys
from pathlib import Path

# The sibling `ai_engine` package lives at the repo root (or `/` inside the
# Docker image, where backend/ is flattened onto /app). Put that root on
# sys.path so `import ai_engine` works however the API is launched.
_repo_root = str(Path(__file__).resolve().parents[2])
if _repo_root not in sys.path:
    sys.path.insert(0, _repo_root)
