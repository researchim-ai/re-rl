from .math_task import MathTask

class TaskComposer:
    """
    Класс для составления различных текстовых задач.
    В данном примере реализована компоновка математических задач.
    """
    def compose_math_task(self, a: float, b: float, c: float) -> MathTask:
        return MathTask(a, b, c)
    
    # Здесь можно добавить методы для составления задач других типов.
