from shutil import copyfile

def main():
  neededFiles = [
    "btnode.py",
    "mybehaviors.py",
    "mycreatepathnetwork.py",
    "mynavigatorhelpers.py",
    "astarnavigator.py"
  ]

  for fileName in neededFiles:
    copyfile(fileName, "testEnv/" + fileName)

if __name__ == "__main__":
  main()
