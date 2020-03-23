from __future__ import print_function
import sys
import os
import string
from glob import glob
from subprocess import call
sys.path.extend(['.', '..'])
from pycparser import c_parser, c_ast

#global Variables
gTransitionList = set()
gPlaceList = set()
gArcInList = set()
gArcOutList = set()

PlaceRandom = 0
TransitionRandom = 0
ArcRandom = 0

class PetriNet:
    def __init__(self, name=[]):
        self.name = name
        self.inputPlaces = set()
        self.outputPlaces = set()
              
    def addInputPlace(self, places):
        for place in places:
            self.inputPlaces.add(place)
    
    def addOutputPlace(self, places):
        for place in places:
            self.outputPlaces.add(place)

    def flushOutputList(self):
        # for x in self.outputPlaces:
        self.outputPlaces.clear()
    def flushInputList(self):
        # for x in self.outputPlaces:
        self.inputPlaces.clear()
        
def checktokens(token1, token2):
    if token1.__class__.__name__ == token2.__class__.__name__:
        if token1.__class__.__name == "VariableToken":
            pass
        else:
            if token1.var.type == token2.var.type and token1.var.value == token2.var.value:
                return True
    return False
            
               
class Place:
    def __init__(self, scope = False):
        global PlaceRandom
        global gPlaceList
        PlaceRandom += 1
        self.name = PlaceRandom
        self.inArcsList = []
        self.outArcsList = []
        self.tokenList = []
        self.scope = scope
        self.children = []
        self.parent = None
        gPlaceList.add(self)

    def addToken(self, token):
        self.tokenList.append(token)
    
    def containsToken(self, iden):
        pass
    
    def addChild(self, child):
        if self.scope == True:
            self.children.append(child)
            
    def setParent(self, parent):
        if self.scope == True:
            self.parent = parent
            parent.addChild(self)  

    def addArc(self, arc):
        if arc.type == "out":
            self.inArcsList.append(arc)
        else:
            self.outArcsList.append(arc)
    def addArcs(self, arcs):
        for arc in arcs:
            arc.place = self
            if arc.type == "out":
                self.inArcsList.append(arc)
            else:
                self.outArcsList.append(arc)
    def addTokens(self, tokens):
        for tok in tokens:
            self.addToken(tok)
            
class Transition:
    def __init__(self):
        global gTransitionList;
        global TransitionRandom;
        TransitionRandom += 1
        self.name = TransitionRandom
        self.inputArc = []
        self.outputArc = []
        self.logic = None
        self.transit = []
        gTransitionList.add(self)
        #check the input arcs and fire if satisfies
        
    def addArc(self, arc):
        if arc.type == "in":
            self.inputArc.append(arc)
        elif arc.type == "out":
            self.outputArc.append(arc)
            
    def addLogic(self, typ, operator, left, right):
        self.logic = (left, operator, right, typ)        
                     
    def Fire(self):
        #availabilty of tokens and #check all constraint
        for arc in self.inputArc:
            for ins in arc.inscription:
                for token in arc.place.tokenList:
                    if token.identifier == ins:
                        if arc.constraint[0] == ins:
                            if token.var.value != arc.constraint[1]:
                                result = False
                                break
                        result = True
                        break
                    else:
                        result = False
                if result == False:
                    break
            if result == False:
                break
        #remove input tokens
        for arc in self.inputArc:
            for ins in arc.inscription:
                for token in arc.place.tokenList:
                    if token.identifier == ins:
                        self.transit.append(token)
                        self.arc.place.tokenList.remove(token)
        
        #check all then apply the logic
        expr = ""
        if self.logic.op == "=":
            pass
        elif self.logic.op == "++": 
            pass
        else:
            for token in self.transit:
                if token.identifier == self.logic.left:
                    expr = expr + token.var.value
                    break
            expr = expr + self.logic.op
            for token in self.transit:
                if token.identifier == self.logic.right:
                    expr = expr + token.var.value    
                    break
            result = eval(expr)
            #create token

            #create the output tokens to output places
            for arc in self.outputArc:
                for ins in arc.inscription:
                    for token in arc.place:
                        if token.identifier == ins:
                            arc.place.tokenList.append(token)
                            self.transit.remove(token)

                                
class Arc:
    def __init__(self, typ, place = None, transition = None):
        global ArcRandom
        
        if typ == "in":
            global gArcInList
            gArcInList.add(self)
        else:
            global gArcOutList
            gArcOutList.add(self)

        # gArcInList.add(self)
        ArcRandom += 1
        self.name = ArcRandom
        self.type = typ
        if place != None:
            self.setPlace(place)
        self.inscription = []
        self.constraint = None
        if transition != None:
            self.setTransition(transition)
        
    def setPlace(self, place):
        self.place = place
        place.addArc(self)
        
    def setTransition(self, transition):
        self.transition = transition
        transition.addArc(self)
        
    def addConstraint(self, boolval, iden):
        self.constraint = (iden, boolval)
                    
    def addinscription(self, inscribe):
        self.inscription.append(inscribe)
            
        
        
class Color():
    def __init__(self, typ):
        self.type = typ
        self.color = name
        
    def getType(self):
        return self.type
    
    def getColor(self):
        return self.color
        
    def updateColor(self, color):
        self.color = color
    
    def updateType(self, typ):
        self.type = typ

class Variable:
    def __init__(self, typ, value = 0):
        self.type = typ
        self.value = value
        
    def getType(self):
        return self.type
    
    def getValue(self):
        return self.value
        
    def setValue(self, value):
        self.value = value
    
    def setType(self, typ):
        self.type = typ
        
    def printVar(self):
        temp = "(Type: " + " ".join(self.type)
        temp = temp + ", Value: "
        temp = temp + str(self.value)
        temp = temp + ")"
        return temp
          
class Token():
    def __init__(self):
        pass

class VariableToken(Token):
    def __init__(self, primitivet, value , iden, qual, stor, typ = "IdentifierType", usrdef = "none"):
        var = Variable(primitivet, value)
        self.type = typ
        self.userdefined = usrdef
        self.var = var
        self.identifier = iden
        self.qualifier = qual
        self.storage = stor
        
    def updateValue(self, value):
        self.var.setValue(value)
        
    def printToken(self):
        temp = "VAR_TOKEN (\nType: " + self.type
        temp = temp + "\nUser Defined Iden: "
        temp = temp + self.userdefined
        temp = temp + "\nVariable: "
        temp = temp + self.var.printVar()
        temp = temp + "\nIdentifier: "
        temp = temp + self.identifier
        temp = temp + "\nQualifier: "
        temp = temp + " ".join(self.qualifier)
        temp = temp + "\nStorage: "
        temp = temp + " ".join(self.storage)
        temp = temp + "\n)"
        #print (temp)    
        
