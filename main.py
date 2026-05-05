"""Main entry point for the ML housing project."""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
SRC_PATH = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_PATH))

from ml_housing.pipeline import run_pipeline


if __name__ == "__main__":
    metrics = run_pipeline()
    print("Pipeline terminé avec succès.")
    print(f"MAE  : {metrics['mae']:.4f}")
    print(f"RMSE : {metrics['rmse']:.4f}")
    print(f"R2   : {metrics['r2']:.4f}")
