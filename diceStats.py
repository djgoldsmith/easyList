
class Die(object):
    """
    """
    def count(self,tally={},total=0):
        for i in self.outcomes:
            if type(i)==type(self):
                tally,total=i.count(tally,total)
            else:
                if tally.has_key(i):
                    tally[i]+=1                    
                else:
                    tally[i]=1
                total+=1
        return tally,total
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
            d.outcomes.append(i) if type(i)!=type(self) else i.clone()
        return d

    def __str__(self):

        return "[%s]"%",".join([str(i) for i in self.outcomes])
    def setOutcome(self,value,slots):
        if type(value)==type(self):
            value=value.clone()
        for i in slots:
            self.outcomes[i-1]=value
                          
def mRange(a,b):
    return range(a,b+1,1)
d=Die()
woundDie=Die()
woundDie.setOutcome("WOUND",[5,6])
woundDie.setOutcome("FAIL",[1,2,3,4])
d.setOutcome(woundDie,mRange(4,6))
d.setOutcome("MISS",mRange(1,3))
d.outcomes[0]=Die()
d.outcomes[0].setOutcome("MISS",mRange(1,5))
d.outcomes[0].setOutcome(woundDie,[6])
print d.count()
print d
