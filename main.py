"""Main entry point for the ML housing project."""

from src.training.pipeline import get_next_version, run_pipeline

if __name__ == "__main__":
    version = get_next_version()
    metrics = run_pipeline(version=version)
    print("Pipeline terminé avec succès.")
    print(f"Version : {version}")
    print(f"MAE  : {metrics['mae']:.4f}")
    print(f"RMSE : {metrics['rmse']:.4f}")
    print(f"R2   : {metrics['r2']:.4f}")
