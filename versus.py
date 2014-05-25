from ruleGrab import Rules
from units import *
import diceStats
from pieces import shootToWoundIndividual

def rollStrip(val):
    try:
        return int("".join([ i for i in str(val) if i.isdigit()]))
    except:
        return 100
def roughInt(val):

    v=""
    for i in str(val):
        if v!="" and not i.isdigit():
            return int(v)
        elif i.isdigit():
            v+=i
    return int(v)
def shoot(a,b, squadSize=1, specials=[]):
    cover=7
    if b.hasRule("Jink"):
        cover=4
    if b.hasRule("Stealth"):
        cover-=1
    if b.hasRule("Shrouded"):
        cover-=2
    if cover<2: cover=2
    reRolls=[]
    if "fortune" in specials:
        reRolls.append("allsaves")
    if b.hasRule("Mantle of the Laughing God"):
        reRolls.append("cover")
    toHit=a.shootToHit()
    print a.name,"hits",b.name,"on",toHit
    print "\tArmour: %d\n\tInvul: %d\n\tCover: %s"%(rollStrip(b.sv),rollStrip(b.inv),str(cover))
    print
    for w in a.weapons:
        if w.type!="shooting": continue
        s=int(w._strength if w._strength!="X" else 1)
        ap=w.ap
        if type(ap)==type(""):
            ap=int(ap[0]) if ap!="-" else 7
        woundOn=shootToWoundIndividual(s,b.t).strip()
        print "{0:<30} (Strength: {1}, AP: {2})".format(w.name, s,ap)
        print "\twounds on %s"%woundOn
        sniper=a.hasRule("Sniper") or w.hasRule("Sniper")
        bladestorm=w.hasRule("Bladestorm")
        twinlinked=w.hasRule("Twinlinked") or "guide" in specials
        if "doom" in specials: reRolls.append("failedWound") 
        d=diceStats.genShotStatsBasic(a.bs, s,b.t, save=rollStrip(b.sv), inv=rollStrip(b.inv), sniper=sniper, bladestorm=bladestorm, twinlinked=twinlinked,cover=cover,reRoll=reRolls)

        print "\tChance to wound:", d.percent("WOUND")*roughInt(w.shots),"\n\tFor Squad of size %d: %0.2f"%(squadSize,d.percent("WOUND")*roughInt(w.shots)*squadSize)
        #print d
    print "-"*80

def melee(a,b):
    reRolls=[]
    if b.i > a.i:
        b,a=a,b
    for pair in ((a,b),(b,a)):        
        print "%s strikes %s at I%d"%(pair[0].name,pair[1].name,pair[0].i)
        for w in pair[0].weapons+[pair[0].hands]:
            if w.type=="melee" or w.hasRule("Pistol"):
                print "\t",w.name
                print "\t-------"
                d=diceStats.genMeleeStatsBasic(pair[0].ws,pair[1].ws,w.strength,pair[1].t,save=rollStrip(pair[1].sv),inv=rollStrip(pair[1].inv),reRoll=reRolls,fleshbane=w.hasRule("Fleshbane"),ap=w.ap if not pair[0].hasRule("Smash") else 2)
                vals= d.count()
                #print d
                if not vals.has_key("WOUND"):
                    print "\tNo wounds inflicted"
                    continue
                else:
                    chance=vals["WOUND"]
                    wounds=pair[1].w
                    attacks=pair[0].attacks()
                    print "\tAttack %0.2f successful.  \n\tAttacks per round of %d \n\t\tagainst %d-wound enemy leads to \n\t\t%0.1f rounds until victory."%(chance,attacks,wounds,wounds/(chance*attacks))
        print
                    
    

#TODO: reroll 1's
#TODO: prescience (using above, twinlinked?)
#TODO: poison
#TODO: debuffs like reroll wounds/hits etc.
        
if __name__ == '__main__':

    w=Wraithlord("Wraithlord")
    w.addWeapon(Weapon("WitchBlade","-","User","-","melee",specialRules=["Melee","Armourbane","Fleshbane"]))
    w.addWeapon(Weapon("WitchBlade","-","User","-","melee",specialRules=["Melee","Armourbane","Fleshbane"]))
    m=SpaceMarine("Marine")
    s=Scout("Scout")
    r=Ranger("Ranger")
    g=Guardian()
    shoot(g,m)

    r.addRule("Mantle of the Laughing god")
    #shoot(w,r)
    #shoot(m,r)
#    shoot(m,w)
    # w.render(r)
    # m.render(r)
