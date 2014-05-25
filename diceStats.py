
import pieces

#Markers with underscore are collapsed into those that don't when
#computing stats. Allows you to stop them being replaced by searches,
#for example with bladestorm that takes out the armour save
#TODO: this is stupid but need to think how to pass down new AP value through tree



def dupe(i):
    if isinstance(i,Die):
        return i.clone()
    return i

class Die(object):
    """
    """
    def count(self,tally=None, mul=1.0):
        if tally==None: tally={}
        for i in self.outcomes:
            if isinstance(i,Die):
                tally=i.count(tally,mul/self._sides)
            else:
                key=i

                if key.endswith("_"):
                    key=key[:-1]
                if tally.has_key(key):
                    tally[key]+=(mul/self._sides)
                else:
                    tally[key]=mul/self._sides

        return tally
    def __init__(self, sides=6):
        """
        
        Arguments:
        - `sides`:
        """
        self._sides = sides
        self.outcomes=range(1,7,1)
    def clone(self):
        d=Die(self._sides)
        d.outcomes=[]
        for i in self.outcomes:
            d.outcomes.append(i if not isinstance(i,Die) else i.clone())
        return d

    def __str__(self):
        return "\n[%s] \n"%(",".join([str(i) for i in self.outcomes]))

    def statString(self):
        vals=self.count()
        return "\n".join(["%s\t: %0.1f%%"%(i,100*vals[i]) for i in vals])

    def percent(self,stat):
        total=0
        count=0
        stats=self.count()
        for i in stats:

            if i==stat or i.startswith(stat+"_"):

                count+=stats[i]
            total+=stats[i]
        return count
        
    
    def setOutcome(self,value,slots):
        value=dupe(value)
        for i in slots:
            self.outcomes[i-1]=value
    def onGTE(self,n,valYes, valNo):
        n=int(n)
        valYes=dupe(valYes)
        valNo=dupe(valNo) 
        self.outcomes=[valYes if i >=n else valNo  for i in range(1,self._sides+1,1)]
    def toHit(self,n):

        self.onGTE(n,"HIT","MISS")
        
    def rollReplace(self,find,n,replaceYes,replaceNo,on={}):

        replaceYes=dupe(replaceYes)
        replaceNo=dupe(replaceNo)

        for i in range(len(self.outcomes)):
            if isinstance(self.outcomes[i],Die):
                self.outcomes[i].rollReplace(find,n,replaceYes,replaceNo, on=on)
            else:
                
                if self.outcomes[i]==find:
                    self.outcomes[i]=Die()
                    self.outcomes[i].onGTE(n,replaceYes,replaceNo)
                    for j in on:
                        self.outcomes[i].outcomes[j]=on[j]

    def toWound(self,n,on={}):

        self.rollReplace("HIT",n,"WOUND","FAIL",on=on)

    def save(self,n,saveWhat="WOUND",on={},saveAlt="SAVE"):
        self.rollReplace(saveWhat,n,saveAlt,"WOUND",on=on)
    def reRoll1s(self):
        self.outcomes[0]=self.clone()
    def feelNoPain(self,on=6):
        self.rollReplace("WOUND",on,"FNP!","WOUND")
    def reRollMisses(self):
        n=self.clone()

        for i in range(len(self.outcomes)):
            if self.outcomes[i]=="MISS":
                self.outcomes[i]=n.clone()
    
        
def mRange(a,b):
    return range(a,b+1,1)

