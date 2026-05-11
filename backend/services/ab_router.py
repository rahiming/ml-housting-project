import hashlib


def choose_variant(user_id: str, traffic_b_percent: int = 50) -> str:
    """Retourne A ou B de façon déterministe.

    Même user_id => même variante.
    traffic_b_percent=50 signifie 50% vers B, 50% vers A.
    """
    if not user_id:
        user_id = "anonymous"

    # Bandit nécessite le commentaire sur la ligne exacte de l'appel.
    # On sépare l'opération pour satisfaire Bandit et les formateurs de code.
    hasher = hashlib.md5(user_id.encode("utf-8"), usedforsecurity=False)  # nosec B303
    hashed_value = int(hasher.hexdigest(), 16)
    bucket = hashed_value % 100

    if bucket < traffic_b_percent:
        return "B"
    return "A"
