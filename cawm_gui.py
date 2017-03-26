
#   ca_wizard_mechanical, version 0.1
#   Allows the generation of comm-files for simple 3D structural analyses in code_aster with an interactive GUI
#
#   This work is licensed under the terms and conditions of the GNU General Public License version 3
#   Copyright (C) 2017 Dominik Lechleitner
#   Contact: kaktus018(at)gmail.com
#   GitHub repository: https://github.com/kaktus018/ca_wizard_mechanical
#
#   This file is part of ca_wizard_mechanical.
# 
#   ca_wizard_mechanical is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
# 
#   ca_wizard_mechanical is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
# 
#   You should have received a copy of the GNU General Public License
#   along with ca_wizard_mechanical.  If not, see <http://www.gnu.org/licenses/>.


import os
import pickle
import shutil
import webbrowser
import time
import re
import codecs
import xml.etree.ElementTree as ET
import urllib.parse

from tkinter import *
from tkinter.ttk import *
from tkinter import messagebox
from tkinter import filedialog

from cawm_classes import *

os.chdir(os.path.dirname(os.path.abspath(__file__)))

names = []
materialSets = []
nodeJointSets = []
restraintSets = []
loadSets = []
contactSets = []
thermalSets = []
geomEntities = ("Volume","Surface","Edge","Vertex/Node","Node joint group")

matLibPath = "matLib.xml"
cawmVersion = "0.1"
mainFormSize = "650x600"

setMatLibPath(matLibPath)
setVersion(cawmVersion)

### General functions

# Get node group names of enum
def getNames(typeEnum):
    list=[]
    for typeEl in typeEnum:
        if not len(names) == 0:
            for el in names:
                if el[1] == geomEntities[typeEl]:
                    list.append(el[0])
        if typeEl == 0:
            list.append("whole mesh")
    list.sort()
    return list        

# Get the names of materials in matLib.xml
def getMatLibNamesFromXML():
    list=[]
    root = ET.parse(matLibPath).getroot()
    for child in root:
        list.append(child.get("name"))
    list.sort()
    return list

### GUI functions

# Create popup window
def createPopup(title,width,height):
    popup = Toplevel()
    popup.title(title)
    popup.geometry(str(width) + "x" + str(height) + "+" + str(int(mainForm.winfo_x() + mainForm.winfo_width()/2 - width/2)) + "+" + str(int(mainForm.winfo_y() + mainForm.winfo_height()/2 - height/2)))
    popup.resizable(width=False, height=False)
    popup.lift()
    popup.grab_set()
    popup.focus_force()
    return popup

# Add a name of a node group
def addName():
    popup = createPopup("Add node group",300,130)
    Label(popup, text="Enter name of the node group:").pack()
    nameEntry = Entry(popup)
    nameEntry.pack()
    Label(popup, text="Select type of node group:").pack()
    typeCB = Combobox(popup, values=geomEntities, state='readonly')
    typeCB.current(1)
    typeCB.pack(pady=5, padx=10)
    def clickOK(close):
        if nameEntry.get():
            if nameEntry.get() == "whole mesh":
                messagebox.showerror("ca_wizard", "\"whole mesh\" is a keyword that can not be used in a name assignment. However, you will be able to assign properties and constraints" + \
                " on the whole mesh (code_aster keyword \"TOUT\") where volumes are allowed.")
                popup.lift()
                return
            if not nameEntry.get() in [names[i][0] for i in range(len(names))]:
                names.append([nameEntry.get(),typeCB.get()])
            else:
                messagebox.showerror("ca_wizard", "Element is already in list!")
                popup.lift()
                return
        else:
            messagebox.showerror("ca_wizard", "Name can not be empty!")
            popup.lift()
            return
        updateNames()
        if close:
            popup.destroy()
        else:
            nameEntry.delete(0, 'end')
            nameEntry.focus_force()
    popup.bind("<Return>", lambda x: clickOK(0))
    popup.bind("<Escape>", lambda x: popup.destroy())
    box = Frame(popup)
    box.pack()
    Button(box, text="Apply", command=lambda: clickOK(0)).pack(side=LEFT,pady=5,padx=2)    
    Button(box, text="Apply & Close", command=lambda: clickOK(1)).pack(side=LEFT,pady=5,padx=2)
    Button(box, text="Close", command=popup.destroy).pack(pady=5,padx=2)
    nameEntry.focus_force()
    
# Update node group names
def updateNames():
    # Names Listbox
    namesListbox.delete(0,END)
    for item in names:
        namesListbox.insert(END, item[0]+" ("+item[1]+")")
    # Materials CB
    matAssiMatCB['values'] = getNames([0])
    if not matAssiMatCB.get() in [getNames([0])[i] for i in range(len(getNames([0])))]:
        matAssiMatCB.set('')
    # Node joints CBs
    nodeJointGroupNameCB['values'] = getNames([4])
    if not nodeJointGroupNameCB.get() in [getNames([4])[i] for i in range(len(getNames([4])))]:
        nodeJointGroupNameCB.set('')
    nodeJointNodeNameCB['values'] = getNames([3])
    if not nodeJointNodeNameCB.get() in [getNames([3])[i] for i in range(len(getNames([3])))]:
        nodeJointNodeNameCB.set('')
    # Restraints CB
    restraintAssiNameCB['values'] = getNames([1,2,3])
    if not restraintAssiNameCB.get() in [getNames([1,2,3])[i] for i in range(len(getNames([1,2,3])))]:
        restraintAssiNameCB.set('')
    # Loads CB
    loadTypeCBChangedEvent(None)
    # Contacts CB
    contactMasterCB['values'] = getNames([1])
    if not contactMasterCB.get() in [getNames([1])[i] for i in range(len(getNames([1])))]:
        contactMasterCB.set('')
    contactSlaveCB['values'] = getNames([1])
    if not contactSlaveCB.get() in [getNames([1])[i] for i in range(len(getNames([1])))]:
        contactSlaveCB.set('')
    # Thermal CB
    thermalAssiNameCB['values'] = getNames([0])
    if not thermalAssiNameCB.get() in [getNames([0])[i] for i in range(len(getNames([0])))]:
        thermalAssiNameCB.set('')
    # Results CB
    resultsNameCB['values'] = getNames([0])
    if not resultsNameCB.get() in [getNames([0])[i] for i in range(len(getNames([0])))]:
        resultsNameCB.set('')
        
# Delete a name
def deleteName():
    if not namesListbox.curselection()==():
        name = str.split(namesListbox.get(namesListbox.curselection()[0]),"(")[0]
        name = name[:-1]
        nameType = str.split(namesListbox.get(namesListbox.curselection()[0]),"(")[1]
        nameType = nameType[:-1]
        if messagebox.askquestion("ca_wizard", "Do you really want to delete "+name+"?", icon='warning')=="yes":
            names.remove([name, nameType])
            updateNames()
    else:
        messagebox.showerror("ca_wizard", "Nothing selected.")
        
# Analysis type combobox changed event
def analysisTypeCBChangedEvent(evt):
    if analysisTypeCB.get() == "linear static":
        ntbook.tab(7, state="disabled")
        disableWidgets(analysisNonLinSolverOptionsBox)
    else:
        ntbook.tab(7, state="normal")
        enableWidgets(analysisNonLinSolverOptionsBox)
        if analysisTimeStepsEntry.get() == "0":
            analysisTimeStepsEntry.delete(0, 'end')
            analysisTimeStepsEntry.insert(END, "1")
        
# Refresh the material list combobox
def refreshMatCB():
    matSelMatCB['values'] = getMatLibNamesFromXML()
    matSelMatCB.set('')
        
# Add a material set
def addMaterialSet():
    popup = createPopup("Add material assignment",300,80)
    Label(popup, text="Enter name of material assignment:").pack()
    nameEntry = Entry(popup)
    nameEntry.pack()
    nameEntry.insert(0,"materialAssignment"+str(len(materialSets)+1))
    def clickOK():
        if nameEntry.get():
            if not nameEntry.get() in [materialSets[i].assiName for i in range(len(materialSets))]:
                materialSets.append(MaterialSet(nameEntry.get(),matAssiMatCB.get(),matSelMatCB.get()))
            else:
                messagebox.showerror("ca_wizard", "This assignment name is already in list!")
                popup.lift()
                return
        else:
            messagebox.showerror("ca_wizard", "Name can not be empty!")
            popup.lift()
            return
        updateMatAssi()
        popup.destroy()
    popup.bind("<Return>", lambda x: clickOK())
    popup.bind("<Escape>", lambda x: popup.destroy())
    box = Frame(popup)
    box.pack()
    Button(box, text="Ok", command=clickOK).pack(side=LEFT,pady=5,padx=2)    
    Button(box, text="Cancel", command=popup.destroy).pack(pady=5,padx=2)
    nameEntry.focus_force()
    
# Update material assignments
def updateMatAssi():
    matAssiListbox.delete(0,END)
    for item in materialSets:
        matAssiListbox.insert(END, item.assiName)
    disableWidgets(matAssiGroup)

# Delete material assignment
def deleteMatAssi():
    if not matAssiListbox.curselection()==():
        if messagebox.askquestion("ca_wizard", "Do you really want to delete "+matAssiListbox.get(matAssiListbox.curselection()[0])+"?", icon='warning')=="yes":
            for item in materialSets:
                if item.assiName == matAssiListbox.get(matAssiListbox.curselection()[0]):
                    materialSets.remove(item)
                    break
            updateMatAssi()
    else:
        messagebox.showerror("ca_wizard", "Nothing selected.")

# Change material assignment
def changeMatAssi():
    name = matAssiNameLbl.cget("text")
    for item in materialSets:
        if item.assiName == name:
            item.__init__(name,matAssiMatCB.get(),matSelMatCB.get())
            disableWidgets(matAssiGroup)
            break
        
# Material assignments listbox selection changed event
def matAssiListboxSelectionChanged(evt):
    assiName = matAssiListbox.get(matAssiListbox.curselection())
    if not assiName == ():
        for item in materialSets:
            if item.assiName == assiName:
                enableWidgets(matAssiGroup)
                matAssiNameLbl['text'] = assiName
                for i in range(len(getNames([0]))):
                    matAssiMatCB.set('')
                    if item.nodalGroupName == getNames([0])[i]:
                        matAssiMatCB.current(i)
                        break
                for i in range(len(getMatLibNamesFromXML())):
                    if item.material.matName == getMatLibNamesFromXML()[i]:
                        matSelMatCB.current(i)
                        break
                matSelMatCBChangedEvent(evt)
                break
                
# Material selection combobox changed event
def matSelMatCBChangedEvent(evt):
    matName = matSelMatCB.get()
    matObj = Material(matName)
    lblMatNum['text'] = "Material number:   "+matObj.matNum
    lblMatCat['text'] = "Material category:   "+matObj.matCat
    lblYoungsModulus['text'] = "Young's modulus:   "+matObj.youngsModulus
    lblPoissonsRatio['text'] = "Poisson's ratio:   "+matObj.poissonRatio
    lblAlpha['text'] = "Coefficient of thermal expansion:   "+matObj.alpha
    lblDensity['text'] = "Density:   "+matObj.density
    
# Add a node joint set
def addNodeJointSet():
    popup = createPopup("Add node joint",300,80)
    Label(popup, text="Enter name of node joint:").pack()
    nameEntry = Entry(popup)
    nameEntry.pack()
    nameEntry.insert(0,"nodeJoint"+str(len(nodeJointSets)+1))
    def clickOK():
        if nameEntry.get():
            if not nameEntry.get() in [nodeJointSets[i].assiName for i in range(len(nodeJointSets))]:
                nodeJointSets.append(NodeJointSet(nameEntry.get(),nodeJointGroupNameCB.get(),nodeJointNodeNameCB.get(),nodeJointCXEntry.get(),
                nodeJointCYEntry.get(),nodeJointCZEntry.get(),nodeJointCPhiXEntry.get(),nodeJointCPhiYEntry.get(),nodeJointCPhiZEntry.get()))
            else:
                messagebox.showerror("ca_wizard", "This assignment name is already in list!")
                popup.lift()
                return
        else:
            messagebox.showerror("ca_wizard", "Name can not be empty!")
            popup.lift()
            return
        updateNodeJointAssi()
        popup.destroy()
    popup.bind("<Return>", lambda x: clickOK())
    popup.bind("<Escape>", lambda x: popup.destroy())
    box = Frame(popup)
    box.pack()
    Button(box, text="Ok", command=clickOK).pack(side=LEFT,pady=5,padx=2)    
    Button(box, text="Cancel", command=popup.destroy).pack(pady=5,padx=2)
    nameEntry.focus_force()
    
