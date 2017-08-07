
#   ca_wizard_mechanical, version 0.2
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

import xml.etree.ElementTree as ET

from keyword import iskeyword
from copy import deepcopy

ls = "\n"

def setMatLibPath(p):
    global matLibPath
    matLibPath = p

def setVersion(v):
    global cawmVersion
    cawmVersion = v

def isNumeric(*args):
    for s in args:
        try:
            float(s)
        except ValueError:
            return False
    return True
    
def isInteger(*args):
    for s in args:
        try:
            int(s)
        except ValueError:
            return False
    return True

def hasFunction(functionList,*args):
    for f in args:
        if f in [functionList[i].funcName for i in range(len(functionList))]:
            return True
    return False
    
def hasConstant(functionList,*args):
    for c in args:
        if c not in [functionList[i].funcName for i in range(len(functionList))] and c:
            return True
    return False

# check if string is either empty, a function or numeric - in which case: return True
def checkValidEntry(functionList,*args):
    for el in args:
        if el and not hasFunction(functionList,el) and not isNumeric(el):
            return False
    return True
            
class cawmInst:
    
    def __init__(self,solverSet,names,workingDir,studyName):
        self.solverSet = solverSet
        self.names = names
        self.workingDir = workingDir
        self.studyName = studyName
        self.cawmVersion = cawmVersion

class PyFunction:
    
    def __init__(self,funcName,funcText):
        self.funcName = funcName
        self.funcText = funcText
    
    # verify function name and see if the interpreter raises an exception
    def verify(self,functionList,checkFuncDefi):
        msgs = []
        if not self.funcName.isidentifier() or iskeyword(self.funcName):
            msgs.append(self.funcName + " is not a valid function name. The function will not be checked for further errors.")
        elif checkFuncDefi:
            try:
                exec("def " + self.funcName + "(x,y,z,t):\n" + self.funcText)
            except Exception as e:
                msgs.append("While trying to evaluate the Python function " + self.funcName + " the Python 3 interpreter raised the following exception:\n" + str(e))
        return msgs

class Material:
    
    def __init__(self,matName):
        root = ET.parse(matLibPath).getroot()
        for child in root:
            if child.attrib["name"] == matName:
                self.matName = matName
                self.matNum = child.find("materialNumber").text
                self.matCat = child.find("category").text
                self.youngsModulus = child.find("YoungsModulus").text
                self.poissonRatio = child.find("PoissonRatio").text
                self.alpha = child.find("alpha").text
                self.density = child.find("density").text
                return

class MaterialSet:
    
    def __init__(self,assiName,nodalGroupName,materialName):
        self.assiName = assiName
        self.nodalGroupName = nodalGroupName
        self.material = Material(materialName)
     
    # verify datatype of properties and node group name
    def verify(self,names,functionList):
        msgs = []
        if not isNumeric(self.material.youngsModulus,self.material.poissonRatio):
            msgs.append(self.assiName + ": Young's modulus or Poisson's ratio is not numeric.")
        if not [self.nodalGroupName, "Volume"] in [names[i] for i in range(len(names))] and not self.nodalGroupName == "whole mesh":
            msgs.append(self.assiName + ": Material is not assigned to a valid node group.")
        return msgs

class NodeJointSet:
    
    def __init__(self,assiName,jointGroupName,nodeName,cX,cY,cZ,cPhiX,cPhiY,cPhiZ):
        self.assiName = assiName
        self.jointGroupName = jointGroupName
        self.nodeName = nodeName
        self.cX = cX
        self.cY = cY
        self.cZ = cZ
        self.cPhiX = cPhiX
        self.cPhiY = cPhiY
        self.cPhiZ = cPhiZ
        
    # verify datatype of properties and node group name
    def verify(self,names,functionList):
        msgs = []
        if not isNumeric(self.cX, self.cY, self.cZ, self.cPhiX, self.cPhiY, self.cPhiZ):
            msgs.append(self.assiName + ": At least one stiffness value is not numeric.")
        if not [self.jointGroupName, "Node joint group"] in [names[i] for i in range(len(names))]:
            msgs.append(self.assiName + ": Node group name for the node joint group is not valid.")
        if not [self.nodeName, "Vertex/Node"] in [names[i] for i in range(len(names))]:
            msgs.append(self.assiName + ": Node group name for the node is not valid.")
        return msgs
        
class RestraintSet:
    
    def __init__(self,assiName,nodalGroupName,rotMatViaPython,deltaX,deltaY,deltaZ,deltaPhiX,deltaPhiY,deltaPhiZ,xTrans,yTrans,zTrans,rotX,rotY,rotZ,reacMX,reacMY,reacMZ):
        self.assiName = assiName
        self.nodalGroupName = nodalGroupName
        self.rotMatViaPython = rotMatViaPython
        self.deltaX = deltaX
        self.deltaY = deltaY
        self.deltaZ = deltaZ
        self.deltaPhiX = deltaPhiX
        self.deltaPhiY = deltaPhiY
        self.deltaPhiZ = deltaPhiZ
        self.xTrans = xTrans
        self.yTrans = yTrans
        self.zTrans = zTrans
        self.rotX = rotX
        self.rotY = rotY
        self.rotZ = rotZ
        self.reacMX = reacMX
        self.reacMY = reacMY
        self.reacMZ = reacMZ
        
    # verify datatype of properties and node group name
    def verify(self,names,functionList):
        msgs = []
        if self.rotMatViaPython:
            if hasFunction(functionList,self.deltaX,self.deltaY,self.deltaZ,self.deltaPhiX,self.deltaPhiY,self.deltaPhiZ):
                raise ValueError(self.assiName + ": When using the provided function for the rotation matrix the entries for the restraints can not be a function.")
            if (self.rotX and not (self.deltaX and self.deltaPhiY and self.deltaPhiZ)) or (self.rotY and not(self.deltaY and self.deltaPhiX and self.deltaPhiZ)) or \
            (self.rotZ and not (self.deltaZ and self.deltaPhiX and self.deltaPhiY)):
                raise ValueError(self.assiName + ": When using the provided function for the rotation matrix the translational DoFs for all axes to which the rotation is applied to have to be restrained.")
            if not isNumeric(self.deltaPhiX, self.deltaPhiY, self.deltaPhiZ, self.xTrans, self.yTrans, self.zTrans):
                msgs.append(self.assiName + ": Inputs for the rotational DoFs and the coordinates of the rotation center have to be numeric. (All rotational DoFs have to be restrained).")
        if not checkValidEntry(functionList,self.deltaX,self.deltaY,self.deltaZ,self.deltaPhiX,self.deltaPhiY,self.deltaPhiZ):
            msgs.append(self.assiName + ": At least one input for translation or rotation is neither a function nor numeric. If this is related to the rotational DoFs and the restraint is not assigned to " + \
            "a node of a node joint group you can ignore this warning.")
        if not isNumeric(self.reacMX, self.reacMY, self.reacMZ):
            msgs.append(self.assiName + ": At least one input for the coordinates for the computation of the torsional reactions is not numeric.")
        if not [self.nodalGroupName, "Surface"] in [names[i] for i in range(len(names))] and not [self.nodalGroupName, "Edge"] in [names[i] for i in range(len(names))] and \
        not [self.nodalGroupName, "Vertex/Node"] in [names[i] for i in range(len(names))]:
            msgs.append(self.assiName + ": Restraint is not assigned to a valid node group.")
        return msgs
        
        
