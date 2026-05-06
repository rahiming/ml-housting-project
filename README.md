[![CI - Python Quality Checks](https://github.com/rahiming/ml-housting-project/actions/workflows/ci.yml/badge.svg)](https://github.com/rahiming/ml-housting-project/actions/workflows/ci.yml)

# ML Housing Project

A machine learning project for housing price prediction.

## Project Structure

```
ml-housing-project/
├── src/
│   └── ml_housing/
│       ├── __init__.py
│       ├── data.py
│       ├── features.py
│       ├── train.py
│       ├── evaluate.py
│       └── pipeline.py
├── tests/
│   ├── __init__.py
│   ├── test_data.py
│   ├── test_features.py
│   └── test_pipeline.py
├── artifacts/
│   └── .gitkeep
├── requirements.txt
├── pyproject.toml
├── README.md
└── main.py
```

## Installation

Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

Run the ML pipeline:

```bash
python main.py
```

## Testing

Run tests with pytest:

```bash
pytest
```