class ConstantToken(Token):
    def __init__(self, typ, value):
        var = Variable(typ, value)
        self.var = var
        self.identifier = str(value)
        
    def printToken(self):
        temp = "CONST_TOKEN (\nType: " + self.var.type
        temp = temp + "\nValue: "
        temp = temp + self.var.value
        temp = temp + "\nIdentifier: "
        temp = temp + self.identifier
        temp = temp + "\n)"
        #print (temp)
       
def search(iden, scope):
    temp = False
    place = None
    token = None
    while (temp is False) and (scope is not None):
        for tok in scope.tokenList:
            if tok.identifier == iden:
                place = scope
                token = tok
                temp = True
                break
        scope = scope.parent
    #print ("In SEARCH")
    # token.printToken()
    # sys.exit(0)
    return (place, token)

def Constant(stmt, scope, pred):

    name = "Constant"
    token = ConstantToken(stmt.type, stmt.value)
    token.printToken()
    # print (token.identifier)
    return [name, token]
   

def ID(stmt, scope, pred):
    name = "ID"
    if pred == "Unknown":
        return (name, stmt.name)
    elif pred == "Known":
        return search(stmt.name, scope) 

def Assignment(stmt, scope, pred):
    name = "Assignment"
    lvalue = stmt.lvalue
    rvalue = stmt.rvalue
    op = stmt.op
    petrinet = PetriNet()

    [lplace, ltoken] = globals()[lvalue.__class__.__name__](lvalue, scope, "Known")

    ltoken = ltoken.identifier
    childright = globals()[rvalue.__class__.__name__](rvalue, scope, "Unknown")

    if childright[0] == "Constant":
        rtoken = childright[1]
        rplace = Place(False)
        rplace.addToken(rtoken)
        inputfinalplace = rplace
        rtoken = rtoken.identifier
        petrinet.addInputPlace([rplace])
    elif childright[0] == "ID":
        [rplace, rtoken] = search(childright[1], scope)
        rtoken = rtoken.identifier
        inputfinalplace = Place(False)
        petrinet.addInputPlace([inputfinalplace])
    elif childright[0] == "Petrinet":
        # print (childright[1].inputPlaces)
        petrinet.addInputPlace(childright[1].inputPlaces)
        for p in childright[1].outputPlaces:
            if p.scope == False:
                rplace = p
                break
        rtoken = "#temp"
        
    transition = Transition()
    transition.addLogic(name, op, ltoken, rtoken)

    if childright[0] == "Constant":
        aa = Arc("out", rplace, transition)
        aa.addinscription(rtoken)

    if rplace == lplace:
        inputarcl = Arc("in", lplace, transition)
        inputarcl.addinscription(ltoken)
        inputarcl.addinscription(rtoken)
        
        petrinet.addOutputPlace([lplace])
        outputarcl = Arc("out", lplace, transition)
        outputarcl.addinscription(rtoken)
        outputarcl.addinscription(ltoken)

        inputarcr = Arc("in", inputfinalplace, transition)
    else:
        if rplace.scope == True:

            inputarcl1 = Arc("in", lplace, transition)
            inputarcl1.addinscription(ltoken)
            inputarcl2 = Arc("in", rplace, transition)
            inputarcl2.addinscription(rtoken)
            petrinet.addOutputPlace([lplace])
            petrinet.addOutputPlace([rplace])
            outputarcl1 = Arc("out", lplace, transition)
            outputarcl1.addinscription(ltoken)
            outputarcl2 = Arc("out", rplace, transition)
            outputarcl2.addinscription(rtoken)
           
            inputarcr = Arc("in", inputfinalplace, transition)
        else:
            inputarcl = Arc("in", lplace, transition)
            inputarcl.addinscription(ltoken)
            #rplace.scope == false
            petrinet.addOutputPlace([lplace])
            # petrinet.addOutputPlace([rplace])
            outputarcl = Arc("out", lplace, transition)
            outputarcl.addinscription(ltoken)

            inputarcr = Arc("in", rplace, transition)
            inputarcr.addinscription(rtoken)

    inputarcr.addinscription("#control")
    outputfinal = Place(False)
    petrinet.addOutputPlace([outputfinal])
    outputarcr = Arc("out", outputfinal, transition)
    outputarcr.addinscription("#control")

    return ("Petrinet", petrinet)
    
    #rplace and rtoken 

    #Calculate and update
    # if stmt.op == "=":
    #     ltoken.updateValue(rtoken.var.value) 
    # elif stmt.op == "*=":
    #     ltoken.updateValue(ltoken.var.value * rtoken.var.value)
    # elif stmt.op == "+=":
    #     ltoken.updateValue(ltoken.var.value + rtoken.var.value)
    # elif stmt.op == "-=":
    #     ltoken.updateValue(ltoken.var.value - rtoken.var.value)
    # elif stmt.op == "/=":
    #     ltoken.updateValue(ltoken.var.value / rtoken.var.value)
    # elif stmt.op == "%=":
    #     ltoken.updateValue(ltoken.var.value % rtoken.var.value)
    # elif stmt.op == "&=":
    #     ltoken.updateValue(ltoken.var.value & rtoken.var.value)
    # elif stmt.op == "|=":
    #     ltoken.updateValue(ltoken.var.value | rtoken.var.value)
    # elif stmt.op == "^=":
    #     ltoken.updateValue(ltoken.var.value ^ rtoken.var.value)
    # elif stmt.op == "<<=":
    #     ltoken.updateValue(ltoken.var.value << rtoken.var.value)
    # elif stmt.op == ">>=":
    #     ltoken.updateValue(ltoken.var.value >> rtoken.var.value)

    #print (aa)
    #print (stmt.children())
    
