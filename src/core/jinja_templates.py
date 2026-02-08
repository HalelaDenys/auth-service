from fastapi.templating import Jinja2Templates
from pathlib import Path

TEMP_DIR = Path(__file__).parent.parent

templates = Jinja2Templates(directory=TEMP_DIR / "templates")
