import hashlib


def choose_variant(user_id: str, traffic_b_percent: int = 50) -> str:
    """
    Détermine la variante A/B pour un utilisateur de façon déterministe.

    Utilise un hachage MD5 de l'ID utilisateur pour garantir que le même utilisateur 
    retombe toujours dans le même bucket, assurant une expérience stable.

    Args:
        user_id: Identifiant de l'utilisateur (ou "anonymous" si absent).
        traffic_b_percent: Pourcentage de trafic dirigé vers la variante B (0-100).
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