def BinaryOp(stmt, scope, pred):
    name = "BinaryOp"
    petrinet = PetriNet()
    op = stmt.op
    left = stmt.left
    right = stmt.right

    intermediatel = set()
    intermediater = set()

    childleft = globals()[left.__class__.__name__](left, scope, "Unknown")
    childright = globals()[right.__class__.__name__](right, scope, "Unknown")

    rtemp = ltemp = False
    #getting left reference 
    if childleft[0] == "Constant":
        leftu = childleft[1]
        ltoken = childleft[1].identifier
        lplace = Place(False)
        lplace.addToken(childleft[1])
        petrinet.addInputPlace([lplace])
    elif childleft[0] == "ID":
        [lplace, ltoken] = search(childleft[1], scope)#ref of the scope containing the token
        leftu = ltoken
        ltoken = ltoken.identifier
        petrinet.addInputPlace([lplace])
    elif childleft[0] == "Petrinet":
        petrinet.addInputPlace(childleft[1].inputPlaces)
        # petrinet.inputPlaces.add(inp)
        for out in childleft[1].outputPlaces:
            intermediatel.add(out)
            if out.scope == False:
                lplace = out
                ltoken = "#temp"
                ltemp = True

    #getting right reference
    if childright[0] == "Constant":
        rtoken = childright[1].identifier
        if childleft[0] == "Constant":
            rplace = lplace
        else:
            rplace = Place()
            petrinet.addInputPlace([rplace])
        rplace.addToken(childright[1])
        rightu = childright[1]
    elif childright[0] == "ID":
        [rplace, rtoken] = search(childright[1], scope)#ref of the scope containing the token
        rightu = rtoken
        rtoken = rtoken.identifier
        petrinet.addInputPlace([rplace])
    elif childright[0] == "Petrinet":
        petrinet.addInputPlace(childright[1].inputPlaces)
        for out in childright[1].outputPlaces:
            intermediater.add(out)
            if out.scope == False:
                rplace = out
                rtoken = "#temp"
                rtemp = True

    
    if rtemp == True and ltemp == True:
        rtoken = rtoken + "r"
        ltoken = ltoken + "l"
    #create transition
    transition = Transition()
    transition.addLogic(name, op, ltoken, rtoken)
    #create output arcs and link to transition and places
    outplace = Place()
    outputarcfinal = Arc("out", outplace, transition)
    outputarcfinal.addinscription("#control")
    outputarcfinal.addinscription("#temp")
    petrinet.addOutputPlace([outplace])

    

    #create input arcs and link to places and transition
    if lplace == rplace:
        # petrinet.addInputPlace(inputplace)
        inputarc = Arc("in", lplace, transition)
        # inputarc.addinscription(ltoken)
        # inputarc.addinscription(rtoken)
        if leftu == rightu:
            inputarc.addinscription(ltoken)
        else:
            inputarc.addinscription(ltoken)
            inputarc.addinscription(rtoken)

        # petrinet.addInputPlace([lplace])

        if lplace.scope == True:
            # print ("YOOOOOOOOOOOOOOOOO")
            inputplace = Place()
            petrinet.addInputPlace([inputplace])
            inputarcfinal = Arc("in", inputplace, transition)
            inputarcfinal.addinscription("#control")

            # petrinet.addOutputPlace([outplace])
            outputarc = Arc("out", lplace, transition)
            if leftu == rightu:
                outputarc.addinscription(ltoken)
            else:
                outputarc.addinscription(ltoken)
                outputarc.addinscription(rtoken)
            # outputarcfinal = Arc("out", outplace, transition)
            # outputarcfinal.addinscription("#control")

            petrinet.addOutputPlace([lplace])
        else:
            if childleft[0] == "Constant" and childright[0] == "Constant":
                aa = Arc("out", lplace, transition)
                if leftu == rightu:
                    outputarc.addinscription(ltoken)
                else:
                    outputarc.addinscription(ltoken)
                    outputarc.addinscription(rtoken)
    else:
        inputarcl = Arc("in", lplace, transition)
        inputarcl.addinscription(ltoken)
        inputarcr = Arc("in", rplace, transition)
        inputarcr.addinscription(rtoken)

        #rejuvating the constant tokens
        if childleft[0] == "Constant":
            aa = Arc("out", lplace, transition)
            aa.addinscription(ltoken)
        if childright[0] == "Constant":
            aa = Arc("out", rplace, transition)
            aa.addinscription(rtoken)

        if lplace.scope == True and rplace.scope == True:
            inputplace = Place(False)
            petrinet.addInputPlace([inputplace])
            inputarcfinal = Arc("in", inputplace, transition)
            inputarcfinal.addinscription("#control")

            petrinet.addOutputPlace([lplace])
            petrinet.addOutputPlace([rplace])
            outputarcl = Arc("out", lplace, transition)
            outputarcl.addinscription(ltoken)
            outputarcr = Arc("out", rplace, transition)
            outputarcr.addinscription(rtoken)
        elif lplace.scope == False and rplace.scope == True:
            inputarcl.addinscription("#control")
            
            petrinet.addOutputPlace([rplace])
            outputarcr = Arc("out", rplace, transition)
            outputarcr.addinscription(rtoken)
        elif lplace.scope == True and rplace.scope == False:
            inputarcr.addinscription("#control")
            
            petrinet.addOutputPlace([lplace])
            outputarcl = Arc("out", lplace, transition)
            outputarcl.addinscription(ltoken)
        else:            
            if rtemp == True and ltemp == True:
                inputarcl.addinscription("#control")
                inputarcr.addinscription("#control")
                temp = True
                for arc in inputarcl.place.inArcsList:
                    for i in range(0, len(arc.inscription)):
                        if arc.inscription[i] == "#temp":
                            ltransition = arc.transition
                            arc.inscription[i] = arc.inscription[i]  + "l"
                            temp = False
                            break
                    if temp == False:
                        break
                temp = True
                for arc in inputarcr.place.inArcsList:
                    for i in  range(0, len(arc.inscription)):
                        if arc.inscription[i] == "#temp":
                            rtransition = arc.transition
                            arc.inscription[i] = arc.inscription[i]  + "r"
                            temp = False
                            break
                    if temp == False:
                        break
            else:
                inputarcl.addinscription("#control")
                # gArcInList.remove(inputarcr)
                for ins in inputarcr.inscription:
                    inputarcl.addinscription(ins)
                gArcInList.remove(inputarcr)
                del inputarcr
                petrinet.inputPlaces.remove(rplace)
                placemerge(lplace, rplace)
    
    return ("Petrinet", petrinet)

def TernaryOp():
    pass

def UnaryOp():
    pass

