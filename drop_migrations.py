from os.path import isdir
from os import listdir, getcwd
from shutil import rmtree

def delete_migrations(folder):
    dirs = listdir(folder)
    for dir in dirs:
        if isdir(folder+dir) and dir == "migrations":
            rmtree(folder+dir)

def main():
    for element in listdir():
        if isdir(element) and '_app' in element:
            delete_migrations(element+'/')

if __name__ == '__main__':
    main()