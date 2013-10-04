from ruleGrab import Rules
validWeaponTypes=["shooting","melee"]
class Weapon(object):
    """
    """
    
    def __init__(self, name, range, strength,ap, weaponType, shots=1,specialRules=None,hitExtras="",woundExtras="", wielder=None):
        """
        
        Arguments:
        - `strength`:
        - `ap`:
        """
        self.shots=shots
        self.type=weaponType
        if not self.type in validWeaponTypes:
            raise TypeError("Weapon type must be one of %s"%str(validWeaponTypes))
        self.range=range
        self.name=name
        self.strength = strength
        self.ap = ap
        self.specialRules=[]
        for i in specialRules:
            self.addSpecialRule(i)
        self.hitExtras=hitExtras
        self.woundExtras=woundExtras
    def addSpecialRule(self,rule):
        if rule in self.specialRules:
            return
        else:
            self.specialRules.append(rule)
            if rule=="Sniper":
                self.addSpecialRule("Pinning")
                self.addSpecialRule("Rending")

    def woundProfile(self):
        toWound=" & ".join([str(shootToWoundIndividual(self.strength,n+1)) for n in range(10)])
        if "Sniper" in self.specialRules:
            toWound=" & ".join(["4"]*10)
        if "Fleshbane" in self.specialRules:
            toWound=" & ".join(["2"]*10)
        return """\\begin{{tabular}}{{l|l|l|l|l|l|l|l|l|l|l|}}
        \\begin{{turn}}{{90}}T\\end{{turn}} & 1 & 2 & 3 & 4 & 5 & 6 & 7 & 8 & 9 & 10 \\\\ \\hline
                \\begin{{turn}}{{90}}Roll\\end{{turn}} & {0}
        \\end{{tabular}}""".format(toWound)
                
    def canShootAfterMoving(self):
        if "Assault" in self.specialRules:
            return "Fire as normal, can assault"
        elif "Heavy" in self.specialRules:
            return "Fired only as snap-shots, cannot assault"
        elif "Ordnance" in self.specialRules:
            return "Cannot fire after moving"
        elif "Pistol" in self.specialRules:
            return "Fire as normal, can assault"
        elif "Rapid Fire" in self.specialRules:
            return "Can fire as normal after moving (1shot at full range, 2 at half or less), but cannot assault."
        elif "Salvo" in self.specialRules:
            return "Can fire using lower of the two values. Cannot assault after firing."
        else:
            return "This weapon doesn't seem to have a rule defined for this!"

        
#TODO: have master list of special rules to check against and also incorporate rule text in output

#TODO: exceptions to snap-shot stuff: relentless, etc. Check wielder

def shootToWoundIndividual(s,t):
    if s>=t+2:
        return 2
    elif s==t+1:
        return 3
    elif s==t:
        return 4
    elif s==t-1:
        return 5
    elif s in [t-2, t-3]:
        return 6
    else:
        return "-"
    


