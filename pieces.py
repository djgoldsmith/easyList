from ruleGrab import Rules
#TODO: turn all dict checks into fn calls that ignore cover
validWeaponTypes=["shooting","melee"]
toHitStats=["-","6","5","4","3","2","2/6","2/5","2/4","2/3","2/2"]
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
        self.shots=shots
        self.type=weaponType
        if not self.type in validWeaponTypes:
            raise TypeError("Weapon type must be one of %s"%str(validWeaponTypes))
        self.range=range
        self.name=name
        self.strength = strength
        self.ap = ap
        self._specialRules=[]
        for i in specialRules:
            self.addSpecialRule(i)
        self.hitExtras=hitExtras
        self.woundExtras=woundExtras
    def hasRule(self,thing):
        for i in self._specialRules:
            if i.upper()==thing.upper(): return True
        return False
    def addSpecialRule(self,rule):
        if self.hasRule(rule):
            return
        else:
            self._specialRules.append(rule)
            if rule=="Sniper":
                self.addSpecialRule("Pinning")
                self.addSpecialRule("Rending")
    
        
    def woundProfile(self):
        toWound=[str(shootToWoundIndividual(self.strength,n+1)) for n in range(10)]

        if self.hasRule("Bladestorm"):
            for i in range(len(toWound)):
                if toWound[i]=="-":
                    toWound[i]="6"
        toWound=" & ".join(toWound)
        if self.hasRule("Sniper"):
            toWound=" & ".join(["4"]*10)
        if self.hasRule("Fleshbane"):
            toWound=" & ".join(["2"]*10)
        return """\\begin{{tabular}}{{l|l|l|l|l|l|l|l|l|l|l|}}
        \\begin{{turn}}{{90}}T\\end{{turn}} & 1 & 2 & 3 & 4 & 5 & 6 & 7 & 8 & 9 & 10 \\\\ \\hline
                \\begin{{turn}}{{90}}Roll\\end{{turn}} & {0}
        \\end{{tabular}}""".format(toWound)
                
    def canShootAfterMoving(self):
        if self.hasRule("Assault"):
            return "Fire as normal, can assault"
        elif self.hasRule("Heavy"):
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
    def hasRule(self,rule):
        for i in self.rules:
            if i.upper()==rule.upper():
                return True
        return False
    def addRule(self,rule):
        if self.hasRule(rule):
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
        return """\\begin{{tabular}}{{l|l|l|l|l|l|l|l|l|l|l|}}
            \\begin{{turn}}{{90}}Opp. WS\\end{{turn}} & 1 & 2 & 3 & 4 & 5 & 6 & 7 & 8 & 9 & 10 \\\\ \\hline
            \\begin{{turn}}{{90}}Roll\\end{{turn}} & {0}
            \\end{{tabular}}""".format(" & ".join([str(mapping[self.ws-1][n]) for n in range(10)]))        

    def shootToHit(self):
    
        return toHitStats[self.bs]
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
                """.format(w,rules="\\begin{description} %s \\end{description}"%("\n".join(["\\item[%s] %s"%(i,r[i]) for i in w._specialRules])),wounding=w.woundProfile(), assault=w.canShootAfterMoving(), range=w.range, apExtra={True:"/(2 on a 'to wound' roll of 6 - Rending)", False:""}[w.hasRule("Rending")])
            if not w.hasRule("Grenade") and (w.type=="melee" or w.hasRule("Pistol")):
                meleeCount+=1
            if w.hasRule("Specialist Weapon"):
                meleeCount+=1000
            if w.type=="melee":# or "Pistol" in w.specialRules:
                strength=w.strength
                strength= str(strength).strip()
                if strength[0]=="+":
                    strength=strength+" (Total: %d)"%(int(self.s)+int(strength[1:]))
                elif strength.upper()=="USER":
                    strength="User (%d)"%self.s
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
                """.format(w,s=strength,rules="\\begin{description} %s \\end{description}"%("\n".join(["\\item[%s] %s"%(i,r[i]) for i in w._specialRules])),hitting=self.assaultToHit(), wounding=w.woundProfile())
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
        profileAssault="""\\begin{{description}}
        \\item[Attacks]{attacks} (Remember to add an attack if charging) {extraAttacks} {hammerExtra}
        \\end{{description}}
        \\subsection{{Melee Weapons}}
        Does not include pistols. See above.
        {weapons}
        
        """.format(attacks=self.a+meleeCount, extraAttacks=extraAttacks,weapons=assaultWeapons, hammerExtra={True:"(Remember to resolve \\textbf{Hammer of Wrath} wounds too)",False:""}["Hammer of Wrath" in self.rules])
        weaponShort="""        \\begin{itemize}
        %s
        \end{itemize}"""%("\n".join(["\\item %s (%s)"%(n.name, n.type[0].upper()) for n in self.weapons ]))
        if len(self.weapons)<1: weaponShort="This model has no weapons"
        specialRules="\\begin{description} %s \\end{description}"%("\n".join(["\\item[%s] %s"%(i,r[i]) for i in self.rules]))
        if len(self.rules)<1: specialRules="This model has no special rules."
        out= """\\documentclass[10pt,a4paper,twocolumn]{{article}}
        \\title{{{0.name}}}
        \\author{{{modelT}}} \\date{{}}
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
        {extraBasic}
        \\subsection{{Weapons}}
        {weaponShort}
        \\end{{sectionbox}}
        \\section{{Shooting}}
        \\begin{{description}}
        \\item[To hit:] {toHit} {0.rerollHits}
        \\end{{description}}
        {shootingProfiles}
        \\section{{Assault/Melee}}
        {assaultProfile}
        \\section{{Special Rules}}
        %\\begin{{multicols}}{{2}}
        {rules}
        %\\end{{multicols}}

        \\end{{document}}
        """.format(self,toHit=self.shootToHit(),shootingProfiles=weaponProfilesShooting, rules=specialRules, assaultProfile=profileAssault, extraBasic=extraBasic, weaponShort=weaponShort,modelT=self.type)
        return out


