"""Joins all walls and columns."""

__title__ = 'Join Walls\n and Columns'



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
columns = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Columns).WhereElementIsNotElementType().ToElements()
opt = Options()

Geom=[i.get_Geometry(opt) for i in walls]
Solids1 = list(itertools.chain(*Geom))


Geom=[i.get_Geometry(opt) for i in columns]
Solids2 = []
for i in range(len(Geom)):
 x = Geom[i].GetEnumerator()
 x.MoveNext()
 x.MoveNext()
 Solids2.append(x.Current)

tx = Transaction(doc, 'join walls and columns')
tx.Start()
for i in range (len(walls)):
 for j in range (len(columns)):
  if not (JoinGeometryUtils.AreElementsJoined(doc, columns[j], walls[i])) and (BooleanOperationsUtils.ExecuteBooleanOperation(Solids1[i], Solids2[j], BooleanOperationsType.Intersect).Volume)*0.0283168 > 0.0 :
    JoinGeometryUtils.JoinGeometry(doc, columns[j], walls[i])
tx.Commit()   
 