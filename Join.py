import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit.DB import *
from System.Collections.Generic import *
clr.AddReference("RevitServices")
import RevitServices
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager

if JoinGeometryUtils.AreElementsJoined(doc, selection[0], selection[1]):
 tx = Transaction(doc, 'set door hinges side')
 tx.Start()


 JoinGeometryUtils.UnjoinGeometry(doc, selection[1], selection[0])

 tx.Commit()
else :
 tx = Transaction(doc, 'set door hinges side')
 tx.Start()


 JoinGeometryUtils.JoinGeometry(doc, selection[1], selection[0])

 tx.Commit()