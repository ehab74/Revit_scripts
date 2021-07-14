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
 for j in range (len(walls)):
  if not (JoinGeometryUtils.AreElementsJoined(doc, walls[i], walls[j])) and (BooleanOperationsUtils.ExecuteBooleanOperation(Solids[i], Solids[j], BooleanOperationsType.Intersect).Volume)*0.0283168 > 0.0 and i!=j:
    JoinGeometryUtils.JoinGeometry(doc, walls[i], walls[j])
    
tx.Commit()