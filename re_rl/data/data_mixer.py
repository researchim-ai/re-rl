from datasets import Dataset, concatenate_datasets
from re_rl.tasks.factory import MathTaskFactory
from re_rl.data.external_data_loader import ExternalDataLoader

class DataMixer:
    @staticmethod
    def generate_artificial_dataset(num_samples=100, language="ru", detail_level=3):
        data = []
        for _ in range(num_samples):
            task = MathTaskFactory.generate_random_task(only_valid=True, language=language, detail_level=detail_level)
            result = task.get_result()
            try:
                task_type = task.get_task_type()
            except:
                task_type = "unknown"
            data.append({
                "task_type": task_type,
                "problem": result["problem"],
                "prompt": result["prompt"],
                "solution_steps": result["solution_steps"],
                "final_answer": result["final_answer"]
            })
        return Dataset.from_dict({k: [d[k] for d in data] for k in data[0]})

    @staticmethod
    def mix_datasets(
            num_artificial=100,
            language="ru",
            detail_level=3
        ):
        """
        Загружает внешний датасет (если есть) для указанного языка,
        генерирует искусственный датасет, а затем объединяет их.
        """
        external_ds = ExternalDataLoader.load_external_datasets(language=language)
        artificial_ds = DataMixer.generate_artificial_dataset(num_artificial, language, detail_level)

        if external_ds is not None:
            combined = concatenate_datasets([external_ds, artificial_ds])
        else:
            combined = artificial_ds

        return combined