# Update node joint assignments
def updateNodeJointAssi():
    nodeJointAssiListbox.delete(0,END)
    for item in nodeJointSets:
        nodeJointAssiListbox.insert(END, item.assiName)
    disableWidgets(nodeJointAssiGroup)

# Delete node joint assignment
def deleteNodeJointAssi():
    if not nodeJointAssiListbox.curselection()==():
        if messagebox.askquestion("ca_wizard", "Do you really want to delete "+nodeJointAssiListbox.get(nodeJointAssiListbox.curselection()[0])+"?", icon='warning')=="yes":
            for item in nodeJointSets:
                if item.assiName == nodeJointAssiListbox.get(nodeJointAssiListbox.curselection()[0]):
                    nodeJointSets.remove(item)
                    break
            updateNodeJointAssi()
    else:
        messagebox.showerror("ca_wizard", "Nothing selected.")

# Change node joint assignment
def changeNodeJointAssi():
    name = nodeJointAssiNameLbl.cget("text")
    for item in nodeJointSets:
        if item.assiName == name:
            item.__init__(name,nodeJointGroupNameCB.get(),nodeJointNodeNameCB.get(),nodeJointCXEntry.get(),nodeJointCYEntry.get(),nodeJointCZEntry.get(),
            nodeJointCPhiXEntry.get(),nodeJointCPhiYEntry.get(),nodeJointCPhiZEntry.get())
            disableWidgets(nodeJointAssiGroup)
            break
        
# Node joint assignments listbox selection changed event
def nodeJointAssiListboxSelectionChanged(evt):
    assiName = nodeJointAssiListbox.get(nodeJointAssiListbox.curselection())
    if not assiName == ():
        for item in nodeJointSets:
            if item.assiName == assiName:
                enableWidgets(nodeJointAssiGroup)
                nodeJointAssiNameLbl['text'] = assiName
                nodeJointGroupNameCB.set('')
                for i in range(len(getNames([4]))):
                    if item.jointGroupName == getNames([4])[i]:
                        nodeJointGroupNameCB.current(i)
                        break
                nodeJointNodeNameCB.set('')
                for i in range(len(getNames([3]))):
                    if item.nodeName == getNames([3])[i]:
                        nodeJointNodeNameCB.current(i)
                        break
                nodeJointCXEntry.delete(0, 'end')
                nodeJointCXEntry.insert(END, item.cX)
                nodeJointCYEntry.delete(0, 'end')
                nodeJointCYEntry.insert(END, item.cY)
                nodeJointCZEntry.delete(0, 'end')
                nodeJointCZEntry.insert(END, item.cZ)
                nodeJointCPhiXEntry.delete(0, 'end')
                nodeJointCPhiXEntry.insert(END, item.cPhiX)
                nodeJointCPhiYEntry.delete(0, 'end')
                nodeJointCPhiYEntry.insert(END, item.cPhiY)
                nodeJointCPhiZEntry.delete(0, 'end')
                nodeJointCPhiZEntry.insert(END, item.cPhiZ)
                break

# Add a restraint set
def addRestraintSet():
    popup = createPopup("Add restraint assignment",300,80)
    Label(popup, text="Enter name of restraint assignment:").pack()
    nameEntry = Entry(popup)
    nameEntry.pack()
    nameEntry.insert(0,"restraint"+str(len(restraintSets)+1))
    def clickOK():
        if nameEntry.get():
            if not nameEntry.get() in [restraintSets[i].assiName for i in range(len(restraintSets))]:
                restraintSets.append(RestraintSet(nameEntry.get(),restraintAssiNameCB.get(),restraintViaPyFun.get(),restraintDeltaXEntry.get(),
                restraintDeltaYEntry.get(),restraintDeltaZEntry.get(),restraintPhiXEntry.get(),restraintPhiYEntry.get(),restraintPhiZEntry.get(),
                restraintXTransEntry.get(),restraintYTransEntry.get(),restraintZTransEntry.get(),rotXVar.get(),rotYVar.get(),rotZVar.get(),
                restraintReacXEntry.get(),restraintReacYEntry.get(),restraintReacZEntry.get()))
            else:
                messagebox.showerror("ca_wizard", "This assignment name is already in list!")
                popup.lift()
                return
        else:
            messagebox.showerror("ca_wizard", "Name can not be empty!")
            popup.lift()
            return
        updateRestraintAssi()
        popup.destroy()
    popup.bind("<Return>", lambda x: clickOK())
    popup.bind("<Escape>", lambda x: popup.destroy())
    box = Frame(popup)
    box.pack()
    Button(box, text="Ok", command=clickOK).pack(side=LEFT,pady=5,padx=2)    
    Button(box, text="Cancel", command=popup.destroy).pack(pady=5,padx=2)
    nameEntry.focus_force()
    
# Update restraint assignments
def updateRestraintAssi():
    restraintAssiListbox.delete(0,END)
    for item in restraintSets:
        restraintAssiListbox.insert(END, item.assiName)
    disableWidgets(restraintAssiGroup)

# Delete restraint assignment
def deleteRestraintAssi():
    if not restraintAssiListbox.curselection()==():
        if messagebox.askquestion("ca_wizard", "Do you really want to delete "+restraintAssiListbox.get(restraintAssiListbox.curselection()[0])+"?", icon='warning')=="yes":
            for item in restraintSets:
                if item.assiName == restraintAssiListbox.get(restraintAssiListbox.curselection()[0]):
                    restraintSets.remove(item)
                    break
            updateRestraintAssi()
    else:
        messagebox.showerror("ca_wizard", "Nothing selected.")

# Change restraint assignment
def changeRestraintAssi():
    name = restraintAssiNameLbl.cget("text")
    for item in restraintSets:
        if item.assiName == name:
            item.__init__(name,restraintAssiNameCB.get(),restraintViaPyFun.get(),restraintDeltaXEntry.get(),restraintDeltaYEntry.get(),
            restraintDeltaZEntry.get(),restraintPhiXEntry.get(),restraintPhiYEntry.get(),restraintPhiZEntry.get(),restraintXTransEntry.get(),
            restraintYTransEntry.get(),restraintZTransEntry.get(),rotXVar.get(),rotYVar.get(),rotZVar.get(),restraintReacXEntry.get(),
            restraintReacYEntry.get(),restraintReacZEntry.get())
            disableWidgets(restraintAssiGroup)
            break
                
# Restraint assignments listbox selection changed event
def restraintAssiListboxSelectionChanged(evt):
    assiName = restraintAssiListbox.get(restraintAssiListbox.curselection())
    if not assiName == ():
        for item in restraintSets:
            if item.assiName == assiName:
                enableWidgets(restraintAssiGroup)
                restraintAssiNameLbl['text'] = assiName
                restraintViaPyFun.set(item.rotMatViaPython)
                restraintDeltaXEntry.delete(0, 'end')
                restraintDeltaXEntry.insert(END, item.deltaX)
                restraintDeltaYEntry.delete(0, 'end')
                restraintDeltaYEntry.insert(END, item.deltaY)
                restraintDeltaZEntry.delete(0, 'end')
                restraintDeltaZEntry.insert(END, item.deltaZ)
                restraintPhiXEntry.delete(0, 'end')
                restraintPhiXEntry.insert(END, item.deltaPhiX)
                restraintPhiYEntry.delete(0, 'end')
                restraintPhiYEntry.insert(END, item.deltaPhiY)
                restraintPhiZEntry.delete(0, 'end')
                restraintPhiZEntry.insert(END, item.deltaPhiZ)
                restraintXTransEntry.delete(0, 'end')
                restraintXTransEntry.insert(END, item.xTrans)
                restraintYTransEntry.delete(0, 'end')
                restraintYTransEntry.insert(END, item.yTrans)
                restraintZTransEntry.delete(0, 'end')
                restraintZTransEntry.insert(END, item.zTrans)
                rotXVar.set(item.rotX)
                rotYVar.set(item.rotY)
                rotZVar.set(item.rotZ)
                restraintReacXEntry.delete(0, 'end')
                restraintReacXEntry.insert(END, item.reacMX)
                restraintReacYEntry.delete(0, 'end')
                restraintReacYEntry.insert(END, item.reacMY)
                restraintReacZEntry.delete(0, 'end')
                restraintReacZEntry.insert(END, item.reacMZ)
                restraintViaPyFunChanged()
                cBList = getNames([1,2,3])
                for i in range(len(cBList)):
                    restraintAssiNameCB.set('')
                    if item.nodalGroupName == cBList[i]:
                        restraintAssiNameCB.current(i)
                        break
                restraintNameCBChangedEvent(None)
                break
                
# Restraint via Python function Checkbutton changed event
def restraintViaPyFunChanged(*args):
    if restraintViaPyFun.get() == 0:
        disableWidgets(restraintRotateViaPythonBox)
        disableWidgets(restraintsRotationBox)
        #restraintAssiNameCB.set("")
    else:
        enableWidgets(restraintRotateViaPythonBox)
        enableWidgets(restraintsRotationBox)
        
# Restraint name CB changed event
def restraintNameCBChangedEvent(evt):
    if restraintViaPyFun.get() == 0:
        for el in nodeJointSets:
            if el.nodeName == restraintAssiNameCB.get():
                enableWidgets(restraintsRotationBox)
                return
        disableWidgets(restraintsRotationBox)
    else:
        enableWidgets(restraintRotateViaPythonBox)
        enableWidgets(restraintsRotationBox)
                
# Add a load set
def addLoadSet():
    popup = createPopup("Add load assignment",300,80)
    Label(popup, text="Enter name of load assignment:").pack()
    nameEntry = Entry(popup)
    nameEntry.pack()
    nameEntry.insert(0,"load"+str(len(loadSets)+1))
    def clickOK():
        if nameEntry.get():
            if not nameEntry.get() in [loadSets[i].assiName for i in range(len(loadSets))]:
                loadSets.append(LoadSet(nameEntry.get(),loadAssiNameCB.get(),loadTypeCB.get(),loadFXEntry.get(),loadFYEntry.get(),loadFZEntry.get(),
                loadMXEntry.get(),loadMYEntry.get(),loadMZEntry.get(),loadPEntry.get(),loadGXEntry.get(),loadGYEntry.get(),loadGZEntry.get(),
                loadOmegaEntry.get(),loadRotCentXEntry.get(),loadRotCentYEntry.get(),loadRotCentZEntry.get(),loadRotAxisXEntry.get(),loadRotAxisYEntry.get(),
                loadRotAxisZEntry.get()))
            else:
                messagebox.showerror("ca_wizard", "This assignment name is already in list!")
                popup.lift()
                return
        else:
            messagebox.showerror("ca_wizard", "Name can not be empty!")
            popup.lift()
            return
        updateLoadAssi()
        popup.destroy()
    popup.bind("<Return>", lambda x: clickOK())
    popup.bind("<Escape>", lambda x: popup.destroy())
    box = Frame(popup)
    box.pack()
    Button(box, text="Ok", command=clickOK).pack(side=LEFT,pady=5,padx=2)    
    Button(box, text="Cancel", command=popup.destroy).pack(pady=5,padx=2)
    enableWidgets(loadAssiGroup)
    loadFXEntry.delete(0, 'end')
    loadFXEntry.insert(END,'0')
    loadFYEntry.delete(0, 'end')
    loadFYEntry.insert(END,'0')
    loadFZEntry.delete(0, 'end')
    loadFZEntry.insert(END,'0')
    loadMXEntry.delete(0, 'end')
    loadMXEntry.insert(END,'0')
    loadMYEntry.delete(0, 'end')
    loadMYEntry.insert(END,'0')
    loadMZEntry.delete(0, 'end')
    loadMZEntry.insert(END,'0')
    loadPEntry.delete(0, 'end')
    loadPEntry.insert(END,'0')
    loadGXEntry.delete(0, 'end')
    loadGXEntry.insert(END,'0')
    loadGYEntry.delete(0, 'end')
    loadGYEntry.insert(END,'0')
    loadGZEntry.delete(0, 'end')
    loadGZEntry.insert(END,'-9.81')
    loadOmegaEntry.delete(0, 'end')
    loadOmegaEntry.insert(END,'0')
    loadRotCentXEntry.delete(0, 'end')
    loadRotCentXEntry.insert(END,'0')
    loadRotCentYEntry.delete(0, 'end')
    loadRotCentYEntry.insert(END,'0')
    loadRotCentZEntry.delete(0, 'end')
    loadRotCentZEntry.insert(END,'0')
    loadRotAxisXEntry.delete(0, 'end')
    loadRotAxisXEntry.insert(END,'0')
    loadRotAxisYEntry.delete(0, 'end')
    loadRotAxisYEntry.insert(END,'0')
    loadRotAxisZEntry.delete(0, 'end')
    loadRotAxisZEntry.insert(END,'1')
    disableWidgets(loadAssiGroup)
    nameEntry.focus_force()
    
