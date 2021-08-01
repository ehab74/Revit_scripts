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
doc2 = doc.GetElement(picked.ElementId).GetLinkDocument()
walls= FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Walls).WhereElementIsNotElementType().ToElements()
floors =  FilteredElementCollector(doc2).OfCategory(BuiltInCategory.OST_Floors).WhereElementIsNotElementType().ToElements()

opt = Options()
Geom=[i.get_Geometry(opt) for i in walls]
Solids1 = list(itertools.chain(*Geom))
Geom=[i.get_Geometry(opt) for i in floors]
Solids2 = list(itertools.chain(*Geom))
trans = doc.GetElement(picked.ElementId).GetTotalTransform()

tx = Transaction(doc, 'join walls and floors')
tx.Start()
for j in range(len(walls)):
 f = []
 for i in range(len(floors)):
  s = SolidUtils.CreateTransformed(Solids2[i],trans)
  if (BooleanOperationsUtils.ExecuteBooleanOperation(Solids1[j], s, BooleanOperationsType.Intersect).Volume)*0.0283168 > 0.0  :
    f.append((Solids2[i].ComputeCentroid()[2],i))
 f.sort()
 if len(f)>=2:
  currHeight = walls[j].GetParameters("Unconnected Height")[0].AsDouble()
  height = (Solids1[j].ComputeCentroid()[2] + Solids1[j].GetBoundingBox().Max[2]) - ((Solids2[f[1][1]].ComputeCentroid()[2] - Solids2[f[1][1]].GetBoundingBox().Max[2]))
  inv = ElementId.InvalidElementId
  walls[j].GetParameters("Top Constraint")[0].Set(inv)
  walls[j].GetParameters("Unconnected Height")[0].Set(currHeight - height) 
tx.Commit() 