class LoadSet:
    
    def __init__(self,assiName,nodalGroupName,loadType,FX,FY,FZ,MX,MY,MZ,p,gX,gY,gZ,omega,centerX,centerY,centerZ,axisX,axisY,axisZ):
        self.assiName = assiName
        self.nodalGroupName = nodalGroupName
        self.loadType = loadType
        self.FX = FX
        self.FY = FY
        self.FZ = FZ
        self.MX = MX
        self.MY = MY
        self.MZ = MZ
        self.p = p
        self.gX = gX
        self.gY = gY
        self.gZ = gZ
        self.omega = omega
        self.centerX = centerX
        self.centerY = centerY
        self.centerZ = centerZ
        self.axisX = axisX
        self.axisY = axisY
        self.axisZ = axisZ
        
    # verify datatype of properties and node group name
    def verify(self,names,functionList):
        msgs = []
        if self.loadType == "Gravity":
            if not isNumeric(self.gX, self.gY, self.gZ):
                msgs.append(self.assiName + ": At least one input for the gravity vector is not numeric.")
            if not [self.nodalGroupName, "Volume"] in [names[i] for i in range(len(names))] and not self.nodalGroupName == "whole mesh":
                msgs.append(self.assiName + ": Load is not assigned to a valid node group.")
        if self.loadType == "Centrifugal force":
            if not isNumeric(self.omega, self.centerX, self.centerY, self.centerZ, self.axisX, self.axisY, self.axisZ):
                msgs.append(self.assiName + ": At least one input for the rotation is not numeric.")
            if not [self.nodalGroupName, "Volume"] in [names[i] for i in range(len(names))] and not self.nodalGroupName == "whole mesh":
                msgs.append(self.assiName + ": Load is not assigned to a valid node group.")
        if self.loadType == "Force on volume":
            if not checkValidEntry(functionList, self.FX, self.FY, self.FZ):
                msgs.append(self.assiName + ": At least one input for the force vector is neither a function nor numeric.")
            if not [self.nodalGroupName, "Volume"] in [names[i] for i in range(len(names))] and not self.nodalGroupName == "whole mesh":
                msgs.append(self.assiName + ": Load is not assigned to a valid node group.")
        if self.loadType == "Force on face":
            if not checkValidEntry(functionList, self.FX, self.FY, self.FZ):
                msgs.append(self.assiName + ": At least one input for the force vector is neither a function nor numeric.")
            if not [self.nodalGroupName, "Surface"] in [names[i] for i in range(len(names))]:
                msgs.append(self.assiName + ": Load is not assigned to a valid node group.")
        if self.loadType == "Force on edge":
            if not checkValidEntry(functionList, self.FX, self.FY, self.FZ):
                msgs.append(self.assiName + ": At least one input for the force vector is neither a function nor numeric.")
            if not [self.nodalGroupName, "Edge"] in [names[i] for i in range(len(names))]:
                msgs.append(self.assiName + ": Load is not assigned to a valid node group.")
        if self.loadType == "Force on node":
            if not checkValidEntry(functionList, self.FX, self.FY, self.FZ, self.MX, self.MY, self.MZ):
                msgs.append(self.assiName + ": At least one input for the force or torque vector is neither a function nor numeric (if this message relates to the torque and the node" + \
                "is not assigned to a node joint group, you can disregard this message).")
            if not self.nodalGroupName in [names[i][0] for i in range(len(names))] and not [self.nodalGroupName, "Node joint group"] in [names[i] for i in range(len(names))]:
                msgs.append(self.assiName + ": Load is not assigned to a valid node group.")
        if self.loadType == "Pressure":
            if not checkValidEntry(functionList, self.p) or not self.p:
                msgs.append(self.assiName + ": Input for the pressure is neither a function nor numeric.")
            if not [self.nodalGroupName, "Surface"] in [names[i] for i in range(len(names))]:
                msgs.append(self.assiName + ": Load is not assigned to a valid node group.")
        return msgs
        
class ContactGlobalSetting:
    
    def __init__(self,formulationType,frictionModel,contactAlgo,frictionAlgo):
        self.formulationType = formulationType
        self.frictionModel = frictionModel
        self.contactAlgo = contactAlgo
        self.frictionAlgo = frictionAlgo
        
class ContactSet:
    
    def __init__(self,assiName,masterName,slaveName,fricCoeff,contactAlgo,E_N,E_T,globalSettings):
        self.assiName = assiName
        self.masterName = masterName
        self.slaveName = slaveName
        self.fricCoeff = fricCoeff
        self.contactAlgo = contactAlgo
        self.E_N = E_N
        self.E_T = E_T
        self.globalSettings = globalSettings
    
    # verify datatype of properties and node group name
    def verify(self,names,functionList):
        msgs = []
        if self.globalSettings.formulationType == "discrete":
            if self.contactAlgo == "PENALISATION":
                if not isNumeric(self.E_N):
                    msgs.append(self.assiName + ": E_N is not numeric.")
            if self.globalSettings.frictionModel == "Coulomb":
                if not isNumeric(self.E_T):
                    msgs.append(self.assiName + ": E_T is not numeric.")
                if not isNumeric(self.fricCoeff):
                    msgs.append(self.assiName + ": Friction coefficient is not numeric.")
        else:
            if self.globalSettings.frictionModel == "Coulomb":
                if not isNumeric(self.fricCoeff):
                    msgs.append(self.assiName + ": Friction coefficient is not numeric.")
        if not [self.masterName, "Surface"] in [names[i] for i in range(len(names))]:
            msgs.append(self.assiName + ": Master is not assigned to a valid node group.")
        if not [self.slaveName, "Surface"] in [names[i] for i in range(len(names))]:
            msgs.append(self.assiName + ": Slave is not assigned to a valid node group.")
        return msgs
        
class ThermalSet:
    
    def __init__(self,assiName,nodalGroupName,assiType,deltaT,unite,T0,funStr):
        self.assiName = assiName
        self.nodalGroupName = nodalGroupName
        self.assiType = assiType
        self.deltaT = deltaT
        self.unite = unite
        self.T0 = T0
        self.funStr = funStr

    # verify datatype of properties and node group name
    def verify(self,names,functionList):
        msgs = []
        if self.assiType == "const":
            if not checkValidEntry(functionList, self.deltaT):
                msgs.append(self.assiName + ": \u0394T is neither a function nor numeric.")
        else:
            if not isNumeric(self.unite, self.T0):
                msgs.append(self.assiName + ": UNITE or T0 is not numeric.")
        if not [self.nodalGroupName, "Volume"] in [names[i] for i in range(len(names))] and not self.nodalGroupName == "whole mesh":
            msgs.append(self.assiName + ": Temp. field is not assigned to a valid node group.")
        return msgs
        
