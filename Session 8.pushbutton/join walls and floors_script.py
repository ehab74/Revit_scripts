"""Joins walls with floors of the selected model."""

__title__ = 'Join Walls\n and Floors'


import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit.DB import *
from System.Collections.Generic import *
clr.AddReference("RevitServices")
import RevitServices
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager
import itertools

uidoc = __revit__.ActiveUIDocument
doc = uidoc.Document

def pickobject():
    from Autodesk.Revit.UI.Selection import ObjectType
    #__window__.Hide()
    picked = uidoc.Selection.PickObject(ObjectType.Element)
    #__window__.Show()
    #__window__.Topmost = True
    return picked
picked = pickobject()	
model = List[ElementId]()
model.Add(picked.ElementId)
#uidoc.Selection.SetElementIds(model)
doc2 = doc.GetElement(model[0]).GetLinkDocument()
walls= FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Walls).WhereElementIsNotElementType().ToElements()
floors =  FilteredElementCollector(doc2).OfCategory(BuiltInCategory.OST_Floors).WhereElementIsNotElementType().ToElements()

opt = Options()
Geom=[i.get_Geometry(opt) for i in walls]
Solids1 = list(itertools.chain(*Geom))
Geom=[i.get_Geometry(opt) for i in floors]
Solids2 = list(itertools.chain(*Geom))
trans = doc.GetElement(model[0]).GetTotalTransform()

tx = Transaction(doc, 'join walls and floors')
tx.Start()
for j in range(len(walls)):
 f1 = -1
 f2 = -1
 intersect = 0 
 for i in range(len(floors)):
  s = SolidUtils.CreateTransformed(Solids2[i],trans)
  if (BooleanOperationsUtils.ExecuteBooleanOperation(Solids1[j], s, BooleanOperationsType.Intersect).Volume)*0.0283168 > 0.0 and  not(floors[i].Document.Equals(walls[j].Document)) :
   if f1 == -1:
    f1 = i
   else:
    f2 = i
   intersect+=1
   continue
  for k in range(2,6):
   if ((Solids1[j].Faces[k].GetSurface()).Project(Solids2[i].Faces[0].GetSurface().Origin)[1] < 0.000001 or (Solids1[j].Faces[k].GetSurface()).Project(Solids2[i].Faces[1].GetSurface().Origin)[1] < 0.000001) and  not(floors[i].Document.Equals(walls[j].Document)):
    f2 = i
    break
 if f1 != -1 and f2 != -1:
  if intersect == 2:
   p1 = walls[j].Location.Curve.GetEndPoint(0)
   p2 = walls[j].Location.Curve.GetEndPoint(1)
   li = Line
   fmin = -1
   if Solids2[f1].Faces[1].Origin[2] < Solids2[f2].Faces[1].Origin[2]:
    fmin = f1
   else:
    fmin = f2
   for k in range(2,6):
     if Solids1[0].Faces[k].FaceNormal[2] == -1:
       p1 = p1.Add(XYZ(0,0,abs(abs(Solids1[j].Faces[k].Origin[2]) - abs(Solids2[fmin].Faces[1].Origin[2]))))
       p2 = p2.Add(XYZ(0,0,abs(abs(Solids1[j].Faces[k].Origin[2]) - abs(Solids2[fmin].Faces[1].Origin[2]))))
       walls[j].Location.Curve = li.CreateBound(p1,p2)
  if (Solids2[f1].ComputeCentroid()[2] > 0 and Solids2[f2].ComputeCentroid()[2] > 0) or (Solids2[f1].ComputeCentroid()[2] < 0 and Solids2[f2].ComputeCentroid()[2] < 0):      
    height = abs( abs(Solids2[f1].ComputeCentroid()[2]) - abs(Solids2[f2].ComputeCentroid()[2])) - floors[i].get_Parameter(BuiltInParameter.FLOOR_ATTR_THICKNESS_PARAM).AsDouble()
  else :
    height = abs( abs(Solids2[f1].ComputeCentroid()[2]) - abs(Solids2[f2].ComputeCentroid()[2]))
  walls[j].GetParameters("Unconnected Height")[0].Set(height) 
tx.Commit()  