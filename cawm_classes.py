
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


import xml.etree.ElementTree as ET
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
            
class cawmInst:
    
    def __init__(self,solverSet,names,workingDir,studyName):
        self.solverSet = solverSet
        self.names = names
        self.workingDir = workingDir
        self.studyName = studyName
        self.cawmVersion = cawmVersion

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
    def verify(self,names):
        msgs = []
        if not isNumeric(self.material.youngsModulus) or not isNumeric(self.material.poissonRatio):
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
    def verify(self,names):
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
    def verify(self,names):
        msgs = []
        if self.rotMatViaPython:
            if not isNumeric(self.deltaPhiX, self.deltaPhiY, self.deltaPhiZ, self.xTrans, self.yTrans, self.zTrans):
                msgs.append(self.assiName + ": Inputs for the rotational DoFs and the coordinates of the rotation center have to be numeric. (All rotational DoFs have to be restrained).")
        if not isNumeric(self.reacMX, self.reacMY, self.reacMZ):
            msgs.append(self.assiName + ": Inputs for the coordinates for the computation of the torsional reactions are not numeric.")
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
    def verify(self,names):
        msgs = []
        if self.loadType == "Gravity":
            if not isNumeric(self.gX, self.gY, self.gZ):
                msgs.append(self.assiName + ": At least one input for the gravity vector is not numeric.")
            if not [self.nodalGroupName, "Volume"] in [names[i] for i in range(len(names))] and not self.nodalGroupName == "whole mesh":
                msgs.append(self.assiName + ": Load is not assigned to a valid node group.")
        if self.loadType == "Centrifugal Force":
            if not isNumeric(self.omega, self.centerX, self.centerY, self.centerZ, self.axisX, self.axisY, self.axisZ):
                msgs.append(self.assiName + ": At least one input for the rotation is not numeric.")
            if not [self.nodalGroupName, "Volume"] in [names[i] for i in range(len(names))] and not self.nodalGroupName == "whole mesh":
                msgs.append(self.assiName + ": Load is not assigned to a valid node group.")
        if self.loadType == "Force on face":
            if not isNumeric(self.omega, self.FX, self.FY, self.FZ):
                msgs.append(self.assiName + ": At least one input for the force vector is not numeric.")
            if not [self.nodalGroupName, "Surface"] in [names[i] for i in range(len(names))]:
                msgs.append(self.assiName + ": Load is not assigned to a valid node group.")
        if self.loadType == "Force on edge":
            if not isNumeric(self.omega, self.FX, self.FY, self.FZ):
                msgs.append(self.assiName + ": At least one input for the force vector is not numeric.")
            if not [self.nodalGroupName, "Edge"] in [names[i] for i in range(len(names))]:
                msgs.append(self.assiName + ": Load is not assigned to a valid node group.")
        if self.loadType == "Force on node":
            if not isNumeric(self.omega, self.FX, self.FY, self.FZ, self.MX, self.MY, self.MZ):
                msgs.append(self.assiName + ": At least one input for the force or torque vector is not numeric (if this message relates to the torque and the node is not assigned to a node joint group," + \
                " you can disregard this message).")
            if not [self.nodalGroupName, "Vertex/Node"] in [names[i] for i in range(len(names))]:
                msgs.append(self.assiName + ": Load is not assigned to a valid node group.")
        if self.loadType == "Pressure":
            if not isNumeric(self.p):
                msgs.append(self.assiName + ": Input for the pressure is not numeric")
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
    def verify(self,names):
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
    def verify(self,names):
        msgs = []
        if self.assiType == "const":
            if not isNumeric(self.deltaT):
                msgs.append(self.assiName + ": \u0394T is not numeric.")
        else:
            if not isNumeric(self.unite, self.T0):
                msgs.append(self.assiName + ": UNITE or T0 is not numeric.")
        if not [self.nodalGroupName, "Volume"] in [names[i] for i in range(len(names))] and not self.nodalGroupName == "whole mesh":
            msgs.append(self.assiName + ": Temp. field is not assigned to a valid node group.")
        return msgs
        