# Update load assignments
def updateLoadAssi():
    loadAssiListbox.delete(0,END)
    for item in loadSets:
        loadAssiListbox.insert(END, item.assiName)
    disableWidgets(loadAssiGroup)

# Delete load assignment
def deleteLoadAssi():
    if not loadAssiListbox.curselection()==():
        if messagebox.askquestion("ca_wizard", "Do you really want to delete "+loadAssiListbox.get(loadAssiListbox.curselection()[0])+\
        "?", icon='warning')=="yes":
            for item in loadSets:
                if item.assiName == loadAssiListbox.get(loadAssiListbox.curselection()[0]):
                    loadSets.remove(item)
                    break
            updateLoadAssi()
    else:
        messagebox.showerror("ca_wizard", "Nothing selected.")

# Change load assignment
def changeLoadAssi():
    name = loadAssiNameLbl.cget("text")
    for item in loadSets:
        if item.assiName == name:
            item.__init__(name,loadAssiNameCB.get(),loadTypeCB.get(),loadFXEntry.get(),loadFYEntry.get(),loadFZEntry.get(),loadMXEntry.get(),loadMYEntry.get(),
            loadMZEntry.get(),loadPEntry.get(),loadGXEntry.get(),loadGYEntry.get(),loadGZEntry.get(),loadOmegaEntry.get(),loadRotCentXEntry.get(),
            loadRotCentYEntry.get(),loadRotCentZEntry.get(),loadRotAxisXEntry.get(),loadRotAxisYEntry.get(),loadRotAxisZEntry.get())
            disableWidgets(loadAssiGroup)
            break
                
# Load assignments listbox selection changed event
def loadAssiListboxSelectionChanged(evt):
    assiName = loadAssiListbox.get(loadAssiListbox.curselection())
    if not assiName == ():
        for item in loadSets:
            if item.assiName == assiName:
                enableWidgets(loadAssiGroup)
                loadAssiNameLbl['text'] = assiName
                loadTypeCB.set(item.loadType)
                loadFXEntry.delete(0, 'end')
                loadFXEntry.insert(END, item.FX)
                loadFYEntry.delete(0, 'end')
                loadFYEntry.insert(END, item.FY)
                loadFZEntry.delete(0, 'end')
                loadFZEntry.insert(END, item.FZ)
                loadMXEntry.delete(0, 'end')
                loadMXEntry.insert(END, item.MX)
                loadMYEntry.delete(0, 'end')
                loadMYEntry.insert(END, item.MY)
                loadMZEntry.delete(0, 'end')
                loadMZEntry.insert(END, item.MZ)
                loadPEntry.delete(0, 'end')
                loadPEntry.insert(END, item.p)
                loadGXEntry.delete(0, 'end')
                loadGXEntry.insert(END, item.gX)
                loadGYEntry.delete(0, 'end')
                loadGYEntry.insert(END, item.gY)
                loadGZEntry.delete(0, 'end')
                loadGZEntry.insert(END, item.gZ)
                loadOmegaEntry.delete(0, 'end')
                loadOmegaEntry.insert(END, item.omega)
                loadRotCentXEntry.delete(0, 'end')
                loadRotCentXEntry.insert(END, item.centerX)
                loadRotCentYEntry.delete(0, 'end')
                loadRotCentYEntry.insert(END, item.centerY)
                loadRotCentZEntry.delete(0, 'end')
                loadRotCentZEntry.insert(END, item.centerZ)
                loadRotAxisXEntry.delete(0, 'end')
                loadRotAxisXEntry.insert(END, item.axisX)
                loadRotAxisYEntry.delete(0, 'end')
                loadRotAxisYEntry.insert(END, item.axisY)
                loadRotAxisZEntry.delete(0, 'end')
                loadRotAxisZEntry.insert(END, item.axisZ)
                loadTypeCBChangedEvent(evt)
                for i in range(len(loadAssiNameCB['values'])):
                    if item.nodalGroupName == loadAssiNameCB['values'][i]:
                        loadAssiNameCB.current(i)
                        break
                break
                
# Load Type selection combobox changed event
def loadTypeCBChangedEvent(evt):
    loadType = loadTypeCB.get()
    enableWidgets(loadAssiGroup)
    if loadType == "Gravity":
        namesList = getNames([0])
        disableWidgets(loadBoxFX)
        disableWidgets(loadBoxFY)
        disableWidgets(loadBoxFZ)
        disableWidgets(loadBoxMX)
        disableWidgets(loadBoxMY)
        disableWidgets(loadBoxMZ)
        disableWidgets(loadBoxP)
        disableWidgets(loadBoxOmega)
        disableWidgets(loadBoxRotCent)
        disableWidgets(loadBoxRotAxis)
    elif loadType == "Centrifugal force":
        namesList = getNames([0])
        disableWidgets(loadBoxFX)
        disableWidgets(loadBoxFY)
        disableWidgets(loadBoxFZ)
        disableWidgets(loadBoxMX)
        disableWidgets(loadBoxMY)
        disableWidgets(loadBoxMZ)
        disableWidgets(loadBoxP)
        disableWidgets(loadBoxGX)
        disableWidgets(loadBoxGY)
        disableWidgets(loadBoxGZ)
    elif loadType == "Force on face":
        namesList = getNames([1])
        disableWidgets(loadBoxMX)
        disableWidgets(loadBoxMY)
        disableWidgets(loadBoxMZ)
        disableWidgets(loadBoxP)
        disableWidgets(loadBoxGX)
        disableWidgets(loadBoxGY)
        disableWidgets(loadBoxGZ)
        disableWidgets(loadBoxOmega)
        disableWidgets(loadBoxRotCent)
        disableWidgets(loadBoxRotAxis)
    elif loadType == "Pressure":
        namesList = getNames([1])
        disableWidgets(loadBoxFX)
        disableWidgets(loadBoxFY)
        disableWidgets(loadBoxFZ)
        disableWidgets(loadBoxMX)
        disableWidgets(loadBoxMY)
        disableWidgets(loadBoxMZ)
        disableWidgets(loadBoxGX)
        disableWidgets(loadBoxGY)
        disableWidgets(loadBoxGZ)
        disableWidgets(loadBoxOmega)
        disableWidgets(loadBoxRotCent)
        disableWidgets(loadBoxRotAxis)
    elif loadType == "Force on edge":
        namesList = getNames([2])
        disableWidgets(loadBoxMX)
        disableWidgets(loadBoxMY)
        disableWidgets(loadBoxMZ)
        disableWidgets(loadBoxP)
        disableWidgets(loadBoxGX)
        disableWidgets(loadBoxGY)
        disableWidgets(loadBoxGZ)
        disableWidgets(loadBoxOmega)
        disableWidgets(loadBoxRotCent)
        disableWidgets(loadBoxRotAxis)
    else:
        namesList = getNames([0,1,2,3])
        disableWidgets(loadBoxP)
        disableWidgets(loadBoxGX)
        disableWidgets(loadBoxGY)
        disableWidgets(loadBoxGZ)
        disableWidgets(loadBoxOmega)
        disableWidgets(loadBoxRotCent)
        disableWidgets(loadBoxRotAxis)
        loadNodeGroupCBChangedEvent(None)
    loadAssiNameCB.set('')
    loadAssiNameCB['values'] = namesList
    if evt is None:
        disableWidgets(loadAssiGroup)
        
# Load node group selection combobox changed event
def loadNodeGroupCBChangedEvent(evt):
    if loadTypeCB.get() == "Force on node":
        if loadAssiNameCB.get() in [nodeJointSets[i].nodeName for i in range(len(nodeJointSets))]:
            enableWidgets(loadBoxMX)
            enableWidgets(loadBoxMY)
            enableWidgets(loadBoxMZ)
        else:
            disableWidgets(loadBoxMX)
            disableWidgets(loadBoxMY)
            disableWidgets(loadBoxMZ)
        
# Add a contact set
def addContactSet():
    popup = createPopup("Add contact assignment",300,80)
    Label(popup, text="Enter name of contact assignment:").pack()
    nameEntry = Entry(popup)
    nameEntry.pack()
    nameEntry.insert(0,"contAssignment"+str(len(contactSets)+1))
    def clickOK():
        if nameEntry.get():
            if not nameEntry.get() in [contactSets[i].assiName for i in range(len(contactSets))]:
                contactSets.append(ContactSet(nameEntry.get(),contactMasterCB.get(),contactSlaveCB.get(),contactFrictionCoeffEntry.get(),contactDContAlgoCB.get(),contactENEntry.get(),
                contactETEntry.get(),contactGlobalSetting))
            else:
                messagebox.showerror("ca_wizard", "This assignment name is already in list!")
                popup.lift()
                return
        else:
            messagebox.showerror("ca_wizard", "Name can not be empty!")
            popup.lift()
            return
        updateContactAssi()
        popup.destroy()
    popup.bind("<Return>", lambda x: clickOK())
    popup.bind("<Escape>", lambda x: popup.destroy())
    box = Frame(popup)
    box.pack()
    Button(box, text="Ok", command=clickOK).pack(side=LEFT,pady=5,padx=2)    
    Button(box, text="Cancel", command=popup.destroy).pack(pady=5,padx=2)
    enableWidgets(contactAssiGroup)
    nameEntry.focus_force()
    
# Update contact assignments
def updateContactAssi():
    contactAssiListbox.delete(0,END)
    for item in contactSets:
        contactAssiListbox.insert(END, item.assiName)
    disableWidgets(contactAssiGroup)

# Delete contact assignment
def deleteContactAssi():
    if not contactAssiListbox.curselection()==():
        if messagebox.askquestion("ca_wizard", "Do you really want to delete "+contactAssiListbox.get(contactAssiListbox.curselection()[0])+\
        "?", icon='warning')=="yes":
            for item in contactSets:
                if item.assiName == contactAssiListbox.get(contactAssiListbox.curselection()[0]):
                    contactSets.remove(item)
                    break
            updateContactAssi()
    else:
        messagebox.showerror("ca_wizard", "Nothing selected.")

# Change contact assignment
def changeContactAssi():
    name = contactAssiNameLbl.cget("text")
    for item in contactSets:
        if item.assiName == name:
            item.__init__(name,contactMasterCB.get(),contactSlaveCB.get(),contactFrictionCoeffEntry.get(),contactDContAlgoCB.get(),contactENEntry.get(),contactETEntry.get(),contactGlobalSetting)
            disableWidgets(contactAssiGroup)
            break
            
# Contact assignments listbox selection changed event
def contactAssiListboxSelectionChanged(evt):
    assiName = contactAssiListbox.get(contactAssiListbox.curselection())
    if not assiName == ():
        for item in contactSets:
            if item.assiName == assiName:
                enableWidgets(contactAssiGroup)
                contactAssiNameLbl['text'] = assiName
                contactMasterCB.set(item.masterName)
                contactSlaveCB.set(item.slaveName)
                contactFrictionCoeffEntry.delete(0, 'end')
                contactFrictionCoeffEntry.insert(0, item.fricCoeff)
                contactDContAlgoCB.set(item.contactAlgo)
                contactENEntry.delete(0, 'end')
                contactENEntry.insert(END, item.E_N)
                contactETEntry.delete(0, 'end')
                contactETEntry.insert(END, item.E_T)
                contactMasterCB.set('')
                for i in range(len(contactMasterCB['values'])):
                    if item.masterName == contactMasterCB['values'][i]:
                        contactMasterCB.current(i)
                        break
                contactSlaveCB.set('')
                for i in range(len(contactSlaveCB['values'])):
                    if item.slaveName == contactSlaveCB['values'][i]:
                        contactSlaveCB.current(i)
                        break
                contactEnableDisableFrames()
                break
                