if __name__=="__main__":
        
    #TODO: bladestom in reroll info
    
    pathfinder=Model("Pathfinder",4,4,3,3,1,5,1,8,5)
    for n in ["Ancient Doom", "Battle Focus", "Bladestorm", "Fleet", "Infiltrate", "Move Through Cover", "Sharpshoot", "Shrouded", "Stealth"]:
        pathfinder.addRule(n) 
    shuP=Weapon("Shuriken Pistol",12,4,5,"shooting",1,specialRules=["Pistol", "Bladestorm"])
    pathfinder.addWeapon(Weapon("Ranger Long Rifle",36,"X",6,"shooting",1,specialRules=["Heavy","Sniper"]))
    pathfinder.addWeapon(shuP)
    
    scorpionCS=Weapon("Scorpion Chainsword","-","+1",6,"melee",specialRules=["Melee"])
    
    farseer=Model("Farseer", 5,5,3,3,3,5,1,10,"-", inv="4++", modelType="Infantry (Character)")
    farseer.addRules(["Ancient Doom", "Battle Focus", "Fleet", "Independent Character", "Psyker ML3"])
    farseer.addBasic("Choose psychic powers from Divination, Runes of Fate or Telepathy")
    farseer.addWeapon(Weapon("WitchBlade","-","User","-","melee",specialRules=["Melee","Armourbane","Fleshbane"]))
    farseer.addWeapon(shuP)
    #TODO: hatred (breackets), preferred enemy (brackets)
    illic=Model("Illic Nightspear",6,9,3,3,3,6,3,10,"5+",modelType="Infantry (Character)")
    
    illic.addRules([ "Ancient Doom", "Battle Focus", "Bladestorm", "Distort", "Fleet", "Hatred (Necrons)", "Independent Character", "Infiltrate", "Preferred Enemy (Necrons)", "Sharpshoot", "Shrouded", "Walker of the Hidden Path", "Master of Pathfinders", "Mark of the Incomparable Hunter"])
    illic.addWeapon(Weapon("Voidbringer",48,"X",2,"shooting",specialRules=["Heavy", "Distort", "Sniper"]))
    illic.addWeapon(shuP)
    
    
    plasmaGrenades=Weapon("Plasma Grenades","8/-",4,4,"shooting",specialRules=["Assault","Blast","No Charge/Cover Penalty"])
    #Assault 1, Blast / - Bearer suffers no Initiave penalty for charging through cover
    sScorpion=Model("Striking Scorpion",4,4,3,3,1,5,1,9,"3+")
    sScorpion.addWeapon(scorpionCS)
    sScorpion.addRule("Mandiblasters")
    sScorpion.addWeapon(shuP)
    sScorpion.addWeapon(plasmaGrenades)
    sScorpion.addRules(["Ancient Doom", "Battle Focus", "Fleet", "Infiltrate", "Move Through Cover", "Stealth"])
    # mandiblasters=Weapon("Mandiblasters","-",3,"-","melee",specialRules=["Mandiblasters"])
    # sScorpion.addWeapon(mandiblasters)
    #pathfinder.addWeapon(scorpionCS)
    
    
    direAvenger=Model("Dire Avenger",4,4,3,3,1,5,1,9,"4+")
    
    direAvenger.addWeapon(Weapon("Avenger Shuriken Catapult",18,4,5,"shooting",shots=2,specialRules=["Assault","Bladestorm"]))
    direAvenger.addWeapon(plasmaGrenades)
    direAvenger.addRules(["Ancient Doom", "Battle Focus", "Counter-attack", "Fleet"])
    
    # #        
    
    #sm=Model("Bog Standard Marine", 3,3,3,4,1,1,7,3)
    guardian=Model("Eldar Guardian",4,4,3,"3(5)",1,5,1,8,"5(3)+")
    guardian.addRules(["Battle Focus","Ancient Doom","Bladestorm", "Fleet"])
    
    guardian.addWeapon(Weapon("Shuriken Catapult",12,4,5,"shooting",shots=2,specialRules=["Bladestorm","Assault"]))
    guardian.addWeapon(plasmaGrenades)
    hwp=Weapon("Heavy Weapon Platform (Shuriken Cannon)",24,6,5,"shooting",shots=3,specialRules=["Assault","Bladestorm","HWP"])
    guardian.addWeapon(hwp)
    
    windrider=Model("Windrider",4,4,3,4,1,5,1,8,"3+", modelType="Eldar Jetbike")
    windrider.addRules(["Ancient Doom", "Battle Focus", "Bladestorm"])
    
    
    twinlinkedShCannon=Weapon("Twin-Linked Shuriken Cannon",24,6,5,"shooting",shots= 3,specialRules=["Assault", "Bladestorm", "Twin-linked"])
    twinlinkedShCatapult=Weapon("Twin-Linked Shuriken Catapult",12,4,5,"shooting",shots= 2,specialRules=["Assault", "Bladestorm", "Twin-Linked"])
    windrider.addWeapon(twinlinkedShCannon)
    windrider.addWeapon(twinlinkedShCatapult)
    
    swoopingHawk=Model("Swooping Hawk",4,4,3,3,1,5,1,9,"4+",modelType="Jump Infantry")
    swoopingHawkEx=Model("Swooping Hawk Exarch",5,5,3,3,1,6,2,9,"3+",modelType="Jump Infantry (Character)")
    ru=["Ancient Doom", "Battle Focus", "Fleet", "Herald of Victory", "Skyleap", "Swooping Hawk Wings","Jump", "Bulky", "Deep Strike"]
    swoopingHawk.addRules(ru)
    swoopingHawk.addRule("Hammer of Wrath")
    swoopingHawk.addBasic("Hammer of Wrath only applies according to the Jump rule")
    
    swoopingHawkEx.addRules(ru)
    swoopingHawkEx.addRule("Hammer of Wrath")
    swoopingHawkEx.addBasic("Hammer of Wrath only applies according to the Jump rule")
    
    grenadePack=Weapon("Grenade Pack",24,4,4,"shooting",specialRules=["Assault", "Ignores Cover", "Skyburst"])
    swoopingHawk.addWeapon  (grenadePack)
    swoopingHawkEx.addWeapon(grenadePack)
    
    haywireGrenades=Weapon("Haywire Grenades",8,2,"-","shooting",specialRules=["Assault", "Haywire"])
    swoopingHawk.addWeapon  (haywireGrenades)
    swoopingHawkEx.addWeapon(haywireGrenades)
    
    hawksTalon=Weapon("Hawk's Talon",24,5,5,"shooting",shots=3,specialRules=["Assault"])
    swoopingHawkEx.addWeapon(hawksTalon)
    
    lasblaster=Weapon("Lasblaster",24,3,5,"shooting",shots=3,specialRules=["Assault"])
    swoopingHawk.addWeapon  (lasblaster)
    
    swoopingHawk.addWeapon  (plasmaGrenades)
    swoopingHawkEx.addWeapon(plasmaGrenades)
    
    
    
    wraithlord=Model("Wraithlord",4,4,8,8,3,4,3,10,"3+")
    wraithlord.addRules(["Ancient Doom", "Fearless"])
    flamer=Weapon("Flamer","Template",4,5,"shooting",specialRules=["Assault"])
    scatterLaser=Weapon("Scatter Laser",36,6,6,"shooting",shots=4,specialRules=["Heavy", "Laser Lock"])
    starcannon=Weapon("Star Cannon",36,6,2,"shooting",specialRules=["Heavy"],shots= 2)
    wraithlord.addWeapon(flamer)
    wraithlord.addWeapon(scatterLaser)
    wraithlord.addWeapon(starcannon)
    
    
    
    interrogator=Model("Interrogator-Chaplain `POP'",5,5,4,4,3,5,3,10,"3+", inv="4+", modelType="Independant Character")
    #interrogator.addRules(["Independant Character", "Zealot","Inner Circle", "Fearless", "Preferred Enemy (Chaos Space Marines)", "Rosarius", "Auspex", "Digital Weapons","Porta-Rack","Power-Field Generator", "Shroud of Heroes"])
    interrogator.addRules(["Independant Character", "Zealot","Inner Circle", "Fearless", "Preferred Enemy (Chaos Space Marines)",  "Digital Weapons"])
    crozius=Weapon("Crozius Arcanum","-","+2","4","melee",specialRules=["Melee", "Concussive"])
    fragGrenades=Weapon("Frag Grenades",8,3,"-","shooting",specialRules=["Assault","Blast","No Charge/Cover Penalty"])
    krakA=Weapon("Krak Grenades (thrown)",8,6,4,"shooting",specialRules=["Assault"])
    krakB=Weapon("Krak Grenades (melee)","-",6,4,"melee",specialRules=["Vehicle/MC only","Grenade"])
    meltaBombs=Weapon("Melta Bombs","-",8,1,"melee",specialRules=["Armourbane","Grenade","Unwieldy","Vehicle/MC only"])
    stormBolter=Weapon("Storm Bolter",24,4,5,"shooting",specialRules=["Assault"],shots=2)
    plasmaPistol=Weapon("Plasma Pistol",12,7,2,"shooting",specialRules=["Pistol"])
    interrogator.addWeapons([crozius, plasmaPistol, fragGrenades,krakA,krakB, meltaBombs])
    
    
    
    r=Rules("/home/james/tmp/easyList/rules.r")
    # r.rules["Porta-Rack"]="f the bearer kills an enemy character in close combat he gains Preferred Enemy (current enemy) and Fear. In addition any enemy Teleport Homers and Locator Beacons can be used as if they were your own."
    # r.rules["Power-Field Generator"]="All models within 3\" have 4++"
    # r.rules["Digital Weapons"]="Re-roll a single failed to wound roll in the assault phase"
    # r.rules["Shroud of Heroes"]="Grants Feel No Pain (5+), in addition as long as the wearer is not in a unit he has Shrouded"
    # r.rules["Auspex"]="Forego shooting to make an enemy unit within 12\" reduce it's cover save by 1, untill the end of the phase"
    #r.rules["HWP"]="Platform has it's own toughness and save, shown in brackets. To do: write the rest of this."
    #r.rules["Jump"]="Jump units can move over all other models and terrain freely.  Begin/end in diff. terrain = dangerous terrain test. Jump move n movement or assault, not both.  Movement: move up to 12\". Assault: re-roll distance and gain Hammer of Wrath for the turn. When falling back, move 3d6\". Confers Bulky and Deep Strike rules."
    #r.rules["Twin-Linked"]="Re-roll misses"
    #r.rules["No Charge/Cover Penalty"]="Bearer suffers no Initiative penalty for charging through cover"
    #r.rules["Mandiblasters"]="At I10 a model with mandiblasters inflicts a S3 AP- hit on one enemy model in base contact"
    # r.rules["ML1"]="Psyker mastery level 1"
    # r.rules["ML2"]="Psyker mastery level 2"
    # r.rules["ML3"]="Psyker mastery level 3"
    #r.save()
    #print shootToHit(9)
    #print shootToWound(4)
    #print direAvenger.createSheet(r)
    #print guardian.createSheet(r)
    #print swoopingHawk.createSheet(r)
    #print swoopingHawkEx.createSheet(r)
    #print wraithlord.createSheet(r)
    #print interrogator.createSheet(r)
    import subprocess
    p=subprocess.Popen(["pdflatex", "-jobname",sanitiseName(interrogator.name)], stdin=subprocess.PIPE)
    p.communicate(interrogator.createSheet(r))
    p.wait()
    #  LocalWords:  sScorpion
