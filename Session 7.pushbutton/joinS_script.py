"""Joins all walls and structural frames."""

__title__ = 'Join Walls\n and Frames'



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
opt = Options()

beams = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_StructuralFraming).WhereElementIsNotElementType().ToElements()

tx = Transaction(doc, 'join walls')
tx.Start()
for i in range(len(beams)):
 r = Reference(beams[i])
 bb = BoundingBoxXYZ
 bb = (beams[i].get_BoundingBox(doc.ActiveView))
 outline = Outline(bb.Min,bb.Max)
 bbfilter = BoundingBoxIntersectsFilter( outline )
 collector = FilteredElementCollector( doc, doc.ActiveView.Id )
 collector.WherePasses(bbfilter)
 j = collector.GetElementIterator()

 while j.MoveNext():
  if j.Current.ToString() == 'Autodesk.Revit.DB.Wall' and not (JoinGeometryUtils.AreElementsJoined(doc, j.Current, beams[i])):
   JoinGeometryUtils.JoinGeometry(doc, j.Current, beams[i])
   j.MoveNext()
tx.Commit() 