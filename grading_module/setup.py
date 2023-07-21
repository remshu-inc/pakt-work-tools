"""#!/usr/bin/python3"""

from setuptools import setup, find_packages

requirements = []
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

readme = ''
with open('README.md') as f:
    readme = f.read()

setup(
    author='Kirill Kulakov',
    name='grading-module',
    description='Библиотека определения степени грубости ошибки и выставления общей оценки за ученический текст на немецком языке.',
    long_description=readme,
    long_description_content_type='text/markdown',
    version='0.1.1',
    license='LGPL-2.1',
    python_requires='>=3.10',
    url='https://github.com/remshu-inc/pakt-work-tools/grading_module',
    package_dir={'': '..'},
    packages=["grading_module"],
    install_requires=requirements,
    scripts=['common.py', 'gross_model.py', 'mark_model.py']
)
