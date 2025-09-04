import os

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def getpath(path):
  return os.path.abspath(ROOT_DIR + path)
