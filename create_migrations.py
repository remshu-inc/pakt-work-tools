import os

APPS = {'search_app','user_app', 'right_app','text_app'}

for app in APPS:
    os.system(f"python3 manage.py makemigrations {app}")

next_step = input('Продолжить? (Y/N)')

if next_step.lower() == 'y':
    os.system("python3 manage.py migrate")