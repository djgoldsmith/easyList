validWeaponTypes=["shooting","melee"]
class Weapon(object):
    """
    """
    
    def __init__(self, name, strength,ap, weaponType, shots=1,specialRules=[],hitExtras="",woundExtras="", wielder=None):
        """
        
        Arguments:
        - `strength`:
        - `ap`:
        """
        self.shots=shots
        self.type=weaponType
        if not self.type in validWeaponTypes:
            raise TypeError("Weapon type must be one of %s"%str(validWeaponTypes))
        self.name=name
        self.strength = strength
        self.ap = ap
        self.specialRules=specialRules
        self.hitExtras=hitExtras
        self.woundExtras=woundExtras
    def woundProfile(self):
        return """\\begin{{tabular}}{{|l|l|l|l|l|l|l|l|l|l|l|}}
        Target Toughness & 1 & 2 & 3 & 4 & 5 & 6 & 7 & 8 & 9 & 10 \\\\ \\hline
        Min. Roll & {0}
        \\end{{tabular}}""".format(" & ".join([str(shootToWoundIndividual(self.strength,n+1)) for n in range(10)]))
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
    
    def __init__(self, name,bs,ws,s,t,w,a,ld,sv,inv, rerollHits="", rerollWounds="",rerollSaves=""):
        """
        """
        self.name=name
        self.bs=bs
        self.ws=ws
        self.s=s
        self.t=t
        self.w=w
        self.a=a
        self.ld=ld
        self.sv=sv
        self.inv=inv
        self.rerollHits=  rerollHits
        self.rerollWounds=rerollWounds
        self.rerollSaves= rerollSaves
        self.weapons=[]
    def addWeapon(self,w):
        w.wielder=self
        self.weapons.append(w)
    def shootToHit(self):
    
        return ["-","6","5","4","3","2","2/6","2/5","2/4","2/3","2/2"][self.bs]
    def shootToWound(self):
        out=[]
        for i in range(10):
            out.append(shootToWoundIndividual(self.s,(i+1)))
        return "| %11s "%"Toughness"+" ".join(["| %2d"%(n+1) for n in range(len(out))]) + " |\n"+"+"+"-"*13+"+----"*len(out)+"+\n"+"| %11s "%"Min roll"+" ".join(["| %2d"%(n) for n in out])+" |"

    def createSheet(self):
        weaponProfiles=""
        for w in self.weapons:
            if w.type=="shooting":
                weaponProfiles+="""\\subsection{{{0.name}}}
                \\begin{{description}}
                \\item[Shots]{0.shots}
                \\item[Strength]{0.strength}
                \\item[AP]{0.ap}
                \\item[Special rules]{rules}
                \\item[Move/Fire/Assault]{assault}
                \\end{{description}}
                {wounding}""".format(w,rules="|".join(w.specialRules),wounding=w.woundProfile(), assault=w.canShootAfterMoving())
        out= """\\documentclass[12pt,a4paper]{{article}}
        \\title{{{0.name}}}
        \\author{{}} \\date{{}}
        \\usepackage{{geometry}}
        \\begin{{document}}
        \\maketitle
        \\section{{Basic}}
        \\begin{{tabular}}{{p{{7mm}}p{{7mm}}p{{7mm}}p{{7mm}}p{{7mm}}p{{7mm}}p{{7mm}}p{{7mm}}p{{7mm}}}}
         Bs & Ws & S & T & W & A & Ld & Sv & Inv \\\\ \\hline
         {0.bs} & {0.ws} & {0.s} & {0.t} & {0.w} & {0.a} & {0.ld} & {0.sv} & {0.inv}         
        \\end{{tabular}}
        \\section{{Shooting}}
        \\begin{{description}}
        \\item[To hit:] {toHit} {0.rerollHits}
        \\end{{description}}
        {profiles}
        \\end{{document}}
        """.format(self,toHit=self.shootToHit(),profiles=weaponProfiles)
        return out


#TODO: bladestom in reroll info
sm=Model("Bog Standard Marine", 3,3,3,4,1,1,7,3,"-")
guardian=Model("Eldar Guardian",4,3,3,3,1,1,7,5,"-")
guardian.addWeapon(Weapon("Shuriken Catapult",3,5,"shooting",shots=2,specialRules=["Bladestorm","Assault"]))

guardian.addWeapon(Weapon("Shuriken Catapult crap",1,5,"shooting",shots=2,specialRules=["Bladestorm","Assault"]))
guardian.addWeapon(Weapon("Shuriken Catapult awesome",10,5,"shooting",shots=2,specialRules=["Bladestorm","Assault"]))
#print shootToHit(9)
#print shootToWound(4)
print guardian.createSheet()