# Enable/disable contact tab frames
def contactEnableDisableFrames():
    if contactGlobalSetting.formulationType == "continuous":
        enableWidgets(contactCAlgoBox)
        if contactGlobalSetting.frictionModel == "neglect friction":
            disableWidgets(contactCFricAlgoBox)
    else:
        disableWidgets(contactCAlgoBox)
    if contactAssiNameLbl.cget('state') == "enable":
        if contactGlobalSetting.frictionModel == "Coulomb":
            enableWidgets(contactFricCoeffBox)
        else:
            disableWidgets(contactFricCoeffBox)
        if contactGlobalSetting.formulationType == "discrete":
            enableWidgets(contactDContAlgoBox)
        else:
            disableWidgets(contactDContAlgoBox)
        if contactGlobalSetting.formulationType == "discrete" and (contactGlobalSetting.frictionModel == "Coulomb" or contactDContAlgoCB.get() == "PENALISATION"):
            enableWidgets(contactPenBox)
            if not contactDContAlgoCB.get() == "PENALISATION":
                disableWidgets(contactPenNBox)
            if not contactGlobalSetting.frictionModel == "Coulomb":
                disableWidgets(contactPenTBox)
        else:
            disableWidgets(contactPenBox)
                
# set contact global settings
def setContactGlobalSettings(globalSettingObj=None):
    global contactGlobalSetting
    if not globalSettingObj is None:
        contactGlobalSetting = None
        contactFormRadioButton.set(globalSettingObj.formulationType)
        contactFrictionModelCB.set(globalSettingObj.frictionModel)
        contactCContAlgoCB.set(globalSettingObj.contactAlgo)
        contactCFricAlgoCB.set(globalSettingObj.frictionAlgo)
    contactGlobalSetting = ContactGlobalSetting(contactFormRadioButton.get(),contactFrictionModelCB.get(),contactCContAlgoCB.get(),contactCFricAlgoCB.get())
    for el in contactSets:
        el.globalSettings = contactGlobalSetting
    contactEnableDisableFrames()
    
# contactGlobalSettings changed event
def contactGlobalSettingsChanged(var):
    if not contactGlobalSetting is None:
        setContactGlobalSettings()

# contactDContAlgoCBChanged changed event
def contactDContAlgoCBChanged(var):
    contactEnableDisableFrames()
    
# Add a thermal set
def addThermalSet():
    popup = createPopup("Add temp. assignment",300,80)
    Label(popup, text="Enter name of temperature assignment:").pack()
    nameEntry = Entry(popup)
    nameEntry.pack()
    nameEntry.insert(0,"tempAssignment"+str(len(thermalSets)+1))
    def clickOK():
        if nameEntry.get():
            if not nameEntry.get() in [thermalSets[i].assiName for i in range(len(thermalSets))]:
                thermalSets.append(ThermalSet(nameEntry.get(),thermalAssiNameCB.get(),thermModeRadioButton.get(),thermConstDeltaTEntry.get(),thermUniteEntry.get(),
                thermT0Entry.get(),''))#,thermFunText.get("1.0",'end-1c')))
            else:
                messagebox.showerror("ca_wizard", "This assignment name is already in list!")
                popup.lift()
                return
        else:
            messagebox.showerror("ca_wizard", "Name can not be empty!")
            popup.lift()
            return
        updateThermalAssi()
        popup.destroy()
    popup.bind("<Return>", lambda x: clickOK())
    popup.bind("<Escape>", lambda x: popup.destroy())
    box = Frame(popup)
    box.pack()
    Button(box, text="Ok", command=clickOK).pack(side=LEFT,pady=5,padx=2)    
    Button(box, text="Cancel", command=popup.destroy).pack(pady=5,padx=2)
    enableWidgets(loadAssiGroup)
    nameEntry.focus_force()
    
# Update thermal assignments
def updateThermalAssi():
    thermalAssiListbox.delete(0,END)
    for item in thermalSets:
        thermalAssiListbox.insert(END, item.assiName)
    disableWidgets(thermalAssiGroup)

# Delete thermal assignment
def deleteThermalAssi():
    if not thermalAssiListbox.curselection()==():
        if messagebox.askquestion("ca_wizard", "Do you really want to delete "+thermalAssiListbox.get(thermalAssiListbox.curselection()[0])+\
        "?", icon='warning')=="yes":
            for item in thermalSets:
                if item.assiName == thermalAssiListbox.get(thermalAssiListbox.curselection()[0]):
                    thermalSets.remove(item)
                    break
            updateThermalAssi()
    else:
        messagebox.showerror("ca_wizard", "Nothing selected.")

# Change thermal assignment
def changeThermalAssi():
    name = thermalAssiNameLbl.cget("text")
    for item in thermalSets:
        if item.assiName == name:
            item.__init__(name,thermalAssiNameCB.get(),thermModeRadioButton.get(),thermConstDeltaTEntry.get(),thermUniteEntry.get(),
                thermT0Entry.get(),'')#thermFunText.get("1.0",'end-1c'))
            disableWidgets(thermalAssiGroup)
            break
                
# Thermal assignments listbox selection changed event
def thermalAssiListboxSelectionChanged(evt):
    assiName = thermalAssiListbox.get(thermalAssiListbox.curselection())
    if not assiName == ():
        for item in thermalSets:
            if item.assiName == assiName:
                enableWidgets(thermalAssiGroup)
                thermalAssiNameLbl['text'] = assiName
                thermModeRadioButton.set(item.assiType)
                thermConstDeltaTEntry.delete(0, 'end')
                thermConstDeltaTEntry.insert(END, item.deltaT)
                thermUniteEntry.delete(0, 'end')
                thermUniteEntry.insert(END, item.unite)
                thermT0Entry.delete(0, 'end')
                thermT0Entry.insert(END, item.T0)
                #thermFunText.delete(0, 'end')
                #thermFunText.insert(END, item.funStr)
                thermalAssiNameCB.set('')
                for i in range(len(thermalAssiNameCB['values'])):
                    if item.nodalGroupName == thermalAssiNameCB['values'][i]:
                        thermalAssiNameCB.current(i)
                        break
                break
                
# get output set
def getOutputSet():
    return OutputSet(resultsNameCB.get(),resuStressTensor.get(),resuEquiStresses.get(),resuEpsilon.get(),resuReactions.get(),resuErrorEsti.get())

# get solver set
def getSolverSet():
    return SolverSet(analysisTypeCB.get(),analysisTimeStepsEntry.get(),analysisTimeRampDown.get(),analysisStrainModelCB.get(),analysisMethodCB.get(),analysisResiEntry.get(),analysisMaxIterEntry.get(),materialSets,
    nodeJointSets,restraintSets,loadSets,contactSets,thermalSets,getOutputSet())
                
# Assemble and save the comm-file
def assembleCOMM():
    try:
        msgs = getSolverSet().verify(names)
    except Exception as e:
        messagebox.showerror("ca_wizard", "Unable to proceed with the comm-file generation due to this error:\n" + str(e))
        return
    for msg in msgs:
        if messagebox.askquestion("ca_wizard", msg + "\nDo you want to continue with the comm-file generation?", icon='warning')=="no":
            return
    fileSave(getSolverSet().assembleCOMM(),".comm",[('code_aster comm-file', '.comm')],studyNameEntry.get(),"Save comm-file")

# Save File dialog
def fileSave(content,defExt,extList,defName,title):
    try:
        if not workingDirSet():
            f = filedialog.asksaveasfile(mode='w',defaultextension=defExt,filetypes=extList,initialfile=defName,title=title)
        else:
            f = filedialog.asksaveasfile(mode='w',defaultextension=defExt,filetypes=extList,initialdir=currWorkingDirEntry.get(),initialfile=defName,title=title)
        if f is None:
            return
        f.write(content)
    except Exception as e:
        messagebox.showerror("ca_wizard", "Error accessing file: " + str(e))
    f.close()

# Save setup dialog
def pickle_save():
    if not workingDirSet():
        f = filedialog.asksaveasfile(mode='wb',defaultextension=".cawm",filetypes=[('ca_wizard_mechanical', '.cawm')],initialfile=studyNameEntry.get(),title="Save current cawm setup")
    else:
        f = filedialog.asksaveasfile(mode='wb',defaultextension=".cawm",filetypes=[('ca_wizard_mechanical', '.cawm')],initialdir=currWorkingDirEntry.get(),initialfile=studyNameEntry.get(),
        title="Save current cawm setup")
    if f is None:
        return
    cawObj = cawmInst(getSolverSet(),names,currWorkingDirEntry.get(),studyNameEntry.get())
    pickle.dump(cawObj,f)
    f.close()
    
# Load setup dialog
def pickle_load():
    if messagebox.askquestion("ca_wizard", "This will overwrite the current setup. Do you want to continue?", icon='warning')=="no":
        return
    if not workingDirSet():
        f = filedialog.askopenfile(mode='rb',defaultextension=".cawm",filetypes=[('ca_wizard_mechanical', '.cawm')],title="Load cawm setup")
    else:
        f = filedialog.askopenfile(mode='rb',defaultextension=".cawm",filetypes=[('ca_wizard_mechanical', '.cawm')],initialdir=currWorkingDirEntry.get(),title="Load cawm setup")
    if f is None:
        return
    try:
        cawObj = pickle.load(f)
    except:
        messagebox.showerror("ca_wizard", "Unable to load file. The file is corrupted or the class module is of a different version.")
        return
    f.close()
    if not cawObj.cawmVersion == cawmVersion:
        if messagebox.askquestion("ca_wizard", "You are trying to load a save file of a different ca_wizard version. This can lead to a corrupted configuration and runtime erros." \
        " Do you want to continue?", icon='warning')=="no":
            return
    global names,materialSets,nodeJointSets,restraintSets,loadSets,contactSets,thermalSets,contactGlobalSetting
    names = cawObj.names
    updateNames()
    materialSets = cawObj.solverSet.materialSets
    nodeJointSets = cawObj.solverSet.nodeJointSets
    restraintSets = cawObj.solverSet.restraintSets
    loadSets = cawObj.solverSet.loadSets
    contactSets = cawObj.solverSet.contactSets
    if len(contactSets) > 0:
        setContactGlobalSettings(contactSets[0].globalSettings)
    thermalSets = cawObj.solverSet.thermalSets
    enableWidgets(analysisNonLinSolverOptionsBox)
    analysisTypeCB.set(cawObj.solverSet.analysisType)
    analysisTimeStepsEntry.delete(0, 'end')
    analysisTimeStepsEntry.insert(END, cawObj.solverSet.timeSteps)
    analysisTimeRampDown.set(cawObj.solverSet.timeRampDown)
    analysisMethodCB.set(cawObj.solverSet.method)
    analysisStrainModelCB.set(cawObj.solverSet.strainModel)
    analysisResiEntry.delete(0, 'end')
    analysisResiEntry.insert(END, cawObj.solverSet.resi)
    analysisMaxIterEntry.delete(0, 'end')
    analysisMaxIterEntry.insert(END, cawObj.solverSet.maxIter)
    analysisTypeCBChangedEvent(None)
    resultsNameCB.set(cawObj.solverSet.outputSet.nodalGroupName)
    resuStressTensor.set(cawObj.solverSet.outputSet.SIGM)
    resuEquiStresses.set(cawObj.solverSet.outputSet.SIEQ)
    resuEpsilon.set(cawObj.solverSet.outputSet.EPS)
    resuReactions.set(cawObj.solverSet.outputSet.REAC)
    resuErrorEsti.set(cawObj.solverSet.outputSet.ERME)
    currWorkingDirEntry.delete(0, 'end')
    currWorkingDirEntry.insert(END, cawObj.workingDir)
    studyNameEntry.delete(0, 'end')
    studyNameEntry.insert(END, cawObj.studyName)
    updateLoadAssi()
    updateMatAssi()
    updateNodeJointAssi()
    updateRestraintAssi()
    updateContactAssi()
    updateThermalAssi()

# Change working directory dialog
def changeWorkingDir():
    dir = filedialog.askdirectory(title="Select working directory")
    if dir is "":
        return
    currWorkingDirEntry.delete(0, 'end')
    currWorkingDirEntry.insert(END, dir)

def workingDirSet():
    if currWorkingDirEntry == "":
        return False
    else:
        return True

