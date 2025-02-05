# -*- coding: utf-8 -*-
from __future__ import unicode_literals
#
# ***************************************************************************
# *                                                                        *
# * This file is a part of the Open Source Nurbs Workbench - FreeCAD.  *
# *                                                                        *
# * Copyright (C) 2021                                                     *
# *                                                                        *
# *                                                                        *
# * This library is free software; you can redistribute it and/or          *
# * modify it under the terms of the GNU Lesser General Public             *
# * License as published by the Free Software Foundation; either           *
# * version 2 of the License, or (at your option) any later version.       *
# *                                                                        *
# * This library is distributed in the hope that it will be useful,        *
# * but WITHOUT ANY WARRANTY; without even the implied warranty of         *
# * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU      *
# * Lesser General Public License for more details.                        *
# *                                                                        *
# * You should have received a copy of the GNU Lesser General Public       *
# * License along with this library; if not, If not, see                   *
# * <http://www.gnu.org/licenses/>.                                        *
# * Modified and adapted to Desing456 by:                                  *
# * Author : Mariwan Jalal   mariwan.jalal@gmail.com                       *
# **************************************************************************

'''dynamic offset node'''

from say import *

import FreeCAD as App
import FreeCADGui as Gui
import os, sys 

import NURBSinit
Gui.ActiveDocument=None
import FreeCAD as App

if 0:
    try:
        App.open(NURBSinit.DATA_PATH+"tt_offset_example.fcstd")
        App.setActiveDocument("tt_offset_example")
        App.ActiveDocument=App.getDocument("tt_offset_example")
        Gui.ActiveDocument=Gui.getDocument("tt_offset_example")
    except:
        pass

import datatools
#reload (datatools)

import scipy.interpolate


## calculates a scipy.interpolate.interp1d 
# for the floatlist obj.datalist
#
# in debug mode the calculated shape contains wires for both curves and 
# connecting lines between corresponding points on all curves



def myupdate(obj):
    '''interpolate the obj.datalist to get the obj.Shape as BSpline'''

    fl=obj.data
    if fl == None: return

    x=range(len(fl.datalist))
    f = scipy.interpolate.interp1d(x, fl.datalist)

    def k(i,l):
        data=fl.datalist
        rc=f(1.0*i/l*(len(data)-1))/fl.factor
        return rc

    print ("update ..")
    apols=[]
    apols1=[]
    apols2=[]
    print ("lens")
    print (len(obj.curveO.Shape.Edges))
    print (len(obj.curveI.Shape.Edges))
    obj.curveI
    obj.curveO
    for i,e in enumerate(obj.curveI.Shape.Edges):

        try:
            c1=obj.curveI.Shape.Edges[i]
            c2=obj.curveO.Shape.Edges[i]
        except:
            continue

        ll=c1.Length
        n=int(round(ll/100))
        if n<2: n=1
        print ("Loop",ll,n)

        pols1=c1.discretize(n)
        pols2=c2.discretize(n)

        apols1 +=pols1[1:]
        apols2 +=pols2[1:]


    l=len(apols1)
    apols=[apols1[i]*k(i,l)+apols2[i]*(1-k(i,l)) for i in range(l)]
    apolsn=[apols[0]]
    apols1n=[apols1[0]]
    apols2n=[apols2[0]]
    for i in range(l-1):
        if (apols[i]-apols[i+1]).Length >70:
            apolsn.append(apols[i+1])
            apols1n.append(apols1[i+1])
            apols2n.append(apols2[i+1])
    l=len(apolsn)
    apols=apolsn
    apols1=apols1n
    apols2=apols2n

    comps=[]
    
    comps=[Part.makePolygon([apols1[i],apols[i],apols2[i]]) for i in range(l)]
    comps += [Part.makePolygon(apols),Part.makePolygon(apols1),Part.makePolygon(apols2)]

    bc=Part.BSplineCurve()
    bc.interpolate(apols)
    # bc.setPeriodic()
    comps.append(bc.toShape())
    if obj.debug: 
        obj.Shape=Part.Compound(comps)
    else:
        obj.Shape=bc.toShape()