def Compound(block, scope, pred):
    name = "Compound"
    petrinet = PetriNet()
    if block.block_items.__class__.__name__ == "NoneType":
        return ("Petrinet", petrinet)
    prevpetrinet = None
    for stmt in block.block_items:
        #print (stmt.__class__.__name__)
        newpetrinet = globals()[stmt.__class__.__name__](stmt, scope, name)
        # sys.exit(0)
        if newpetrinet == None:
            continue
        if prevpetrinet == None:
            for place in newpetrinet[1].inputPlaces:
                if place.scope == False:
                    #add control token
                    controltok = ConstantToken("char", "#control")
                    place.addToken(controltok)
                    # break
            petrinet = newpetrinet[1]
            prevpetrinet = newpetrinet[1]
        else:
            outputplaces = []
            for place in newpetrinet[1].inputPlaces:  
                if place.scope == False:
                    outputplaces.append(place)
            # transition = Transition()
            # inputplaces = []
            for place in petrinet.outputPlaces:
                if place.scope == False:
                    inputplace = place 
                    break
            # print/ ("LENGTH: ",len(outputplaces))
            if len(outputplaces) > 1:
                # pnwp  = Place(False)
                # print ("NAME: ",pnwp.name)
                inmerge(outputplaces, inputplace)
                # placemerge(inputplace, pnwp)
            else:
                placemerge(inputplace, outputplaces[0])
            # placemerge()
            petrinet.flushOutputList()
            petrinet.addOutputPlace(newpetrinet[1].outputPlaces)

    return ("Petrinet", petrinet)

# def placeconsistency(place):
#     #output
#     for arc in place.inArcsList:
#         if arc.

def placemerge(place1, place2):
    global gPlaceList
    place1.addTokens(place2.tokenList)
    place1.addArcs(place2.outArcsList)
    place1.addArcs(place2.inArcsList)


    # for tok in place2.tokenList:
    gPlaceList.remove(place2)
    del place2
    place2 = place1
    # place1.addArcs(place2.inputArcList)
    #arcstransfer

    return place1

def inmerge(OutputPlaces, inputplace):
    places = []
    for place in OutputPlaces:
        if place.scope == False:
            places.append(place)
    transition = Transition()
    for outplace in places:
        outarc = Arc('out', outplace, transition)
        outarc.addinscription("#control")
    outarc = Arc('in', inputplace, transition)
    outarc.addinscription("#control")

def merge(OutputPlaces, outfinalplace):
    places = []
    for place in OutputPlaces:
        if place.scope == False:
            places.append(place)
    transition = Transition()
    for outplace in places:
        outarc = Arc('in', outplace, transition)
        outarc.addinscription("#control")
    outarc = Arc('out', outfinalplace, transition)
    outarc.addinscription("#control")

def ExprList(exps, scope, pred):
    name = "ExprList"
    petrinet = PetriNet()
    prevpetrinet = None
    
    for stmt in exps.exprs:
        newpetrinet = globals()[stmt.__class__.__name__](stmt, scope, "Unknown")
        if newpetrinet[0] == "Petrinet":
            if prevpetrinet == None:
                petrinet = newpetrinet[1]
                prevpetrinet = newpetrinet
            else:
                for place in newpetrinet[1].inputPlaces:  
                    if place.scope == False:
                        outputplace = place
                for place in petrinet.outputPlaces:
                    if place.scope == False:
                        inputplace = place 
                        break
                placemerge(inputplace, outputplace)
                petrinet.flushOutputList()
            petrinet.addOutputPlace(newpetrinet[1].outputPlaces)

    if newpetrinet[0] == "Petrinet":
        return ("Petrinet", petrinet)
    else:
        return (newpetrinet, petrinet)
       
def DeclList(decls, scope, pred):
    name = "DeclList"
    # petrinet = PetriNet()
    for stmt in decls.decls:
        child = globals()[stmt.__class__.__name__](stmt, scope, "Unknown")

    return None

def For(stmt, scope, pred):
    # print ("For1")
    # print ("Forrr")
    name = "For"
    # petrinetb = PetriNet()
    petrinet = PetriNet()

    init = stmt.init
    cond = stmt.cond
    nex = stmt.next
    com = stmt.stmt

    newscope = Place(True)
    newscope.setParent(scope)

    # An init petri
    childinit = ifplace = iftoken = ifplace1 = ifplace2 = startplace = None
    
    if init.__class__.__name__ != "NoneType":
        childinit = globals()[init.__class__.__name__](init, newscope, "Unknown")
        if childinit != None:
            ifplace2 = FindFalsePlace(childinit[1], "out")

    # sys.exit(0)
    if cond.__class__.__name__ != "NoneType":
        child = globals()[cond.__class__.__name__](cond, newscope, "Unknown")
        if cond.__class__.__name__ == "ExprList":
            startplace = FindFalsePlace(child[1], "in")
            if child[0] != "Petrinet":
                ifplace1 = FindFalsePlace(child[1], "out")
                child = child[0]

        if child[0] == "Constant":
            inputplace = Place(False)
            inputplace.addToken(child[1])
            ifplace = inputplace
            iftoken = child[1].identifier
            if startplace == None:
                startplace = ifplace
        elif child[0] == "ID":
            [ifplace, iftoken] = search(child[1], newscope)
            if startplace == None:
                startplace = ifplace
            iftoken = iftoken.identifier
        elif child[0] == "Petrinet":
            if startplace == None:
                startplace = FindFalsePlace(child[1], "in")
            ifplace = FindFalsePlace(child[1], "out")
            iftoken = None
            for arc in ifplace.inArcsList:
                for ins in arc.inscription:
                    if ins == "#temp":
                        iftoken = "#temp"
                        break

            assignment_operators = ['=', '+=', "-=", '*=', "/=", "%="]
            if iftoken == None:
            # trans = ifplace
                for ki in range(0, len(ifplace.inArcsList)):
                    tran = ifplace.inArcsList[ki].transition
                    if tran.logic[1] in assignment_operators:
                        iftoken = tran.logic[0]
                        break
        if ifplace1 != None and ifplace.scope == False and ifplace1.scope == False:
            placemerge(ifplace, ifplace1)
        # if childinit != None:
        #     placemerge(startplace, ifplace2)
        petrinet.addInputPlace([ifplace])
            
    check = False
    if iftoken != None:
        outplace = Place(False)
        transition = Transition()
        transition.addLogic("BinaryOp", "!=", iftoken, "0")
        #add input arcs
        # petrinet.addInputPlace([iftoken])
        inarc = Arc('in', ifplace, transition)
        inarc.addinscription(iftoken)
        # inarc.addinscription("#control")
        if ifplace.scope == True:
            nplace = Place(False)
            petrinet.addInputPlace([nplace])
            inarc = Arc('in', nplace, transition)
            inarc.addinscription("#control")
            if startplace == None:
                startplace = nplace
            if ifplace1 != None:
                placemerge(nplace, ifplace1)
        else:
            inarc.addinscription("#control")
            # if ifplace1 != None:
            #     placemerge(ifplace, ifplace1)

        #add output arcs
        outarc = Arc('out', outplace, transition)
        outarc.addinscription("#control")
        outarc.addinscription('#temp')
        if child[0] != "Petrinet":
            outarc = Arc('out', ifplace, transition)
            outarc.addinscription(iftoken)
    else:
        if ifplace == None:
            ifplace = Place(False)
        if startplace == None:
            startplace = ifplace
        outplace = ifplace
        ttok = ConstantToken("int", "1")
        outplace.addToken(ttok)
        check = True


    #the body of the while loop
    if ifplace2 != None:
        placemerge(startplace, ifplace2)
    transition1 = Transition()
    inarc1 = Arc('in', outplace, transition1)
    inarc1.addinscription('#temp')
    inarc1.addinscription('#control')
    inarc1.addConstraint("1", "#temp")

    if check == True:
        outar = Arc("out", outplace, transition1)
        outar.addinscription("#temp")

    childt = globals()[com.__class__.__name__](com, newscope, name)

    if len(childt[1].inputPlaces) != 0:
        places = []
        for place in childt[1].inputPlaces:
            if place.scope == False:
                places.append(place)
        for outplace1 in places:
            outarc1 = Arc('out', outplace1, transition1)
            outarc1.addinscription("#control")
        OutputPlaces = childt[1].outputPlaces
    else:
        outplace1 = Place(False)
        OutputPlaces = [outplace1]
        outarc1 = Arc('out', outplace1, transition1)
        outarc1.addinscription("#control")
    
    if nex.__class__.__name__ != "NoneType":
        childnex = globals()[nex.__class__.__name__](nex, scope, "Unknown")
        inplace1 = FindFalsePlace(childnex[1], "in")
        merge(OutputPlaces, inplace1)
        outplace1 = FindFalsePlace(childnex[1], "out")
        # placemerge(outplace1, inplace1)
        merge([outplace1], startplace)
    else:
        merge(OutputPlaces, startplace)

    outfinalplace = Place(False)
    petrinet.addOutputPlace([outfinalplace])
    
    # the false part of the while loop
    transition2 = Transition()
    inarc2 = Arc('in', outplace, transition2)
    inarc2.addinscription('#temp')
    inarc2.addinscription('#control')
    inarc2.addConstraint("0", "#temp")
    outarc2 = Arc("out", outfinalplace, transition2)
    outarc2.addinscription("#control")

    if ifplace1 != None:
        petrinet.flushInputList()
        petrinet.addInputPlace(childinit[1].inputPlaces)

    return ("Petrinet", petrinet)

