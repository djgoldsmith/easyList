
from pieces import  Weapon

shurikenPistol=Weapon("Shuriken Pistol",12,4,5,"shooting",1,specialRules=["Pistol", "Bladestorm"])
witchBlade=Weapon("WitchBlade","-","User","-","melee",specialRules=["Melee","Armourbane","Fleshbane"])
twinlinkedShurikenCatapult=Weapon("Twin-Linked Shuriken Catapult",12,4,5,"shooting",shots= 2,specialRules=["Assault", "Bladestorm", "Twin-Linked"])
boltGun=Weapon("Bolt Gun", 24,4,5,"shooting",specialRules=["Rapid Fire"], shots="1 (full range)/2 (half range)")
boltPistol=Weapon("Bolt Pistol", 12,4,5,"shooting",specialRules=["Pistol"])
plasmaGrenades=Weapon("Plasma Grenades","8/-",4,4,"shooting",specialRules=["Assault","Blast","No Charge/Cover Penalty"])


singingSpearDuo=[Weapon("Singing Spear (melee)","-","X","-","melee",specialRules=["Melee","Armourbane","Fleshbane"]),
              Weapon("Singing Spear (shooting)",12,9,"-","shooting",specialRules=["Assault","Fleshbane"])]



forceStave=Weapon("Force Stave","-","+2",4,"melee",specialRules=["Melee","Force","Concussive","Instant Death"])


heavyBolter=Weapon("Heavy Bolter",36,5,4,"shooting",specialRules=["Heavy 3"])

mlFrag=Weapon("Missile Launcher (Frag)",48,4,6,"shooting",specialRules=["Heavy 1", "Blast"])

mlKrak=Weapon("Missile Launcher (Krak)",48,8,3,"shooting",specialRules=["Heavy 1"])

plasmaCannon=Weapon("Plasma Cannon",36,7,2,"shooting",specialRules=["Heavy 1", "Blast", "Gets Hot"])

plasmaGun=Weapon("Plasma Gun",24,7,2,"shooting",specialRules=["Rapid Fire", "Gets Hot"])

sniperRifle=Weapon("Sniper Rifle",36,"-",6,"shooting",specialRules=["Heavy 1", "Sniper"])

flamer=Weapon("Flamer","Template",4,5,"shooting",specialRules=["Assault"])
scatterLaser=Weapon("Scatter Laser",36,6,6,"shooting",shots=4,specialRules=["Heavy", "Laser Lock"])
starCannon=Weapon("Star Cannon",36,6,2,"shooting",specialRules=["Heavy"],shots= 2)
shurikenCatapult=Weapon("Shuriken Catapult",12,4,5,"shooting",shots=2,specialRules=["Bladestorm","Assault"])
shurikenCannon=Weapon("Shuriken Cannon",24,6,5,"shooting",shots= 3,specialRules=["Assault", "Bladestorm"])
brightLance=Weapon("Bright Lance",36,8,2,"shooting",shots= 1,specialRules=["Heavy", "Lance"])
ghostGlave=Weapon("Ghost Glave","-","+1",2,"melee",specialRules=["Master-Crafted"])
