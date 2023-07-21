"""#!/usr/bin/python3"""

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
    license='LGPL-2.1',
    python_requires='>=3.10',
    url='https://github.com/remshu-inc/pakt-work-tools',
    package_dir={'': '.'},
    packages=find_packages(where='.') + ["templates", "static"],
    include_package_data=True,
    package_data={'templates': ['*'], 'static': ["*"]},
    install_requires=requirements,
    scripts=['manage.py', 'create_folders.py', 'create_migrations.py', 'drop_migrations.py'],
    entry_points = {
        'console_scripts': ['run-pakt-server = manage:main']
    }
)
