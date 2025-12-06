from indices.q_otu import IndexWeights, compute_q_otu


def test_q_otu_clamped_to_unit_interval():
    value = compute_q_otu(q_vi=1.0, q_si=1.0, q_bi=1.0, q_relief=1.5)
    assert value == 1.0


def test_weights_normalization():
    weights = IndexWeights(k_vi=0.1, k_si=0.1, k_bi=0.1)
    normalized = weights.normalized()
    assert abs(normalized.k_vi - 1 / 3) < 1e-6