class OutputSet:
    
    def __init__(self,nodalGroupName,SIGM,SIEQ,EPS,REAC,ERME,TEMP):
        self.nodalGroupName = nodalGroupName
        self.SIGM = SIGM
        self.SIEQ = SIEQ
        self.EPS = EPS
        self.REAC = REAC
        self.ERME = ERME
        self.TEMP = TEMP
        
class SolverSet:
    
    def __init__(self,analysisType,timeSteps,endTime,timeRampUp,timeRampDown,timeRampFunc,strainModel,method,resi,maxIter,functions,checkFuncDefis,materialSets,nodeJointSets,restraintSets,loadSets,contactSets,
    thermalSets,outputSet):
        self.analysisType = analysisType
        self.timeSteps = timeSteps
        self.endTime = endTime
        self.timeRampUp = timeRampUp
        self.timeRampDown = timeRampDown
        self.timeRampFunc = timeRampFunc
        self.strainModel = strainModel
        self.method = method
        self.resi = resi
        self.maxIter = maxIter
        self.functions = functions
        self.checkFuncDefis = checkFuncDefis
        self.materialSets = materialSets
        self.nodeJointSets = nodeJointSets
        self.restraintSets = restraintSets
        self.loadSets = loadSets
        self.contactSets = contactSets
        self.thermalSets = thermalSets
        self.outputSet = outputSet
        
    # this method will check if relevant inputs are numeric and all assignments to node groups are valid. It will NOT check in anyway if the resulting comm-file will run in code_aster!
    def verify(self,names,functionList):
        msgs = []
        if len(self.materialSets) == 0 or len(self.restraintSets) == 0:
            msgs.extend(["The current setup has no material assignments and/or no restraint assignments."])
        for el in self.functions:
            msgs.extend(el.verify(functionList,self.checkFuncDefis))
        for el in self.materialSets + self.nodeJointSets + self.restraintSets + self.loadSets + self.contactSets + self.thermalSets:
            msgs.extend(el.verify(names,functionList))
        if not isInteger(self.timeSteps):
            raise ValueError("The number of time steps is not of type integer.")
        if not isNumeric(self.endTime):
            msgs.extend(["The simulation end time is not numeric."])
        if self.analysisType == "non-linear static":
            if not isInteger(self.maxIter):
                msgs.extend(["The number of max. iterations has to be of type integer."])
            if not isNumeric(self.resi):
                msgs.extend(["Max. relative global residual is not numeric."])
            if int(self.timeSteps) < 1:
                msgs.extend(["A non-linear analysis requires at least one time step."])
        if self.timeRampUp and self.timeRampDown and not int(self.timeSteps) % 2 == 0:
            msgs.extend(["Ramping loads and restraints up AND down requires an even amount of time steps. Otherwise a computation with their max. values will not happen."])
        if self.outputSet.ERME and len(self.nodeJointSets) > 0:
            msgs.extend(["Calculation of the error a posteriori (ERME) with code_aster version <= 13.2 can only be performed on the whole mesh. This will not work with the discrete element" + \
            " of a node joint (MODELISATION='DIS_TR')."])
        return msgs
        
    # generate string for comm-file
    def assembleCOMM(self):
        
        def getFormuleName(funcName):
            for el in formules:
                if el[1] == funcName:
                    return el[0]
            return None
        
        pythonFuns = ""
        # If any restraints require the application of the roational matrix, add generic translation functions
        if sum([self.restraintSets[i].rotMatViaPython for i in range(len(self.restraintSets))]) > 0:
            pythonFuns = "# Generic translation functions:" + ls + "def translate_X(deltaX,phiY,phiZ,XTrans,YTrans,ZTrans,X,Y,Z):" + ls + \
            " return deltaX+(X-XTrans)*cos(phiY)+(Z-ZTrans)*sin(phiY)+(X-XTrans)*cos(phiZ)-(Y-YTrans)*sin(phiZ)-2*(X-XTrans)" + ls + ls + \
            "def translate_Y(deltaY,phiX,phiZ,XTrans,YTrans,ZTrans,X,Y,Z):" + ls + \
            " return deltaY+(Y-YTrans)*cos(phiX)-(Z-ZTrans)*sin(phiX)+(Y-YTrans)*cos(phiZ)+(X-XTrans)*sin(phiZ)-2*(Y-YTrans)" + ls + ls + \
            "def translate_Z(deltaZ,phiX,phiY,XTrans,YTrans,ZTrans,X,Y,Z):" + ls + \
            " return deltaZ+(Z-ZTrans)*cos(phiX)+(Y-YTrans)*sin(phiX)+(Z-ZTrans)*cos(phiY)-(X-XTrans)*sin(phiY)-2*(Z-ZTrans)" + ls + ls
        
        # For restraints that use the generic translation functions defined above, add wrapper functions to the functions list
        restraintSetsLocal = deepcopy(self.restraintSets) # allow local modification of the restraint sets without compromising the original data
        functionsLocal = deepcopy(self.functions) # allow local modification of the functions list without compromising the original data
        for el in restraintSetsLocal:
            if el.rotMatViaPython:
                if not el.deltaX == "" or el.rotX:
                    if el.rotX:
                        phiY = str(float(el.deltaPhiY))
                        phiZ = str(float(el.deltaPhiZ))
                    else:
                        phiY = "0.0"
                        phiZ = "0.0"
                    functionsLocal.append(PyFunction("DX_" + el.assiName, " return translate_X("+str(float(el.deltaX))+","+phiY+","+phiZ+","+ \
                    str(float(el.xTrans))+","+str(float(el.yTrans))+","+str(float(el.zTrans))+",x,y,z)"))
                    el.deltaX = "DX_" + el.assiName
                if not el.deltaY == "" or el.rotY:
                    if el.rotY:
                        phiX = str(float(el.deltaPhiX))
                        phiZ = str(float(el.deltaPhiZ))
                    else:
                        phiX = "0.0"
                        phiZ = "0.0"
                    functionsLocal.append(PyFunction("DY_" + el.assiName, " return translate_Y("+str(float(el.deltaY))+","+phiX+","+phiZ+","+ \
                    str(float(el.xTrans))+","+str(float(el.yTrans))+","+str(float(el.zTrans))+",x,y,z)"))
                    el.deltaY = "DY_" + el.assiName
                if not el.deltaZ == "" or el.rotZ:
                    if el.rotZ:
                        phiX = str(float(el.deltaPhiX))
                        phiY = str(float(el.deltaPhiY))
                    else:
                        phiX = "0.0"
                        phiY = "0.0"
                    functionsLocal.append(PyFunction("DZ_" + el.assiName, " return translate_Z("+str(float(el.deltaZ))+","+phiX+","+phiY+","+ \
                    str(float(el.xTrans))+","+str(float(el.yTrans))+","+str(float(el.zTrans))+",x,y,z)"))
                    el.deltaZ = "DZ_" + el.assiName

        # Add all Python functions in the functions list to the comm-file
        if len(functionsLocal) > 0:
            pythonFuns = pythonFuns + "# User defined Python functions and wrappers for the generic translation functions" + ls + ls
        for el in functionsLocal:
            pythonFuns = pythonFuns + "def " + el.funcName + "(x,y,z,t):" + ls + el.funcText + ls + ls

        # DEBUT statement
        debutStr = ls + "# Start of code_aster commands" + ls + "DEBUT();" + ls + ls
        
        # list of time steps
        if int(self.timeSteps) > 0:
            tListStr = "# list of time steps" + ls + "TLIST=DEFI_LIST_REEL(DEBUT=0.0,INTERVALLE=_F(JUSQU_A=" + self.endTime + ",NOMBRE=" + self.timeSteps + ",),);" + ls + ls
            "SF=DEFI_FONCTION(NOM_PARA='INST',VALE=("
            if self.timeRampUp == 1 and self.timeRampDown == 1:
                tListStr = tListStr + "SF=DEFI_FONCTION(NOM_PARA='INST',VALE=(0.0, 0.0, 0.5, 1.0 ,1.0 ,0.0,),);" + ls + ls
            elif self.timeRampUp:
                tListStr = tListStr + "SF=DEFI_FONCTION(NOM_PARA='INST',VALE=(0.0, 0.0, 1.0, 1.0,),);" + ls + ls
            elif self.timeRampDown:
                tListStr = tListStr + "SF=DEFI_FONCTION(NOM_PARA='INST',VALE=(0.0, 1.0, 1.0, 0.0,),);" + ls + ls 
        else:
            tListStr = ""
        
        # Bind all Python functions to corresponding code_aster formules
        formuleStr = ""
        formules = []
        for el in functionsLocal:
            if formuleStr == "":
                formuleStr = "# Assign formules" + ls
            # store all identifiers for the formules in a list (max. 8 characters allowed for identifier -> can not use the actual function name)
            # formule name at index 0, function name at index 1
            formules.append(["F" + str(len(formules)),el.funcName])
            formuleStr = formuleStr + formules[-1][0] + "=FORMULE(VALE='" + el.funcName + "(X,Y,Z,INST)',NOM_PARA=('X','Y','Z','INST',),);" + ls
        if not formuleStr == "":
            formuleStr = formuleStr + ls
        
        # material definitions
        matDefiStr = "# Material definitions" + ls
        matDefiNames = [] # same here as with the formules - use short identifiers for the material definitions
        for el in self.materialSets:
            matDefiNames.append("MA"+str(len(matDefiNames)))
            matDefiStr = matDefiStr + matDefiNames[-1] + "=" + "DEFI_MATERIAU(ELAS=_F(E=" + el.material.youngsModulus + ",NU=" + el.material.poissonRatio + \
            ",RHO=" + el.material.density + ",ALPHA=" + el.material.alpha + ",),);" + ls
        matDefiStr = matDefiStr + ls
        
        # reading/modifying the mesh
        meshName = "MAIL0"
        # reading
        meshStr = "# reading/modifying the mesh" + ls + meshName + "=LIRE_MAILLAGE(FORMAT='MED',);" + ls
        # create points for node joints
        if len(self.nodeJointSets) > 0:
            meshName = "MAIL1"
            meshStr = meshStr + meshName + "=CREA_MAILLAGE(MAILLAGE=MAIL0,CREA_POI1=("
            for el in self.nodeJointSets:
                meshStr = meshStr + "_F(NOM_GROUP_MA='" + el.nodeName + "',GROUP_NO='" + el.nodeName + "',)," + ls
            meshStr = meshStr + "),);" + ls
        # mesh adaption for pressure loads and contacts
        groupMAStr = ""
        groupMAList = []
        for el in self.loadSets:
            if el.loadType == "Pressure" and not el.nodalGroupName in groupMAList:
                groupMAStr = groupMAStr + "'" + el.nodalGroupName + "',"
                groupMAList.append(el.nodalGroupName)
        if self.analysisType == "non-linear static":
            for el in self.contactSets:
                if not el.masterName in groupMAList:
                    groupMAStr = groupMAStr + "'" + el.masterName + "',"
                    groupMAList.append(el.masterName)
                if not el.slaveName in groupMAList:
                    groupMAStr = groupMAStr + "'" + el.slaveName + "',"
                    groupMAList.append(el.slaveName)
        if not groupMAStr == "":
                meshStr = meshStr + meshName + "=MODI_MAILLAGE(reuse=" + meshName + ",MAILLAGE=" + meshName + ",ORIE_PEAU_3D=_F(GROUP_MA=(" + ls + \
                groupMAStr + "),),);" + ls
        meshStr = meshStr + ls
        
        # create model
        modelStr = "# create model" + ls + "MODE=AFFE_MODELE(MAILLAGE=" + meshName + ",AFFE=(_F(TOUT='OUI',PHENOMENE='MECANIQUE',MODELISATION='3D',)," + ls
        groupMAStr = ""
        for el in self.nodeJointSets:
            groupMAStr = groupMAStr + ls + "'" + el.nodeName + "',"
        if not groupMAStr == "":
            modelStr = modelStr + "_F(GROUP_MA=(" + groupMAStr + ")," + ls + "PHENOMENE='MECANIQUE',MODELISATION='DIS_TR',),"
        modelStr = modelStr + "),);" + ls + ls

        # create temperature fields from constant or function
        tempFieldStr = ""
        tempFieldNames = []
        if sum([self.thermalSets[i].assiType == "const" for i in range(len(self.thermalSets))]) > 0:
            tempFieldStr = "# Create temperature fields" + ls
        for el in self.thermalSets:
            if el.assiType == "const":
                tempFieldNames.append("TFld" + str(len(tempFieldNames)))
                tempFieldStr = tempFieldStr + tempFieldNames[-1] + "=CREA_CHAMP(TYPE_CHAM='NOEU_TEMP_"
                if hasFunction(functionsLocal,el.deltaT):
                    tempFieldStr = tempFieldStr + "F"
                else:
                    tempFieldStr = tempFieldStr + "R"
                tempFieldStr = tempFieldStr + "',OPERATION='AFFE',MODELE=MODE,AFFE=(_F("
                if el.nodalGroupName == "whole mesh":
                    tempFieldStr = tempFieldStr + "TOUT='OUI'"
                else:
                    tempFieldStr = tempFieldStr + "GROUP_MA='" + el.nodalGroupName + "'"
                tempFieldStr = tempFieldStr + ",NOM_CMP='TEMP'"
                if hasFunction(functionsLocal,el.deltaT):
                    tempFieldStr = tempFieldStr + ",VALE_F=" + getFormuleName(el.deltaT)
                else:
                    tempFieldStr = tempFieldStr + ",VALE=" + el.deltaT
                tempFieldStr = tempFieldStr + ",),),);" + ls
        if not tempFieldStr == "":
            tempFieldStr = tempFieldStr + ls
                
        # create a code_aster-result for all temp. fields
        tempResStr = ""
        tempResNames = []
        if len(tempFieldNames) > 0:
            tempResStr = "# Create results for all temperature fields" + ls
        for el in tempFieldNames:
            tempResNames.append("TRes" + str(len(tempResNames)))
            tempResStr = tempResStr + tempResNames[-1] + "=CREA_RESU(OPERATION='AFFE',TYPE_RESU='EVOL_THER',NOM_CHAM='TEMP',AFFE=_F(CHAM_GD=" + el + ","
            if int(self.timeSteps) > 0:
                tempResStr = tempResStr + "LIST_INST=TLIST"
            else:
                tempResStr = tempResStr + "INST=0.0"
            tempResStr = tempResStr + ",),);" + ls
        if not tempResStr == "":
            tempResStr = tempResStr + ls
        
        # create a code_aster-result for the temp. field from a med-file
        if sum([self.thermalSets[i].assiType == "file" for i in range(len(self.thermalSets))]) > 0:
            tempResStr = tempResStr + "# create result for the temperature field from a med-files"
        for el in self.thermalSets:
            if el.assiType == "file":
                tempResNames.append("TRes" + str(len(tempResNames)))
                tempResStr = tempResStr + tempResNames[-1] + "=LIRE_RESU(TYPE_RESU='EVOL_THER',FORMAT='MED'," + \
                "MAILLAGE=" + meshName + "," + ls + "UNITE=" + el.unite + "," + \
                "FORMAT_MED=_F(NOM_CHAM='TEMP',NOM_CHAM_MED='TEMP____TEMP',),TOUT_ORDRE='OUI',);" + ls
        if sum([self.thermalSets[i].assiType == "file" for i in range(len(self.thermalSets))]) > 0:
            tempResStr = tempResStr + ls
        
        # assign materials and temperature results
        matTempAssiStr = "# Assign materials and temp. results" + ls + "MATE=AFFE_MATERIAU(MAILLAGE=" + meshName + ",AFFE=(" + ls
        i=0
        for el in self.materialSets:
            matTempAssiStr = matTempAssiStr + "_F(" 
            if el.nodalGroupName == "whole mesh":
                matTempAssiStr = matTempAssiStr + "TOUT='OUI',"
            else:
                matTempAssiStr = matTempAssiStr + "GROUP_MA='" + el.nodalGroupName + "',"
            matTempAssiStr = matTempAssiStr + "MATER=" + matDefiNames[i] + ",)," + ls
            i = i+1
        matTempAssiStr = matTempAssiStr + "),"
        i = 0
        if len(self.thermalSets) > 0:
            matTempAssiStr = matTempAssiStr + "AFFE_VARC=(" + ls
        for el in self.thermalSets:
            matTempAssiStr = matTempAssiStr + "_F("
            if el.nodalGroupName == "whole mesh":
                matTempAssiStr = matTempAssiStr + "TOUT='OUI'"
            else:
                matTempAssiStr = matTempAssiStr + "GROUP_MA='" + el.nodalGroupName + "'"
            matTempAssiStr = matTempAssiStr + ",NOM_VARC='TEMP',EVOL=" + tempResNames[i] + ","
            if el.assiType == "file":
                matTempAssiStr = matTempAssiStr + "VALE_REF=" + str(float(el.T0))
            else:
                matTempAssiStr = matTempAssiStr + "VALE_REF=0.0"
            matTempAssiStr = matTempAssiStr + ",)," + ls
            i = i+1
        if len(self.thermalSets) > 0:
            matTempAssiStr = matTempAssiStr + "),"
        matTempAssiStr = matTempAssiStr + ");" + ls + ls
        
        # assign properties for node joints
        caraStr = ""
        for el in self.nodeJointSets:
            if caraStr == "":
                caraStr = "# assign properties for node joints" + ls + "CARA=AFFE_CARA_ELEM(MODELE=MODE,DISCRET=("
            caraStr = caraStr + "_F(CARA='K_TR_D_N',GROUP_MA='" + el.nodeName + "',VALE=(" + el.cX + "," + el.cY + "," + el.cZ + \
            "," + el.cPhiX + "," + el.cPhiY + "," + el.cPhiZ + ",),)," + ls
        if not caraStr == "":
            caraStr = caraStr + "),);" + ls + ls
        
        # assign restraints/loads via formules
        affeCharMecaFStr = ""
        # restraints
        for el in restraintSetsLocal:
            hasFormulesTrans = hasFunction(functionsLocal,el.deltaX, el.deltaY, el.deltaZ)  # at least one delta is not numeric (is a function)
            hasFormulesRot = 0
            if el.nodalGroupName in [self.nodeJointSets[i].nodeName for i in range(len(self.nodeJointSets))]: # restraint applied to a node of a node joint -> rotational DOFs
                hasFormulesRot = hasFunction(functionsLocal,el.deltaPhiX, el.deltaPhiY, el.deltaPhiZ)
            if hasFormulesTrans or hasFormulesRot: # restraint uses at least one function
                affeCharMecaFStr = affeCharMecaFStr + "_F(GROUP_NO='" + el.nodalGroupName + "',"
                if hasFunction(functionsLocal,el.deltaX):
                    affeCharMecaFStr = affeCharMecaFStr + "DX=" + getFormuleName(el.deltaX) + ","
                if hasFunction(functionsLocal,el.deltaY):
                    affeCharMecaFStr = affeCharMecaFStr + "DY=" + getFormuleName(el.deltaY) + ","
                if hasFunction(functionsLocal,el.deltaZ):
                    affeCharMecaFStr = affeCharMecaFStr + "DZ=" + getFormuleName(el.deltaZ) + ","
                if hasFormulesRot:
                    if hasFunction(functionsLocal,el.deltaPhiX):
                        affeCharMecaFStr = affeCharMecaFStr + "DRX=" + getFormuleName(el.deltaPhiX) + ","
                    if hasFunction(functionsLocal,el.deltaPhiY):
                        affeCharMecaFStr = affeCharMecaFStr + "DRY=" + getFormuleName(el.deltaPhiY) + ","
                    if hasFunction(functionsLocal,el.deltaPhiZ):
                        affeCharMecaFStr = affeCharMecaFStr + "DRZ=" + getFormuleName(el.deltaPhiZ) + ","
                affeCharMecaFStr = affeCharMecaFStr + ")," + ls
        if not affeCharMecaFStr == "":
            affeCharMecaFStr = "DDL_IMPO=(" + ls + affeCharMecaFStr + ")," + ls
        # loads
        forceOnVolumeStr = ""
        forceOnFaceStr = ""
        forceOnEdgeStr = ""
        forceOnNodeStr = ""
        pressureStr = ""
        for el in self.loadSets:
            # forces/torques
            if el.loadType in ["Force on volume","Force on face","Force on edge","Force on node"]:
                hasFormulesForce = hasFunction(functionsLocal,el.FX,el.FY,el.FZ)
                hasFormulesTorque = 0
                if el.loadType == "Force on node":
                    if el.nodalGroupName in [self.nodeJointSets[i].nodeName for i in range(len(self.nodeJointSets))]: # load applied to a node of a node joint -> torque assignment possible
                        hasFormulesTorque = hasFunction(functionsLocal,el.MX,el.MY,el.MZ)
                if hasFormulesForce or hasFormulesTorque:
                    if el.nodalGroupName == "whole mesh":
                        assiStr = "TOUT='OUI',"
                    elif el.loadType == "Force on node":
                        assiStr = "GROUP_NO='" + el.nodalGroupName + "',"
                    else:
                        assiStr = "GROUP_MA='" + el.nodalGroupName + "',"
                    tempStr = "_F(" + assiStr
                    if hasFunction(functionsLocal,el.FX):
                        tempStr = tempStr + "FX=" + getFormuleName(el.FX) + ","
                    if hasFunction(functionsLocal,el.FY):
                        tempStr = tempStr + "FY=" + getFormuleName(el.FY) + ","
                    if hasFunction(functionsLocal,el.FZ):
                        tempStr = tempStr + "FZ=" + getFormuleName(el.FZ) + ","
                    if hasFormulesTorque:
                        if hasFunction(functionsLocal,el.MX):
                            tempStr = tempStr + "MX=" + getFormuleName(el.MX) + ","
                        if hasFunction(functionsLocal,el.MY):
                            tempStr = tempStr + "MY=" + getFormuleName(el.MY) + ","
                        if hasFunction(functionsLocal,el.MZ):
                            tempStr = tempStr + "MZ=" + getFormuleName(el.MZ) + ","
                    tempStr = tempStr + ")," + ls
                    if el.loadType == "Force on volume":
                        forceOnVolumeStr = forceOnVolumeStr + tempStr
                    elif el.loadType == "Force on face":
                        forceOnFaceStr = forceOnFaceStr + tempStr
                    elif el.loadType == "Force on edge":
                        forceOnEdgeStr = forceOnEdgeStr + tempStr
                    elif el.loadType == "Force on node":
                        forceOnNodeStr = forceOnNodeStr + tempStr
            # pressures
            if el.loadType == "Pressure":
                if hasFunction(functionsLocal,el.p):
                    pressureStr = pressureStr + "_F(GROUP_MA='" + el.nodalGroupName + "',PRES=" + getFormuleName(el.p) + ",)," + ls
        if not forceOnVolumeStr == "":
            affeCharMecaFStr = affeCharMecaFStr + "FORCE_INTERNE=(" + ls + forceOnVolumeStr + ")," + ls
        if not forceOnFaceStr == "":
            affeCharMecaFStr = affeCharMecaFStr + "FORCE_FACE=(" + ls + forceOnFaceStr + ")," + ls
        if not forceOnEdgeStr == "":
            affeCharMecaFStr = affeCharMecaFStr + "FORCE_ARETE=(" + ls + forceOnEdgeStr + ")," + ls
        if not forceOnNodeStr == "":
            affeCharMecaFStr = affeCharMecaFStr + "FORCE_NODALE=(" + ls + forceOnNodeStr + ")," + ls
        if not pressureStr == "":
            affeCharMecaFStr = affeCharMecaFStr + "PRES_REP=(" + ls + pressureStr + ")," + ls
        if not affeCharMecaFStr == "":
            affeCharMecaFStr = "# assign restraints/loads via formules" + ls + "CHARF=AFFE_CHAR_MECA_F(MODELE=MODE," + ls + affeCharMecaFStr + ");" + ls + ls

        # assign remaining restraints, node joints and loads
        affeCharMecaStr = ""
        # restraints
        for el in restraintSetsLocal:
            hasConstantsTrans = hasConstant(functionsLocal,el.deltaX, el.deltaY, el.deltaZ)  # at least one delta is not a function
            hasConstantsRot = 0
            if el.nodalGroupName in [self.nodeJointSets[i].nodeName for i in range(len(self.nodeJointSets))]: # restraint applied to a node of a node joint -> rotational DOFs
                hasConstantsRot = hasConstant(functionsLocal,el.deltaPhiX, el.deltaPhiY, el.deltaPhiZ)
            if hasConstantsTrans or hasConstantsRot: # restraint uses at least one constant
                if not el.rotMatViaPython:
                    affeCharMecaStr = affeCharMecaStr + "_F(GROUP_NO='" + el.nodalGroupName + "',"
                    if hasConstant(functionsLocal,el.deltaX):
                        affeCharMecaStr = affeCharMecaStr + "DX=" + el.deltaX + ","
                    if hasConstant(functionsLocal,el.deltaY):
                        affeCharMecaStr = affeCharMecaStr + "DY=" + el.deltaY + ","
                    if hasConstant(functionsLocal,el.deltaZ):
                        affeCharMecaStr = affeCharMecaStr + "DZ=" + el.deltaZ + ","
                    if hasConstantsRot:
                        if hasConstant(functionsLocal,el.deltaPhiX):
                            affeCharMecaStr = affeCharMecaStr + "DRX=" + el.deltaPhiX + ","
                        if hasConstant(functionsLocal,el.deltaPhiY):
                            affeCharMecaStr = affeCharMecaStr + "DRY=" + el.deltaPhiY + ","
                        if hasConstant(functionsLocal,el.deltaPhiZ):
                            affeCharMecaStr = affeCharMecaStr + "DRZ=" + el.deltaPhiZ + ","
                    affeCharMecaStr = affeCharMecaStr + ")," + ls
        if not affeCharMecaStr == "":
            affeCharMecaStr = "DDL_IMPO=(" + ls + affeCharMecaStr + ")," + ls
        # node joints
        nodeJointsStr = ""
        for el in self.nodeJointSets:
            nodeJointsStr = nodeJointsStr + "_F(GROUP_NO='" + el.jointGroupName + "',)," + ls
        # loads
        forceOnVolumeStr = ""
        forceOnFaceStr = ""
        forceOnEdgeStr = ""
        forceOnNodeStr = ""
        pressureStr = ""
        gravityStr = ""
        centrifugalForceStr = ""
        for el in self.loadSets:
            # forces/torques
            if el.loadType in ["Force on volume","Force on face","Force on edge","Force on node"]:
                hasConstantsForce = hasConstant(functionsLocal,el.FX,el.FY,el.FZ)
                hasConstantsTorque = 0
                if el.loadType == "Force on node":
                    if el.nodalGroupName in [self.nodeJointSets[i].nodeName for i in range(len(self.nodeJointSets))]: # load applied to a node of a node joint -> torque assignment possible
                        hasConstantsTorque = hasConstant(functionsLocal,el.MX,el.MY,el.MZ)
                if hasConstantsForce or hasConstantsTorque:
                    if el.nodalGroupName == "whole mesh":
                        assiStr = "TOUT='OUI',"
                    elif el.loadType == "Force on node":
                        assiStr = "GROUP_NO='" + el.nodalGroupName + "',"
                    else:
                        assiStr = "GROUP_MA='" + el.nodalGroupName + "',"
                    tempStr = "_F(" + assiStr
                    if hasConstant(functionsLocal,el.FX):
                        tempStr = tempStr + "FX=" + el.FX + ","
                    if hasConstant(functionsLocal,el.FY):
                        tempStr = tempStr + "FY=" + el.FY + ","
                    if hasConstant(functionsLocal,el.FZ):
                        tempStr = tempStr + "FZ=" + el.FZ + ","
                    if hasConstantsTorque:
                        if hasConstant(functionsLocal,el.MX):
                            tempStr = tempStr + "MX=" + el.MX + ","
                        if hasConstant(functionsLocal,el.MY):
                            tempStr = tempStr + "MY=" + gel.MY + ","
                        if hasConstant(functionsLocal,el.MZ):
                            tempStr = tempStr + "MZ=" + el.MZ + ","
                    tempStr = tempStr + ")," + ls
                    if el.loadType == "Force on volume":
                        forceOnVolumeStr = forceOnVolumeStr + tempStr
                    elif el.loadType == "Force on face":
                        forceOnFaceStr = forceOnFaceStr + tempStr
                    elif el.loadType == "Force on edge":
                        forceOnEdgeStr = forceOnEdgeStr + tempStr
                    elif el.loadType == "Force on node":
                        forceOnNodeStr = forceOnNodeStr + tempStr
            # pressures
            if el.loadType == "Pressure":
                if hasConstant(functionsLocal,el.p):
                    pressureStr = pressureStr + "_F(GROUP_MA='" + el.nodalGroupName + "',PRES=" + el.p + ",)," + ls
            # gravity
            if el.loadType == "Gravity":
                g = (float(el.gX)**2+float(el.gY)**2+float(el.gZ)**2)**0.5
                dirStr = "(" + str(float(el.gX)/g) + "," + str(float(el.gY)/g) + "," + str(float(el.gZ)/g) + ",)"
                if el.nodalGroupName == "whole mesh":
                    assiStr = ""
                else:
                    assiStr = "GROUP_MA='" + el.nodalGroupName + "',"
                gravityStr = gravityStr + "_F(" + assiStr + "GRAVITE=" + str(g) + ",DIRECTION=" + dirStr + ",)," + ls
            # centrifugal forces
            if el.loadType == "Centrifugal force":
                if el.nodalGroupName == "whole mesh":
                    assiStr = "TOUT='OUI',"
                else:
                    assiStr = "GROUP_MA='" + el.nodalGroupName + "',"
                centrifugalForceStr = centrifugalForceStr + "_F(" + assiStr + "VITESSE=" + el.omega + ",AXE=(" + \
                el.axisX + "," + el.axisY + "," + el.axisZ + ",),CENTRE=(" + el.centerX + "," + el.centerY + "," + el.centerZ + ",),)," + ls
        if not nodeJointsStr == "":
            affeCharMecaStr = affeCharMecaStr + "LIAISON_SOLIDE=(" + ls + nodeJointsStr + ")," + ls
        if not forceOnVolumeStr == "":
            affeCharMecaStr = affeCharMecaStr + "FORCE_INTERNE=(" + ls + forceOnVolumeStr + ")," + ls
        if not forceOnFaceStr == "":
            affeCharMecaStr = affeCharMecaStr + "FORCE_FACE=(" + ls + forceOnFaceStr + ")," + ls
        if not forceOnEdgeStr == "":
            affeCharMecaStr = affeCharMecaStr + "FORCE_ARETE=(" + ls + forceOnEdgeStr + ")," + ls
        if not forceOnNodeStr == "":
            affeCharMecaStr = affeCharMecaStr + "FORCE_NODALE=(" + ls + forceOnNodeStr + ")," + ls
        if not pressureStr == "":
            affeCharMecaStr = affeCharMecaStr + "PRES_REP=(" + ls + pressureStr + ")," + ls
        if not gravityStr == "":
            affeCharMecaStr = affeCharMecaStr + "PESANTEUR=(" + ls + gravityStr + ")," + ls
        if not centrifugalForceStr == "":
            affeCharMecaStr = affeCharMecaStr + "ROTATION=(" + ls + centrifugalForceStr + ")," + ls
        if not affeCharMecaStr == "":
            affeCharMecaStr = "# assign constant restraints/loads and node joints" + ls + "CHAR=AFFE_CHAR_MECA(MODELE=MODE," + ls + affeCharMecaStr + ");" + ls + ls
            
        # contact definition
        contactStr = ""
        if self.analysisType == "non-linear static" and len(self.contactSets) > 0:
            contactStr = "# contact definition" + ls +"CONT=DEFI_CONTACT(MODELE=MODE,"
            if self.contactSets[0].globalSettings.formulationType == "discrete":
                contactStr = contactStr + "FORMULATION='DISCRETE',"
            else:
                contactStr = contactStr + "FORMULATION='CONTINUE',ALGO_RESO_CONT='" + self.contactSets[0].globalSettings.contactAlgo + "',"
            if self.contactSets[0].globalSettings.frictionModel == "Coulomb":
                contactStr = contactStr + "FROTTEMENT='COULOMB',"
                if self.contactSets[0].globalSettings.formulationType == "continuous":
                    contactStr = contactStr + "ALGO_RESO_FROT='" + self.contactSets[0].globalSettings.frictionAlgo + "',"
            else:
                contactStr = contactStr + "FROTTEMENT='SANS',"
            contactStr = contactStr + "ZONE="
            for el in self.contactSets:
                contactStr = contactStr  + ls + "_F(GROUP_MA_MAIT='" + el.masterName + "',GROUP_MA_ESCL='" + el.slaveName + "',"
                if el.globalSettings.formulationType == "discrete":
                    contactStr = contactStr + "ALGO_CONT='" + el.contactAlgo + "',"
                    if el.contactAlgo == "PENALISATION":
                        contactStr = contactStr + "E_N=" + el.E_N + ","
                    if el.globalSettings.frictionModel == "Coulomb":
                        contactStr = contactStr + "COULOMB=" + el.fricCoeff + "," + "ALGO_FROT='PENALISATION',E_T=" + el.E_T + ","
                else:
                    if el.globalSettings.frictionModel == "Coulomb":
                        contactStr = contactStr + "COULOMB=" + el.fricCoeff + ","
                contactStr = contactStr + "),"
            contactStr = contactStr + ");" + ls + ls

        # setting up and calling the solver
        if self.analysisType == "linear static":
            # MECA_STATIQUE
            solverStr = "# calling MECA_STATIQUE" + ls + "RESU=MECA_STATIQUE(MODELE=MODE,CHAM_MATER=MATE,"
            if not caraStr == "":
                solverStr = solverStr + "CARA_ELEM=CARA,"
            solverStr = solverStr + "EXCIT=("
            if not affeCharMecaStr == "":
                solverStr = solverStr + "_F(CHARGE=CHAR,"
                if not tListStr == "" and (self.timeRampUp or self.timeRampDown):
                    solverStr = solverStr + "FONC_MULT=SF,),"
                else:
                    solverStr = solverStr + "),"
            if not affeCharMecaFStr == "":
                solverStr = solverStr + "_F(CHARGE=CHARF,"
                if not tListStr == "" and self.timeRampFunc and (self.timeRampUp or self.timeRampDown):
                    solverStr = solverStr + "FONC_MULT=SF,),"
                else:
                    solverStr = solverStr + "),"
            solverStr = solverStr + "),"
            if not tListStr == "":
                solverStr = solverStr + "LIST_INST=TLIST,"
            solverStr = solverStr + "SOLVEUR=_F(METHODE='" + self.method + "',),);" + ls + ls
        else:
            # STAT_NON_LINE
            solverStr = "# calling STAT_NON_LINE" + ls + "RESU=STAT_NON_LINE(MODELE=MODE,CHAM_MATER=MATE,"
            if not caraStr == "":
                solverStr = solverStr + "CARA_ELEM=CARA,"
            solverStr = solverStr + "EXCIT=("
            if not affeCharMecaStr == "":
                solverStr = solverStr + "_F(CHARGE=CHAR,"
                if (self.timeRampUp or self.timeRampDown):
                    solverStr = solverStr + "FONC_MULT=SF,),"
                else:
                    solverStr = solverStr + "),"
            if not affeCharMecaFStr == "":
                solverStr = solverStr + "_F(CHARGE=CHARF,"
                if self.timeRampFunc and (self.timeRampUp or self.timeRampDown):
                    solverStr = solverStr + "FONC_MULT=SF,),"
                else:
                    solverStr = solverStr + "),"
            solverStr = solverStr + "),"
            if not contactStr == "":
                solverStr = solverStr + "CONTACT=CONT," + ls
            if self.strainModel == "Green-Lagrange":
                solverStr = solverStr + "COMPORTEMENT=_F(RELATION='ELAS',DEFORMATION='GROT_GDEP',)," + ls
            solverStr = solverStr + "NEWTON=_F(REAC_ITER=1,),INCREMENT=_F(LIST_INST=TLIST,),CONVERGENCE=_F(ITER_GLOB_MAXI=" + self.maxIter + ",RESI_GLOB_RELA=" + self.resi + \
            "),SOLVEUR=_F(METHODE='" + self.method + "',),);" + ls + ls
            
        # compute quantities from result
        calcChampStr = ""
        if self.outputSet.SIGM + self.outputSet.EPS + self.outputSet.SIEQ + self.outputSet.REAC > 0:
            calcChampStr = "# compute output quantities" + ls + "RESU=CALC_CHAMP(reuse =RESU,RESULTAT=RESU," + ls
        if self.outputSet.SIGM:
            calcChampStr = calcChampStr + "CONTRAINTE=('SIGM_NOEU',)," + ls
        if self.outputSet.EPS:
            if self.strainModel == "Green-Lagrange" and self.analysisType == "non-linear static":
                calcChampStr = calcChampStr + "DEFORMATION=('EPSG_NOEU',)," + ls
            else:
                calcChampStr = calcChampStr + "DEFORMATION=('EPSI_NOEU',)," + ls
        if self.outputSet.SIEQ:
            calcChampStr = calcChampStr + "CRITERES=('SIEQ_NOEU',)," + ls
        if self.outputSet.REAC:
            calcChampStr = calcChampStr + "FORCE=('REAC_NODA',)," + ls
        calcChampStr = calcChampStr + ");" + ls + ls
                
        # estimate error
        erreurStr = ""
        if self.outputSet.ERME:
            erreurStr = "# error estimation a posteriori " + ls + "RESU=CALC_ERREUR(reuse=RESU,RESULTAT=RESU,OPTION=('ERME_ELEM',),);" + ls + ls
        
        # compute reactions at restraints
        reacStr = ""
        if self.outputSet.REAC and len(restraintSetsLocal) > 0:
            reacStr = "# integrate reactions at restraints" + ls + "Reac_Sum=POST_RELEVE_T(ACTION=("
            for el in restraintSetsLocal:
                reacStr = reacStr + "_F(OPERATION='EXTRACTION',INTITULE='" + el.nodalGroupName + \
                "',RESULTAT=RESU,NOM_CHAM='REAC_NODA',GROUP_NO=('" + el.nodalGroupName + "',),RESULTANTE=('DX','DY','DZ',),MOMENT=('DRX','DRY','DRY',)," + \
                "POINT=(" + el.reacMX + "," + el.reacMY + "," + el.reacMZ + ",),),"
            reacStr = reacStr + "),);" + ls + ls + "IMPR_TABLE(TABLE=Reac_Sum,);" + ls + ls
        
        # write the results to file
        writeStr = "# write result to file (mechanical quantities)" + ls + "IMPR_RESU(FORMAT='MED',RESU=_F(RESULTAT=RESU,NOM_CHAM=('DEPL',"
        if self.outputSet.SIGM:
            writeStr = writeStr + "'SIGM_NOEU',"
        if self.outputSet.SIEQ:
            writeStr = writeStr + "'SIEQ_NOEU',"
        if self.outputSet.EPS:
            if self.strainModel == "Green-Lagrange" and self.analysisType == "non-linear static":
                writeStr = writeStr + "'EPSG_NOEU',"
            else:
                writeStr = writeStr + "'EPSI_NOEU',"
        if self.outputSet.REAC:
            writeStr = writeStr + "'REAC_NODA',"
        if self.outputSet.ERME:
            writeStr = writeStr + "'ERME_ELEM',"
        writeStr = writeStr + "),"
        if self.outputSet.nodalGroupName == "whole mesh":
            writeStr = writeStr + "TOUT='OUI',),);" + ls + ls
        else:
            writeStr = writeStr + "GROUP_MA='" + self.outputSet.nodalGroupName + "',),);" + ls + ls
        if self.outputSet.TEMP and len(self.thermalSets) > 0:
            writeStr = writeStr + "# write result to file (temperature)" + ls 
            for el in tempResNames:
                writeStr = writeStr + "IMPR_RESU(FORMAT='MED',RESU=_F(RESULTAT=" + el + ",NOM_CHAM='TEMP',TOUT='OUI',),);" + ls
            writeStr = writeStr + ls

        # FIN statement
        finStr = "FIN();"
        
        # assemble everything
        commStr = pythonFuns + debutStr + tListStr + formuleStr + matDefiStr + meshStr + modelStr + tempFieldStr + tempResStr + matTempAssiStr + caraStr + affeCharMecaFStr + \
        affeCharMecaStr + contactStr + solverStr + calcChampStr + erreurStr + reacStr + writeStr + finStr

        return commStr