def While(stmt, scope, pred):
    name = "While"
    petrinet = PetriNet()
    cond = stmt.cond
    com = stmt.stmt

    ifplace1 = None
    if cond.__class__.__name__ == "ExprList":
        child = globals()[cond.__class__.__name__](cond, scope, "Unknown")
        startplace = FindFalsePlace(child[1], "in")
        if child[0] != "Petrinet":
            ifplace1 = FindFalsePlace(child[1], "out")
            child = child[0]
    else:
        child = globals()[cond.__class__.__name__](cond, scope, "Unknown")
        startplace = None

    if child[0] == "Constant":
        inputplace = Place(False)
        inputplace.addToken(child[1])
        ifplace = inputplace
        iftoken = child[1].identifier
        if startplace == None:
            startplace = ifplace
    elif child[0] == "ID":
        [ifplace, iftoken] = search(child[1], scope)
        if startplace == None:
            startplace = ifplace
        iftoken = iftoken.identifier
    elif child[0] == "Petrinet":
        if startplace == None:
            startplace = FindFalsePlace(child[1], "in")
        ifplace = FindFalsePlace(child[1], "out")

        iftoken = None
        for arc in ifplace.inArcsList:
            for ins in arc.inscription:
                if ins == "#temp":
                    iftoken = "#temp"
                    break

        assignment_operators = ['=', '+=', "-=", '*=', "/=", "%="]
        if iftoken == None:
        # trans = ifplace
            for ki in range(0, len(ifplace.inArcsList)):
                tran = ifplace.inArcsList[ki].transition
                if tran.logic[1] in assignment_operators:
                    iftoken = tran.logic[0]
                    break

    if ifplace1 != None and ifplace.scope == False and ifplace1.scope == False:
        placemerge(ifplace, ifplace1)

    petrinet.addInputPlace([ifplace])
        # if iftoken != None:
    outplace = Place(False)
    check = False
    if iftoken != None:
        transition = Transition()
        transition.addLogic("BinaryOp", "!=", iftoken, "0")
        #add input arcs
        # petrinet.addInputPlace([iftoken])
        inarc = Arc('in', ifplace, transition)
        inarc.addinscription(iftoken)
        # inarc.addinscription("#control")
        if ifplace.scope == True:
            nplace = Place(False)
            petrinet.addInputPlace([nplace])
            inarc = Arc('in', nplace, transition)
            inarc.addinscription("#control")
            if startplace == None:
                startplace = nplace
            if ifplace1 != None:
                placemerge(nplace, ifplace1)
        else:
            inarc.addinscription("#control")

        #add output arcs
        outarc = Arc('out', outplace, transition)
        outarc.addinscription("#control")
        outarc.addinscription('#temp')
        if child[0] != "Petrinet":
            outarc = Arc('out', ifplace, transition)
            outarc.addinscription(iftoken)
    else:
        outplace = ifplace
        ttok = ConstantToken("int", "1")
        outplace.addToken(ttok)
        check = True

    #the body of the while loop
    transition1 = Transition()
    inarc1 = Arc('in', outplace, transition1)
    inarc1.addinscription('#temp')
    inarc1.addinscription('#control')
    inarc1.addConstraint("1", "#temp")

    if check == True:
        outar = Arc("out", outplace, transition1)
        outar.addinscription("#temp")
    #new while scope
    newscope1 = Place(True)
    newscope1.setParent(scope)

    childt = globals()[com.__class__.__name__](com, newscope1, name)

    if len(childt[1].inputPlaces) != 0:
        # print ("YAAAAAAA")
        places = []
        for place in childt[1].inputPlaces:
            if place.scope == False:
                places.append(place)
        for outplace1 in places:
            outarc1 = Arc('out', outplace1, transition1)
            outarc1.addinscription("#control")
        OutputPlaces = childt[1].outputPlaces
    else:
        outplace1 = Place(False)
        OutputPlaces = [outplace1]
        outarc1 = Arc('out', outplace1, transition1)
        outarc1.addinscription("#control")
    merge(OutputPlaces, startplace)


    outfinalplace = Place(False)
    petrinet.addOutputPlace([outfinalplace])
    
    # the false part of the while loop
    transition2 = Transition()
    inarc2 = Arc('in', outplace, transition2)
    inarc2.addinscription('#temp')
    inarc2.addinscription('#control')
    inarc2.addConstraint("0", "#temp")
    outarc2 = Arc("out", outfinalplace, transition2)
    outarc2.addinscription("#control")
    return ("Petrinet", petrinet)

