from re_rl.multiturn_generator import MultiturnGenerator


def test_generate_multiturn_followup_mode():
    generator = MultiturnGenerator()
    dataset = generator.generate_multiturn_dataset(
        modes=["followup"],
        task_types=["quadratic"],
        num_samples=6,
        language="ru",
        difficulties=[3],
        reasoning_mode=True,
        turns=3,
        show_progress=False,
    )

    assert len(dataset) > 0
    assert all(item["metadata"]["mode"] == "followup" for item in dataset)
    assert all(len(item["messages"]) >= 4 for item in dataset)


def test_generate_multiturn_variations_mode():
    generator = MultiturnGenerator()
    dataset = generator.generate_multiturn_dataset(
        modes=["variations"],
        task_types=["arithmetic"],
        num_samples=6,
        language="ru",
        difficulties=[3],
        reasoning_mode=True,
        turns=3,
        show_progress=False,
    )

    assert len(dataset) > 0
    assert all(item["metadata"]["mode"] == "variations" for item in dataset)
    assert all(len(item["messages"]) >= 4 for item in dataset)
