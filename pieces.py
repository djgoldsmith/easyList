from ruleGrab import Rules
import copy, StringIO
#from versus import melee

#TODO: check wielder for slow and purposeful and modify move/shoot note when present

#TODO: turn all dict checks into fn calls that ignore case
validWeaponTypes=["shooting","melee"]
toHitStats=["-","6","5","4","3","2","2/6","2/5","2/4","2/3","2/2"]

moveStats={}
moveStatLines=[("Infantry",6,"max(2d6)","2d6","Run D6","2d6","3D6, discarding highest",""),
               ( "Jump",12,"Starting or ending in difficult terrain requires a dangerous terrain test","3d6","2d6, may re-roll both dice","3D6, discarding highest, can re-roll all dice. Must take Dangerous Terrain test if starting or ending in difficult terrain","Run D6","When not 'jumping', move distance and difficult terrain behaviour are inherited from the base type, but fallback is still 3d6"),
               ( "Beast",12,"No effect","3D6","Run D6","2d6","No effect.",""),
               ( "Cavalry",12,"Count as dangerous","3d6","Run D6","2d6","2D6, take dangerous terrain test",""),
               ( "Bike",12,"Count as dangerous","3d6","Turbo-Boost 12","2d6","2D6, take dangerous terrain test",""),
               ( "Jetbike",12,"Starting or ending in difficult terrain requires a dangerous terrain test","3d6","Turbo-Boost 24","2d6","2D6, take dangerous terrain test if beginning or ending in difficult terrain",""),
               ( "Eldar Jetbike",12,"Starting or ending in difficult terrain requires a dangerous terrain test","3d6","Turbo-Boost 36","2D6","2D6, take dangerous terrain test if beginning or ending in difficult terrain",""),
               ( "Monstrous Creature",6,"max(3d6)","2d6","Run D6","2d6","3D6, discarding highest",""),
               ( "Artillery",6,"max(2d6)","2d6","Run D6","2d6","3D6, discarding highest",""),

               ( "Jetpack",6,"Starting or ending in difficult terrain requires a dangerous terrain test","2d6", "run D6",
                 "2d6","2D6, take dangerous terrain test if beginning or ending in difficult terrain (or just 3d6\" discarding highest if not using Jet Pack)","when not using the jetpack, move distance and difficult terrain behaviour are inherited from the base type, and fallback is 2d6"),

               ( "Skimmer",12,"Starting or ending in difficult terrain requires a dangerous terrain test","N/A","Flat-Out 6","To be done!","To be done!",""),
               ( "Walker",6,"max(2d6)","N/A","Run D6","2d6","3D6, discarding highest",""),
               ( "Fast Skimmer",12,"Dangerous terrain test","N/A","Flat-Out 18","To be done!","To be done!",""),
               ( "Fast",12,"Dangerous terrain test","N/A","Flat-Out 12","To be done!","To be done!",""),
               ( "Vehicle",12,"Dangerous terrain test","N/A","Flat-Out 6","To be done!","To be done!","")
               ]
for i in moveStatLines:

    moveStats[i[0]]={"move":i[1],"terrain":i[2],"fallback":i[3],"run":i[4],"notes":i[7],"charge":i[5],"chargeTerrain":i[6]} 



 
#TODO: Flyer movement
#TODO: Make note about falling back in fallback section when any rule that effects it applies
def sanitiseName(n):
    allowed="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_"
    return "".join([i if i in allowed else "" if i!=" " else "_" for i in n])

class Weapon(object):
    """
    """
    def __init__(self, name, range, strength,ap, weaponType, shots=1,specialRules=None,hitExtras="",woundExtras="", wielder=None):
        """
        
        Arguments:
        - `strength`:
        - `ap`:
        """

        self.wielder=wielder

        self.shots=shots
        self.type=weaponType

        if not self.type in validWeaponTypes:
            raise TypeError("Weapon type must be one of %s, can't be %s"%(str(validWeaponTypes),self.type))
        self.range=range
        self.name=name
        self._strength = strength
        self._ap = ap

        self._specialRules=[]
        if specialRules!=None:
            for i in specialRules:
                self.addSpecialRule(i)
        self.hitExtras=hitExtras
        self.woundExtras=woundExtras

    def clone(self):
        return Weapon(self.name, self.range, self._strength, self._ap, self.type, shots=self.shots, specialRules=list(self._specialRules),woundExtras=self.woundExtras,wielder=None)
                      
        
    def hasRule(self,thing):
        for i in self._specialRules:
            if i.upper()==thing.upper(): return True
        return False
    def addSpecialRule(self,rule):
        if rule!="Heavy" and rule.startswith("Heavy"):
            self.addSpecialRule("Heavy")
            return

        if self.hasRule(rule):
            return
        else:
            self._specialRules.append(rule)
            if rule=="Sniper":
                self.addSpecialRule("Pinning")
                self.addSpecialRule("Rending")
            self._specialRules.sort()
    
    def __getattribute__(self,attr):
        if attr=="strength":
            val=0
            if type(self._strength)==type("") and self._strength[0]=="+":
                val= (int(self.wielder.s)+int(self._strength[1:]))
            elif type(self._strength)==type("") and self._strength[0]=="x":
                val= (int(self.wielder.s)*int(self._strength[1:]))
            else:
                val= int(self._strength) if type(self._strength)==type(1) else self._strength
            if val>10: val=10

            return val
        if attr=="ap":

            return str(self._ap) + ("" if self.type!="melee" or ( self.wielder!=None and not self.wielder.hasRule("Smash")) else " (AP2 due to Smash)") +\
                   ("" if not self.hasRule("Bladestorm") else "(Auto-wound AP2 on roll of 6)")
        else:
            return object.__getattribute__(self,attr)

    def woundProfile(self):

        out=""
        doubleLoop=[False]
        if self.wielder!=None and self.wielder.hasRule("Smash"):
            doubleLoop.append(True)

        for willDouble in doubleLoop:
            oldS=self.wielder.s
            if willDouble:
                self.wielder.s*=2
                if self.wielder.s>10: self.wielder.s=10
            toWound=[str(shootToWoundIndividual(self.strength,n+1)) for n in range(10)]

            if self.hasRule("Bladestorm") or self.hasRule("Rending"):
                for i in range(len(toWound)):
                    if toWound[i]=="-":
                        toWound[i]="6"
            toWound=" & ".join(toWound)
            if self.hasRule("Sniper"):
                toWound=" & ".join(["4"]*10)
            if self.hasRule("Fleshbane"):
                toWound=" & ".join(["2"]*10)
            if self.hasRule("Poisoned"):
                toWound=" & ".join(["4" if i>self.strength else "4r" for i in range(1,11)])
            if not (willDouble and self.type!="melee"):

                if willDouble:
                    out+="\\vspace{1em}\\\\Smash (halve attacks)\\\\"
                out+= """\\begin{{tabular}}{{l|l|l|l|l|l|l|l|l|l|l|}}
            \\begin{{turn}}{{45}}T\\end{{turn}} & 1 & 2 & 3 & 4 & 5 & 6 & 7 & 8 & 9 & 10 \\\\ \\hline
                \\begin{{turn}}{{45}}Roll\\end{{turn}} & {0}
            \\end{{tabular}}""".format(toWound)
                if self.type=="melee" and self.wielder!=None and self.wielder.hasRule("Furious Charge"):
                    toWound=[str(shootToWoundIndividual(self.strength+1,n+1)) for n in range(10)]
                    toWound=" & ".join(toWound)
                    if self.hasRule("Poisoned"):
                        toWound=" & ".join(["4" if i>self.strength+1 else "4r" for i in range(1,11)])
                    elif self.hasRule("Fleshbane"):
                        toWound=" & ".join(["2"]*10)

                    out+= """\n\subsubsection*{{On Charge (Furious Charge rule)}}\\begin{{tabular}}{{l|l|l|l|l|l|l|l|l|l|l|}}
                \\begin{{turn}}{{45}}T\\end{{turn}} & 1 & 2 & 3 & 4 & 5 & 6 & 7 & 8 & 9 & 10 \\\\ \\hline
                    \\begin{{turn}}{{45}}Roll\\end{{turn}} & {0}
                \\end{{tabular}}""".format(toWound)
            self.wielder.s=oldS

            
        return out
    
    def canShootAfterMoving(self):
        if self.wielder.hasRule("Relentless"):
            return "Relentless: fire as normal, assault after move. Flip sugar up."
        if self.hasRule("Assault"):
            return "Fire as normal, can assault"
        elif self.hasRule("Heavy"):
            if self.hasRule("Blast") or self.hasRule("Large Blast"):
                return "Blast weapons cannot be fired after moving"
            else:
                return "Fired only as snap-shots, cannot assault"
        elif self.hasRule("Ordnance"):
            return "Cannot fire after moving"
        elif self.hasRule("Pistol"):
            return "Fire as normal, can assault"
        elif self.hasRule("Rapid Fire"):
            return "Can fire as normal after moving (1shot at full range, 2 at half or less), but cannot assault."
        elif self.hasRule("Salvo"):
            return "Can fire using lower of the two values. Cannot assault after firing."
        else:
            return "This weapon doesn't seem to have a rule defined for this!"

        