def FindFalsePlace(petrinet, where):
    if where == "in":
        for place in petrinet.inputPlaces:
            if place.scope == False:
                return place 
    else:
        for place in petrinet.outputPlaces:
            if place.scope == False:
                return place 
    return None

def If(stmt, scope, pred):
    name = "If"
    petrinet = PetriNet()
    cond = stmt.cond
    iftrue = stmt.iftrue
    iffalse = stmt.iffalse

    ifplace1 = None
    if cond.__class__.__name__ == "ExprList":
        child = globals()[cond.__class__.__name__](cond, scope, "Unknown")
        if child[0] == "Petrinet":
            pass
        else:
            ifplace1 = FindFalsePlace(child[1], "out")
            child = child[0]
    else:
        child = globals()[cond.__class__.__name__](cond, scope, "Unknown")

    if child[0] == "Constant":
        inputplace = Place(False)
        inputplace.addToken(child[1])
        ifplace = inputplace
        iftoken = child[1].identifier
    elif child[0] == "ID":
        [ifplace, iftoken] = search(child[1], scope)
        iftoken = iftoken.identifier
    elif child[0] == "Petrinet":
        # for place in child[1].outputPlaces:
        #     if place.scope == False:
        #         ifplace = place
        ifplace = FindFalsePlace(child[1], "out")
        iftoken = None
        for arc in ifplace.inArcsList:
            for ins in arc.inscription:
                if ins == "#temp":
                    iftoken = "#temp"
                    break
        
        # if iftoken is None then it would have been an assignment statement
        assignment_operators = ['=', '+=', "-=", '*=', "/=", "%="]
        if iftoken == None:
            # trans = ifplace
            for ki in range(0, len(ifplace.inArcsList)):
                tran = ifplace.inArcsList[ki].transition
                if tran.logic[1] in assignment_operators:
                    iftoken = tran.logic[0]
                    break

    if ifplace1 != None and ifplace.scope == False and ifplace1.scope == False:
        placemerge(ifplace, ifplace1)
    petrinet.addInputPlace([ifplace])
        # if iftoken != None:
    outplace = Place(False)
    check = False
    if iftoken != None:
        transition = Transition()
        transition.addLogic("BinaryOp", "!=", iftoken, "0")
        #add input arcs
        # petrinet.addInputPlace([iftoken])
        inarc = Arc('in', ifplace, transition)
        inarc.addinscription(iftoken)
        # inarc.addinscription("#control")
        if ifplace.scope == True:
            nplace = Place(False)
            petrinet.addInputPlace([nplace])
            inarc = Arc('in', nplace, transition)
            inarc.addinscription("#control")
            if ifplace1 != None:
                placemerge(nplace, ifplace1)
        else:
            inarc.addinscription("#control")

            # inarc.addinscription(iftoken)

        #add output arcs
        outarc = Arc('out', outplace, transition)
        outarc.addinscription("#control")
        outarc.addinscription('#temp')
        if child[0] != "Petrinet":
            outarc = Arc('out', ifplace, transition)
            outarc.addinscription(iftoken)
    else:
        outplace = ifplace
        ttok = ConstantToken("int", "1")
        outplace.addToken(ttok)
        check = True

    outfinalplace = Place(False)
    petrinet.addOutputPlace([outfinalplace])

    if iftrue.__class__.__name__ != "NoneType":
        transition1 = Transition()
        inarc1 = Arc('in', outplace, transition1)
        inarc1.addinscription('#temp')
        inarc1.addinscription('#control')
        inarc1.addConstraint("1", "#temp")

        if check == True:
            outar = Arc("out", outplace, transition1)
            outar.addinscription("#temp")
        # print (inarc1.constraint[0] + " " + inarc1.constraint[1])
        #new if scope
        newscope1 = Place(True)
        newscope1.setParent(scope)

        childt = globals()[iftrue.__class__.__name__](iftrue, newscope1, name)

        if len(childt[1].inputPlaces) != 0:
            # print ("YAAAAAAA")
            places = []
            for place in childt[1].inputPlaces:
                if place.scope == False:
                    places.append(place)
            for outplace1 in places:
                outarc1 = Arc('out', outplace1, transition1)
                outarc1.addinscription("#control")
            OutputPlaces = childt[1].outputPlaces
        else:
            outplace1 = Place(False)
            OutputPlaces = [outplace1]
            outarc1 = Arc('out', outplace1, transition1)
            outarc1.addinscription("#control")
        merge(OutputPlaces, outfinalplace)

    if iffalse.__class__.__name__ != "NoneType" and check == False:
        transition2 = Transition()
        inarc1 = Arc('in', outplace, transition2)
        inarc1.addinscription('#temp')
        inarc1.addinscription('#control')
        inarc1.addConstraint("0", "#temp")
        
        #new else scope
        newscope2 = Place(True)
        newscope2.setParent(scope)
        childf = globals()[iffalse.__class__.__name__](iffalse, newscope2, name)

        if len(childf[1].inputPlaces) != 0:
            # print ("NOOOOOOOOOO")
            places = []
            for place in childf[1].inputPlaces:
                if place.scope == False:
                    places.append(place)
            for outplace2 in places:
                outarc2 = Arc('out', outplace2, transition2)
                outarc2.addinscription("#control")

            OutputPlaces = childf[1].outputPlaces
            # petrinet.addOutputPlace(childf[1].outputPlaces)
        else:
            outplace2 = Place(False)
            OutputPlaces = [outplace2]
            outarc2 = Arc('out', outplace2, transition2)
            outarc2.addinscription("#control")
            # petrinet.addOutputPlace([outplace2])
        merge(OutputPlaces, outfinalplace)
        
    elif check == False:
        transition2 = Transition()
        inarc1 = Arc('in', outplace, transition2)
        inarc1.addinscription('#temp')
        inarc1.addinscription('#control')
        inarc1.addConstraint("0", "#temp")
        # outplace2 = Place(False)
        outarc2 = Arc('out', outfinalplace, transition2)
        outarc2.addinscription("#control")
        # petrinet.addOutputPlace([outplace2])
        # OutputPlaces = [outplace2]
        # merge(OutputPlaces, outfinalplace)
    elif check == True:
        pass
    return ("Petrinet", petrinet)

