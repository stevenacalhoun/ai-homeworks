import json
from collections import OrderedDict

def main():
  constructHeroTree()
  # testTree("BTs/testTree.json")

def testTree(filename):
  print parseJsonBTFile(filename)

def constructHeroTree():
  destination = "MyHero.py"

  # Read lines
  with open(destination, 'r') as readfile:
    fileLines = readfile.readlines()

  # Rewrite lines with new tree
  with open(destination, 'w') as writefile:
    for i,line in enumerate(fileLines):
      if i < len(fileLines) - 1:
        writefile.write(line)

    writefile.write("")
    writefile.write("TREE = " + parseJsonBTFile("BTs/HeroTree.json"))
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
  listStr += parseParent(rootKey)
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

def parseParent(key):
  # Create key
  keyParts = key.split("-")
  keyClass = keyParts[0]
  keyId = keyParts[1]

  return "(" + keyClass + ", " + str(keyId) + ")"

def parseLeaf(key, data):
  # Create key
  keyParts = key.split("-")
  keyClass = keyParts[0]
  keyId = keyParts[1]

  # Gather args
  args = []
  if keyId != "N":
    args.append(keyId)
  for arg in data:
    args.append(arg)

  # Create string
  leafString = ""
  if keyId != "N":
    leafString += "("
  leafString += keyClass

  for arg in args:
    leafString += ", "
    leafString += str(arg)

  if keyId != "N":
    leafString += ")"

  return leafString

if __name__ == "__main__":
  main()