#DONE: have master list of special rules to check against and also incorporate rule text in output

#TODO: exceptions to snap-shot stuff: relentless, etc. Check wielder

def shootToWoundIndividual(s,t):
    result=""
    
    if s>=t+2:
        result+="2"
    elif s==t+1:
        result+="3"
    elif s==t:
        result+="4"
    elif s==t-1:
        result+="5"
    elif s in [t-2, t-3]:
        result+="6"
    else:
        result+="-"
    if s>=t*2:
        result+="D"
    return result

class Model(object):
    """
    """


    
    def __init__(self, name,ws,bs,s,t,w,i,a,ld,sv,inv="-", rerollHits="", rerollWounds="",rerollSaves="",rules=None, modelType="Infantry"):
        """
        """
        self.classType="non-vehicle"
        self.type=modelType
        self.name=name
        self.bs=bs
        self.ws=ws
        self.s=s
        self.t=t
        self.w=w
        self.a=a
        self.i=i
        self.ld=ld
        self.sv=sv
        self.inv=inv
        self.rerollHits=  rerollHits
        self.rerollWounds=rerollWounds
        self.rerollSaves= rerollSaves
        self.extraBasics=[]
        self.weapons=[]

        self.hands=Weapon("Bare Hands",0,"+0","-","melee",wielder=self)
        
        self.moveStats=copy.deepcopy(moveStats[self.type if not self.type.startswith("Jump") else "Jump"])
        if self.type=="Eldar Jetbike":
            self.moveStats["move"]=str(self.moveStats["move"])+" - Can move 2d6\" in assault phase even if not assaulting"
        self.rules=[]
        if rules!=None: self.addRules(rules)

    def addBasic(self,info):
        self.extraBasics.append(info)
    def hasRule(self,rule):
        for i in self.rules:
            if i.upper()==rule.upper():
                return True
        return False
    def addRule(self,rule):
        if self.hasRule(rule):
            return

            
        if rule=="Independent Character":            
            self.addBasic("Independent Character")
        if rule=="Battle Focus" and self.type !="Eldar Jetbike":
            self.moveStats["run"]+="(Battle focus allows shoot+run in any order)"
        if rule=="Fleet":
            self.moveStats["run"]+="(Fleet allows one die to be rerolled)"
        if len(rule) >3 and rule[-3:].startswith("ML"):
            self.addRule("Psyker")
            self.addRule(rule[-3:])
            return
        if rule.startswith("Preferred Enemy"):
            self.rules.append("Preferred Enemy")
            self.addBasic(rule)
            return
        if rule.startswith("Hatred"):
            self.rules.append("Hatred")
            self.addBasic(rule)
            return
        if rule=="Slow and Purposeful":
            self.moveStats["run"]="Slow and Purposeful: cannot run"
        if rule.upper()=="MOVE THROUGH COVER":
            
            self.moveStats["terrain"]="max(3d6) (extra die for MtC)"
        if rule.upper()=="MONSTROUS CREATURE":
            for i in ["Fear","Hammer of Wrath", "Move Through Cover", "Relentless" , "Smash"]:
                self.addRule(i)
        self.rules.append(rule)
    def addRules(self,rules):
        for r in rules: self.addRule(r)
    def addWeapon(self,w):

        w=w.clone()
        w.wielder=self
        self.weapons.append(w)

    def addWeapons(self,weapons):
        for i in weapons:
            self.addWeapon(i)


            
    def assaultToHit(self):
        mapping=[[4,4,5,5,5,5,5,5,5,5],
                [3,4,4,4,5,5,5,5,5,5],
                [3,3,4,4,4,4,5,5,5,5],
                [3,3,3,4,4,4,4,4,5,5],
                [3,3,3,3,4,4,4,4,4,4],
                [3,3,3,3,3,4,4,4,4,4],
                [3,3,3,3,3,3,4,4,4,4],
                [3,3,3,3,3,3,3,4,4,4],
                [3,3,3,3,3,3,3,3,4,4],
                [3,3,3,3,3,3,3,3,3,4]]
                 
        if self.ws==1:
            mapping[-2]=5
        if self.classType!="vehicle" :

            return """\\begin{{tabular}}{{p{{0.55cm}}|l|l|l|l|l|l|l|l|l|l|}}
            Opp. WS & 1 & 2 & 3 & 4 & 5 & 6 & 7 & 8 & 9 & 10 \\\\ \\hline
            \\begin{{turn}}{{45}}Roll\\end{{turn}} & {0}
            \\end{{tabular}}""".format(" & ".join([str(mapping[self.ws-1][n]) for n in range(10)])) 
        else:
            return ""
    def shootToHit(self):

        return toHitStats[self.bs]
    def shootToWound(self):

        out=[]
        for i in range(10):
            out.append(shootToWoundIndividual(self.s,(i+1)))

        return "| %11s "%"Toughness"+" ".join(["| %2d"%(n+1) for n in range(len(out))]) + " |\n"+"+"+"-"*13+"+----"*len(out)+"+\n"+"| %11s "%"Min roll"+" ".join(["| %2d"%(n) for n in out])+" |"

    def attacks(self):
        meleeCount=0
        for w in self.weapons:
            if not w.hasRule("Grenade") and (w.type=="melee" or w.hasRule("Pistol")):
                meleeCount+=1
                if w.hasRule("Specialist Weapon"):
                    meleeCount+=1000
        if 1000<=meleeCount<2000 or meleeCount in [0,1]:
            meleeCount=0
        else:
            meleeCount=1
        return self.a+meleeCount
    
    def createSheet(self,r):
        meleeCount=0
        assaultWeapons=""
        weaponProfilesShooting=""
        for w in self.weapons:
            if w.type=="shooting":
                weaponProfilesShooting+=""" \\subsection{{{0.name}}}
                \\begin{{description}}
                \\item[Range]{range}\"
                \\item[Shots]{0.shots}
                \\item[Strength]{0.strength}
                \\item[AP]{0.ap}{apExtra}
                \\item[Move/Fire/Assault]{assault}
                \\end{{description}}
                
                {wounding}
                \\subsubsection{{Weapon Rules}}
                {rules}
                \\hrule
                """.format(w,rules="\\begin{description} %s \\end{description}"%("\n".join(["\\item[%s] %s"%(i,r[i]) for i in w._specialRules])),wounding=w.woundProfile(), assault=w.canShootAfterMoving(), range=w.range, apExtra={True:"/(2 on a 'to wound' roll of 6 - Rending)", False:""}[w.hasRule("Rending")])
            if not w.hasRule("Grenade") and (w.type=="melee" or w.hasRule("Pistol")):
                meleeCount+=1
            if w.hasRule("Specialist Weapon"):
                meleeCount+=1000
            if w.type=="melee" : #or w.hasRule("Pistol")
                strength=w._strength
                strength= str(strength).strip()
                if strength[0]=="+":
                    news=(int(self.s)+int(strength[1:]))
                    strength=strength+" (Total: %d)"%(news if news<=10 else 10)
                elif strength.upper()=="USER":
                    strength="User (%d)"%self.s
                assaultWeapons+=""" \\subsubsection{{{0.name}}}                
                \\begin{{description}}
                \\item[Strength]{s}
                \\item[AP]{0.ap} {apExtra}
                \\end{{description}}
                \\subsubsection{{To Hit}}
                {hitting}
                \\subsubsection{{To Wound}}
                {wounding}                
                \\subsubsection{{Weapon Rules}}
                {rules}
                \\hrule
                """.format(w,s=strength,rules="\\begin{description} %s \\end{description}"%("\n".join(["\\item[%s] %s"%(i,r[i]) for i in w._specialRules])),hitting=self.assaultToHit(), wounding=w.woundProfile(),apExtra={True:"/(2 on a 'to wound' roll of 6 - Rending)", False:""}[w.hasRule("Rending")])


        if 1000<=meleeCount<2000 or meleeCount in [0,1]:
            meleeCount=0
        else:
            meleeCount=1

            
        extraBasic=""" \\begin{itemize}
        %s
        \\end{itemize}
        """%"\n".join(["\\item %s"%d for d in self.extraBasics])
        if len(self.extraBasics)<1:
            extraBasic=""


        extraAttacks={True:"(Includes dual wielding bonus)",False:""}[meleeCount==1]
        if self.hasRule("Mandiblasters"):
            extraAttacks+="(Plus Mandiblaster attack)"
        if self.hasRule("Fleet"):
            extraAttacks+=" \\item[Fleet] allows one charge-range die to be rereolled"
        if self.hasRule("Rage"):
            extraAttacks+="(Rage: Add 2 attacks on charge, not 1)"

        profileAssault="""\\begin{{description}}
        \\item[Attacks] {attacks} (Remember to add an attack if charging) {extraAttacks} {hammerExtra}
        \\item[Charge] {charge}
        \\item[Charge through terrain] {chargeTerrain}
        \\end{{description}}
        \\subsection*{{Unmodified Attack Profile}}
        \\subsubsection*{{To Hit}}
        {unodProfileHit}
        \\subsubsection*{{To Wound}}
        {unodProfileWound}

        \\subsection{{Melee Weapons}}

        {weapons}
        
        """.format(attacks=self.a+meleeCount, extraAttacks=extraAttacks,weapons=assaultWeapons, hammerExtra={True:"(Remember to resolve \\textbf{Hammer of Wrath} wounds too)",False:""}["Hammer of Wrath" in self.rules],charge=self.moveStats["charge"],chargeTerrain=self.moveStats["chargeTerrain"],unodProfileHit=self.assaultToHit(),unodProfileWound=self.hands.woundProfile())
        
        weaponShort="""        \\begin{itemize}
        %s
        \end{itemize}"""%("\n".join(["\\item %s (%s)"%(n.name, n.type[0].upper()) for n in self.weapons ]))
        if len(self.weapons)<1: weaponShort="This model has no weapons"
        specialRules="\\begin{description} %s \\end{description}"%("\n".join(["\\item[%s] %s"%(i,r[i]) for i in self.rules]))
        if len(self.rules)<1: specialRules="This model has no special rules."
        out= """\\documentclass[10pt,a4paper,twocolumn]{{article}}
        \\title{{{0.name}}}
        \\author{{{modelT}}} \\date{{}}
        \\usepackage[width=7in,height=9in]{{geometry}}
        \\usepackage{{multicol}}
        \\usepackage{{sectionbox}}
        \\usepackage{{rotating}}
        \\begin{{document}}
        \\maketitle
        \\begin{{sectionbox}}{{Basic}}
        {basictable}
        {extraBasic}
        \\subsection{{Weapons}}
        {weaponShort}
        \\end{{sectionbox}}
        \\section{{Movement}}
        \\begin{{description}}
        \\item[Move Distance] {moveD}
        \\item[Difficult Terrain] {dTerrain}
        \\item[Fallback] {fallback}
        \\item[Forego shooting to] {fast}
        \\item[Notes] {notes}

        \\end{{description}}
        \\section{{Shooting}}
        \\begin{{description}}
        \\item[To hit:] {toHit} {0.rerollHits}
        \\end{{description}}
        {shootingProfiles}
        {assaultheader}
        {assaultProfile}
        \\section{{Model Special Rules}}
        %\\begin{{multicols}}{{2}}
        {rules}
        %\\end{{multicols}}

        \\end{{document}}
        """.format(self,toHit=self.shootToHit(),shootingProfiles=weaponProfilesShooting, rules=specialRules, assaultProfile=profileAssault if self.classType!="vehicle" else "", extraBasic=extraBasic, weaponShort=weaponShort,modelT=self.type, moveD=self.moveStats["move"],dTerrain=self.moveStats["terrain"],fallback=self.moveStats["fallback"],notes=self.moveStats["notes"],fast=self.moveStats["run"],assaultheader="\\section{Assault/Melee}" if self.classType!="vehicle" else "", basictable=self.basicTable())
        return out
    def basicTable(self):
        return """ \\begin{{tabular}}{{p{{2ex}}p{{2ex}}p{{2ex}}p{{2ex}}p{{2ex}}p{{2ex}}p{{2ex}}p{{2ex}}p{{2ex}}p{{2ex}}}}
         Ws & Bs & S & T & W & I & A & Ld & Sv & Inv \\\\ \\hline
         {0.ws} & {0.bs} & {0.s} & {0.t} & {0.w} & {0.i} & {0.a} & {0.ld} & {0.sv} & {0.inv}         
        \\end{{tabular}}""".format(self)




    
    def render(self,rules):
        import subprocess
        self.rules.sort()
        p=subprocess.Popen(["pdflatex", "-jobname",sanitiseName(self.name)], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p.communicate(input=self.createSheet(rules))
        p.wait()


class Vehicle(Model):
    def __init__(self, name, bs, front, side, rear,rules=None,modelType="Vehicle"):
        """
        """
        if rules==None: rules=[]
        self.vehicletypes=[modelType]
        Model.__init__(self, name,-10,-10,-10,-10,-10,-10,-10,-10,-10,modelType=modelType,rules=rules)
        self.front=front
        self.side=side
        self.rear=rear
        self.classType="vehicle"
#TODO: assult section when open-topped
    def basicTable(self):
        return """ \\begin{{tabular}}{{p{{4ex}}p{{4ex}}p{{4ex}}p{{4ex}}p{{12ex}}}}
         Bs & Front & Side & Rear & Type  \\\\ \\hline
         {0.bs} & {0.front} & {0.side} & {0.rear} & {typestuff}
        \\end{{tabular}}""".format(self,typestuff=",".join(self.vehicletypes))

    def addRule(self,rule):


        if self.hasRule(rule):
            return
        if rule.upper()=="OPEN-TOPPED":
            self.vehicletypes=self.vehicletypes+["Open-topped"]

        if rule.upper()=="WARTRAKK":
            self.moveStats["terrain"]+=" Wartrakk: re-reoll dangerous terrain test"
        if rule.upper()=="RED PAINT JOB":
            self.moveStats["move"]=str(self.moveStats["move"])+" + 1 (The red ones go faster)"
        Model.addRule(self,rule)
#TODO: subclass walker

def orkKillTeam(r):
    nob=Model("Nob",4,2,4,4,2,3,3,7,"6+(4+ eavy)",modelType="Infantry")
    bigChoppa=Weapon("Big choppa","-", "+2","-","melee",specialRules=["Two-Handed"])
    nob.addWeapon(bigChoppa)



    shootaTL=Weapon("Shoota",18,4,6,"shooting",shots=2,specialRules=["Assault","Twin-Linked"])
    nob.addWeapon(shootaTL)

    nob.addRules(["Mob Rule","Waaagh!","Furious Charge"])



    grot=Model("Gretchin (Grot)",2,3,2,2,1,2,1,5,"-","-",modelType="Infantry",rules=["It's a Grot's Life"] )
    grotBlaster=Weapon("Grot Blasta",12,3,"-","shooting",specialRules=["Assault"])
    grot.addWeapon(grotBlaster)


    runtherd=Model("Runtherd",4,2,3,4,1,2,2,7,"6+",modelType="Infantry")
    runtherd.addRules(["Mob Rule","Waaagh!","Furious Charge","Squig Hound"])
    grotprod=Weapon("Grot-Prod","-",1,"-","melee", specialRules=["Poisoned"])

    
    slugga=Weapon("Slugga",12,4,6,"shooting",specialRules=["pistol"])
    runtherd.addWeapons([grotprod,slugga])


    boy=Model("Ork Boy",4,2,3,4,1,2,2,7,"6+",modelType="Infantry", rules=["Furious Charge", "Mob Rule", "Waaagh!"])
    choppa=Weapon("Choppa","-", "+0","-","melee",specialRules=[])
    rokkit=Weapon("Rokkit Launcha","24\"",8,3,"shooting",specialRules=["Assault"])
    boy.addWeapons([choppa,slugga,rokkit])

    nob.render(r)
    grot.render(r)
    boy.render(r)
    runtherd.render(r)
def eldarKillTeam(r):
    

    shuP=Weapon("Shuriken Pistol",12,4,5,"shooting",1,specialRules=["Pistol", "Bladestorm"])

    scorpionCS=Weapon("Scorpion Chainsword","-","+1",6,"melee",specialRules=["Melee"])
    mandiblasters=Weapon("Mandiblasters","-",3,"-","melee",specialRules=["Mandiblasters"])
  
    twinlinkedShCatapult=Weapon("Twin-Linked Shuriken Catapult (jetbike)",12,4,5,"shooting",shots= 2,specialRules=["Assault", "Bladestorm", "Twin-Linked"])
    
    plasmaGrenades=Weapon("Plasma Grenades","8/-",4,4,"shooting",specialRules=["Assault","Blast","No Charge/Cover Penalty"])

    

    windrider=Model("Windrider",4,4,3,4,1,5,1,8,"3+", modelType="Eldar Jetbike")
    windrider.addRules(["Ancient Doom", "Battle Focus", "Bladestorm","Hammer of Wrath", "Jink", "Relentless"])
    windrider.addWeapon(twinlinkedShCatapult)
        
    sScorpion=Model("Striking Scorpion",4,4,3,3,1,5,1,9,"3+")
    sScorpion.addWeapon(scorpionCS)
    sScorpion.addRule("Mandiblasters")
    sScorpion.addWeapon(shuP)
    sScorpion.addWeapon(plasmaGrenades)
    sScorpion.addRules(["Ancient Doom", "Battle Focus", "Fleet", "Infiltrate", "Move Through Cover", "Stealth"])
    sScorpion.addWeapon(mandiblasters)


    chainsabreShooting=Weapon("Chainsabres","12\"",4,5,"shooting",shots=2,specialRules=["Assault", "Bladestorm"])
    chainsabreMelee=Weapon("Chainsabres (melee)","-","+1",5,"melee",specialRules=["Melee", "Rending"])
    #bitingBlade=Weapon("Biting blade","-","+2",4,"melee",specialRules=["Melee", "Two-handed"])

    sScorpionEX=Model("Striking Scorpion Exarch",5,5,3,3,1,6,2,9,"3+")
    sScorpionEX.addRule("Mandiblasters")   
    sScorpionEX.addWeapon(plasmaGrenades)
    sScorpionEX.addRules(["Ancient Doom", "Battle Focus", "Fleet", "Infiltrate", "Move Through Cover", "Stealth"])
    sScorpionEX.addWeapon(mandiblasters)
    sScorpionEX.addWeapons([chainsabreShooting,chainsabreMelee])
    #sScorpionEX.addWeapon(bitingBlade)
    
    sScorpion.render(r)
    sScorpionEX.render(r)
    windrider.render(r)

def ultramarineKillteam(r):
    fragGrenades=Weapon("Frag Grenades",8,3,"-","shooting",specialRules=["Assault","Blast","No Charge/Cover Penalty"])
    krakA=Weapon("Krak Grenades (thrown)",8,6,4,"shooting",specialRules=["Assault"])
    krakB=Weapon("Krak Grenades (melee)","-",6,4,"melee",specialRules=["Vehicle/MC only","Grenade"])

    boltPistol=Weapon("Bolt Pistol", 12,4,5,"shooting",specialRules=["Pistol"])
    marine=Model("Marine",4,4,4,4,1,4,1,8,"3+",modelType="Infantry")
    marine.addRules(["And They Shall Know No Fear", "Combat Squads","Chapter Tactics (Ultramarines)"])
    boltGun=Weapon("Bolt Gun", 24,4,5,"shooting",specialRules=["Rapid Fire"], shots="1 (full range)/2 (half range)")
    boltGunTL=Weapon("Bolt Gun", 24,4,5,"shooting",specialRules=["Rapid Fire","Twin-Linked"], shots="1 (full range)/2 (half range)")
    marine.addWeapon(boltGun)
    marine.addWeapons([boltPistol,fragGrenades,krakA,krakB])
    
    plasmaCannon=Weapon("Plasma Cannon",36,7,2,"shooting",specialRules=["Heavy 1", "Blast", "Gets Hot"], shots=1)
    marine.addWeapon(plasmaCannon)
    flamer=Weapon("Flamer","Template",4,5,"shooting",specialRules=["Assault"])
    marine.addWeapon(flamer)
    chainsword=Weapon("Chainsword","-","+0","-","melee",specialRules=["Melee"])
    marine.addWeapon(chainsword)
    heavyBolter=Weapon("Heavy Bolter","36\"",5,4,"shooting",shots=3,specialRules=["Heavy"])
    bike=Model("Attack Bike",4,4,4,5,2,4,2,8,"3+",modelType="Bike")
    bike.addRules(["And They Shall Know No Fear","Chapter Tactics (Ultramarines)","Hammer of Wrath", "Jink", "Relentless"])
    bike.addWeapons([heavyBolter,boltPistol,boltGunTL,fragGrenades,krakA,krakB])
    bike.render(r)

    
    marine.render(r)

    
    
if __name__=="__main__":

    r=Rules("./rules.r")
    
    # r.rules["Mantle of the Laughing God"]="The bearer loses the Independent Character special rule but has the Hit & Run, Shrouded and Stealth special rules. In addition the bearer can re-roll failed cover saves."
    # r.rules["Runes of Warding"]= "One use only. Immediately before the Farseer makes a Deny the Witch roll, he can choose to use these runes to grant his unit an additional +2 modifier to the dice roll."
    # r.rules["Runes of Witessing"]= "One use only. If the Farseer fails a Psychic test, he can use these runes to re-roll the test (potentially negating Perls of the Warp in the process)"
    # r.save()
    #eldarKillTeam(r)
    #orkKillTeam(r)
    #ultramarineKillteam(r)
    #TODO: bladestom in reroll info
    
    # pathfinder=Model("Pathfinder",4,4,3,3,1,5,1,8,5)
    # for n in ["Ancient Doom", "Battle Focus", "Bladestorm", "Fleet", "Infiltrate", "Move Through Cover", "Sharpshoot", "Shrouded", "Stealth"]:
    #     pathfinder.addRule(n) 
    shuP=Weapon("Shuriken Pistol",12,4,5,"shooting",1,specialRules=["Pistol", "Bladestorm"])
    rangerLR=Weapon("Ranger Long Rifle",36,"X",6,"shooting",1,specialRules=["Heavy","Sniper"])


    
    # pathfinder.addWeapon(rangerLR)
    # pathfinder.addWeapon(shuP)


       

    #Two plasmarines vs 5 rangers -------------------------------------------------
    ranger=Model("Ranger",4,4,3,3,1,5,1,8,5)
    ranger.addRules(["Ancient Doom", "Battle Focus", "Bladestorm", "Fleet", "Infiltrate", "Move Through Cover", "Outflank", "Stealth"])
    ranger.addWeapon(rangerLR)

    plasmarine=Model("Plasma Marine",4,4,4,4,1,4,1,8,"3+",modelType="Infantry")
    plasmarine.addRules(["And They Shall Know No Fear","Grim Resolve","Stubborn", "Combat Squads"])
    plasmaCannon=Weapon("Plasma Cannon",36,7,2,"shooting",specialRules=["Heavy 1", "Blast", "Gets Hot"], shots=1)
    plasmarine.addWeapon(plasmaCannon)
    #------------------------------------------------------------------------------------------------------------------------
    

    
    # scorpionCS=Weapon("Scorpion Chainsword","-","+1",6,"melee",specialRules=["Melee"])
    
    farseer=Model("Farseer", 5,5,3,3,3,5,1,10,"-", inv="4++", modelType="Eldar Jetbike")
    farseer.addRules(["Ancient Doom", "Battle Focus", "Fleet", "Independent Character", "Psyker ML3", "Hammer of Wrath", "Jink", "Relentless"])
    farseer.addBasic("Choose psychic powers from Divination, Runes of Fate or Telepathy")
    farseer.addWeapon(Weapon("WitchBlade","-","User","-","melee",specialRules=["Melee","Armourbane","Fleshbane"]))
    farseer.addWeapon(shuP)
    farseer.addWeapon(Weapon("Shard of Anaris","-","+2","-","melee",specialRules=["Melee","Rending","Vaul's Work"]))
    twinlinkedShCatapult=Weapon("Twin-Linked Shuriken Catapult",12,4,5,"shooting",shots= 2,specialRules=["Assault", "Bladestorm", "Twin-Linked"])
    farseer.addWeapon(twinlinkedShCatapult)
    farseer.render(r)
    # #DONE: hatred (breackets), preferred enemy (brackets)
    # illic=Model("Illic Nightspear",6,9,3,3,3,6,3,10,"5+",modelType="Infantry")
    
    # illic.addRules([ "Ancient Doom", "Battle Focus", "Bladestorm", "Distort", "Fleet", "Hatred (Necrons)", "Independent Character", "Infiltrate", "Preferred Enemy (Necrons)", "Sharpshoot", "Shrouded", "Walker of the Hidden Path", "Master of Pathfinders", "Mark of the Incomparable Hunter"])
    # illic.addWeapon(Weapon("Voidbringer",48,"X",2,"shooting",specialRules=["Heavy", "Distort", "Sniper"]))
    # illic.addWeapon(shuP)
    
    
    # plasmaGrenades=Weapon("Plasma Grenades","8/-",4,4,"shooting",specialRules=["Assault","Blast","No Charge/Cover Penalty"])
    # #Assault 1, Blast / - Bearer suffers no Initiave penalty for charging through cover
    # sScorpion=Model("Striking Scorpion",4,4,3,3,1,5,1,9,"3+")
    # sScorpion.addWeapon(scorpionCS)
    # sScorpion.addRule("Mandiblasters")
    # sScorpion.addWeapon(shuP)
    # sScorpion.addWeapon(plasmaGrenades)
    # sScorpion.addRules(["Ancient Doom", "Battle Focus", "Fleet", "Infiltrate", "Move Through Cover", "Stealth"])
    # # mandiblasters=Weapon("Mandiblasters","-",3,"-","melee",specialRules=["Mandiblasters"])
    # # sScorpion.addWeapon(mandiblasters)
    # #pathfinder.addWeapon(scorpionCS)
    
    
    # direAvenger=Model("Dire Avenger",4,4,3,3,1,5,1,9,"4+")
    
    # direAvenger.addWeapon(Weapon("Avenger Shuriken Catapult",18,4,5,"shooting",shots=2,specialRules=["Assault","Bladestorm"]))
    # direAvenger.addWeapon(plasmaGrenades)
    # direAvenger.addRules(["Ancient Doom", "Battle Focus", "Counter-attack", "Fleet"])
    
    # # #        
    
    # #sm=Model("Bog Standard Marine", 3,3,3,4,1,1,7,3)
    # guardian=Model("Eldar Guardian",4,4,3,"3(5)",1,5,1,8,"5(3)+")
    # guardian.addBasic("Bracketed values refer to the support weapon")
    # guardian.addRules(["Battle Focus","Ancient Doom","Bladestorm", "Fleet"])
    
    # guardian.addWeapon(Weapon("Shuriken Catapult",12,4,5,"shooting",shots=2,specialRules=["Bladestorm","Assault"]))
    # guardian.addWeapon(plasmaGrenades)
    # hwp=Weapon("Heavy Weapon Platform (Shuriken Cannon)",24,6,5,"shooting",shots=3,specialRules=["Assault","Bladestorm","HWP"])
    # guardian.addWeapon(hwp)
    
    # windrider=Model("Windrider",4,4,3,4,1,5,1,8,"3+", modelType="Eldar Jetbike")
    # windrider.addRules(["Ancient Doom", "Battle Focus", "Bladestorm"])
    
    
    # twinlinkedShCannon=Weapon("Twin-Linked Shuriken Cannon",24,6,5,"shooting",shots= 3,specialRules=["Assault", "Bladestorm", "Twin-linked"])
    # twinlinkedShCatapult=Weapon("Twin-Linked Shuriken Catapult",12,4,5,"shooting",shots= 2,specialRules=["Assault", "Bladestorm", "Twin-Linked"])
    # windrider.addWeapon(twinlinkedShCannon)
    # windrider.addWeapon(twinlinkedShCatapult)
    
    # swoopingHawk=Model("Swooping Hawk",4,4,3,3,1,5,1,9,"4+",modelType="Jump Infantry")
    # swoopingHawkEx=Model("Swooping Hawk Exarch",5,5,3,3,1,6,2,9,"3+",modelType="Jump Infantry (Character)")
    # ru=["Ancient Doom", "Battle Focus", "Fleet", "Herald of Victory", "Skyleap", "Swooping Hawk Wings","Jump", "Bulky", "Deep Strike"]
    # swoopingHawk.addRules(ru)
    # swoopingHawk.addRule("Hammer of Wrath")
    # swoopingHawk.addBasic("Hammer of Wrath only applies according to the Jump rule")
    
    # swoopingHawkEx.addRules(ru)
    # swoopingHawkEx.addRule("Hammer of Wrath")
    # swoopingHawkEx.addBasic("Hammer of Wrath only applies according to the Jump rule")
    
    # grenadePack=Weapon("Grenade Pack",24,4,4,"shooting",specialRules=["Assault", "Ignores Cover", "Skyburst"])
    # swoopingHawk.addWeapon  (grenadePack)
    # swoopingHawkEx.addWeapon(grenadePack)
    
    # haywireGrenades=Weapon("Haywire Grenades",8,2,"-","shooting",specialRules=["Assault", "Haywire"])
    # swoopingHawk.addWeapon  (haywireGrenades)
    # swoopingHawkEx.addWeapon(haywireGrenades)
    
    # hawksTalon=Weapon("Hawk's Talon",24,5,5,"shooting",shots=3,specialRules=["Assault"])
    # swoopingHawkEx.addWeapon(hawksTalon)
    
    # lasblaster=Weapon("Lasblaster",24,3,5,"shooting",shots=3,specialRules=["Assault"])
    # swoopingHawk.addWeapon  (lasblaster)
    
    # swoopingHawk.addWeapon  (plasmaGrenades)
    # swoopingHawkEx.addWeapon(plasmaGrenades)
    
    
    
    # wraithlord=Model("Wraithlord",4,4,8,8,3,4,3,10,"3+")
    # wraithlord.addRules(["Ancient Doom", "Fearless"])
    # flamer=Weapon("Flamer","Template",4,5,"shooting",specialRules=["Assault"])
    # scatterLaser=Weapon("Scatter Laser",36,6,6,"shooting",shots=4,specialRules=["Heavy", "Laser Lock"])
    # starcannon=Weapon("Star Cannon",36,6,2,"shooting",specialRules=["Heavy"],shots= 2)
    # wraithlord.addWeapon(flamer)
    # wraithlord.addWeapon(scatterLaser)
    # wraithlord.addWeapon(starcannon)
    
    
    
    # interrogator=Model("Interrogator-Chaplain POP",5,5,4,4,3,5,3,10,"3+", inv="4+")
    # #interrogator.addRules(["Independent Character", "Zealot","Inner Circle", "Fearless", "Preferred Enemy (Chaos Space Marines)", "Rosarius", "Auspex", "Digital Weapons","Porta-Rack","Power-Field Generator", "Shroud of Heroes"])
    # interrogator.addRules(["Independent Character", "Zealot","Inner Circle", "Fearless", "Preferred Enemy (Chaos Space Marines)",  "Digital Weapons"])
    # crozius=Weapon("Crozius Arcanum","-","+2","4","melee",specialRules=["Melee", "Concussive"])
    fragGrenades=Weapon("Frag Grenades",8,3,"-","shooting",specialRules=["Assault","Blast","No Charge/Cover Penalty"])
    krakA=Weapon("Krak Grenades (thrown)",8,6,4,"shooting",specialRules=["Assault"])
    krakB=Weapon("Krak Grenades (melee)","-",6,4,"melee",specialRules=["Vehicle/MC only","Grenade"])
    meltaBombs=Weapon("Melta Bombs","-",8,1,"melee",specialRules=["Armourbane","Grenade","Unwieldy","Vehicle/MC only"])
    stormBolter=Weapon("Storm Bolter",24,4,5,"shooting",specialRules=["Assault"],shots=2)
    plasmaPistol=Weapon("Plasma Pistol",12,7,2,"shooting",specialRules=["Pistol"])
    boltPistol=Weapon("Bolt Pistol", 12,4,5,"shooting",specialRules=["Pistol"])
    # interrogator.addWeapons([crozius, plasmaPistol, fragGrenades,krakA,krakB, meltaBombs])
    

    # tacMarine=Model("Tactical MArine",4,4,4,4,1,4,1,8,"3+",modelType="Infantry")
    # tacMarine.addRules(["And They Shall Know No Fear","Grim Resolve","Stubborn", "Combat Squads"])

    # boltGun=Weapon("Bolt Gun", 24,4,5,"shooting",specialRules=["Rapid Fire"], shots="1 (full range)/2 (half range)")
    # plasmaCannon=Weapon("Plasma Cannon",36,7,2,"shooting",specialRules=["Heavy 1", "Blast", "Gets Hot"], shots=1)
    # tacMarine.addWeapon(boltPistol)
    # tacMarine.addWeapon(boltGun)
    # tacMarine.addWeapon(fragGrenades)
    # tacMarine.addWeapon(krakA)
    # tacMarine.addWeapon(krakB)
    # tacMarine.addWeapon(plasmaCannon)
    # tacMarine.addBasic("One squad member has a plasma cannon")

    # celestine=Model("Saint Celestine",7,7,3,3,3,7,5,10,"2+", modelType="Jump Infantry")
    # celestine.addRules(["Beacon of Faith", "Act of Faith", "Fearless", "Hit and Run", "Independent Character", "Martyrdom","Shield of Faith","Miraculous Intervention"])
    # ardent=Weapon("Ardent Blade ","Template",5,4,"shooting",specialRules=["Assault 1"])
    # celestine.addWeapon(ardent)


    # grot=Model("Gretchin (Grot)",2,3,2,2,1,2,1,5,"-","-",modelType="Infantry",rules=["It's a Grot's Life"] )
    # grotBlaster=Weapon("Grot Blasta",12,3,"-","shooting",specialRules=["Assault"])
    # grot.addWeapon(grotBlaster)

    nob=Model("Nob",4,2,4,4,2,3,3,7,"4+",modelType="Infantry")
    bigChoppa=Weapon("Big choppa","-", "+2","-","melee",specialRules=["Two-Handed"])
    nob.addWeapon(bigChoppa)
    # slugga=Weapon("Slugga",12,4,6,"shooting",specialRules=["pistol"])
    # nob.addWeapon(slugga)
    nob.addRules(["Mob Rule","Waaagh!","Furious Charge"])
    deffGun=Weapon("DeffGun",48,7,4,"shooting",shots="D3",specialRules=["Heavy"])
    nob.addWeapon(deffGun)
    nob.render(r)
    # runtherd=Model("Runtherd",4,2,3,4,1,2,2,7,"6+",modelType="Infantry")
    # runtherd.addRules(["Mob Rule","Waaagh!","Furious Charge","Squig Hound"])
    # grotprod=Weapon("Grot-Prod","-",1,"-","melee", specialRules=["Poisoned"])
    # runtherd.addWeapon(grotprod)
    # runtherd.addWeapon(slugga)

    # boy=Model("Ork Boy",4,2,3,4,1,2,2,7,"4+",modelType="Infantry", rules=["Furious Charge", "Mob Rule", "Waaagh!","'Eavy Armour"])
    # choppa=Weapon("Choppa","-", "+0","-","melee",specialRules=[])
    # boy.addWeapons([choppa,slugga])

    # shootaBoy=Model("Shoota Boy",4,2,3,4,1,2,2,7,"6+",modelType="Infantry", rules=["Furious Charge", "Mob Rule", "Waaagh!"])
    # shoota=Weapon("Shoota",18,4,6,"shooting",shots=2,specialRules=["Assault"])
    # shootaBoy.addWeapons([shoota])

    
    # gaz=Model("Ghazghkull",6,2,5,5,4,4,5,9,"2+" ,inv="5++")
    # gaz.addRules(["Furious Charge", "Independent Character", "Mob Rule", "Prophet of the Waaagh!","Mega Armour", "Slow and Purposeful","Bosspole","Adamantium Skull","Rage","Eternal Warrior","Cybork Body"])
    # stikk=Weapon("Stikkbombs",8,3,"-","shooting",specialRules=["Assault","Blast","No Charge/Cover Penalty"])
    # bigshoota=Weapon("Big Shoota",36,5,5,"shooting",shots=3,specialRules=["Assault"])
    # powerklaw=Weapon("Power Klaw","-","x2","2","melee", specialRules=["Specialist Weapon","Unwieldy"])
    # gaz.addWeapons([stikk,bigshoota,powerklaw])


    # deffkopta=Model("Deffkopta",4,2,3,5,2,2,2,7,"4+",modelType="Jetbike",rules=["Furious Charge", "Hit and Run", "Mob Rule", "Scouts"])
    # buzzsaw=Weapon("Buzzsaw","-","x2",2,"melee",specialRules=["Specialist Weapon", "Unwieldy"])
    # rokkitLauncha=Weapon("Rokkit Launcha",24,8,3,"shooting",specialRules=["Assault"])
    # deffkopta.addWeapons([buzzsaw,rokkitLauncha,choppa])

    # warboss=Model("Warboss Big Dingus",6,2,5,5,3,5,4,9,"4+" ,inv="5++")
    # warboss.addRules(["Furious Charge", "Independent Character", "Mob Rule", "'Eavy Armour", "Bosspole","Cybork Body", "Waaagh!"])
    # tlbigshoota=Weapon("Twin-Linked Shoota",18,4,6,"shooting",shots=2,specialRules=["Assault","Twin-Linked"])
    # warboss.addWeapons([tlbigshoota,powerklaw,stikk])

    # warbuggy=Vehicle("Warbuggy",2,10,10,10,modelType="Fast",rules=["Open-topped","Armour Plates","Grot Riggers","Red Paint Job", "Wartrakk"])
    # warbuggy.addWeapon(tlbigshoota)


#     tigurius=Model("Tigurius",5,4,4,4,3,4,2,10,"3+")
#     tigurius.addRules(["Hood of Hellfire","Storm of Fire","And They Shall Know No Fear", "Chapter Tactics (Ultramarines)", "Gift of Prescience","Independent Character","Master Psyker","Psyker ML3","Psychic Hood"])
#     tigurius.addBasic("Tigurius can generate powers from Biomancy, Divination, Pyromancy, Telekinesis and Telepathy tables")
#     tigurius.addWeapons([boltPistol,fragGrenades,krakA,krakB])
#     tiggerRod=Weapon("Rod of Tigurius","-","+2",4,"melee",specialRules=["Melee","Master-Crafted","Force","Concussive","Soul Blaze"])
#     tigurius.addWeapon(tiggerRod)
    
#     r=Rules("./rules.r")

#     r.rules["Gift of Prescience"]="If your army contains Tigurius, you can choose to re-roll any Reserve Rolls that apply to units from the same detachment- even successful ones. "
#     r.rules["Master Psyker"]="When generating psychic powers, Tigurius may re-roll any or all of the dice to see which powers he knows. "
#     r.rules["Hood of Hellfire"]="The Hood of Hellfire is a psychic hood. Furtl1ermore, it enables Tigurius to re-roll failed Psychic tests."
#     r.rules["Psychic Hood"]="Each time a unit (or rnodel) is targeted by an enemy psychic power and is within 6\" of a friendly model with a psychic hood, the wearer of the hood can attempt to Deny the Witch in their stead, as if he were in that unit. If a model with a psychic hood is embarked on a vehicle, he can only use the hood to protect the vehicle he is embarked upon."
#     r.rules["Storm of Fire"]="Warlord Trait: One use only. Declare your Warlord is using this ability at the start of one of your Shooting phases. For the duration of that phase, a single friendly unit from Codex: Space Marines within 12\" of the Warlord may re-roll any fai led To Hit rolls. "
#     r.rules["Chapter Tactics (Ultramarines)"]="""Combat Doctrines: This detachment can utilise each of the
# following Combat Doctrines once per game. To do so, at the
# start of your turn, state which doctrine you wish to use (if
# any)- that doctrine is in effect until the beginning of your
# next turn. You can only use one Combat Doctrine per turn.
# \\begin{description}
# \\item[Tactical Doctrine] Models in this detachment re-roll
# all To Hit ro lls of 1 made in the Shooting phase.
# Models in the detachment's Tactical Squads instead
# re-ro ll all failed To Hit rolls made in the Shooting phase.
# \\item[Assault Doctrine] Units in this detachment can re-roll
# their charge range. Models in the detachment's
# Assault Squads, Bike Squads and Attack Bike Squads
# instead have the Fleet special rule.
# \\item[Devastator Doctrine] Models in this detachment may
# re-roll To Hit with Snap Shot~ (including Overwatch
# shots) . In addition, models in the detachment's
# Devastator Squads have the Relentl ess special rule unless they
# disembark from a Transport in their Movement phase.
# \end{description}
# """
#     r.rules["Master-Crafted"]="Weapons with the Master-crafted rule allow the bearerto re-roll one failed roll To Hit per rurn with that weapon. "
#     r.rules["Grenade"]="Some grenades can be used both in the Shooting phase and the Assault phase, albeit to different effect. Only one grenade (of any type) can be thrown by a unit per Shooting phase."
#     r.rules["Melee"]="This is a melee weapon"
#     r.rules["Blast"]="Against vehicles, see BRB pp. 73.  Against other units, pp 33"
#     r.save()
#     tigurius.render(r)
    # r.rules["Wartrakk"]="Warbuggies are sometimes equipped with heavy duty trakk units. Any Warbuggy that has been upgraded to a Wartrakk or Skorcha may re-roll any Dangerous Terrain tests it must take. (Ork Codex pp. 49)"
    # r.rules["Armour Plates"]="An Ork vehicle with armour plates has extra thick sheets of metal welded onto its hull. It treats 'Crew Stunned' results as 'Crew Shaken' results instead."
    # r.rules["Grot Riggers"]=" When an Ork vehicle takes a hit, Grots will swarm out of its recesses and repair the damage. An Immobilised Ork vehicle with Grot riggers may roll a dice during the ork shooting phase - on a 4+ the Immobilised result is negated. The vehicle is able to start moving next turn." 
    # r.rules["Red Paint Job"]=" Orks believe that a vehicle that has been painted red can outstrip a similar vehicle that isn't. As odd as it may seem, they are quite right. Ork vehicles with red paint jobs add +1 to their move in the Movement phase but do not incur penalties for this extra inch. for example, a vehicle could move 13'' and still count as moving 12''."
    # r.save()
    # plasmarine.render(r)
    # ranger.render(r)
    # runtherd.render(r)
    # gaz.render(r)
    # nob.render(r)
    # warboss.render(r)
    # grot.render(r)
    # boy.render(r)
    # shootaBoy.render(r)
    # deffkopta.render(r)
    # warbuggy.render(r)
    # interrogator.render(r)
    # guardian.render(r)
    # windrider.render(r)
    #tacMarine.render(r)
    #celestine.render(r)


        
        # r.rules["Hatred"]="""Commonly, a model only has Hatred towards a specific type of foe, in which case, the unlucky target will be expressed, in brackets, after the special rule. This can refer to a whole army, or a specific unit from that army. For example, Hatred (Orks) would mean any model from Codex: Orks, whilst Hatred (Big Meks) would mean only Big Meks. A model striking a hated foe in close combat re-rolls all misses during the first round of each combat - he does not make re-rolls for Hatred in subsequent rounds.(Source: 40k Rulebook, p.37)"""
    # r.save()


    
    #  LocalWords:  sScorpion
    #r.rules["Monstrous Creature"]="SHOOTING: Monstrous Creatures can fire up to two of their weapons each Shooting phase - they must, of course, fire both of them at the same target. SPECIAL RULES: Monstrous Creatures have the fear, Hammer of Wrath, Move Through Cover, Relentless and Smash special rules."
    #r.save()