class OutputSet:
    
    def __init__(self,nodalGroupName,SIGM,SIEQ,EPS,REAC,ERME):
        self.nodalGroupName = nodalGroupName
        self.SIGM = SIGM
        self.SIEQ = SIEQ
        self.EPS = EPS
        self.REAC = REAC
        self.ERME = ERME
        
class SolverSet:
    
    def __init__(self,analysisType,timeSteps,timeRampDown,strainModel,method,resi,maxIter,materialSets,nodeJointSets,restraintSets,loadSets,contactSets,thermalSets,outputSet):
        self.analysisType = analysisType
        self.timeSteps = timeSteps
        self.timeRampDown = timeRampDown
        self.strainModel = strainModel
        self.method = method
        self.resi = resi
        self.maxIter = maxIter
        self.materialSets = materialSets
        self.nodeJointSets = nodeJointSets
        self.restraintSets = restraintSets
        self.loadSets = loadSets
        self.contactSets = contactSets
        self.thermalSets = thermalSets
        self.outputSet = outputSet
    
    # this method will check if relevant inputs are numeric and all assignments to node groups are valid. It will NOT check in anyway if the resulting comm-file will run in code_aster!
    def verify(self,names):
        msgs = []
        if len(self.materialSets) == 0 or len(self.restraintSets) == 0:
            msgs.extend(["The current setup has no material assignments and/or no restraint assignments."])
        for el in self.materialSets + self.nodeJointSets + self.restraintSets + self.loadSets + self.contactSets + self.thermalSets:
            msgs.extend(el.verify(names))
        if not isInteger(self.timeSteps):
            raise ValueError("The number of time steps has to be of type integer.")
        if self.analysisType == "non-linear static":
            if not isInteger(self.maxIter):
                msgs.extend(["The number of max. iterations has to be of type integer."])
            if not isNumeric(self.resi):
                msgs.extend(["Max. relative global residual is not numeric."])
            if int(self.timeSteps) < 1:
                msgs.extend(["A non-linear analysis requires at least one time step."])
        if self.timeRampDown and not int(self.timeSteps) % 2 == 0:
            msgs.extend(["Ramping loads and restraints up AND down requires an even amount of time steps. Otherwise a computation with their max. values will not happen."])
        if self.outputSet.ERME and len(self.nodeJointSets) > 0:
            msgs.extend(["Calculation of the error a posteriori (ERME) with code_aster version < 13.2 can only be performed on the whole mesh. This will not work with the discrete element" + \
            " of a node joint (MODELISATION='DIS_TR')."])
        return msgs
        
    # generate string for comm-file
    def assembleCOMM(self):
        
        pythonFuns = ""
        displXFunNames = []
        displYFunNames = []
        displZFunNames = []
        displFunAssis = []
        for el in self.restraintSets:
            if el.rotMatViaPython:
                # Generic displacement functions for restraints
                pythonFuns = "# Generic translation functions:" + ls + "def translate_X(deltaX,phiY,phiZ,XTrans,YTrans,ZTrans,X,Y,Z):" + ls + \
                "   return deltaX+(X-XTrans)*cos(phiY)+(Z-ZTrans)*sin(phiY)+(X-XTrans)*cos(phiZ)-(Y-YTrans)*sin(phiZ)-2*(X-XTrans)" + ls + ls + \
                "def translate_Y(deltaY,phiX,phiZ,XTrans,YTrans,ZTrans,X,Y,Z):" + ls + \
                "   return deltaY+(Y-YTrans)*cos(phiX)-(Z-ZTrans)*sin(phiX)+(Y-YTrans)*cos(phiZ)+(X-XTrans)*sin(phiZ)-2*(Y-YTrans)" + ls + ls + \
                "def translate_Z(deltaZ,phiX,phiY,XTrans,YTrans,ZTrans,X,Y,Z):" + ls + \
                "   return deltaZ+(Z-ZTrans)*cos(phiX)+(Y-YTrans)*sin(phiX)+(Z-ZTrans)*cos(phiY)-(X-XTrans)*sin(phiY)-2*(Z-ZTrans)" + ls + ls
        
                # Wrapper functions for displacement of single restraints
                pythonFuns = pythonFuns + "# Wrapper functions for displacement of single restraints" + ls
                for el in self.restraintSets:
                    if el.rotMatViaPython:
                        xName = ""
                        yName = ""
                        zName = ""
                        if not el.deltaX == "" or el.rotX:
                            if el.rotX:
                                phiY = str(float(el.deltaPhiY))
                                phiZ = str(float(el.deltaPhiZ))
                            else:
                                phiY = "0.0"
                                phiZ = "0.0"
                            xName = "DX" + str(len(displXFunNames))
                            displXFunNames.append(xName)
                            pythonFuns = pythonFuns + "def " + displXFunNames[-1] + "(X,Y,Z):" + ls + \
                            "    return translate_X("+str(float(el.deltaX))+","+phiY+","+phiZ+","+str(float(el.xTrans)) \
                            +","+str(float(el.yTrans))+","+str(float(el.zTrans))+",X,Y,Z)" + ls + ls
                        if not el.deltaY == "" or el.rotY:
                            if el.rotY:
                                phiX = str(float(el.deltaPhiX))
                                phiZ = str(float(el.deltaPhiZ))
                            else:
                                phiX = "0.0"
                                phiZ = "0.0"
                            yName = "DY" + str(len(displYFunNames))
                            displYFunNames.append(yName)
                            pythonFuns = pythonFuns + "def " + displYFunNames[-1] + "(X,Y,Z):" + ls + \
                            "    return translate_Y("+str(float(el.deltaY))+","+phiX+","+phiZ+","+str(float(el.xTrans)) \
                            +","+str(float(el.yTrans))+","+str(float(el.zTrans))+",X,Y,Z)" + ls + ls
                        if not el.deltaZ == "" or el.rotZ:
                            if el.rotZ:
                                phiX = str(float(el.deltaPhiX))
                                phiY = str(float(el.deltaPhiY))
                            else:
                                phiX = "0.0"
                                phiY = "0.0"
                            zName = "DZ" + str(len(displZFunNames))
                            displZFunNames.append(zName)
                            pythonFuns = pythonFuns + "def " + displZFunNames[-1] + "(X,Y,Z):" + ls + \
                            "    return translate_Z("+str(float(el.deltaZ))+","+phiX+","+phiY+","+str(float(el.xTrans)) \
                            +","+str(float(el.yTrans))+","+str(float(el.zTrans))+",X,Y,Z)" + ls + ls
                        displFunAssis.append([el.nodalGroupName,xName,yName,zName])
                break
                
        # DEBUT statement
        debutStr = ls + "# Start of code_aster commands" + ls + "DEBUT();" + ls + ls
        
        # material definitions
        matDefiStr = "# Material definitions" + ls
        matDefiNames = []
        for el in self.materialSets:
            matDefiNames.append("MA"+str(len(matDefiNames)))
            matDefiStr = matDefiStr + matDefiNames[-1] + "=" + "DEFI_MATERIAU(ELAS=_F(E=" + el.material.youngsModulus + ",NU=" + el.material.poissonRatio + ",RHO=" + el.material.density + \
            ",ALPHA=" + el.material.alpha + ",),);" + ls
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

        # read temperature field from med-file
        thermalResStr = ""
        for el in self.thermalSets:
            if el.assiType == "file":
                thermalResStr = "# read temp. field from med-file" + ls + "ResTher=LIRE_RESU(TYPE_RESU='EVOL_THER',FORMAT='MED'," + \
                "MAILLAGE=" + meshName + "," + ls + "UNITE=" + el.unite + "," + \
                "FORMAT_MED=_F(NOM_CHAM='TEMP',NOM_CHAM_MED='TEMP____TEMP',),TOUT_ORDRE='OUI',);" + ls + ls
                
        # create constant temperature field
        tempFieldStr = ""
        flag=0
        for el in self.thermalSets:
            if el.assiType == "const":
                if not flag:
                    tempFieldStr = tempFieldStr + "temp=CREA_CHAMP(TYPE_CHAM='NOEU_TEMP_R',OPERATION='AFFE',MODELE=MODE,AFFE=(" + ls
                    flag = 1
                tempFieldStr = tempFieldStr + "_F("
                if el.nodalGroupName == "whole mesh":
                    tempFieldStr = tempFieldStr + "TOUT='OUI'"
                else:
                    tempFieldStr = tempFieldStr + "GROUP_MA='" + el.nodalGroupName + "'"
                tempFieldStr = tempFieldStr + ",NOM_CMP='TEMP',VALE=" + el.deltaT + ",),"
        if flag:
            tempFieldStr = tempFieldStr + "),);" + ls + ls
        
        # assign materials and temperature field
        matAssiStr = "# Assign materials and temp. field" + ls + "MATE=AFFE_MATERIAU(MAILLAGE=" + meshName + ",AFFE=(" + ls
        i=0
        for el in self.materialSets:
            matAssiStr = matAssiStr + "_F(" 
            if el.nodalGroupName == "whole mesh":
                matAssiStr = matAssiStr + "TOUT='OUI',"
            else:
                matAssiStr = matAssiStr + "GROUP_MA='" + el.nodalGroupName + "',"
            matAssiStr = matAssiStr + "MATER=" + matDefiNames[i] + ",)," + ls
            i=i+1
        matAssiStr = matAssiStr + "),"
        flag = 0
        for el in self.thermalSets:
            if el.assiType == "file" or el.assiType == "const":
                if not flag:
                    matAssiStr = matAssiStr + "AFFE_VARC=("
                    flag = 1
                matAssiStr = matAssiStr + "_F("
                if el.nodalGroupName == "whole mesh":
                    matAssiStr = matAssiStr + "TOUT='OUI'"
                else:
                    matAssiStr = matAssiStr + "GROUP_MA='" + el.nodalGroupName + "'"
                
                matAssiStr = matAssiStr + ",NOM_VARC='TEMP',"
                if el.assiType == "file":
                    matAssiStr = matAssiStr + "EVOL=ResTher,VALE_REF=" + str(float(el.T0)) + ",)," + ls
                else:
                    matAssiStr = matAssiStr + "CHAM_GD=temp,VALE_REF=0.0,)," + ls
        if flag:
            matAssiStr = matAssiStr + "),"
        matAssiStr = matAssiStr + ");" + ls + ls
        
        # assign properties for node joints
        caraStr = ""
        for el in self.nodeJointSets:
            if caraStr == "":
                caraStr = "# assign properties for node joints" + ls + "CARA=AFFE_CARA_ELEM(MODELE=MODE,DISCRET=("
            caraStr = caraStr + "_F(CARA='K_TR_D_N',GROUP_MA='" + el.nodeName + "',VALE=(" + el.cX + "," + el.cY + "," + el.cZ + \
            "," + el.cPhiX + "," + el.cPhiY + "," + el.cPhiZ + ",),)," + ls
        if not caraStr == "":
            caraStr = caraStr + "),);" + ls + ls
        
        # create formulas for restraints
        formuleStr = ""
        for el in displXFunNames + displYFunNames + displZFunNames:
            formuleStr = formuleStr + el + "F=FORMULE(VALE='" + el + "(X,Y,Z)',NOM_PARA=('X','Y','Z',),);" + ls
        if not formuleStr == "":
            formuleStr = formuleStr + ls
        
        # assign restraints via formulas
        affeCharMecaFStr = ""
        if not formuleStr == "":
            affeCharMecaFStr = "# assign FORMULE restraints" + ls + "CHARF=AFFE_CHAR_MECA_F(MODELE=MODE,DDL_IMPO=("
            for el in displFunAssis:
                if not el[1] + el[2] +  el[3] == "":
                    affeCharMecaFStr = affeCharMecaFStr + "_F(GROUP_NO='" + el[0] + "',"
                    if not el[1] == "":
                        affeCharMecaFStr = affeCharMecaFStr + "DX=" + el[1] + "F,"
                    if not el[2] == "":
                        affeCharMecaFStr = affeCharMecaFStr + "DY=" + el[2] + "F," 
                    if not el[3] == "":
                        affeCharMecaFStr = affeCharMecaFStr + "DZ=" + el[3] + "F,"
                    affeCharMecaFStr = affeCharMecaFStr + ")," + ls
            affeCharMecaFStr = affeCharMecaFStr + "),);" + ls + ls

        # assign remaining restraints, node joints and loads
        affeCharMecaStr = ""
        flag1 = 0
        flag2 = 0
        # restraints
        for el in self.restraintSets:
            if not el.rotMatViaPython:
                if not flag1:
                    affeCharMecaStr = "# assign restraints, loads and node joints" + ls + "CHAR=AFFE_CHAR_MECA(MODELE=MODE," + ls
                    flag1 = 1
                if not flag2:
                    affeCharMecaStr = affeCharMecaStr + "DDL_IMPO=("
                    flag2 = 1
                affeCharMecaStr = affeCharMecaStr + "_F(GROUP_NO='" + el.nodalGroupName + "'"
                if not el.deltaX == "":
                    affeCharMecaStr = affeCharMecaStr + ",DX=" + el.deltaX
                if not el.deltaY == "":
                    affeCharMecaStr = affeCharMecaStr + ",DY=" + el.deltaY
                if not el.deltaZ == "":
                    affeCharMecaStr = affeCharMecaStr + ",DZ=" + el.deltaZ
                for el1 in self.nodeJointSets:
                    if el1.nodeName == el.nodalGroupName:   # restraint applied on a node of a node joint -> rotational DOFs
                        if not el.deltaPhiX == "":
                            affeCharMecaStr = affeCharMecaStr + ",DRX=" + el.deltaPhiX
                        if not el.deltaPhiY == "":
                            affeCharMecaStr = affeCharMecaStr + ",DRY=" + el.deltaPhiY
                        if not el.deltaPhiZ == "":
                            affeCharMecaStr = affeCharMecaStr + ",DRZ=" + el.deltaPhiZ
                        break
                affeCharMecaStr = affeCharMecaStr + ",)," + ls
        if flag2:
            affeCharMecaStr = affeCharMecaStr + ")," + ls
        # node joints
        flag2 = 0
        for el in self.nodeJointSets:
            if not flag1:
                affeCharMecaStr = "# assign restraints, loads and node joints" + ls + "CHAR=AFFE_CHAR_MECA(MODELE=MODE," + ls
                flag1 = 1
            if not flag2:
                affeCharMecaStr = affeCharMecaStr + "LIAISON_SOLIDE=("
                flag2 = 1
            affeCharMecaStr = affeCharMecaStr + "_F(GROUP_NO='" + el.jointGroupName + "',)," + ls
        if flag2:
            affeCharMecaStr = affeCharMecaStr + ")," + ls
        # force on face
        flag2 = 0
        for el in self.loadSets:
            if not flag1:
                affeCharMecaStr = "# assign restraints, loads and node joints" + ls + "CHAR=AFFE_CHAR_MECA(MODELE=MODE," + ls
                flag1 = 1
            if el.loadType == "Force on face":
                if not flag2:
                    affeCharMecaStr = affeCharMecaStr + "FORCE_FACE=("
                    flag2 = 1
                affeCharMecaStr = affeCharMecaStr + "_F(GROUP_MA='" + el.nodalGroupName + "',FX=" + el.FX + ",FY=" + el.FY + ",FZ=" + el.FZ + ",)," + ls
        if flag2:
            affeCharMecaStr = affeCharMecaStr + ")," + ls
        # force on edge
        flag2 = 0
        for el in self.loadSets:
            if el.loadType == "Force on edge":
                if not flag2:
                    affeCharMecaStr = affeCharMecaStr + "FORCE_ARETE=("
                    flag2 = 1
                affeCharMecaStr = affeCharMecaStr + "_F(GROUP_MA='" + el.nodalGroupName + "',FX=" + el.FX + ",FY=" + el.FY + ",FZ=" + el.FZ + ",)," + ls
        if flag2:
            affeCharMecaStr = affeCharMecaStr + ")," + ls
        # force on node
        flag2 = 0
        for el in self.loadSets:
            if el.loadType == "Force on node":
                if not flag2:
                    affeCharMecaStr = affeCharMecaStr + "FORCE_NODALE=("
                    flag2 = 1
                affeCharMecaStr = affeCharMecaStr + "_F(GROUP_NO='" + el.nodalGroupName + "',FX=" + el.FX + ",FY=" + el.FY + ",FZ=" + el.FZ
                if not el.MX + el.MY + el.MZ == "":
                    affeCharMecaStr = affeCharMecaStr + ",MX=" + el.MX + ",MY=" + el.MY + ",MZ=" + el.MZ
                affeCharMecaStr = affeCharMecaStr + ",)," + ls
        if flag2:
            affeCharMecaStr = affeCharMecaStr + ")," + ls
        # pressure
        flag2 = 0
        for el in self.loadSets:
            if el.loadType == "Pressure":
                if not flag2:
                    affeCharMecaStr = affeCharMecaStr + "PRES_REP=("
                    flag2 = 1
                affeCharMecaStr = affeCharMecaStr + "_F(GROUP_MA='" + el.nodalGroupName + "',PRES=" + el.p + ",)," + ls
        if flag2:
            affeCharMecaStr = affeCharMecaStr + ")," + ls
        # gravity
        flag2 = 0
        for el in self.loadSets:
            if el.loadType == "Gravity":
                if not flag2:
                    affeCharMecaStr = affeCharMecaStr + "PESANTEUR=("
                    flag2 = 1
                g = (float(el.gX)**2+float(el.gY)**2+float(el.gZ)**2)**0.5
                dirStr = "(" + str(float(el.gX)/g) + "," + str(float(el.gY)/g) + "," + str(float(el.gZ)/g) + ",)"
                if el.nodalGroupName == "whole mesh":
                    assiStr = ""
                else:
                    assiStr = "GROUP_MA='" + el.nodalGroupName + "',"
                affeCharMecaStr = affeCharMecaStr + "_F(" + assiStr + "GRAVITE=" + str(g) + ",DIRECTION=" + dirStr + ",)," + ls
        if flag2:
            affeCharMecaStr = affeCharMecaStr + ")," + ls
        # centrifugal force
        flag2 = 0
        for el in self.loadSets:
            if el.loadType == "Centrifugal force":
                if not flag2:
                    affeCharMecaStr = affeCharMecaStr + "ROTATION=("
                    flag2 = 1
                if el.nodalGroupName == "whole mesh":
                    assiStr = "TOUT='OUI'"
                else:
                    assiStr = "GROUP_MA='" + el.nodalGroupName + "'"
                affeCharMecaStr = affeCharMecaStr + "_F(" + assiStr + ",VITESSE=" + el.omega + ",AXE=(" + \
                el.axisX + "," + el.axisY + "," + el.axisZ + ",),CENTRE=(" + el.centerX + "," + el.centerY + "," + el.centerZ + ",),)," + ls
        if flag2:
            affeCharMecaStr = affeCharMecaStr + ")," + ls
        if not affeCharMecaStr == "":
            affeCharMecaStr = affeCharMecaStr + ");" + ls + ls
            
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
                    if el.globalSettings.frictionModel == "COULOMB":
                        contactStr = contactStr + "COULOMB=" + el.fricCoeff + "," + "ALGO_FROT='PENALISATION',E_T=" + el.E_T + ","
                else:
                    if el.globalSettings.frictionModel == "Coulomb":
                        contactStr = contactStr + "COULOMB=" + el.fricCoeff + ","
                contactStr = contactStr + "),"
            contactStr = contactStr + ");" + ls + ls

        # list of time steps
        if int(self.timeSteps) > 0:
            tListStr = "# list of time steps" + ls + "TLIST=DEFI_LIST_REEL(DEBUT=0.0,INTERVALLE=_F(JUSQU_A=1.0,NOMBRE=" + self.timeSteps + ",),);" + ls + ls + \
            "SF=DEFI_FONCTION(NOM_PARA='INST',VALE=(0.0 ,0.0 ,"
            if self.timeRampDown == 1:
                tListStr = tListStr + "0.5 ,1.0 ,1.0 ,0.0"
            else:
                tListStr = tListStr + "1.0 ,1.0"
            tListStr = tListStr +  ",),);" + ls + ls
        else:
            tListStr = ""

        # setting up the solver
        if self.analysisType == "linear static":
            # MECA_STATIQUE
            solverStr = "# setting up MECA_STATIQUE" + ls + "RESU=MECA_STATIQUE(MODELE=MODE,CHAM_MATER=MATE,"
            if not caraStr == "":
                solverStr = solverStr + "CARA_ELEM=CARA,"
            solverStr = solverStr + "EXCIT=("
            if not affeCharMecaStr == "":
                solverStr = solverStr + "_F(CHARGE=CHAR,"
                if not tListStr == "":
                    solverStr = solverStr + "FONC_MULT=SF,),"
                else:
                    solverStr = solverStr + "),"
            if not affeCharMecaFStr == "":
                solverStr = solverStr + "_F(CHARGE=CHARF,"
                if not tListStr == "":
                    solverStr = solverStr + "FONC_MULT=SF,),"
                else:
                    solverStr = solverStr + "),"
            solverStr = solverStr + "),"
            if not tListStr == "":
                solverStr = solverStr + "LIST_INST=TLIST,"
            solverStr = solverStr + "SOLVEUR=_F(METHODE='" + self.method + "',),);" + ls + ls
        else:
            # STAT_NON_LINE
            solverStr = "# setting up STAT_NON_LINE" + ls + "RESU=STAT_NON_LINE(MODELE=MODE,CHAM_MATER=MATE,"
            if not caraStr == "":
                solverStr = solverStr + "CARA_ELEM=CARA,"
            solverStr = solverStr + "EXCIT=("
            if not affeCharMecaStr == "":
                solverStr = solverStr + "_F(CHARGE=CHAR,FONC_MULT=SF,),"
            if not affeCharMecaFStr == "":
                solverStr = solverStr + "_F(CHARGE=CHARF,FONC_MULT=SF,),"
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
        if self.outputSet.REAC:
            reacStr = "# integrate reactions at restraints" + ls + "Reac_Sum=POST_RELEVE_T(ACTION=("
            for el in self.restraintSets:
                reacStr = reacStr + "_F(OPERATION='EXTRACTION',INTITULE='" + el.nodalGroupName + \
                "',RESULTAT=RESU,NOM_CHAM='REAC_NODA',GROUP_NO=('" + el.nodalGroupName + "',),RESULTANTE=('DX','DY','DZ',),MOMENT=('DRX','DRY','DRY',)," + \
                "POINT=(" + el.reacMX + "," + el.reacMY + "," + el.reacMZ + ",),),"
            reacStr = reacStr + "),);" + ls + ls + "IMPR_TABLE(TABLE=Reac_Sum,);" + ls + ls
        
        # write the results to file
        writeStr = "# write result to file" + ls + "IMPR_RESU(FORMAT='MED',RESU=_F(RESULTAT=RESU,NOM_CHAM=('DEPL',"
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

        # FIN statement
        finStr = "FIN();"
        
        # assemble everything
        commStr = pythonFuns + debutStr + matDefiStr + meshStr + modelStr + thermalResStr + tempFieldStr + matAssiStr + caraStr + formuleStr + affeCharMecaFStr + \
        affeCharMecaStr + contactStr + tListStr + solverStr + calcChampStr + erreurStr + reacStr + writeStr + finStr

        return commStr