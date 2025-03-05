from datasets import load_dataset, Dataset, concatenate_datasets

EXTERNAL_DATASETS = {
    "ru": [
        {"name": "d0rj/gsm8k-ru", "config": None},
        {"name": "some_ru_ds2", "config": None}
    ],
    "en": [
        {"name": "openai/gsm8k", "config": None},
        {"name": "SynthLabsAI/Big-Math-RL-Verified", "config": None}
    ]
}

class ExternalDataLoader:
    @staticmethod
    def load_external_datasets(language: str = "en"):
        """
        Загрузка списка датасетов, предопределённых в EXTERNAL_DATASETS[language].
        Возвращает Dataset (объединённый) или None, если ничего не загружено.
        """
        if language not in EXTERNAL_DATASETS:
            return None

        ds_list = []
        for ds_info in EXTERNAL_DATASETS[language]:
            loaded = load_dataset(ds_info["name"], ds_info["config"])
            if "train" in loaded:
                transformed = loaded["train"].map(ExternalDataLoader._transform_example)
                ds_list.append(transformed)
            # можно также обрабатывать "validation" или "test" по желанию

        if ds_list:
            return concatenate_datasets(ds_list)
        else:
            return None

    @staticmethod
    def _transform_example(example):
        """
        Преобразовать пример к единому формату:
          {
            'problem': str,
            'prompt': str,
            'solution_steps': list[str],
            'final_answer': str
          }
        Здесь только примерная логика: зависит от полей реального датасета.
        """
        # допустим, датасеты имеют поля "question", "answer", "explanation"
        return {
            "problem": example.get("question", ""),
            "prompt": example.get("question", ""),
            "solution_steps": example.get("explanation", "").split("\n") if example.get("explanation") else [],
            "final_answer": example.get("answer", "")
        }
