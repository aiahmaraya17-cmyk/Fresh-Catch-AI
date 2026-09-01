from ai.prediction.infer import FRESHNESS_RANK


def test_model_taxonomy_matches_dataset_classes():
    expected = {"Fresh", "Moderately Fresh", "Less Fresh", "Not Fresh"}
    assert set(FRESHNESS_RANK) == expected
    assert "Spoiled" not in FRESHNESS_RANK
