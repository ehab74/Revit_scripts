"""Alignment of walls with floors and beams of different model"""


import clr
clr.AddReference('RevitAPI')
clr.AddReference("RevitServices")
from Autodesk.Revit.UI.Selection import ObjectType
from RevitServices.Transactions import TransactionManager
from RevitServices.Persistence import DocumentManager
from System.Collections.Generic import *
from Autodesk.Revit.DB import *
from os.path import expanduser
import itertools
import RevitServices
__title__ = 'Alignment'


activeProject = __revit__.ActiveUIDocument
doc = activeProject.Document
opt = Options()
homeDirectory = expanduser("~")


def pickObject():
    __window__.Hide()
    pickedObject = activeProject.Selection.PickObject(ObjectType.Element)
    __window__.Show()
    __window__.Topmost = True
    return pickedObject

def getLinkedDocument(pickedObject):
  return doc.GetElement(pickedObject.ElementId).GetLinkDocument()

def getWallIDs(data):
  index = data.IndexOf("id ")
  wallIds = []
  while index != -1:
    index += 3
    id = getID(data,index)
    wallIds.append(id)
    index = data.IndexOf("id ", index+1) # Floor ID, should be skipped
    index = data.IndexOf("id ", index+1)
  return list(set(wallIds))

def getID(data,index):
  stringID = ""
  while data[index] != " ":
        stringID += data[index]
        index += 1
  return int(stringID)

def getWalls(doc,wallIds):
  walls = []
  for i in wallIds:
    id = ElementId(i)
    walls.append(doc.GetElement(id))
  return walls

def getElements(objectType):
  return FilteredElementCollector(docLink).OfCategory(objectType).WhereElementIsNotElementType().ToElements()

def getSolids(solidType):
  Geom = [i.get_Geometry(opt) for i in solidType]
  return list(itertools.chain(*Geom))

def getBeamSolid(solid):
  instance = solid.GetInstanceGeometry()
  enumerator = instance.GetEnumerator()
  enumerator.MoveNext()
  if enumerator.Current.Faces.Size == 0:
    enumerator.MoveNext()
  return enumerator.Current

def getWallFace(wall):
  for face in range(2, 6):
    if round(wall.Faces[face].FaceNormal[2],1) == 1.0:
        return face

def getBeamFace(beam,z_coord):
  for face in range(0, 6):
    if beam.Faces[face].FaceNormal[2] == z_coord:
        return face

def calculateIntersectedVolume(wall,solid):
  return (BooleanOperationsUtils.ExecuteBooleanOperation(wall, solid, BooleanOperationsType.Intersect).Volume)*0.0283168

def setHeight(wall,height):
  invalidId = ElementId.InvalidElementId
  wall.GetParameters("Top Constraint")[0].Set(invalidId)
  wall.GetParameters("Unconnected Height")[0].Set(height)

pickedObject = pickObject()
docLink = getLinkedDocument(pickedObject)

#file = open(homeDirectory + r'\Desktop\walls.html', "r")
#data = file.read()
#wallIds = getWallIDs(data)

walls = selection
floors = getElements(BuiltInCategory.OST_Floors)
beams = getElements(BuiltInCategory.OST_StructuralFraming)

wallSolids = getSolids(walls)
beamSolids = getSolids(beams)
floorSolids = getSolids(floors)

# Filter solids of beams and floors
beamFloorSolids = []
itr = 0
while itr < len(beamSolids):
    if beamSolids[itr].GetType().ToString() == "Autodesk.Revit.DB.GeometryInstance" and (itr == (len(beamSolids) - 1) or beamSolids[itr+1].GetType().ToString() == "Autodesk.Revit.DB.GeometryInstance"):
        solid = getBeamSolid(beamSolids[itr])
        beamFloorSolids.append(solid)
        itr += 1
    else:
        if beamSolids[itr + 1].Faces.Size != 0:
            beamFloorSolids.append(beamSolids[itr+1])
        elif beamSolids[itr + 2].Faces.Size != 0:
            beamFloorSolids.append(beamSolids[itr + 2])
        itr += 3

# fix geometryInstance (maybe) for hew
for itr in range(len(floorSolids)):
    if floorSolids[itr].GetType().ToString() == "Autodesk.Revit.DB.Solid":
        beamFloorSolids.append(floorSolids[itr])

align = [0.00001, 0.00005, 0.0001, 0.0005]
trans = doc.GetElement(pickedObject.ElementId).GetTotalTransform()
tx = Transaction(doc, 'join walls and floors')
tx.Start()
for j in range(len(walls)):
    if walls[j].WallType.FamilyName == "Curtain Wall":
        continue
    try:
        centroidTest = wallSolids[j].ComputeCentroid()
    except:
        continue

    intersectingElements = []
    wallHeight = walls[j].GetParameters("Unconnected Height")[0].AsDouble()
    wallUpperFace = getWallFace(wallSolids[j])
    for i in range(len(beamFloorSolids)):
        #print(wallUpperFace)
        intersectLowerFace = 0 if i>=len(beams) else getBeamFace(beamFloorSolids[i],-1.0)
        #intersectUpperFace = 1 if i>=len(beams) else getBeamFace(beamFloorSolids[i],1.0)
      
        #wallIntersectDistance = abs(
        #    wallSolids[j].Faces[wallUpperFace].Origin[2] - beamFloorSolids[i].Faces[intersectUpperFace].Origin[2])

        # Check intersection
        for value in align:
            AlignmentTransform = Transform.CreateRotation(XYZ(0, 0, 1), value)
            alignTrans = AlignmentTransform.Multiply(trans)
            transformedSolid = SolidUtils.CreateTransformed(
                beamFloorSolids[i], alignTrans)
            try:
                intersectedVolume = calculateIntersectedVolume(wallSolids[j],transformedSolid)
                if intersectedVolume > value*100:
                    intersectingElements.append(
                        (beamFloorSolids[i].Faces[intersectLowerFace].Origin[2]))
                    break
            except:
                continue
        
        # Check position
        #if round(wallIntersectDistance, 3) == round(wallHeight, 3) and i >= len(beams) and wallSolids[j].ComputeCentroid()[2] > #beamFloorSolids[i].ComputeCentroid()[2]:
#            intersectingElements.append(
#                (beamFloorSolids[i].Faces[intersectUpperFace].Origin[2]))
   
    intersectingElements.sort()

    # Check first upper solid
    #if len(intersectingElements) >= 2:
    roofIndex = -1
    for itr in range(len(intersectingElements)):
        if intersectingElements[itr] > wallSolids[j].ComputeCentroid()[2]:
             roofIndex = itr
             break
    if roofIndex == -1:
        continue
            
    newHeight = abs( wallHeight - abs(wallSolids[j].Faces[wallUpperFace].Origin[2] - intersectingElements[roofIndex]))
    if wallHeight - newHeight < 10:
            setHeight(walls[j],newHeight)
tx.Commit()
