import sys
from pathlib import Path

from falcons_qa import build_index

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))


def main():
    index, chunks = build_index()
    print(f"Indexed {len(chunks)} paragraph chunks into {BASE_DIR / 'data' / 'index.faiss'}")
    print(f"Saved chunk metadata to {BASE_DIR / 'data' / 'chunks.json'}")


if __name__ == "__main__":
    main()