# delete all code_aster files belonging to set study name
def delCAFiles():
    if not workingDirSet():
        messagebox.showerror("ca_wizard", "Working directory is not set")
        return
    studyName = studyNameEntry.get()
    dir = currWorkingDirEntry.get()
    path = dir + "/" + studyName
    if messagebox.askquestion("ca_wizard", "Do you really want to delete all files belonging to "+studyName+" in the current" + \
    " working directory?")=="yes":
        flag = 0
        try:
            if os.path.isfile(path+".export"):
                os.chmod(path+".export", 0o777)
                os.remove(path+".export")
                flag = 1
            if os.path.isfile(path+".mess"):
                os.chmod(path+".mess", 0o777)
                os.remove(path+".mess")
                flag = 1
            if os.path.isfile(path+".mmed"):
                os.chmod(path+".mmed", 0o777)
                os.remove(path+".mmed")
                flag = 1
            if os.path.isfile(path+".resu"):
                os.chmod(path+".resu", 0o777)
                os.remove(path+".resu")
                flag = 1
            if os.path.isfile(path+".rmed"):
                os.chmod(path+".rmed", 0o777)
                os.remove(path+".rmed")
                flag = 1
            def del_rw(action, name, exc):
                os.chmod(name, 0o777)
                os.remove(name)
            if os.path.isdir(path+".base"):
                shutil.rmtree(path+".base",onerror=del_rw)
                flag = 1
        except Exception as e:
            messagebox.showerror("ca_wizard", "Error deleting files: " + str(e))
            return
        if not flag:
            messagebox.showinfo("ca_wizard", "Nothing deleted. Are the study name and working directory correct?")
            
# open mess-file
def openMessFile():
    if not workingDirSet():
        messagebox.showerror("ca_wizard", "Working directory is not set")
        return
    studyName = studyNameEntry.get()
    dir = currWorkingDirEntry.get()
    path = dir + "/" + studyName + ".mess"
    if os.path.isfile(path):
        webbrowser.open(path)
    else:
        messagebox.showerror("ca_wizard", "File not found. Are the study name and working directory correct?")
        
# open resu-file
def openResuFile():
    if not workingDirSet():
        messagebox.showerror("ca_wizard", "Working directory is not set")
        return
    studyName = studyNameEntry.get()
    dir = currWorkingDirEntry.get()
    path = dir + "/" + studyName + ".resu"
    if os.path.isfile(path):
        webbrowser.open(path)
    else:
        messagebox.showerror("ca_wizard", "File not found. Are the study name and working directory correct?")

# Export restraint reactions to CSV-file
def exportReacCSV():
    if not workingDirSet():
        messagebox.showerror("ca_wizard", "Working directory is not set")
        return
    popup = createPopup("Settings for CSV export",300,140)
    box = Frame(popup)
    box.pack(pady=5)
    Label(box, text="Line delimiter:").pack(side=LEFT)
    lineDelEntry = Entry(box)
    lineDelEntry.pack()
    lineDelEntry.insert(0,"\n")
    box = Frame(popup)
    box.pack(pady=5)
    Label(box, text="Column delimiter:").pack(side=LEFT)
    colDelEntry = Entry(box)
    colDelEntry.pack()
    colDelEntry.insert(0,",")
    box = Frame(popup)
    box.pack(pady=5)
    Label(box, text="Decimal mark:").pack(side=LEFT)
    decMarkEntry = Entry(box)
    decMarkEntry.pack()
    decMarkEntry.insert(0,".")
    def clickOK():
        lineDel = lineDelEntry.get()
        colDel = colDelEntry.get()
        decimal = decMarkEntry.get()
        popup.destroy()
        studyName = studyNameEntry.get()
        dir = currWorkingDirEntry.get()
        path = dir + "/" + studyName + ".resu"
        if not os.path.isfile(path):
            messagebox.showerror("ca_wizard", "File not found. Are the study name and working directory correct?")
            popup.destroy()
            return
        csvStr = studyName + colDel + time.strftime("%c") + lineDel + "name" + colDel + "timeInst" + colDel + "FX" + colDel + "FY" + colDel + "FZ" + colDel + "MX" + \
        colDel + "MY" + colDel + "MZ" + lineDel
        resuFile = open(path, "r")
        resuContent = resuFile.readlines()
        resuFile.close()
        reacLines = []
        flag = 0
        for line in resuContent:
            if flag:
                if not line == "\n":
                    reacLines.append(re.sub(' +',' ',line))
                else:
                    break
            if "CONCEPT Reac_Sum" in line:
                flag = 1
        if reacLines == []:
            messagebox.showerror("ca_wizard", "No reactions in resu-file found.")
            return
        reacLines.remove(reacLines[0])
        reacLines.remove(reacLines[0])
        for line in reacLines:
            cellVals = line.rsplit(" ",7)
            cellVals.remove(cellVals[0])
            lineName = line.split(" ",1)
            csvStr = csvStr + lineName[0] + colDel
            for cell in cellVals:
                csvStr = csvStr + cell.replace(" ","").replace(".",decimal).replace("\n","") + colDel
            csvStr = csvStr[:-len(colDel)] + lineDel
        csvStr = csvStr[:-len(lineDel)]
        fileSave(csvStr,".csv",[("CSV",".csv")],studyName+"_reactions","Export restraint reactions to CSV")
    popup.bind("<Return>", lambda x: clickOK())
    popup.bind("<Escape>", lambda x: popup.destroy())
    Button(popup,text="OK",command=clickOK).pack(pady=10)
    
# extract all error and alarm messages from mess-file and translate them to English
def showErrorsAlarms():
    if not workingDirSet():
        messagebox.showerror("ca_wizard", "Working directory is not set")
        return
    studyName = studyNameEntry.get()
    dir = currWorkingDirEntry.get()
    path = dir + "/" + studyName + ".mess"
    if not os.path.isfile(path):
        messagebox.showerror("ca_wizard", "File not found. Are the study name and working directory correct?")
        return
    messFile = codecs.open(path, encoding='utf-8')
    messContent = messFile.readlines()
    messFile.close()
    errAlList = []
    tempList = []
    flag = 0
    flagStr = "!-----------------------------"
    for line in messContent:
        if flag and not flagStr in line:
            tempList.append(re.sub(' +',' ',line.replace("!","")))
            continue
        else:
            if flag == 1:
                flag = 0
                tempStr = ""
                for el in tempList:
                    if el[0] == " ":
                        el = el[1:]
                    tempStr = tempStr + el
                errAlList.append(tempStr)
                tempList = []
                continue
        if flagStr in line:
            flag = 1
    errAlStr = ""
    for el in errAlList:
        errAlStr = errAlStr + el + "\n" + "------------------------------------------------------------------------" + "\n"
    popup = Toplevel()
    popup.title("Errors and alarms in " + studyName + ".mess")
    popup.geometry("600x800")
    popup.resizable(width=False, height=False)
    popup.lift()
    Button(popup,text="Open in Google Translator",command=lambda: webbrowser.open("https://translate.google.com/?hl=de#fr/en/" + \
    urllib.parse.quote(errAlStr).replace("/","%2F"),new=0,autoraise=True)).pack()
    box = Label(popup)
    box.pack()
    T = Text(box, height=50, width=80)
    S = Scrollbar(box)
    S.pack(side=RIGHT, fill=Y)
    T.pack(side=LEFT, fill=Y)
    S.config(command=T.yview)
    T.config(yscrollcommand=S.set)
    T.insert(END, errAlStr)
    
    
# Enable all child, grandchild and great-grandchild widgets of a parent
def enableWidgets(parent):
    for child in parent.winfo_children():
        try:
            if child.winfo_class() == "TCombobox":
                child.configure(state='readonly')
            else:
                child.configure(state='enable')
        except:
            pass
        for grandchild in child.winfo_children():
            try:
                if grandchild.winfo_class() == "TCombobox":
                    grandchild.configure(state='readonly')
                else:
                    grandchild.configure(state='enable')
            except:
                pass
            for greatgrandchild in grandchild.winfo_children():
                try:
                    if greatgrandchild.winfo_class() == "TCombobox":
                        greatgrandchild.configure(state='readonly')
                    else:
                        greatgrandchild.configure(state='enable')
                except:
                    pass
    
# Disable all child, grandchild and great-grandchild widgets of a parent
def disableWidgets(parent):
    for child in parent.winfo_children():
        try:
            child.configure(state='disable')
        except:
            pass
        for grandchild in child.winfo_children():
            try:
                grandchild.configure(state='disable')
            except:
                pass
            for greatgrandchild in grandchild.winfo_children():
                try:
                    greatgrandchild.configure(state='disable')
                except:
                    pass


### Build the GUI

# Main Window
mainForm = Tk()
mainForm.title("ca_wizard_mechanical v" + cawmVersion)
mainForm.geometry(mainFormSize)
mainForm.resizable(width=False, height=False)
# mainForm.style = Style()
# mainForm.style.theme_use("clam")

# Notebook
ntbook = Notebook(mainForm)
licenseTab = Frame(ntbook)
namesTab = Frame(ntbook)
analysisTab = Frame(ntbook)
materialsTab = Frame(ntbook)
nodeJointsTab = Frame(ntbook)
restraintsTab = Frame(ntbook)
loadsTab = Frame(ntbook)
contactsTab = Frame(ntbook)
thermalTab = Frame(ntbook)
resultsTab = Frame(ntbook)
filesTab = Frame(ntbook)
ntbook.add(licenseTab, text='License')
ntbook.add(namesTab, text='Names')
ntbook.add(analysisTab, text='Analysis')
ntbook.add(materialsTab, text='Materials')
ntbook.add(nodeJointsTab, text='Node joints')
ntbook.add(restraintsTab, text='Restraints')
ntbook.add(loadsTab, text='Loads')
ntbook.add(contactsTab, text='Contacts')
ntbook.add(thermalTab, text='Thermal')
ntbook.add(resultsTab, text='Results')
ntbook.add(filesTab, text='Files')
ntbook.pack(fill=BOTH, expand=1)

# License Tab
Label(licenseTab,text= \
"This work is licensed under the terms and conditions of the\nGNU General Public License version 3\n\n" \
"Copyright (C) 2017 Dominik Lechleitner\n" + \
"Contact: kaktus018(at)gmail.com\n" + \
"GitHub repository: https://github.com/kaktus018/ca_wizard_mechanical", \
justify=CENTER,font=("Helvetica",10,"bold")).pack(pady=50)
Label(licenseTab,text= \
"ca_wizard_mechanical is free software: you can redistribute it and/or modify " + \
"it under the terms of the GNU General Public License as published by " + \
"the Free Software Foundation, either version 3 of the License, or " + \
"(at your option) any later version.\n\n" + \
"ca_wizard_mechanical is distributed in the hope that it will be useful, " + \
"but WITHOUT ANY WARRANTY; without even the implied warranty of " + \
"MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the " + \
"GNU General Public License for more details. " + \
"You should have received a copy of the GNU General Public License " + \
"along with ca_wizard_mechanical.  If not, see <http://www.gnu.org/licenses/>.", \
wraplength=500, justify=CENTER).pack()

# Names Tab
group = LabelFrame(namesTab, text="List of node groups")
group.pack(fill=Y, padx=10, pady=10, ipadx=5, ipady=5)
box = Frame(group, height=500, width=180)
box.pack_propagate(0)
box.pack(side=LEFT)
namesListbox = Listbox(box)
namesListbox.pack(side=LEFT,padx=5,fill=BOTH,expand=TRUE)
box = Frame(group)
box.pack(pady=20)
Button(box, text="Add name", command=addName).pack(pady=5)
Button(box, text="Delete name", command=deleteName).pack()

