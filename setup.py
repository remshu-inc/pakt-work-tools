from setuptools import setup, find_packages

requirements = []
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

readme = ''
with open('README.md') as f:
    readme = f.read()

setup(
    author='Nikita Remshu',
    name='pakt-work-tools',
    description='Комплекс инструментов для работы с петрозаводским аннотированным корпусом.',
    long_description=readme,
    long_description_content_type='text/markdown',
    version='0.1.1',
    license='Apache 2.0',
    python_requires='>=3.7',
    url='https://github.com/remshu/pakt-work-tools',
    package_dir={'': '.'},
    packages=find_packages(where='.'),
    include_package_data=True,
    install_requires=requirements
)