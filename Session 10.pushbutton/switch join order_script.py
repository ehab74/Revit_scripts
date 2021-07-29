"""Switch Join Order of Floors and Columns."""

__title__ = 'Switch Join\nFloors and Columns'



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

floors= FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Floors).WhereElementIsNotElementType().ToElements()
columns = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Columns).WhereElementIsNotElementType().ToElements()
opt = Options()

Geom=[i.get_Geometry(opt) for i in floors]
Solids1 = list(itertools.chain(*Geom))


Geom=[i.get_Geometry(opt) for i in columns]
Solids2 = []
for i in range(len(Geom)):
 x = Geom[i].GetEnumerator()
 x.MoveNext()
 x.MoveNext()
 Solids2.append(x.Current)

tx = Transaction(doc, 'Switch join order of floors and columns')
tx.Start()
for i in range (len(floors)):
 for j in range (len(columns)):
  if (JoinGeometryUtils.AreElementsJoined(doc, columns[j], floors[i])):
    JoinGeometryUtils.SwitchJoinOrder(doc, columns[j], floors[i])
tx.Commit()   
 