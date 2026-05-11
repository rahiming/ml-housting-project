import random

import requests

API_URL = "http://127.0.0.1:8000/predict"


def build_payload(user_id: str, rng: random.Random) -> dict:
    """Build one synthetic payload aligned with the public API schema."""
    return {
        "user_id": user_id,
        "median_income": round(rng.uniform(1.0, 8.0), 2),  # noqa: S311
        "housing_median_age": float(rng.randint(1, 50)),  # noqa: S311
        "average_rooms": round(rng.uniform(2.0, 8.0), 2),  # noqa: S311
        "average_bedrooms": round(rng.uniform(0.5, 2.5), 2),  # noqa: S311
        "population": float(rng.randint(200, 5000)),  # noqa: S311
        "average_occupancy": round(rng.uniform(1.0, 6.0), 2),  # noqa: S311
        "latitude": round(rng.uniform(32.0, 42.0), 3),  # noqa: S311
        "longitude": round(rng.uniform(-124.0, -114.0), 3),  # noqa: S311
    }


def main():
    """Send synthetic A/B traffic to the local FastAPI backend."""
    rng = random.Random()  # noqa: S311

    for i in range(500):
        payload = build_payload(f"user_{i}", rng)
        response = requests.post(API_URL, json=payload, timeout=10)
        result = response.json()
        print(
            i, response.status_code, result.get("variant"), result.get("model_version")
        )


if __name__ == "__main__":
    main()
