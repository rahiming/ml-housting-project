from backend.services.ab_router import choose_variant


def test_choose_variant_stability():
    """Vérifie que le même user_id reçoit toujours la même variante."""
    user_id = "user_123"
    variant_1 = choose_variant(user_id, traffic_b_percent=50)
    variant_2 = choose_variant(user_id, traffic_b_percent=50)
    assert variant_1 == variant_2


def test_choose_variant_none_handling():
    """Vérifie que None ou string vide sont traités comme 'anonymous'
    de façon stable."""
    v_none = choose_variant(None)
    v_empty = choose_variant("")
    v_anon = choose_variant("anonymous")
    assert v_none == v_empty == v_anon


def test_choose_variant_distribution():
    """Vérifie sommairement que le changement de traffic_b_percent
    impacte le routage."""
    # On vérifie les comportements aux limites du routage.
    # On teste aux extrêmes
    assert choose_variant("user_test", traffic_b_percent=0) == "A"
    assert choose_variant("user_test", traffic_b_percent=100) == "B"


def test_choose_variant_determinism():
    """Test de régression pour s'assurer que l'algo de hash ne change pas par erreur."""
    # 'charlie' -> MD5: 6cd2... -> bucket 35.
    # Si traffic_b=50, 35 < 50 => B
    # Si traffic_b=30, 35 >= 30 => A
    assert choose_variant("charlie", traffic_b_percent=50) == "B"
    assert choose_variant("charlie", traffic_b_percent=30) == "A"