# Analysis Tab
box = Frame(analysisTab)
box.pack(pady=20)
Label(box,text="Select type of analysis: ").pack(side=LEFT)
analysisTypeCB = Combobox(box, values=("linear static", "non-linear static"), state='readonly')
analysisTypeCB.current(0)
analysisTypeCB.pack(pady=5, padx=10)
analysisTypeCB.bind("<<ComboboxSelected>>", analysisTypeCBChangedEvent)
analysisSolverGroup = LabelFrame(analysisTab, text="Solver configuration")
analysisSolverGroup.pack(padx=10, pady=10, ipadx=5, ipady=5)
box = Frame(analysisSolverGroup)
box.pack()
Label(box, text="  Time steps: ").pack(side=LEFT)
box = Frame(box)
box.pack(padx=10,pady=5)
analysisTimeStepsEntry = Entry(box)
analysisTimeStepsEntry.pack(pady=5)
analysisTimeStepsEntry.insert(END, '0')
analysisTimeRampDown = IntVar()
analysisTimeRampDown.set(0)
Checkbutton(box, text = "ramp down as well", variable = analysisTimeRampDown, onvalue = 1, offvalue = 0).pack()
box = Frame(analysisSolverGroup)
box.pack()
Label(box, text="            Method: ").pack(side=LEFT)
analysisMethodCB = Combobox(box, values=("MULT_FRONT", "MUMPS"), state='readonly')
analysisMethodCB.current(0)
analysisMethodCB.pack(pady=5, padx=10)
analysisNonLinSolverOptionsBox = Frame(analysisSolverGroup)
analysisNonLinSolverOptionsBox.pack()
box = Frame(analysisNonLinSolverOptionsBox)
box.pack()
Label(box, text="    Strain model: ").pack(side=LEFT)
analysisStrainModelCB = Combobox(box, values=("linear", "Green-Lagrange"), state='readonly')
analysisStrainModelCB.current(0)
analysisStrainModelCB.pack(pady=5, padx=10)
box = Frame(analysisNonLinSolverOptionsBox)
box.pack()
Label(box, text="  Max. relative global residual: ").pack(side=LEFT)
analysisResiEntry = Entry(box, width=10)
analysisResiEntry.pack(pady=5)
analysisResiEntry.insert(END, '1E-6')
box = Frame(analysisNonLinSolverOptionsBox)
box.pack()
Label(box, text="  Max. iterations: ").pack(side=LEFT)
analysisMaxIterEntry = Entry(box, width=10)
analysisMaxIterEntry.pack(pady=5)
analysisMaxIterEntry.insert(END, '50')
disableWidgets(analysisNonLinSolverOptionsBox)

# Materials Tab
group = LabelFrame(materialsTab, text="List of material assignments")
group.pack(side=LEFT, fill=Y, padx=10, pady=10, ipadx=5, ipady=5)
box = Frame(group, height=500, width=180)
box.pack_propagate(0)
box.pack(side=LEFT)
matAssiListbox = Listbox(box)
matAssiListbox.pack(side=LEFT,padx=5,fill=BOTH,expand=TRUE)
matAssiListbox.bind('<<ListboxSelect>>', matAssiListboxSelectionChanged)
box = Frame(group)
box.pack(pady=20)
Button(box, text="Add", command=addMaterialSet).pack(pady=5)
Button(box, text="Delete", command=deleteMatAssi).pack()
boxR = Frame(materialsTab)
boxR.pack(side=LEFT,fill=Y)
matAssiGroup = LabelFrame(boxR, text="Create/Modify material assignment")
matAssiGroup.pack(padx=10, pady=10, ipadx=5, ipady=5)
box = Frame(matAssiGroup)
box.pack(fill=BOTH)
Label(box, text="  Name of assignment: ").pack(side=LEFT)
matAssiNameLbl = Label(box, text="")
matAssiNameLbl.pack(side=RIGHT)
box = Frame(matAssiGroup)
box.pack(fill=BOTH)
Label(box, text="  Assign to: ").pack(side=LEFT)
matAssiMatCB = Combobox(box, values=getNames([0]), state='readonly')
matAssiMatCB.current(0)
matAssiMatCB.pack(side=RIGHT, pady=5, padx=10)
box = Frame(matAssiGroup)
box.pack(fill=BOTH)
Label(box, text="  Select material: ").pack(side=LEFT)
matSelMatCB = Combobox(box, values=getMatLibNamesFromXML(), state='readonly')
matSelMatCB.current(0)
matSelMatCB.pack(side=RIGHT, pady=5, padx=10)
matSelMatCB.bind("<<ComboboxSelected>>", matSelMatCBChangedEvent)
box = Frame(matAssiGroup)
box.pack(fill=BOTH, padx=5, pady=5)
Button(box, text="Done", command=changeMatAssi).pack(side=RIGHT,padx=10)
Button(box, text="Refresh material list", command=refreshMatCB).pack(side=RIGHT)
group = LabelFrame(boxR, text="Material info")
group.pack(fill=X, padx=10, pady=10)
lblMatNum = Label(group, text="Material number: -")
lblMatNum.pack(fill=BOTH, padx=5, pady=5)
lblMatCat = Label(group, text="Material category: -")
lblMatCat.pack(fill=BOTH, padx=5, pady=5)
lblYoungsModulus = Label(group, text="Young's modulus: -")
lblYoungsModulus.pack(fill=BOTH, padx=5, pady=5)
lblPoissonsRatio = Label(group, text="Poisson's ratio: -")
lblPoissonsRatio.pack(fill=BOTH, padx=5, pady=5)
lblAlpha = Label(group, text="Coefficient of thermal expansion: -")
lblAlpha.pack(fill=BOTH, padx=5, pady=5)
lblDensity = Label(group, text="Density: -")
lblDensity.pack(fill=BOTH, padx=5, pady=5)
disableWidgets(matAssiGroup)

# Node joints Tab
group = LabelFrame(nodeJointsTab, text="List of node joints")
group.pack(side=LEFT, fill=Y, padx=10, pady=10, ipadx=5, ipady=5)
box = Frame(group, height=500, width=180)
box.pack_propagate(0)
box.pack(side=LEFT)
nodeJointAssiListbox = Listbox(box)
nodeJointAssiListbox.pack(side=LEFT,padx=5,fill=BOTH,expand=TRUE)
nodeJointAssiListbox.bind('<<ListboxSelect>>', nodeJointAssiListboxSelectionChanged)
box = Frame(group)
box.pack(pady=20)
Button(box, text="Add", command=addNodeJointSet).pack(pady=5)
Button(box, text="Delete", command=deleteNodeJointAssi).pack()
box = Frame(nodeJointsTab)
box.pack(side=LEFT,fill=Y)
nodeJointAssiGroup = LabelFrame(box, text="Create/Modify rigid node joint")
nodeJointAssiGroup.pack(padx=10, pady=10, ipadx=5, ipady=5)
box = Frame(nodeJointAssiGroup)
box.pack(fill=BOTH)
Label(box, text="  Name of node joint: ").pack(side=LEFT)
nodeJointAssiNameLbl = Label(box, text="")
nodeJointAssiNameLbl.pack(side=RIGHT)
box = Frame(nodeJointAssiGroup)
box.pack(fill=BOTH)
Label(box, text="  Node joint group: ").pack(side=LEFT)
nodeJointGroupNameCB = Combobox(box, values=getNames([4]), state='readonly')
nodeJointGroupNameCB.pack(side=RIGHT, pady=5, padx=10)
box = Frame(nodeJointAssiGroup)
box.pack(fill=BOTH)
Label(box, text="  Node: ").pack(side=LEFT)
nodeJointNodeNameCB = Combobox(box, values=getNames([3]), state='readonly')
nodeJointNodeNameCB.pack(side=RIGHT, pady=5, padx=10)
Label(nodeJointAssiGroup, text="Stiffness:").pack()
box = Frame(nodeJointAssiGroup)
box.pack(fill=BOTH, padx=5, pady=5)
Label(box, text="    cX: ").pack(side=LEFT)
nodeJointCXEntry = Entry(box,width=20)
nodeJointCXEntry.pack()
nodeJointCXEntry.insert(END, '0.1')
box = Frame(nodeJointAssiGroup)
box.pack(fill=BOTH, padx=5, pady=5)
Label(box, text="   cY: ").pack(side=LEFT)
nodeJointCYEntry = Entry(box,width=20)
nodeJointCYEntry.pack()
nodeJointCYEntry.insert(END, '0.1')
box = Frame(nodeJointAssiGroup)
box.pack(fill=BOTH, padx=5, pady=5)
Label(box, text="   cZ: ").pack(side=LEFT)
nodeJointCZEntry = Entry(box,width=20)
nodeJointCZEntry.pack()
nodeJointCZEntry.insert(END, '0.1')
box = Frame(nodeJointAssiGroup)
box.pack(fill=BOTH, padx=5, pady=5)
Label(box, text=" c\u03D5X: ").pack(side=LEFT)
nodeJointCPhiXEntry = Entry(box,width=20)
nodeJointCPhiXEntry.pack()
nodeJointCPhiXEntry.insert(END, '0.1')
box = Frame(nodeJointAssiGroup)
box.pack(fill=BOTH, padx=5, pady=5)
Label(box, text=" c\u03D5Y: ").pack(side=LEFT)
nodeJointCPhiYEntry = Entry(box,width=20)
nodeJointCPhiYEntry.pack()
nodeJointCPhiYEntry.insert(END, '0.1')
box = Frame(nodeJointAssiGroup)
box.pack(fill=BOTH, padx=5, pady=5)
Label(box, text=" c\u03D5Z: ").pack(side=LEFT)
nodeJointCPhiZEntry = Entry(box,width=20)
nodeJointCPhiZEntry.pack()
nodeJointCPhiZEntry.insert(END, '0.1')
box = Frame(nodeJointAssiGroup)
box.pack(fill=BOTH, padx=5, pady=5)
Button(box, text="Done", command=changeNodeJointAssi).pack(side=RIGHT,padx=10)
disableWidgets(nodeJointAssiGroup)

