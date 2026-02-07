from setuptools import setup, find_packages

def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as req_file:
        return [
            line.strip() for line in req_file
            if line.strip() and not line.strip().startswith("#")
        ]

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