from say import *
import pyob

## A configurable offset curve
#
# Properties
# ----------
#
#  - **data** - link to a FloatList node
#  - **curveO** - inner offset curve node 
#  - **curveI** - outer offset curve node
#  - **debug**  - displays some helping 2D information
# 
# Icon
# ----
# @image html plane.svg
#
# Links
# -----
#
#  - [Usage](http://freecadbuch.de/doku.php?id=nurbs:dynaoffset)
#  - [Video](https://youtu.be/7wKXfh2fifY) (25.06.2017)<br>
#  - [Git source](https://github.com/microelly2/freecad-nurbs/blob/master//dynamicoffset.py)
#
# Example
# -------
#\code 
#datatools
#fl=.datatools.createFloatlist("ParameterList")
#fl.val007=10
#
#dof=createDynaoffset()
#dof.data=fl
#
#  \endcode



#  link run()
#  link DynaOffset
#  link DynaOffset.execute()
#  link datatools.FloatList
#



class DynaOffset(pyob.FeaturePython):

    ##\cond
    def __init__(self, obj):
        obj.Proxy = self
        self.Type = self.__class__.__name__
        pyob.ViewProvider(obj.ViewObject) 


    def XonChanged(proxy,obj,prop):
        '''run myExecute for property prop: relativePosition and vertexNumber'''
        
        print ("onChanged ",prop)
        if prop.startswith("val"):
            data=[]
            for i in range(12):
                data.append(getattr(obj, "val%03d" % (i)))
            print (data)
            obj.datalist=data
    ##\endcond


    def execute(self,proxy,obj):
        ''' update curve'''
        myupdate(obj)



def createDynaoffset(name="DynamicOffset"):
    '''create a DynaOffset node'''

    obj = App.ActiveDocument.addObject("Part::FeaturePython",name)

    obj.addProperty("App::PropertyLink", "data", "Values")
    obj.addProperty("App::PropertyLink", "curveO", "Values")
    obj.addProperty("App::PropertyLink", "curveI", "Values")
    obj.addProperty("App::PropertyBool", "debug", "Values")

    DynaOffset(obj)
    return obj

## method for workbench menu entry
class Nurbs_DynamicOffsetRun:
    def Activated(self):
        '''create a DynaOffset'''
        createDynaoffset()

    def GetResources(self):
        
        from PySide.QtCore import QT_TRANSLATE_NOOP
        """Set icon, menu and tooltip."""
        _tooltip = ("Nurbs_DynamicOffsetRun")
        return {'Pixmap': NURBSinit.ICONS_PATH+'draw.svg',
                'MenuText': QT_TRANSLATE_NOOP("Nurbs", "Nurbs_DynamicOffsetRun"),
                'ToolTip': QT_TRANSLATE_NOOP("Nurbs ", _tooltip)}

Gui.addCommand("Nurbs_DynamicOffsetRun", Nurbs_DynamicOffsetRun())



#\cond
class Nurbs_DynamicOffsetMain:
    def Activated(self):
        self.runmain()
    def runmain(self):
        fl2=App.ActiveDocument.getObject("ParmeterList")
        if fl2 == None: 
            fl2=datatools.createFloatlist("ParameterList")
            fl2.val007=10
        dof=createDynaoffset()
        dof.data=fl2

    def GetResources(self):
        
        from PySide.QtCore import QT_TRANSLATE_NOOP
        """Set icon, menu and tooltip."""
        _tooltip = ("Nurbs_DynamicOffsetMain")
        return {'Pixmap': NURBSinit.ICONS_PATH+'draw.svg',
                'MenuText': QT_TRANSLATE_NOOP("Nurbs", "Nurbs_DynamicOffsetMain"),
                'ToolTip': QT_TRANSLATE_NOOP("Nurbs ", _tooltip)}

Gui.addCommand("Nurbs_DynamicOffsetMain", Nurbs_DynamicOffsetMain())




#\endcond