def IdentifierType(stmt, scope, pred):
    name = "IdentifierType"
    return stmt.names

def TypeDecl(stmt, scope, pred):
    name = "TypeDecl"
    dec = stmt.type
    return globals()[dec.__class__.__name__](dec, scope, name)

def ParamList(stmt, scope, pred):
    name = "ParamList"
    for decl in stmt.block_items:
        primitivetype = globals()[decl.__class__.__name__](decl, scope, name)
    # sys.exit(0)
    return None

def FuncDecl(stmt, scope, pred):
    name = "FuncDecl"
    args = stmt.args
    dec = stmt.type

    if args.__class__.__name__ != "NoneType":
        globals()[dec.__class__.__name__](dec, scope, name)

    # newtoken = VariableToken(primitivetype, 0, iden, quals, storage) 
    # newtoken.printToken()        
    
    # if init.__class__.__name__ != "NoneType":
    #     newtoken.updateValue(init.value) 
    #     newtoken.printToken()             
    #     #assign the value of token
    # scope.addToken(newtoken)   
    return None

def Decl(stmt, scope, pred):
    name = "Decl"
    iden = stmt.name
    quals = stmt.quals
    storage = stmt.storage
    
    dec = stmt.type
    init = stmt.init

    primitivetype = globals()[dec.__class__.__name__](dec, scope, name)

    if pred == "FuncDef":
        return None
    newtoken = VariableToken(primitivetype, 0, iden, quals, storage) 
    #newtoken.printToken()        
    
    if init.__class__.__name__ != "NoneType":
        newtoken.updateValue(init.value) 
        #newtoken.printToken()             
        #assign the value of token
    scope.addToken(newtoken)   
    return None

def FuncDef(func, scope_par, pred):
    name = "FuncDef"
    # petrinet = PetriNet(func.decl.name)
    #print (func.body.children())
    decl = func.decl
    com = func.body

    scope = Place(True)
    scope.setParent(scope_par)
    childDecl = globals()[decl.__class__.__name__](decl, scope, name)
    child = globals()[com.__class__.__name__](com, scope, name)
    
    return ("Petrinet", child[1]) 
        # elif name == "Switch":
        #     print ()
        # elif name == "DoWhile":
        #     print ()
        # elif name == "Continue":
        #     print ()
        # elif name == "Break":
        #     print ()
        # elif name == "Case":
        #     print ()
        # elif name == "Default":
        #     print ()
        # elif name == "UnaryOp":
        #     print ()

def GenerateXML(filename, directory):
    global gArcInList
    global gArcOutList
    global gTransitionList
    global gPlaceList

    filename = "out-" + filename
    filename = filename.replace(".c", ".xml")
    direct = directory + '/'
    direct = direct + filename
    fptr = open(direct, "w")

    fptr.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n")
    
    #Places with tokens
    fptr.write("<places>\n")
    for place in gPlaceList:
        fptr.write("\t<place>\n")
        fptr.write("\t\t<name>")
        fptr.write(str(place.name))
        fptr.write("</name>\n")
        fptr.write("\t\t<scope>")
        fptr.write(str(place.scope))
        fptr.write("</scope>\n")
        fptr.write("\t\t<parent>")
        if place.parent == None:
            fptr.write(str(place.parent))
        else:
            fptr.write(str(place.parent.name))
        fptr.write("</parent>\n")
        fptr.write("\t\t<children>\n")
        for chil in place.children:
            fptr.write("\t\t\t<child>")
            fptr.write(str(chil.name))
            fptr.write("</child>\n")
        fptr.write("\t\t</children>\n")

        fptr.write("\t\t<tokens>\n")
        for toke in place.tokenList:
            if toke.__class__.__name__ == "VariableToken":
                fptr.write("\t\t\tvariable<token>\n")
                fptr.write("\t\t\t\t<identifier>")
                fptr.write(toke.identifier)
                fptr.write("</identifier>\n")
                fptr.write("\t\t\t\t<qualifiers>\n")
                for qual in toke.qualifier:
                    fptr.write("\t\t\t\t\t<qualifier>")
                    fptr.write(qual)
                    fptr.write("</qualifier>\n")
                fptr.write("\t\t\t\t</qualifiers>\n")
                fptr.write("\t\t\t\t<storages>\n")
                for sto in toke.storage:
                    fptr.write("\t\t\t\t\t<storage>")
                    fptr.write(sto)
                    fptr.write("</storage>\n")
                fptr.write("\t\t\t\t</storages>\n")
                fptr.write("\t\t\t\t<types>\n")
                for sto in toke.var.type:
                    fptr.write("\t\t\t\t\t<type>")
                    fptr.write(sto)
                    fptr.write("</type>\n")
                fptr.write("\t\t\t\t</types>\n")
                fptr.write("\t\t\t\t<value>")
                fptr.write(toke.var.value)
                fptr.write("</value>\n")
                fptr.write("\t\t\t</constanttoken>\n")

            elif toke.__class__.__name__ == "ConstantToken":
                fptr.write("\t\t\t<constanttoken>\n")
                fptr.write("\t\t\t\t<type>")
                fptr.write(toke.var.type)
                fptr.write("</type>\n")
                fptr.write("\t\t\t\t<value>")
                fptr.write(toke.var.value)
                fptr.write("</value>\n")
                fptr.write("\t\t\t\t<identifier>")
                fptr.write(toke.identifier)
                fptr.write("</identifier>\n")
                fptr.write("\t\t\t</constanttoken>\n")
        fptr.write("\t\t</tokens>\n")
        fptr.write("\t</place>\n")
        
    fptr.write("</places>\n")

    #Transitions
    fptr.write("<transitions>\n")
    for tras in gTransitionList:
        fptr.write("\t<transition>\n")
        fptr.write("\t\t<name>")
        fptr.write(str(tras.name))
        fptr.write("</name>\n")
        fptr.write("\t\t<logic>\n")
        if tras.logic != None:
            fptr.write("\t\t\t<operator>")
            fptr.write(tras.logic[1])
            fptr.write("</operator>\n")
            fptr.write("\t\t\t<left>")
            fptr.write(tras.logic[0])
            fptr.write("</left>\n")
            fptr.write("\t\t\t<right>")
            fptr.write(tras.logic[2])
            fptr.write("</right>\n")
            fptr.write("\t\t\t<type>")
            fptr.write(tras.logic[3])
            fptr.write("</type>\n")
        else:
            fptr.write(str(tras.logic))
        fptr.write("\t\t</logic>\n")
        fptr.write("\t</transition>\n")    
    fptr.write("</transitions>\n")    

    #Arcs
    fptr.write("<arcs>\n")
    for ar in gArcInList:
        fptr.write("\t<arc>\n")
        fptr.write("\t\t<type>")
        fptr.write(str(ar.type))
        fptr.write("</type>\n")
        fptr.write("\t\t<name>")
        fptr.write(str(ar.name))
        fptr.write("</name>\n")
        fptr.write("\t\t<place>")
        fptr.write(str(ar.place.name))
        fptr.write("</place>\n")
        fptr.write("\t\t<transition>")
        fptr.write(str(ar.transition.name))
        fptr.write("</transition>\n")
        fptr.write("\t\t<inscriptions>\n")
        for ins in ar.inscription:
            fptr.write("\t\t\t<inscription>")
            fptr.write(ins)
            fptr.write("</inscription>\n")
        fptr.write("\t\t</inscriptions>\n")
        fptr.write("\t\t<constraint>\n")
        if ar.constraint != None:
            fptr.write("\t\t\t<identifier>")
            fptr.write(ar.constraint[0])
            fptr.write("</identifier>\n")
            fptr.write("\t\t\t<boolval>")
            fptr.write(ar.constraint[1])
            fptr.write("</boolval>\n")
        else:
            fptr.write("\t\t\t" + str(ar.constraint) + "\n")
        fptr.write("\t\t</constraint>\n")
        fptr.write("\t</arc>\n")
    fptr.write("</arcs>\n")

    fptr.close()

