"""Alignment of walls with floors and beams of different model"""

from Autodesk.Revit.UI.Selection import ObjectType
from RevitServices.Transactions import TransactionManager
from RevitServices.Persistence import DocumentManager
from System.Collections.Generic import *
from Autodesk.Revit.DB import *
from os.path import expanduser
import itertools
import RevitServices
__title__ = 'Alignment'


import clr
clr.AddReference('RevitAPI')
clr.AddReference("RevitServices")

activeProject = __revit__.ActiveUIDocument
doc = activeProject.Document
opt = Options()
homeDirectory = expanduser("~")


def pickobject():
    # __window__.Hide()
    pickedObject = activeProject.Selection.PickObject(ObjectType.Element)
    # __window__.Show()
    #__window__.Topmost = True
    return pickedObject


pickedObject = pickobject()
docLink = doc.GetElement(pickedObject.ElementId).GetLinkDocument()

file = open(homeDirectory + r'\Desktop\walls.html', "r")
data = file.read()

index = data.IndexOf("id ")
wallIds = []

while index != -1:
    index += 3
    stringID = ""

    while data[index] != " ":
        stringID += data[index]
        index += 1

    id = int(stringID)
    wallIds.append(id)
    index = data.IndexOf("id ", index+1)
    index = data.IndexOf("id ", index+1)

wallIds = list(set(wallIds))
walls = []
for i in wallIds:
    id = ElementId(i)
    walls.append(doc.GetElement(id))

floors = FilteredElementCollector(docLink).OfCategory(
    BuiltInCategory.OST_Floors).WhereElementIsNotElementType().ToElements()
beams = FilteredElementCollector(docLink).OfCategory(
    BuiltInCategory.OST_StructuralFraming).WhereElementIsNotElementType().ToElements()

Geom = [i.get_Geometry(opt) for i in walls]
wallSolids = list(itertools.chain(*Geom))

Geom = [i.get_Geometry(opt) for i in beams]
beamSolids = list(itertools.chain(*Geom))
beamFloorSolids = []

Geom = [i.get_Geometry(opt) for i in floors]
floorSolids = list(itertools.chain(*Geom))

itr = 0
while itr < len(beamSolids):
    if beamSolids[l].GetType().ToString() == "Autodesk.Revit.DB.GeometryInstance" and (itr == (len(beamSolids) - 1) or beamSolids[l+1].GetType().ToString() == "Autodesk.Revit.DB.GeometryInstance"):
        instance = beamSolids[l].GetInstanceGeometry()
        enumerator = instance.GetEnumerator()
        enumerator.MoveNext()
        if enumerator.Current.Faces.Size == 0:
            enumerator.MoveNext()
        beamFloorSolids.append(enumerator.Current)
        itr += 1
    else:
        if beamSolids[itr + 1].Faces.Size != 0:
            beamFloorSolids.append(beamSolids[l+1])
        elif beamSolids[itr + 2].Faces.Size != 0:
            beamFloorSolids.append(beamSolids[itr + 2])
        itr += 3

# fix geometryInstance (maybe) for hew
for itr in range(len(floorSolids)):
    if floorSolids[itr].GetType().ToString() == "Autodesk.Revit.DB.Solid":
        beamFloorSolids.append(floorSolids[itr])

align = [0.00001, 0.00005, 0.0001, 0.0005]
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

    IntersectingElements = []
    wallHeight = walls[j].GetParameters("Unconnected Height")[0].AsDouble()
    for i in range(len(beamFloorSolids)):
        wallUpperFace = 0
        beamUpperFace = 0
        beamLowerFace = 1
        if i < len(beams):
            for face in range(0, 6):
                if beamFloorSolids[i].Faces[face].FaceNormal[2] == -1.0:
                    beamUpperFace = face
                elif beamFloorSolids[i].Faces[face].FaceNormal[2] == 1.0:
                    beamLowerFace = face
        for wallUpperFace in range(2, 6):
            if wallSolids[j].Faces[wallUpperFace].FaceNormal[2] == 1.0:
                break
        wallFloorDistance = abs(
            wallSolids[j].Faces[wallUpperFace].Origin[2] - beamFloorSolids[i].Faces[1].Origin[2])
        for value in align:
            AlignmentTransform = Transform.CreateRotation(XYZ(0, 0, 1), value)
            t2 = AlignmentTransform.Multiply(trans)
            transformedSolid = SolidUtils.CreateTransformed(
                beamFloorSolids[i], t2)
            try:
                flag = (BooleanOperationsUtils.ExecuteBooleanOperation(
                    wallSolids[j], transformedSolid, BooleanOperationsType.Intersect).Volume)*0.0283168
                if flag > value*100:
                    IntersectingElements.append(
                        (beamFloorSolids[i].Faces[beamUpperFace].Origin[2]))
                    break
            except:
                continue
        if round(wallFloorDistance, 3) == round(wallHeight, 3) and i >= len(beams) and wallSolids[j].ComputeCentroid()[2] > beamFloorSolids[i].ComputeCentroid()[2]:
            IntersectingElements.append(
                (beamFloorSolids[i].Faces[beamLowerFace].Origin[2]))
    IntersectingElements.sort()
    if len(IntersectingElements) >= 2:
        roofIndex = -1
        for itr in range(len(IntersectingElements)):
            if IntersectingElements[itr] > wallSolids[j].ComputeCentroid()[2]:
                roofIndex = itr
                break
        if roofIndex == -1:
            continue
        currHeight = walls[j].GetParameters("Unconnected Height")[0].AsDouble()
        height = abs(
            IntersectingElements[roofIndex] - IntersectingElements[roofIndex-1])
        if currHeight - height < 10:
            invalidId = ElementId.InvalidElementId
            walls[j].GetParameters("Top Constraint")[0].Set(invavlidId)
            walls[j].GetParameters("Unconnected Height")[0].Set(height)
tx.Commit()
