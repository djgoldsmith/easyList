"""
Classes to describe Models and Units
"""

from ruleGrab import Rules
from pieces import Model, Weapon
import weapons
# Weapon("Shard of Anaris","-","+2","-","melee",specialRules=["Melee","Rending","Vaul's Work"])

class Farseer(Model):
    """
    """
    
    def __init__(self, jetbike=False, spear=False):
        """
        
        Arguments:
        - `jetbike`:
        """
        self._jetbike = jetbike
        armour="-"
        toughness=3
        name="Farseer"
        rules=["Ancient Doom", "Battle Focus", "Fleet",  "Psyker ML3","Ghosthelm"]
        if jetbike:
            toughness+=1
            name+=" (Jetbike)"
            rules+=["Hammer of Wrath", "Jink", "Relentless"]
            armour=3
        else:
            rules.append("Independent Character")
            
        Model.__init__(self,"Farseer", 5,5,3,toughness,3,5,1,10,armour, inv="4++", modelType="Infantry" if not jetbike else "Eldar Jetbike")
        self.addRules(rules)
        self.addBasic("Choose psychic powers from Divination, Runes of Fate or Telepathy")
        if spear:
            self.addWeapons(weapons.singingSpearDuo)
        else:
            self.addWeapon(weapons.witchBlade)
        self.addWeapon(weapons.shurikenPistol)
        if jetbike:
            self.addWeapon(weapons.twinlinkedShurikenCatapult)

class DireAvenger(Model):
    def __init__(self, name="Dire Avenger"):        
        Model.__init__(self,name,4,4,3,3,1,5,1,9,"4+")
        self.addWeapon(Weapon("Avenger Shuriken Catapult",18,4,5,"shooting",shots=2,specialRules=["Assault","Bladestorm"]))
        self.addWeapon(weapons.plasmaGrenades)
        self.addRules(["Ancient Doom", "Battle Focus", "Counter-attack", "Fleet"])
class Guardian(Model):
    def __init__(self, name="Guardian"):
        Model.__init__(self,name,4,4,3,3,1,5,1,8,"5+")
        self.addRules(["Battle Focus","Ancient Doom","Bladestorm", "Fleet"])

        self.addWeapon(Weapon("Shuriken Catapult",12,4,5,"shooting",shots=2,specialRules=["Bladestorm","Assault"]))
        self.addWeapon(weapons.plasmaGrenades)


class EldarSupportWeapon(Model):
    def __init__(self, name="Heavy Weapon Platform"):
        Model.__init__(self,name,0,0,0,5,0,0,0,0,"3+")

        
        self.addWeapon(weapons.scatterLaser)
        self.addRule("Relentless")
        


    
class Wraithlord(Model):
    def __init__(self, name):
        Model.__init__(self,name,4,4,8,8,3,4,3,10,"3+")
        self.addRules(["Ancient Doom", "Fearless","Monstrous Creature"])

        flamer=Weapon("Flamer","Template",4,5,"shooting",specialRules=["Assault"])
        scatterLaser=Weapon("Scatter Laser",36,6,6,"shooting",shots=4,specialRules=["Heavy", "Laser Lock"])
        starCannon=Weapon("Star Cannon",36,6,2,"shooting",specialRules=["Heavy"],shots= 2)
        shurikenCatapult=Weapon("Shuriken Catapult",12,4,5,"shooting",shots=2,specialRules=["Bladestorm","Assault"])
        shurikenCannon=Weapon("Shuriken Cannon",24,6,5,"shooting",shots= 3,specialRules=["Assault", "Bladestorm"])
        brightLance=Weapon("Bright Lance",36,8,2,"shooting",shots= 1,specialRules=["Heavy", "Lance"])
        ghostGlave=Weapon("Ghost Glave","-","+1",2,"melee",specialRules=["Master-Crafted"])
        self.weaponPool={a.name:a for a in [flamer,scatterLaser,starCannon, shurikenCatapult, shurikenCannon, brightLance, ghostGlave]}
        #self.addWeapons([scatterLaser, shurikenCatapult,shurikenCatapult, shurikenCannon,shurikenCannonTL,brightLance, brightLanceTL])
        #self.addWeapons([scatterLaser, shurikenCannon,flamer])


        #self.addWeapons([shurikenCatapult])