def genShotStatsBasic(bs,weaponStrength, targetToughness, ap=None, cover=None, save=None,inv=None, bladestorm=False, twinlinked=False, sniper=False, reRoll=None):
    if reRoll==None: reRoll=[]
    toHit=pieces.toHitStats[bs]

    d=Die()
    if toHit=="-":        
        d.onGTE(0,"MISS","MISS")
    else:
        d.toHit(int(toHit[0]))
    if twinlinked:
        d2=dupe(d)
        for i in range(len(d.outcomes)):
            if d.outcomes[i]=="MISS":
                d.outcomes[i]=dupe(d2)


    if toHit.find("/")>=0:
        v2=int(toHit[2])
        d.rollReplace("MISS",v2,"HIT","MISS")
    
    woundRequired=pieces.shootToWoundIndividual(weaponStrength,targetToughness)
    instagib=False
    if woundRequired.endswith("D"):
        instagib=True
    woundRequired=int(woundRequired[0]) if woundRequired[0]!="-" else "8"

    on={}
    if sniper:
        on[5]="WOUND"
        on[4]="WOUND"
        on[3]="WOUND"
    if bladestorm:
        on[5]="WOUND_bs"

    d.toWound(woundRequired,on=on)

    if "failedWound" in reRoll:
        d.rollReplace("FAIL",woundRequired,d,"FAIL",on=on)
    
    if save!=None and ap!=None and ap<=save:
        save=None
    best=min([cover if cover!=None else 100,save if save!=None else 100,inv if inv!=None else 100])
    if best<100:
        if best==cover:
            saveName="SAVE(cover)"
        elif best==inv:
            saveName="SAVE(inv)"
        elif best==save:
            saveName="SAVE(armour)"
        d.save(best,saveAlt=saveName)
        if (saveName=="SAVE(cover)" and "cover" in reRoll) or "allsaves" in reRoll:
            d.save(best,saveAlt=saveName)
    #Bladestorm saves
    if bladestorm:
        #Nothing beats AP2, so just pick best from others
        best=min([cover if cover!=None else 100,inv if inv!=None else 100])
        saveName=None

        if best<100:
            if best==cover:
                saveName="SAVE(cover)"
            elif best==inv:
                saveName="SAVE(inv)"
            d.save(best,saveWhat="WOUND_bs",saveAlt=saveName)
            if (saveName=="SAVE(cover)" and "cover" in reRoll) or "allsaves" in reRoll:
                d.save(best,saveAlt=saveName)

        
    
    return d
    #return 


def meleeToHit(wsA,wsB):
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
    return mapping[wsA-1][wsB-1]
    
def genMeleeStatsBasic(wsA,wsB, weaponStrength, targetToughness, ap=None,  save=None,inv=None, reRoll=None, fleshbane=False):
    #TODO: hammer of wrath, etc?
    if reRoll==None: reRoll=[]
    toHit=meleeToHit(wsA,wsB)

    d=Die()

    d.toHit(int(toHit))

    woundRequired=pieces.shootToWoundIndividual(weaponStrength,targetToughness)
    woundRequired=int(woundRequired[0]) if woundRequired[0]!="-" else "8"

    on={}

    
    if fleshbane:
        woundRequired=2

    d.toWound(woundRequired,on=on)
    if save!=None and ap!=None and ap<=save:
        save=None
    best=min([save if save!=None else 100,inv if inv!=None else 100])
    if best<100:
        if best==inv:
            saveName="SAVE(inv)"
        elif best==save:
            saveName="SAVE(armour)"
        d.save(best,saveAlt=saveName)
        if saveName=="SAVE(cover)" and "cover" in reRoll:
            d.save(best,saveAlt=saveName)
    return d
    #return 

    
if __name__ == '__main__':

    
    #d= genShotStatsBasic(4,4,4, save=4, bladestorm=True, sniper=False, cover=2,inv=6,reRoll=[])
    d=genMeleeStatsBasic(5,4,3,4,fleshbane=True,save=3)
    print d.statString()
    print d.count()
    print d
# d=Die()
# d.toHit(3)


# #d.reRoll1s()
# #d.reRollMisses()

# d.toWound(3)
# d.save(6)
# d.feelNoPain()
# # woundDie=Die()
# # woundDie.setOutcome("WOUND",[5,6])
# # woundDie.setOutcome("FAIL",[1,2,3,4])
# # d.setOutcome(woundDie,mRange(4,6))
# # d.setOutcome("MISS",mRange(1,3))
# # d.outcomes[0]=Die()
# # d.outcomes[0].setOutcome("MISS",mRange(1,5))
# # d.outcomes[0].setOutcome(woundDie,[6])

# #print d
# print d.statString()
