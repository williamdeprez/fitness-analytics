from load_data import load_training_data
from pathlib import Path

PROCESSED_DIR = Path(__file__).resolve().parents[1] / "data" / "processed"

def main():
    PROCESSED_DIR.mkdir(exist_ok=True)

    df = load_training_data()

    out_path = PROCESSED_DIR / "training_sets_normalized.csv"
    df.to_csv(out_path, index=False)

    print(f"Saved normalized data to {out_path}")

if __name__ == "__main__":
    main()