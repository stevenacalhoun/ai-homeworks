from shutil import copyfile

def main():
  neededFiles = [
    "astarnavigator.py",
    "btnode.py",
    "mybehaviors.py",
    "mycreatepathnetwork.py"
  ]

  for fileName in neededFiles:
    copyfile(fileName, "testEnv/" + fileName)

if __name__ == "__main__":
  main()
