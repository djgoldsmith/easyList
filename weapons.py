
from pieces import  Weapon

shurikenPistol=Weapon("Shuriken Pistol",12,4,5,"shooting",1,specialRules=["Pistol", "Bladestorm"])
witchBlade=Weapon("WitchBlade","-","User","-","melee",specialRules=["Melee","Armourbane","Fleshbane"])
twinlinkedShurikenCatapult=Weapon("Twin-Linked Shuriken Catapult",12,4,5,"shooting",shots= 2,specialRules=["Assault", "Bladestorm", "Twin-Linked"])
boltGun=Weapon("Bolt Gun", 24,4,5,"shooting",specialRules=["Rapid Fire"], shots="1 (full range)/2 (half range)")
boltPistol=Weapon("Bolt Pistol", 12,4,5,"shooting",specialRules=["Pistol"])
plasmaGrenades=Weapon("Plasma Grenades","8/-",4,4,"shooting",specialRules=["Assault","Blast","No Charge/Cover Penalty"])


singingSpearDuo=[Weapon("Singing Spear","-","User","-","melee",specialRules=["Melee","Armourbane","Fleshbane"]),
              Weapon("Singing Spear",12,9,"-","shooting",specialRules=["Assault","Fleshbane"])]
