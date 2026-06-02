from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = Path("data")
PAPERS_DIR = DATA_DIR / "papers"
METADATA_DIR = DATA_DIR / "metadata"
INDEX_PATH = DATA_DIR / "index.json"
DEMO_PAPER_ID = "demo-ife-paper"
DEMO_PAPER_SOURCE = PROJECT_ROOT / "demo_ife_paper.pdf"
