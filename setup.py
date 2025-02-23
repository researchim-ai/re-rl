from setuptools import setup, find_packages

def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as req_file:
        return req_file.read().splitlines()

setup(
    name='re_rl',
    version='0.0.1',
    description='Библиотека для решения математических задач и генерации заданий для обучения LLM с использованием reasoning RL',
    author='Tokarev Igor (Researchim AI)',
    author_email='your_email@example.com',
    packages=find_packages(),
    install_requires=read_requirements(),
    classifiers=[
         'Programming Language :: Python :: 3',
         'License :: OSI Approved :: MIT License',
         'Operating System :: OS Independent',
    ],
)
