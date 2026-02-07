from setuptools import setup, find_packages


def read_requirements():
    """Читает requirements.txt, корректно обрабатывая git-зависимости."""
    deps = []
    with open("requirements.txt", "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            # setuptools не поддерживает "pkg @ git+..." в install_requires,
            # но pip install -r requirements.txt — поддерживает.
            # Для setup.py оставляем только имя пакета.
            if " @ " in line:
                line = line.split(" @ ")[0].strip()
            deps.append(line)
    return deps


setup(
    name='re_rl',
    version='0.0.1',
    description='Библиотека для генерации искусственных задач для обучения LLM с использованием reasoning RL',
    author='Tokarev Igor (Researchim AI)',
    packages=find_packages(),
    install_requires=read_requirements(),
    classifiers=[
         'Programming Language :: Python :: 3',
         'License :: OSI Approved :: MIT License',
         'Operating System :: OS Independent',
    ],
)
