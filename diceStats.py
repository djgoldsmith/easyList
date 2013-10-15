import pieces
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
                if tally.has_key(i):
                    tally[i]+=(mul/self._sides)
                else:
                    tally[i]=mul/self._sides

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

    def setOutcome(self,value,slots):
        value=dupe(value)
        for i in slots:
            self.outcomes[i-1]=value
    def onGTE(self,n,valYes, valNo):
        valYes=dupe(valYes)
        valNo=dupe(valNo)
        self.outcomes=[valYes if i >=n else valNo for i in range(1,self._sides+1,1)]
    def toHit(self,n):

        self.onGTE(n,"HIT","MISS")
        
    def rollReplace(self,find,n,replaceYes,replaceNo):
        replaceYes=dupe(replaceYes)
        replaceNo=dupe(replaceNo)
        for i in range(len(self.outcomes)):
            if isinstance(self.outcomes[i],Die):
                self.outcomes[i].rollReplace(find,n,replaceYes,replaceNo)
            else:
                if self.outcomes[i]==find:
                    self.outcomes[i]=Die()
                    self.outcomes[i].onGTE(n,replaceYes,replaceNo)
    def toWound(self,n):
        self.rollReplace("HIT",n,"WOUND","FAIL")
    def save(self,n):
        self.rollReplace("WOUND",n,"SAVE","WOUND")
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

def genShotStatsBasic(bs,weaponStrength, targetToughness, ap=None, cover=None, save=None,inv=None):
    toHit=pieces.toHitStats[bs]
    d=Die()
    if toHit=="-":        
        d.onGTE(0,"MISS","MISS")
        return d
    d.toHit(int(toHit[0]))
    if toHit.find("/")>=0:
        v2=int(toHit[2])
        d.rollReplace("MISS",v2,"HIT","MISS")
    woundRequired=pieces.shootToWoundIndividual(weaponStrength,targetToughness)
    d.toWound(woundRequired)
    if save!=None and ap!=None and ap<=save:
        save=None
    best=min([cover if cover!=None else 100,save if save!=None else 100,inv if inv!=None else 100])
    if best<100:
        d.save(best)
        
    return d
    #return 
    
    
d= genShotStatsBasic(4,4,4,save=6)

print d.statString()
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
