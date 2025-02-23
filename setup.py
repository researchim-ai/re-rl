from setuptools import setup, find_packages

setup(
    name='re_rl',
    version='0.0.1',
    description='Библиотека для решения математических задач и генерации заданий для обучения LLM с использованием reasoning RL',
    author='Tokarev Igor (Researchim AI)',
    author_email='your_email@example.com',
    packages=find_packages(),
    install_requires=[
        'sympy>=1.9',
        # можно добавить другие зависимости
    ],
    classifiers=[
         'Programming Language :: Python :: 3',
         'License :: OSI Approved :: MIT License',
         'Operating System :: OS Independent',
    ],
)