# Restraints Tab
group = LabelFrame(restraintsTab, text="List of restraint assignments")
group.pack(side=LEFT, fill=Y, padx=10, pady=10, ipadx=5, ipady=5)
box = Frame(group, height=500, width=180)
box.pack_propagate(0)
box.pack(side=LEFT)
restraintAssiListbox = Listbox(box)
restraintAssiListbox.pack(side=LEFT,padx=5,fill=BOTH,expand=TRUE)
restraintAssiListbox.bind('<<ListboxSelect>>', restraintAssiListboxSelectionChanged)
box = Frame(group)
box.pack(pady=20)
Button(box, text="Add", command=addRestraintSet).pack(pady=5)
Button(box, text="Delete", command=deleteRestraintAssi).pack()
box = Frame(restraintsTab)
box.pack(side=LEFT,fill=Y)
restraintAssiGroup = LabelFrame(box, text="Create/Modify rigid restraint assignment")
restraintAssiGroup.pack(padx=10, pady=10, ipadx=5, ipady=5)
box = Frame(restraintAssiGroup)
box.pack(fill=BOTH)
Label(box, text="  Name of assignment: ").pack(side=LEFT)
restraintAssiNameLbl = Label(box, text="")
restraintAssiNameLbl.pack(side=RIGHT)
box = Frame(restraintAssiGroup)
box.pack(fill=BOTH)
restraintViaPyFun = IntVar()
restraintViaPyFun.set(0)
restraintViaPyFun.trace("w",restraintViaPyFunChanged)
Checkbutton(box, text = "Apply rotation matrix via Python function", variable = restraintViaPyFun, onvalue = 1, offvalue = 0).pack()
box = Frame(restraintAssiGroup)
box.pack(fill=BOTH)
Label(box, text="  Assign to: ").pack(side=LEFT)
restraintAssiNameCB = Combobox(box, values=getNames([1,2,3]), state='readonly')
restraintAssiNameCB.pack(side=RIGHT, pady=5, padx=10)
restraintAssiNameCB.bind('<<ComboboxSelected>>', restraintNameCBChangedEvent)
Label(restraintAssiGroup, text="  Leave respective field empty for no restraint").pack(pady=5)
box = Frame(restraintAssiGroup)
box.pack(fill=BOTH, pady=5)
Label(box, text="  \u0394X:   ").pack(side=LEFT)
restraintDeltaXEntry = Entry(box)
restraintDeltaXEntry.pack()
box = Frame(restraintAssiGroup)
box.pack(fill=BOTH, pady=5)
Label(box, text="  \u0394Y:   ").pack(side=LEFT)
restraintDeltaYEntry = Entry(box)
restraintDeltaYEntry.pack()
box = Frame(restraintAssiGroup)
box.pack(fill=BOTH, pady=5)
Label(box, text="  \u0394Z:   ").pack(side=LEFT)
restraintDeltaZEntry = Entry(box)
restraintDeltaZEntry.pack()
restraintsRotationBox = Frame(restraintAssiGroup)
restraintsRotationBox.pack(fill=BOTH, pady=5)
box = Frame(restraintsRotationBox)
box.pack(fill=BOTH, pady=5)
Label(box, text="  \u0394\u03D5X: ").pack(side=LEFT)
restraintPhiXEntry = Entry(box)
restraintPhiXEntry.pack()
restraintPhiXEntry.insert(END, '0')
box = Frame(restraintsRotationBox)
box.pack(fill=BOTH, pady=5)
Label(box, text="  \u0394\u03D5Y: ").pack(side=LEFT)
restraintPhiYEntry = Entry(box)
restraintPhiYEntry.pack()
restraintPhiYEntry.insert(END, '0')
box = Frame(restraintsRotationBox)
box.pack(fill=BOTH, pady=5)
Label(box, text="  \u0394\u03D5Z: ").pack(side=LEFT)
restraintPhiZEntry = Entry(box)
restraintPhiZEntry.pack()
restraintPhiZEntry.insert(END, '0')
restraintRotateViaPythonBox = Frame(restraintAssiGroup)
restraintRotateViaPythonBox.pack(fill=BOTH, pady=5)
Label(restraintRotateViaPythonBox, text="  Rotate around point:").pack(pady=5)
box = Frame(restraintRotateViaPythonBox)
box.pack(fill=BOTH, pady=5)
Label(box, text="     X:").pack(side=LEFT)
restraintXTransEntry = Entry(box,width=8)
restraintXTransEntry.pack(side=LEFT)
restraintXTransEntry.insert(END, '0')
Label(box, text="  Y:").pack(side=LEFT)
restraintYTransEntry = Entry(box,width=8)
restraintYTransEntry.pack(side=LEFT)
restraintYTransEntry.insert(END, '0')
Label(box, text="  Z:").pack(side=LEFT)
restraintZTransEntry = Entry(box,width=8)
restraintZTransEntry.pack(side=LEFT)
restraintZTransEntry.insert(END, '0')
Label(restraintRotateViaPythonBox, text=" Apply rotation to:").pack(pady=5)
box = Frame(restraintRotateViaPythonBox)
box.pack(pady=5)
rotXVar = IntVar()
rotXVar.set(0)
Checkbutton(box, text = "X", variable = rotXVar, onvalue = 1, offvalue = 0).pack(side=LEFT)
rotYVar = IntVar()
rotYVar.set(0)
Checkbutton(box, text = "Y", variable = rotYVar, onvalue = 1, offvalue = 0).pack(side=LEFT)
rotZVar = IntVar()
rotZVar.set(0)
Checkbutton(box, text = "Z", variable = rotZVar, onvalue = 1, offvalue = 0).pack()
Label(restraintAssiGroup, text=" Compute torsional reactions around point:").pack(pady=5)
box = Frame(restraintAssiGroup)
box.pack(pady=5)
Label(box, text="X:").pack(side=LEFT)
restraintReacXEntry = Entry(box,width=8)
restraintReacXEntry.pack(side=LEFT)
restraintReacXEntry.insert(END, '0')
Label(box, text="  Y:").pack(side=LEFT)
restraintReacYEntry = Entry(box,width=8)
restraintReacYEntry.pack(side=LEFT)
restraintReacYEntry.insert(END, '0')
Label(box, text="  Z:").pack(side=LEFT)
restraintReacZEntry = Entry(box,width=8)
restraintReacZEntry.pack(side=LEFT)
restraintReacZEntry.insert(END, '0')
box = Frame(restraintAssiGroup)
box.pack(fill=BOTH, padx=5, pady=5)
Button(box, text="Done", command=changeRestraintAssi).pack(side=RIGHT,padx=10)
disableWidgets(restraintAssiGroup)

# Loads Tab
group = LabelFrame(loadsTab, text="List of load assignments")
group.pack(side=LEFT, fill=Y, padx=10, pady=10, ipadx=5, ipady=5)
box = Frame(group, height=500, width=180)
box.pack_propagate(0)
box.pack(side=LEFT)
loadAssiListbox = Listbox(box)
loadAssiListbox.pack(side=LEFT,padx=5,fill=BOTH,expand=TRUE)
loadAssiListbox.bind('<<ListboxSelect>>', loadAssiListboxSelectionChanged)
box = Frame(group)
box.pack(pady=20)
Button(box, text="Add", command=addLoadSet).pack(pady=5)
Button(box, text="Delete", command=deleteLoadAssi).pack()
box = Frame(loadsTab)
box.pack(side=LEFT,fill=Y)
loadAssiGroup = LabelFrame(box, text="Create/Modify load assignment")
loadAssiGroup.pack(padx=10, pady=10, ipadx=5, ipady=5)
box = Frame(loadAssiGroup)
box.pack(fill=BOTH)
Label(box, text="  Name of assignment: ").pack(side=LEFT)
loadAssiNameLbl = Label(box, text="")
loadAssiNameLbl.pack(side=RIGHT)
box = Frame(loadAssiGroup)
box.pack(fill=BOTH)
Label(box, text="  Type: ").pack(side=LEFT)
loadTypeCB = Combobox(box, values=["Gravity","Centrifugal force","Force on face","Force on edge","Force on node","Pressure"], state='readonly')
loadTypeCB.current(0)
loadTypeCB.pack(side=RIGHT, pady=5, padx=10)
loadTypeCB.bind("<<ComboboxSelected>>", loadTypeCBChangedEvent)
box = Frame(loadAssiGroup)
box.pack(fill=BOTH)
Label(box, text="  Assign to: ").pack(side=LEFT)
loadAssiNameCB = Combobox(box, values=getNames([0]), state='readonly')
loadAssiNameCB.pack(side=RIGHT, pady=5, padx=10)
loadAssiNameCB.current(0)
loadAssiNameCB.bind("<<ComboboxSelected>>", loadNodeGroupCBChangedEvent)
box = Frame(loadAssiGroup)
box.pack(fill=BOTH)
loadBoxFX = Frame(box)
loadBoxFX.pack(side=LEFT, pady=5)
Label(loadBoxFX, text="  FX: ").pack(side=LEFT)
loadFXEntry = Entry(loadBoxFX,width=15)
loadFXEntry.pack()
loadBoxMX = Frame(box)
loadBoxMX.pack(pady=5)
Label(loadBoxMX, text="  MX: ").pack(side=LEFT)
loadMXEntry = Entry(loadBoxMX,width=15)
loadMXEntry.pack()
box = Frame(loadAssiGroup)
box.pack(fill=BOTH)
loadBoxFY = Frame(box)
loadBoxFY.pack(side=LEFT, pady=5)
Label(loadBoxFY, text="  FY: ").pack(side=LEFT)
loadFYEntry = Entry(loadBoxFY,width=15)
loadFYEntry.pack()
loadBoxMY = Frame(box)
loadBoxMY.pack(pady=5)
Label(loadBoxMY, text="  MY: ").pack(side=LEFT)
loadMYEntry = Entry(loadBoxMY,width=15)
loadMYEntry.pack()
box = Frame(loadAssiGroup)
box.pack(fill=BOTH)
loadBoxFZ = Frame(box)
loadBoxFZ.pack(side=LEFT, pady=5)
Label(loadBoxFZ, text="  FZ: ").pack(side=LEFT)
loadFZEntry = Entry(loadBoxFZ,width=15)
loadFZEntry.pack()
loadBoxMZ = Frame(box)
loadBoxMZ.pack(pady=5)
Label(loadBoxMZ, text="  MZ: ").pack(side=LEFT)
loadMZEntry = Entry(loadBoxMZ,width=15)
loadMZEntry.pack()
loadBoxP = Frame(loadAssiGroup)
loadBoxP.pack(fill=BOTH, pady=5)
Label(loadBoxP, text="  p:   ").pack(side=LEFT)
loadPEntry = Entry(loadBoxP)
loadPEntry.pack()
loadBoxGX = Frame(loadAssiGroup)
loadBoxGX.pack(fill=BOTH, pady=5)
Label(loadBoxGX, text="  gX: ").pack(side=LEFT)
loadGXEntry = Entry(loadBoxGX)
loadGXEntry.pack()
loadBoxGY = Frame(loadAssiGroup)
loadBoxGY.pack(fill=BOTH, pady=5)
Label(loadBoxGY, text="  gY: ").pack(side=LEFT)
loadGYEntry = Entry(loadBoxGY)
loadGYEntry.pack()
loadBoxGZ = Frame(loadAssiGroup)
loadBoxGZ.pack(fill=BOTH, pady=5)
Label(loadBoxGZ, text="  gZ: ").pack(side=LEFT)
loadGZEntry = Entry(loadBoxGZ)
loadGZEntry.pack()
loadBoxOmega = Frame(loadAssiGroup)
loadBoxOmega.pack(fill=BOTH, pady=5)
Label(loadBoxOmega, text="  \u03C9:  ").pack(side=LEFT)
loadOmegaEntry = Entry(loadBoxOmega)
loadOmegaEntry.pack()
loadBoxRotCent = Frame(loadAssiGroup)
loadBoxRotCent.pack()
Label(loadBoxRotCent, text="  Center of rotation: ").pack()
box = Frame(loadBoxRotCent)
box.pack()
Label(box, text="X: ").pack(side=LEFT)
loadRotCentXEntry = Entry(box, width=7)
loadRotCentXEntry.pack(side=LEFT)
Label(box, text=" Y: ").pack(side=LEFT)
loadRotCentYEntry = Entry(box, width=7)
loadRotCentYEntry.pack(side=LEFT)
Label(box, text=" Z: ").pack(side=LEFT)
loadRotCentZEntry = Entry(box, width=7)
loadRotCentZEntry.pack()
loadBoxRotAxis = Frame(loadAssiGroup)
loadBoxRotAxis.pack()
Label(loadBoxRotAxis, text="  Direction vector of axis: ").pack()
box = Frame(loadBoxRotAxis)
box.pack()
Label(box, text="X: ").pack(side=LEFT)
loadRotAxisXEntry = Entry(box, width=7)
loadRotAxisXEntry.pack(side=LEFT)
Label(box, text=" Y: ").pack(side=LEFT)
loadRotAxisYEntry = Entry(box, width=7)
loadRotAxisYEntry.pack(side=LEFT)
Label(box, text=" Z: ").pack(side=LEFT)
loadRotAxisZEntry = Entry(box, width=7)
loadRotAxisZEntry.pack(side=LEFT)
box = Frame(loadAssiGroup)
box.pack(fill=BOTH, padx=5, pady=5)
Button(box, text="Done", command=changeLoadAssi).pack(side=RIGHT,padx=10)
disableWidgets(loadAssiGroup)

