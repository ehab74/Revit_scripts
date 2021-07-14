clr.AddReference("RevitServices")
import RevitServices
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager

from System.Collections.Generic import *

import itertools

doc = DocumentManager.Instance.CurrentDBDocument
uiapp = DocumentManager.Instance.CurrentUIApplication
app = uiapp.Application

elements=selection
opt = Options()

Geom=[i.get_Geometry(opt) for i in elements]
Solids = list(itertools.chain(*Geom))
OUT=(BooleanOperationsUtils.ExecuteBooleanOperation(Solids[0], Solids[1], BooleanOperationsType.Intersect).Volume)*0.0283168
print(OUT)