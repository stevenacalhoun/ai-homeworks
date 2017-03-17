import json
from collections import OrderedDict

def main():
  constructHeroTree()
  # testTree("BTs/testTree.json")

def testTree(filename):
  print parseJsonBTFile(filename)

def constructHeroTree():
  destination = "mybehaviors.py"

  # Read lines
  with open(destination, 'r') as readfile:
    fileLines = readfile.readlines()

  # Rewrite lines with new tree
  with open(destination, 'w') as writefile:
    for i,line in enumerate(fileLines):
      if i < len(fileLines) - 1:
        writefile.write(line)

    # writefile.write("\n")
    writefile.write("TREE = " + parseJsonBTFile("BTs/HeroTree.json"))
    writefile.write("\n")
    writefile.close()

def parseJsonBTFile(filename):
  with open(filename) as dataFile:
    data = json.load(dataFile, object_pairs_hook=OrderedDict)
    for i,key in enumerate(data):
      return parseJsonBT(key, data[key])

def parseJsonBT(rootKey, rootData):
  # Leaf node
  if isLeafNode(rootData):
    return parseLeaf(rootKey, rootData)

  # Sequence or selector
  listStr = ""
  listStr += parseLeaf(rootKey, [])
  leavesStringsList = []

  # Parse all nodes under
  for key in rootData:
    listStr += ", "
    listStr += parseJsonBT(key, rootData[key])

  return "[" + listStr + "]"

def isLeafNode(data):
  return isinstance(data, list)

def allChildrenAreLeaves(data):
  result = True
  for key in data:
    if isLeafNode(data[key]) == False:
      result = False
  return result

def parseLeaf(key, data):
  # Create key
  keyParts = key.split("-")
  leafString = ""
  if keyParts[1] != "N":
    leafString += "("
  leafString += keyParts[0]

  # Gather args
  arguments = []
  if keyParts[1] != "N":

    for arg in keyParts[1:]:
      leafString += ", "
      try:
        float(arg)
        leafString += "" + str(arg) + ""
      except ValueError:
        leafString += "'" + str(arg) + "'"

    leafString += ")"

  return leafString

if __name__ == "__main__":
  main()