def GenerateScipt(filename, directory):
    global gArcInList
    global gArcOutList
    global gTransitionList
    global gPlaceList
    filename = "out-" + filename
    filename = filename.replace(".c", ".dot")
    direct = directory + '/'
    direct = direct + filename
    fptr = open(direct, "w")
    fptr.write("digraph boxes_and_circles { \n") 
    fptr.write("graph [overlap = true, fontsize = 10] \n")
    
    fptr.write("node [shape = circle, fixedsize = true, color = greenyellow, style = \"filled\", fontsize = 7] \n")

    #add all places as scope
    for pla in gPlaceList:
        # print (pla)
        # sys.exit(0)
        if pla.scope == True:
            label = "Place " + str(pla.name)
            name =  "Place" + str(pla.name)
            # name = name
            name = name + "[ label = \""
            name = name + label
            name = name + "\" ]; "
            fptr.write(name)

    fptr.write("\n node [shape = circle, fixedsize = true, color = powderblue, style = \"filled\", fontsize = 7] \n ")

    #add all places as scope
    for pla in gPlaceList:
        if pla.scope == False:
            label = "Place " + str(pla.name)
            name =  "Place" + str(pla.name)
            # name = name + "; "
            name = name + "[ label = \""
            name = name + label
            name = name + "\" ]; "
            fptr.write(name)

    fptr.write("\n node [shape = box, fontname = Helvetica, color = gold, style = \"filled\", fontsize = 8, width = 1.25] \n")
    for tran in gTransitionList:
        label = "Transition " + str(tran.name)
        if tran.logic != None:
            label = label + " \n("
            label =  label + tran.logic[3]
            label = label + ": "
            label =  label + tran.logic[0]
            label = label + " "
            label =  label + tran.logic[1]
            label = label + " "
            label =  label + tran.logic[2]
            label = label + ")"

        name =  "Transition" + str(tran.name)
        # name = name + "; "
        name = name + " [ label = \""
        name = name + label
        name = name + "\" ]; "
        fptr.write(name)
    fptr.write("\n")
    # fptr.write("edge [arrowhead = dot, arrowsize = 0.5]")
    for arc in gArcInList:
        source = "Place" + str(arc.place.name)
        destination = "Transition" + str(arc.transition.name)

        ins = ", ".join(arc.inscription)
        if ins != "":
            ins = " [ label = \"" + ins

        if arc.constraint != None:
            # print (arc.constraint[0] + " " + arc.constraint[1])
            ins = ins + " ("
            ins = ins + str(arc.constraint[0])
            ins = ins + " == "
            ins = ins + str(arc.constraint[1])
            ins = ins + ")"
        ins = ins + " \"]; \n "
        # print (ins)
        final = source + " -> "
        final = final + destination
        final = final + ins
        fptr.write(final)

    for arc in gArcOutList:
        destination = "Place" + str(arc.place.name)
        source = "Transition" + str(arc.transition.name)
        ins = ", ".join(arc.inscription)
        ins = " [ label = \"" + ins

        if arc.constraint != None:
            ins = ins + " ("
            ins = ins + str(arc.constraint[0])
            ins = ins + str(arc.constraint[1])
            ins = ins + ")"
        ins = ins + " \"]; "

        final = source + " -> "
        final = final + destination
        final = final + ins
        fptr.write(final)

    fptr.write("\n } \n \")")
    fptr.close()
    # print (os.path.abspath("output.dot"))
    ssc = "dot -Tsvg " + direct
    direct = direct.replace(".dot", ".svg")
    ssc = ssc + " -o "
    ssc = ssc + direct
    print (ssc)
    call(ssc,  shell=True)

    # call(["ls"])
    # os.system("dot -Tsvg output.dot -o output.svg")
    # subprocess.call("/usr/bin/Rscript --vanilla output.R", shell=True)


if __name__ == "__main__":
    directory = "./INPUT"
    files = os.listdir(directory)
    files = sorted(files)
    for filename in files:
        PlaceRandom = 0
        TransitionRandom = 0
        ArcRandom = 0
        gPlaceList.clear()
        gTransitionList.clear()
        gArcInList.clear()
        gArcOutList.clear()
        direct = directory + "/"
        direct = direct + filename
        # print (filename)
        with open(direct, 'r') as myfile:
            text=myfile.read()

        parser = c_parser.CParser()
        ast = parser.parse(text, filename='<none>')
        ast.show(attrnames=True, nodenames=True)
        
        
        scope_parent = Place(True)
        name = ast.__class__.__name__
        # print ("-----------------------------")
        petrinet = PetriNet()
        for translation_unit in ast.ext:
            name = translation_unit.__class__.__name__
            child = globals()[name](translation_unit, scope_parent, name)
        print ("-----------------------RESULT-------------------")
        print (filename)

        print ("#Places: ",len(gPlaceList))
        print ("#Transition: ",len(gTransitionList))
        print ("#Input Arcs: ",len(gArcInList))
        print ("#Output Arcs: ",len(gArcOutList))
        print ("\n")
        GenerateScipt(filename, directory)
        GenerateXML(filename, directory)