# Contacts Tab
group = LabelFrame(contactsTab, text="List of contact assignments")
group.pack(side=LEFT, fill=Y, padx=10, pady=10, ipadx=5, ipady=5)
box = Frame(group, height=500, width=180)
box.pack_propagate(0)
box.pack(side=LEFT)
contactAssiListbox = Listbox(box)
contactAssiListbox.pack(side=LEFT,padx=5,fill=BOTH,expand=TRUE)
contactAssiListbox.bind('<<ListboxSelect>>', contactAssiListboxSelectionChanged)
box = Frame(group)
box.pack(pady=20)
Button(box, text="Add", command=addContactSet).pack(pady=5)
Button(box, text="Delete", command=deleteContactAssi).pack()
rightBox = Frame(contactsTab)
rightBox.pack(side=LEFT,fill=Y)
contactGlobalGroup = LabelFrame(rightBox, text="Global settings")
contactGlobalGroup.pack(padx=10, pady=10, ipadx=5, ipady=5)
box = Frame(contactGlobalGroup)
box.pack(fill=BOTH,padx=5,pady=5)
Label(box, text="Note: Changing the global settings will affect all defined contacts in the assignment list.", wraplength=300, justify=CENTER).pack()
box = Frame(contactGlobalGroup)
box.pack(fill=BOTH,pady=10)
Label(box, text="  Formulation: ").pack(side=LEFT)
formulations = [("Continuous", "continuous"),("Discrete", "discrete")]
contactFormRadioButton = StringVar()
contactFormRadioButton.set("discrete")
contactFormRadioButton.trace("w",lambda name,index,mode,contactFormRadioButton=contactFormRadioButton: contactGlobalSettingsChanged(contactFormRadioButton))
Radiobutton(box, text=formulations[1][0],variable=contactFormRadioButton, value=formulations[1][1]).pack(padx=30,anchor=W)
Radiobutton(box, text=formulations[0][0],variable=contactFormRadioButton, value=formulations[0][1]).pack(padx=30,anchor=W)
box = Frame(contactGlobalGroup)
box.pack(fill=BOTH,pady=3)
Label(box, text="  Friction model: ").pack(side=LEFT)
contactFrictionModelCB = Combobox(box, values=["neglect friction","Coulomb"], state='readonly')
contactFrictionModelCB.pack(anchor=W,pady=3, padx=10)
contactFrictionModelCB.current(0)
contactFrictionModelCB.bind("<<ComboboxSelected>>", contactGlobalSettingsChanged)
contactCAlgoBox = Frame(contactGlobalGroup)
contactCAlgoBox.pack(fill=BOTH,pady=5)
box = Frame(contactCAlgoBox)
box.pack(fill=BOTH)
Label(box, text="  Contact algorithm: ").pack(side=LEFT)
contactCContAlgoCB = Combobox(box, values=["NEWTON","POINT_FIXE"], state='readonly')
contactCContAlgoCB.pack(anchor=W,pady=5, padx=10)
contactCContAlgoCB.current(0)
contactCContAlgoCB.bind("<<ComboboxSelected>>", contactGlobalSettingsChanged)
contactCFricAlgoBox = Frame(contactCAlgoBox)
contactCFricAlgoBox.pack(fill=BOTH)
Label(contactCFricAlgoBox, text="  Friction algorithm:  ").pack(side=LEFT)
contactCFricAlgoCB = Combobox(contactCFricAlgoBox, values=["NEWTON","POINT_FIXE"], state='readonly')
contactCFricAlgoCB.pack(anchor=W,pady=5, padx=10)
contactCFricAlgoCB.current(0)
contactCFricAlgoCB.bind("<<ComboboxSelected>>", contactGlobalSettingsChanged)
contactGlobalSetting = ContactGlobalSetting(contactFormRadioButton.get(),contactFrictionModelCB.get(),contactCContAlgoCB.get(),contactCFricAlgoCB.get())  # set initial global settings at this point
contactAssiGroup = LabelFrame(rightBox, text="Create/Modify contact assignment")
contactAssiGroup.pack(padx=10, pady=5, ipadx=5, ipady=5)
box = Frame(contactAssiGroup)
box.pack(fill=BOTH)
Label(box, text="  Name of assignment: ").pack(side=LEFT)
contactAssiNameLbl = Label(box, text="")
contactAssiNameLbl.pack(anchor=W)
box = Frame(contactAssiGroup)
box.pack(fill=BOTH)
Label(box, text="  Master: ").pack(side=LEFT)
contactMasterCB = Combobox(box, values=getNames([1]), state='readonly')
contactMasterCB.pack(anchor=W,pady=5, padx=10)
box = Frame(contactAssiGroup)
box.pack(fill=BOTH)
Label(box, text="  Slave:    ").pack(side=LEFT)
contactSlaveCB = Combobox(box, values=getNames([1]), state='readonly')
contactSlaveCB.pack(anchor=W,pady=5, padx=10)
contactFricCoeffBox = Frame(contactAssiGroup)
contactFricCoeffBox.pack(fill=BOTH)
Label(contactFricCoeffBox, text="  Coefficient of Friction: ").pack(side=LEFT, anchor=N)
contactFrictionCoeffEntry = Entry(contactFricCoeffBox)
contactFrictionCoeffEntry.pack(anchor=W, padx=3)
contactFrictionCoeffEntry.insert(END, "0")
contactDContAlgoBox = Frame(contactAssiGroup)
contactDContAlgoBox.pack(fill=BOTH, pady=10)
Label(contactDContAlgoBox, text="  Contact algorithm: ").pack(side=LEFT)
contactDContAlgoCB = Combobox(contactDContAlgoBox, values=["CONTRAINTE","GCP","PENALISATION"], state='readonly')
contactDContAlgoCB.pack(anchor=W,pady=5, padx=10)
contactDContAlgoCB.current(0)
contactDContAlgoCB.bind("<<ComboboxSelected>>", contactDContAlgoCBChanged)
contactPenBox = Frame(contactAssiGroup)
contactPenBox.pack(fill=BOTH, pady=10)
Label(contactPenBox, text="  Penalty factors: ").pack(side=LEFT)
contactPenNBox = Frame(contactPenBox)
contactPenNBox.pack(fill=BOTH,pady=3)
Label(contactPenNBox, text="   E_N: ").pack(side=LEFT)
contactENEntry = Entry(contactPenNBox)
contactENEntry.pack(anchor=W)
contactENEntry.insert(END, "1e7")
contactPenTBox = Frame(contactPenBox)
contactPenTBox.pack(fill=BOTH,pady=3)
Label(contactPenTBox, text="   E_T:  ").pack(side=LEFT)
contactETEntry = Entry(contactPenTBox)
contactETEntry.pack(anchor=W)
contactETEntry.insert(END, "1e7")
box = Frame(contactAssiGroup)
box.pack(fill=BOTH, padx=5, pady=5)
Button(box, text="Done", command=changeContactAssi).pack(side=RIGHT,padx=10)
disableWidgets(contactAssiGroup)
contactEnableDisableFrames()

# Thermal Tab
group = LabelFrame(thermalTab, text="List of temperature assignments")
group.pack(side=LEFT, fill=Y, padx=10, pady=10, ipadx=5, ipady=5)
box = Frame(group, height=500, width=180)
box.pack_propagate(0)
box.pack(side=LEFT)
thermalAssiListbox = Listbox(box)
thermalAssiListbox.pack(side=LEFT,padx=5,fill=BOTH,expand=TRUE)
thermalAssiListbox.bind('<<ListboxSelect>>', thermalAssiListboxSelectionChanged)
box = Frame(group)
box.pack(pady=20)
Button(box, text="Add", command=addThermalSet).pack(pady=5)
Button(box, text="Delete", command=deleteThermalAssi).pack()
box = Frame(thermalTab)
box.pack(side=LEFT,fill=Y)
thermalAssiGroup = LabelFrame(box, text="Create/Modify temperature assignment")
thermalAssiGroup.pack(padx=10, pady=10, ipadx=5, ipady=5)
box = Frame(thermalAssiGroup)
box.pack(fill=BOTH)
Label(box, text="  Name of assignment: ").pack(side=LEFT)
thermalAssiNameLbl = Label(box, text="")
thermalAssiNameLbl.pack(anchor=W)
box = Frame(thermalAssiGroup)
box.pack(fill=BOTH)
Label(box, text="  Assign to: ").pack(side=LEFT)
thermalAssiNameCB = Combobox(box, values=getNames([0]), state='readonly')
thermalAssiNameCB.pack(anchor=W,pady=5, padx=10)
thermalAssiNameCB.current(0)
modes = [("Constant", "const"),("From file", "file"),("Python function", "fun")]
thermModeRadioButton = StringVar()
thermModeRadioButton.set("const")
Radiobutton(thermalAssiGroup, text=modes[0][0],variable=thermModeRadioButton, value=modes[0][1]).pack(anchor=W)
box = Frame(thermalAssiGroup)
box.pack(fill=BOTH, padx=5, pady=5)
Label(box,text="    \u0394T:       ").pack(side=LEFT)
thermConstDeltaTEntry = Entry(box)
thermConstDeltaTEntry.pack(anchor=W)
thermConstDeltaTEntry.insert(END, "0")
Radiobutton(thermalAssiGroup, text=modes[1][0],variable=thermModeRadioButton, value=modes[1][1]).pack(anchor=W)
box = Frame(thermalAssiGroup)
box.pack(fill=BOTH, padx=5, pady=5)
Label(box,text="    UNITE: ").pack(side=LEFT)
thermUniteEntry = Entry(box)
thermUniteEntry.pack(anchor=W)
thermUniteEntry.pack(anchor=W)
thermUniteEntry.insert(END, "21")
box = Frame(thermalAssiGroup)
box.pack(fill=BOTH, padx=5, pady=5)
Label(box,text="           T0: ").pack(side=LEFT)
thermT0Entry = Entry(box)
thermT0Entry.pack(anchor=W)
thermT0Entry.pack(anchor=W)
thermT0Entry.insert(END, "0")
# Radiobutton(thermalAssiGroup, text=modes[2][0],variable=thermModeRadioButton, value=modes[2][1]).pack(anchor=W)
# box = Frame(thermalAssiGroup)
# box.pack(fill=BOTH, padx=5, pady=5)
# Label(box,text=" def deltaT(X,Y,Z):").pack(anchor=W)
# thermFunText = Text(box, height=15)
# thermFunText.pack(padx=5)
# thermFunText.insert(END, 'not yet implemented')
box = Frame(thermalAssiGroup)
box.pack(fill=BOTH, padx=5, pady=5)
Button(box, text="Done", command=changeThermalAssi).pack(side=RIGHT,padx=10)
disableWidgets(thermalAssiGroup)

# Results Tab
group = LabelFrame(resultsTab, text="Select output quantities")
group.pack(fill=Y, padx=10, pady=10, ipadx=5, ipady=5)
box = Frame(group)
box.pack(fill=BOTH, padx=5, pady=5)
Label(box, text="Output for: ").pack(side=LEFT)
resultsNameCB = Combobox(box, values=getNames([0]), state='readonly')
resultsNameCB.pack(anchor=W,pady=5, padx=10)
resultsNameCB.current(0)
resuStressTensor = IntVar()
resuEquiStresses = IntVar()
resuEpsilon = IntVar()
resuReactions = IntVar()
resuErrorEsti = IntVar()
resuStressTensor.set(1)
resuEquiStresses.set(1)
resuEpsilon.set(0)
resuReactions.set(1)
resuErrorEsti.set(0)
Checkbutton(group, text = "Stress tensor", variable = resuStressTensor, onvalue = 1, offvalue = 0).pack(fill=X)
Checkbutton(group, text = "Equivalent stresses", variable = resuEquiStresses, onvalue = 1, offvalue = 0).pack(fill=X)
Checkbutton(group, text = "Strain tensor", variable = resuEpsilon, onvalue = 1, offvalue = 0).pack(fill=X)
Checkbutton(group, text = "Reactions at restraints", variable = resuReactions, onvalue = 1, offvalue = 0).pack(fill=X)
Checkbutton(group, text = "A posteriori error estimation", variable = resuErrorEsti, onvalue = 1, offvalue = 0).pack(fill=X)

# Files Tab
box = Frame(filesTab)
box.pack(padx=5, pady=20)
Label(box,text="Current working directory: ").pack(side=LEFT)
currWorkingDirBox = Frame(box, height=22, width=380)
currWorkingDirBox.pack_propagate(0)
currWorkingDirBox.pack(side=LEFT)
currWorkingDirEntry = Entry(currWorkingDirBox,width=65)
currWorkingDirEntry.pack(fill=BOTH,expand=TRUE)
Button(box,text="change",command=changeWorkingDir).pack(padx=10)
box = Frame(filesTab)
box.pack(padx=5, pady=5)
Label(box,text="Study name: ").pack(side=LEFT)
studyNameEntry = Entry(box)
studyNameEntry.pack(side=LEFT)
studyNameEntry.insert(END, "new_case")
box1 = Frame(filesTab)
box1.pack(padx=5, pady=5)
group = LabelFrame(box1, text="Save/Load cawm-setup")
group.pack(side=LEFT, anchor=N, padx=10, pady=10, ipadx=5, ipady=5)
box = Frame(group)
box.pack(fill=BOTH, padx=5, pady=5)
Button(box,text="Save",command=pickle_save).pack(side=LEFT)
Button(box,text="Load",command=pickle_load).pack()
group = LabelFrame(box1, text="Manage code_aster files")
group.pack(side=LEFT, padx=10, pady=10, ipadx=5, ipady=5)
box = Frame(group, height=10)
box.pack()
box.pack_propagate()
Button(group,text="Create comm-file",width=20,command=assembleCOMM).pack(pady=5)
Label(group, text="for code_aster version 12.6 (may work with other versions, especially newer ones)",wraplength=200,justify=CENTER).pack()
box = Frame(group, height=25)
box.pack()
box.pack_propagate()
Button(group,text="Delete files",width=20,command=delCAFiles).pack(pady=3)
Button(group,text="Open mess-file",width=20,command=openMessFile).pack(pady=3)
Button(group,text="Open resu-file",width=20,command=openResuFile).pack(pady=3)
Button(group,text="Export reactions to csv",width=20,command=exportReacCSV).pack(pady=3)
Button(group,text="Show errors/alarms",width=20,command=showErrorsAlarms).pack(pady=3)

ntbook.tab(7, state="disabled")
ntbook.select(1)
mainloop()