class Model(object):
    """
    """
    
    def __init__(self, name,bs,ws,s,t,w,i,a,ld,sv,inv="-", rerollHits="", rerollWounds="",rerollSaves="",rules=None, modelType="Infantry"):
        """
        """
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
        if rules!=None:
            self.rules=rules
        else:
            self.rules=[]
    def addBasic(self,info):
        self.extraBasics.append(info)
    def addRule(self,rule):
        if rule in self.rules:
            return
        if len(rule) >3 and rule[-3:].startswith("ML"):
            self.addRule("Psyker")
            self.addRule(rule[-3:])
            return
        self.rules.append(rule)
    def addRules(self,rules):
        for r in rules: self.addRule(r)
    def addWeapon(self,w):
        w.wielder=self
        self.weapons.append(w)
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
        return """\\begin{{tabular}}{{l|l|l|l|l|l|l|l|l|l|l|}}
            \\begin{{turn}}{{90}}Opp. WS\\end{{turn}} & 1 & 2 & 3 & 4 & 5 & 6 & 7 & 8 & 9 & 10 \\\\ \\hline
            \\begin{{turn}}{{90}}Roll\\end{{turn}} & {0}
            \\end{{tabular}}""".format(" & ".join([str(mapping[self.ws-1][n]) for n in range(10)]))        

    def shootToHit(self):
    
        return ["-","6","5","4","3","2","2/6","2/5","2/4","2/3","2/2"][self.bs]
    def shootToWound(self):
        out=[]
        for i in range(10):
            out.append(shootToWoundIndividual(self.s,(i+1)))
        return "| %11s "%"Toughness"+" ".join(["| %2d"%(n+1) for n in range(len(out))]) + " |\n"+"+"+"-"*13+"+----"*len(out)+"+\n"+"| %11s "%"Min roll"+" ".join(["| %2d"%(n) for n in out])+" |"

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
                """.format(w,rules="\\begin{description} %s \\end{description}"%("\n".join(["\\item[%s] %s"%(i,r[i]) for i in w.specialRules])),wounding=w.woundProfile(), assault=w.canShootAfterMoving(), range=w.range, apExtra={True:"/(2 on a 'to wound' roll of 6 - Rending)", False:""}["Rending" in w.specialRules])
            if w.type=="melee" or "Pistol" in w.specialRules:
                meleeCount+=1
            if "Specialist Weapon" in w.specialRules:
                meleeCount+=1000
            if w.type=="melee":# or "Pistol" in w.specialRules:
                strength=w.strength
                strength= str(strength).strip()
                if strength[0]=="+":
                    strength=strength+" (Total: %d)"%(int(self.s)+int(strength[1:]))
                assaultWeapons+=""" \\subsubsection{{{0.name}}}
                \\begin{{description}}
                \\item[Strength]{s}
                \\item[AP]{0.ap}
                \\end{{description}}
                \\subsubsection{{To Hit}}
                {hitting}
                \\subsubsection{{To Wound}}
                {wounding}                
                \\subsubsection{{Weapon Rules}}
                {rules}
                \\hrule
                """.format(w,s=strength,rules="\\begin{description} %s \\end{description}"%("\n".join(["\\item[%s] %s"%(i,r[i]) for i in w.specialRules])),hitting=self.assaultToHit(), wounding=w.woundProfile())
        if 1000<=meleeCount<2000 or meleeCount in [0,1]:
            meleeCount=0
        else:
            meleeCount=1


        profileAssault="""\\begin{{description}}
        \\item[Attacks]{attacks} (Remember to add an attack if charging) {extraAttacks} {hammerExtra}
        \\end{{description}}
        \\subsection{{Assault Weapons}}
        Does not include pistols. See above.
        {weapons}
        
        """.format(attacks=self.a+meleeCount, extraAttacks={True:"(Includes dual wielding bonus)",False:""}[meleeCount==1],weapons=assaultWeapons, hammerExtra={True:"(Remember to resolve \\textbf{Hammer of Wrath} wounds too)",False:""}["Hammer of Wrath" in self.rules])

        specialRules="\\begin{description} %s \\end{description}"%("\n".join(["\\item[%s] %s"%(i,r[i]) for i in self.rules]))
        out= """\\documentclass[10pt,a4paper,twocolumn]{{article}}
        \\title{{{0.name}}}
        \\author{{}} \\date{{}}
        \\usepackage[width=6.5in,height=8.5in]{{geometry}}
        \\usepackage{{multicol}}
        \\usepackage{{sectionbox}}
        \\usepackage{{rotating}}
        \\begin{{document}}
        \\maketitle
        \\begin{{sectionbox}}{{Basic}}
        \\begin{{tabular}}{{p{{2ex}}p{{2ex}}p{{2ex}}p{{2ex}}p{{2ex}}p{{2ex}}p{{2ex}}p{{2ex}}p{{2ex}}}}
         Bs & Ws & S & T & W & A & Ld & Sv & Inv \\\\ \\hline
         {0.bs} & {0.ws} & {0.s} & {0.t} & {0.w} & {0.a} & {0.ld} & {0.sv} & {0.inv}         
        \\end{{tabular}}
        \\begin{{itemize}}
        {extraBasic}
        \\end{{itemize}}
        \\subsection{{Weapons}}
        \\begin{{itemize}}
        {weaponShort}
        \end{{itemize}}
        \\end{{sectionbox}}
        \\section{{Shooting}}
        \\begin{{description}}
        \\item[To hit:] {toHit} {0.rerollHits}
        \\end{{description}}
        {shootingProfiles}
        \\section{{Assault}}
        {assaultProfile}
        \\section{{Special Rules}}
        %\\begin{{multicols}}{{2}}
        {rules}
        %\\end{{multicols}}

        \\end{{document}}
        """.format(self,toHit=self.shootToHit(),shootingProfiles=weaponProfilesShooting, rules=specialRules, assaultProfile=profileAssault, extraBasic="\n".join(["\\item %s"%d for d in self.extraBasics]), weaponShort="\n".join(["\\item %s (%s)"%(n.name, n.type[0].upper()) for n in self.weapons ]))
        return out


#TODO: bladestom in reroll info

pathfinder=Model("Pathfinder",4,4,3,3,1,5,1,8,5)
for n in ["Ancient Doom", "Battle Focus", "Bladestorm", "Fleet", "Infiltrate", "Move Through Cover", "Sharpshoot", "Shrouded", "Stealth"]:
    pathfinder.addRule(n) 
shuP=Weapon("Shuriken Pistol",12,4,5,"shooting",1,specialRules=["Pistol", "Bladestorm"])
pathfinder.addWeapon(Weapon("Ranger Long Rifle",36,"X",6,"shooting",1,specialRules=["Heavy","Sniper"]))
pathfinder.addWeapon(shuP)

scorpionCS=Weapon("Scorpion Chainsword","-","+1",6,"melee",specialRules=["Melee"])

farseer=Model("Farseer", 5,5,3,3,3,5,1,10,"-", inv="4++")
farseer.addRules(["Ancient Doom", "Battle Focus", "Fleet", "Independent Character", "Psyker ML3"])
farseer.addBasic("Choose psychic powers from Divination, Runes of Fate or Telepathy")
farseer.addWeapon(Weapon("WitchBlade","-","+0","-","melee",specialRules=["Melee","Armourbane","Fleshbane"]))
farseer.addWeapon(shuP)



#pathfinder.addWeapon(scorpionCS)
    
# #        

#sm=Model("Bog Standard Marine", 3,3,3,4,1,1,7,3)
# guardian=Model("Eldar Guardian",4,3,3,3,1,1,7,5)
# guardian.addRule("Battle Focus")
# guardian.addRule("Girly Space Elf")
# guardian.addWeapon(Weapon("Shuriken Catapult",12,3,5,"shooting",shots=2,specialRules=["Bladestorm","Assault"]))
# guardian.addWeapon(Weapon("Shuriken Catapult crap",12,1,5,"shooting",shots=2,specialRules=["Bladestorm","Assault"]))
# guardian.addWeapon(Weapon("Shuriken Catapult awesome",12,10,5,"shooting",shots=2,specialRules=["Bladestorm","Assault"]))

r=Rules("/home/james/tmp/easyList/rules.r")
# r.rules["ML1"]="Psyker mastery level 1"
# r.rules["ML2"]="Psyker mastery level 2"
# r.rules["ML3"]="Psyker mastery level 3"
# r.save()
#print shootToHit(9)
#print shootToWound(4)
print farseer.createSheet(r)
#print guardian.createSheet(r)
