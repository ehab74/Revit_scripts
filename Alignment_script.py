"""Alignment of walls with floors and beams of different model"""

__title__ = 'Alignment'





import clr
clr.AddReference('RevitAPI')
clr.AddReference("RevitServices")
import RevitServices
import itertools
from os.path import expanduser
from Autodesk.Revit.DB import *
from System.Collections.Generic import *
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager
from Autodesk.Revit.UI.Selection import ObjectType

activeProject = __revit__.ActiveUIDocument
doc = activeProject.Document
opt = Options()
homeDirectory = expanduser("~")

def pickobject():
    #__window__.Hide()
    pickedObject = activeProject.Selection.PickObject(ObjectType.Element)
    #__window__.Show()
    #__window__.Topmost = True
    return pickedObject

pickedObject = pickobject()	
docLink = doc.GetElement(pickedObject.ElementId).GetLinkDocument()

file = open(homeDirectory + r'\Desktop\walls.html',"r")
data = file.read()

index = data.IndexOf("id ")
wallIds = []

while index!=-1:
 index+=3
 stringID = ""
 
 while data[index] != " ":
  stringID+=data[index]
  index+=1 

 id = int(stringID)
 wallIds.append(id)
 index = data.IndexOf("id ",index+1)
 index = data.IndexOf("id ",index+1)

wallIds = list(set(wallIds))
walls = []
for i in wallIds:
 id = ElementId(i)
 walls.append(doc.GetElement(id))
 
floors =  FilteredElementCollector(docLink).OfCategory(BuiltInCategory.OST_Floors).WhereElementIsNotElementType().ToElements()
beams =  FilteredElementCollector(docLink).OfCategory(BuiltInCategory.OST_StructuralFraming).WhereElementIsNotElementType().ToElements()

Geom=[i.get_Geometry(opt) for i in walls]
wallSolids = list(itertools.chain(*Geom))

Geom=[i.get_Geometry(opt) for i in beams]
beamSolids = list(itertools.chain(*Geom))
beamFloorSolids = []

Geom=[i.get_Geometry(opt) for i in floors]
floorSolids = list(itertools.chain(*Geom))

itr = 0
while itr <len(beamSolids): 
 if  beamSolids[l].GetType().ToString() == "Autodesk.Revit.DB.GeometryInstance" and (itr == (len(beamSolids) - 1) or beamSolids[l+1].GetType().ToString() == "Autodesk.Revit.DB.GeometryInstance"):
  instance = beamSolids[l].GetInstanceGeometry()
  enumerator = instance.GetEnumerator()
  enumerator.MoveNext()
  if enumerator.Current.Faces.Size == 0:
   enumerator.MoveNext()
  beamFloorSolids.append(enumerator.Current)
  itr +=1
 else:
  if beamSolids[itr +1].Faces.Size != 0:
   beamFloorSolids.append(beamSolids[l+1])
  elif beamSolids[itr +2].Faces.Size !=0:
   beamFloorSolids.append(beamSolids[itr +2])
  itr +=3

## fix geometryInstance (maybe) for hew
for i in range(len(floorSolids)):
 if floorSolids[i].GetType().ToString() == "Autodesk.Revit.DB.Solid":
  beamFloorSolids.append(floorSolids[i])

align = [0.00001,0.00005,0.0001,0.0005]
trans = doc.GetElement(picked.ElementId).GetTotalTransform()
tx = Transaction(doc, 'join walls and floors')
tx.Start()
for j in range(len(walls)):
 if walls[j].WallType.FamilyName == "Curtain Wall":
  continue
 try:
  centroidTest = wallSolids[j].ComputeCentroid()
 except:
  continue
  
 f = []
 wallHeight = walls[j].GetParameters("Unconnected Height")[0].AsDouble()
 for i in range(len(beamFloorSolids)):
  itr = 0
  b1 = 0
  b2 = 1
  if i < len(beams):
   for x in range(0,6):
    if beamFloorSolids[i].Faces[x].FaceNormal[2] == -1.0:
     b1 = x
    elif beamFloorSolids[i].Faces[x].FaceNormal[2] == 1.0:
     b2 = x
  for itr in range(2,6):
   if wallSolids[j].Faces[itr].FaceNormal[2] == 1.0:
    break 
  h1 = abs(wallSolids[j].Faces[itr].Origin[2] - beamFloorSolids[i].Faces[1].Origin[2])
  for value in align:
   t1 = Transform.CreateRotation(XYZ(0,0,1),value)
   t2 = t1.Multiply(trans)
   s = SolidUtils.CreateTransformed(beamFloorSolids[i],t2)
   try:
    flag = (BooleanOperationsUtils.ExecuteBooleanOperation(wallSolids[j], s, BooleanOperationsType.Intersect).Volume)*0.0283168
    if flag > value*100 :
     f.append((beamFloorSolids[i].Faces[b1].Origin[2],i))
     break
   except:
    continue   
  if round(h1,3) == round(wallHeight,3) and i>=len(beams) and wallSolids[j].ComputeCentroid()[2]>beamFloorSolids[i].ComputeCentroid()[2]:
   f.append((beamFloorSolids[i].Faces[b2].Origin[2],i)) 
 f.sort()
 if len(f)>=2:
  roof = -1
  for n in range(len(f)):
   if f[n][0]>wallSolids[j].ComputeCentroid()[2]:
    roof = n
    break
  if roof == -1:
   continue
  currHeight = walls[j].GetParameters("Unconnected Height")[0].AsDouble()
  height = abs(f[roof][0] - f[roof-1][0])
  if currHeight - height< 10 :
   inv = ElementId.InvalidElementId
   walls[j].GetParameters("Top Constraint")[0].Set(inv)
   walls[j].GetParameters("Unconnected Height")[0].Set(height) 
tx.Commit() 