class SpaceMarine(Model):
    def __init__(self, name):      

        Model.__init__(self,name,4,4,4,4,1,4,1,8,"3+",modelType="Infantry")
        self.addRules(["And They Shall Know No Fear", "Combat Squads"])
        self.addWeapon(weapons.boltPistol)

class Ravenwing(SpaceMarine):
    def __init__(self,name="RavenWing"):
        Model.__init__(self,name,4,4,4,5,1,4,1,8,"3+",modelType="Bike")
        self.addRules(["And They Shall Know No Fear", "Ravenwing Combat Squads", "Scouts", "Hit & Run", "Grim Resolve","Teleport Homer"])
        self.addWeapon(weapons.boltPistol.tl())
        #self.addWeapon(weapons.meltaGun)
        self.addWeapon(weapons.fragGrenade)
        self.addWeapon(weapons.krakGrenade)
        self.addWeapon(weapons.plasmaGun)        
        

class Librarian(SpaceMarine):
    def __init__(self,name="Librarian", ml=2):
        SpaceMarine.__init__(self,name)
        self.ws=5
        self.w=2
        self.a=2
        self.ld=10
        self.rules.remove("Combat Squads")
        self.addRules(["Independent Character", "Psyker ML%d"%ml])

class Avatar(Model):
    def __init__(self, name="Avatar of Khaine", fastShot=False, crushingBlow=False):
        """
        
        Arguments:
        - `name`:
        """
        Model.__init__(self,name,10,10,6,6,5,10,5,10,"3+",inv="5+",modelType="Infantry")
        self.addRules(["Ancient Doom","Battle Focus", "Daemon", "Fearless", "Fleet", "Khaine Awakened", "Molten Body"])
        self.addWeapon(Weapon("Wailing Doom",12, 8, 1, "shooting", shots=(1 if (not fastShot) else 2), specialRules=["Assault 1", "Melta"]))
        self.addWeapon(Weapon("Wailing Doom (melee)","-", "User", 1, "melee"))
        if crushingBlow:
            self.s+=1
        
class Terminator(Model):
    def __init__(self, name, stormShield=False):      

        Model.__init__(self,name,4,4,4,4,1,4,2,9,"2+",inv="5+",modelType="Infantry")
        self.addRules(["And They Shall Know No Fear"])

        self.addWeapons([weapons.boltGun,weapons.boltPistol])
        if stormShield:
            self.inv="3+"
        
class Scout(Model):
    def __init__(self, name):
        """
        
        Arguments:
        - `name`:
        """
        

        Model.__init__(self,name,3,3,4,4,1,4,1,8,"4+",modelType="Infantry")
        self.addWeapon(Weapon("Sniper Rifle",36,"X",6,"shooting",1,specialRules=["Heavy","Sniper"]))
class Ranger(Model):
    """
    """
    
    def __init__(self, name):
        """
        
        Arguments:
        - `name`:
        """
        Model.__init__(self,name,4,4,3,3,1,5,1,8,"5+",modelType="Infantry")
        rangerLR=Weapon("Ranger Long Rifle",36,"X",6,"shooting",1,specialRules=["Heavy","Sniper"])


    

        self.addRules(["Ancient Doom", "Battle Focus", "Bladestorm", "Fleet", "Infiltrate", "Move Through Cover", "Outflank", "Stealth"])
        self.addWeapon(rangerLR)



class Celestine(Model):
    """
    """
    
    def __init__(self, name="Saint Celestine"):
        """
        
        Arguments:
        - `name`:
        """
        Model.__init__(self,name,5,5,4,5,3,9,3,9,"3+",modelType="Infantry")
        

    

        self.addRules([ "Fleet", "Infiltrate", "Move Through Cover", "Outflank","Smash", "Relentless"])
        self.addWeapon(Weapon("Heavy Bolter","36\"",5,4,"shooting",shots=3,specialRules=["Heavy"]))
        self.addWeapon(Weapon("Flamer","Template",4,5,"shooting",specialRules=["Assault"]))
                       
        

        

if __name__ == '__main__':
    w=Wraithlord("Wraithlord")
    c=Celestine("Sororitas Sister")
    
    s=Scout("Scout")
    r=Rules("./rules.r")
    c.render(r)
    fs=Farseer(jetbike=True)
    #fs.render(r)
    w.render(r)
    #s.render(r)
    rn=Ranger("Rangern")
    #rn.render(r)
    
#    print r.rules["Jink"]
