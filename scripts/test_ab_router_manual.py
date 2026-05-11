import hashlib
import sys
from collections import Counter
from pathlib import Path

# Allow running this script directly from the repository's scripts/ folder.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.services.ab_router import choose_variant  # noqa: E402


def compute_bucket(user_id: str) -> int:
    if not user_id:
        user_id = "anonymous"
    hashed_value = int(
        hashlib.md5(user_id.encode("utf-8"), usedforsecurity=False).hexdigest(), 16
    )
    return hashed_value % 100


def normalize_user_id(user_id) -> str:
    if not user_id:
        return "anonymous"
    return str(user_id)


def display_user_label(user_id) -> str:
    if user_id is None:
        return "NONE"
    if user_id == "":
        return "EMPTY_STRING"
    return str(user_id)


def inspect_users(users, traffic_b_percent=50):
    print(f"\n=== Inspection with traffic_b_percent={traffic_b_percent}% ===")
    print(f"{'input_user':<15} {'routed_as':<15} {'bucket':<8} {'variant':<8}")
    print("-" * 55)

    results = []
    for user in users:
        input_label = display_user_label(user)
        routed_user = normalize_user_id(user)
        bucket = compute_bucket(user)
        variant = choose_variant(user, traffic_b_percent=traffic_b_percent)
        print(f"{input_label:<15} {routed_user:<15} {bucket:<8} {variant:<8}")
        results.append(variant)

    counts = Counter(results)
    print("\nDistribution:")
    print(f"A: {counts.get('A', 0)}")
    print(f"B: {counts.get('B', 0)}")


def test_stability(user_id, runs=5, traffic_b_percent=50):
    input_label = display_user_label(user_id)
    routed_user = normalize_user_id(user_id)
    print(
        f"\n=== Stability test for user '{input_label}' (routed as '{routed_user}') ==="
    )
    variants = [
        choose_variant(user_id, traffic_b_percent=traffic_b_percent)
        for _ in range(runs)
    ]
    print("Results:", variants)
    print("Stable:", len(set(variants)) == 1)


def test_multiple_traffic_levels(user_id, levels=(10, 25, 50, 75, 90)):
    input_label = display_user_label(user_id)
    routed_user = normalize_user_id(user_id)
    print(
        f"\n=== Traffic sensitivity for user '{input_label}' "
        f"(routed as '{routed_user}') ==="
    )
    print(f"{'traffic_b_percent':<20} {'bucket':<8} {'variant':<8}")
    print("-" * 40)

    bucket = compute_bucket(user_id)
    for level in levels:
        variant = choose_variant(user_id, traffic_b_percent=level)
        print(f"{level:<20} {bucket:<8} {variant:<8}")


if __name__ == "__main__":
    sample_users = [
        "alice",
        "bob",
        "charlie",
        "david",
        "eve",
        "frank",
        "grace",
        "heidi",
        "ivan",
        "judy",
        "",
        None,
        "anonymous",
    ]

    inspect_users(sample_users, traffic_b_percent=50)
    test_stability("alice", runs=7, traffic_b_percent=50)
    test_stability("eve", runs=7, traffic_b_percent=50)
    test_stability("", runs=7, traffic_b_percent=50)
    test_stability(None, runs=7, traffic_b_percent=50)
    test_stability("anonymous", runs=7, traffic_b_percent=50)
    test_multiple_traffic_levels("alice")
    test_multiple_traffic_levels("eve")
    test_multiple_traffic_levels("")
    test_multiple_traffic_levels(None)
    test_multiple_traffic_levels("anonymous")
