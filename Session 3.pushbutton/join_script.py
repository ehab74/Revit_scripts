"""Joins all walls."""

__title__ = 'Join\nWalls'



import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit.DB import *
from System.Collections.Generic import *
clr.AddReference("RevitServices")
import RevitServices
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager
import itertools
doc = __revit__.ActiveUIDocument.Document

walls= FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Walls).WhereElementIsNotElementType().ToElements()
opt = Options()

Geom=[i.get_Geometry(opt) for i in walls]
Solids = list(itertools.chain(*Geom))
tx = Transaction(doc, 'join walls')
tx.Start()
for i in range (len(walls)):
 surface1 = Solids[i].Faces[0].GetSurface()
 surface2 = Solids[i].Faces[1].GetSurface()
 for j in range (i+1,len(walls)):
  surface3 = Solids[j].Faces[0].GetSurface()
  surface4 = Solids[j].Faces[1].GetSurface()
  if not (JoinGeometryUtils.AreElementsJoined(doc, walls[i], walls[j])) and (BooleanOperationsUtils.ExecuteBooleanOperation(Solids[i], Solids[j], BooleanOperationsType.Intersect).Volume)*0.0283168 > 0.0:
    JoinGeometryUtils.JoinGeometry(doc, walls[i], walls[j])
  elif surface1.Project(surface4.Origin)[1] < 0.000001 or surface2.Project(surface3.Origin)[1] < 0.000001:
     JoinGeometryUtils.JoinGeometry(doc, walls[i], walls[j])
    
tx.Commit()