import clr
clr.AddReference ("RevitNodes")
import Revit
clr.ImportExtensions(Revit.Elements)
clr.AddReference("RevitServices")
import RevitServices
from RevitServices.Persistence import DocumentManager
from System.Collections.Generic import *
import Autodesk
from Autodesk.Revit.DB import *
def pickobject():
    from Autodesk.Revit.UI.Selection import ObjectType
    __window__.Hide()
    picked = uidoc.Selection.PickObject(ObjectType.Element)
    __window__.Show()
    __window__.Topmost = True
    return picked
x = pickobject()	
list = List[ElementId]()
list.Add(x.ElementId)
sel = uidoc.Selection.SetElementIds(list)