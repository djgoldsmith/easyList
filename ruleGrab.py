from xml.dom import minidom
import pickle
from termcolor import colored
from getch import getch
#TODO: Turn this into a rules database with functions to update it from BS files.  Use sqlite? Or just serialisation?
class Rules(object):
    """
    """
    
    def __init__(self,fn=None, data=None):
        """
        
        Arguments:
        - `filename`:
        """
        self.rules={}
        if fn!=None:
            self.rules=pickle.load(open(fn,"r"))
        if data!=None:
            self.rules=data
    def save(self,fn):
        f=open(fn,"w")
        pickle.dump(self.rules,f)
        f.close()
        
    def __repr__(self):
        return "Rules(data=%s)"%self.rules.__repr__()
    def load(self,filename):

        
        xml=minidom.parse(filename)
        rulesXML=xml.getElementsByTagName("rule")


        added=0
        dupes=0
        mismatched=0
        mismatchD={}
        for i in rulesXML:

            for j in i.childNodes:

                if len( j.childNodes)!=0 and  j.childNodes[0].nodeType==j.TEXT_NODE:

                    r= i.attributes["name"].value

                    b="??"
                    try:
                        b=i.attributes["book"].value
                        b+=", p."+i.attributes["page"].value
                    except KeyError:
                        pass
                    k=j.childNodes[0].nodeValue+"(Source: %s)"%b

                    if self.rules.has_key(r):
                        if self.rules[r]==k:
                            dupes+=1
                        else:
                            mismatched+=1
                            mismatchD[r]=k
                    else:
                        added+=1
                        self.rules[r]=k
        return {"added":added,"dupes":dupes,"mismatched":mismatched,"problems":mismatchD}

def diff (a,b):
    #Dumb diff
    out=""
    for i in range(len(a)):
        try:
            if a[i]==b[i]:
                out+=a[i]
            else:
                out+=colored(a[i],"red","on_white")
        except:
            out+=colored(a[i],"red","on_grey")
    return out
    
def loadHelper(rules,cat):
        d=rules.load(cat)
        if d["added"]>0:
            print "After new import of %s, %d new rules were loaded, %d were complete dupes and %d rules were found with differing definitions"%(cat,d["added"],d["dupes"],d["mismatched"])
        else:
            print "After new import of %s, no changes were made"%cat
        print "Resolving mismatches:"
        for k in d["problems"]:
            next=False
            print k.center(30,"-")
            while not next:
                A=rules.rules[k]
                B=d["problems"][k]
                #print "Rule: %s.\nCurrent: %s\nNew    : %s\n"%(k,A,B)
                print "Choose:"
                print "A:",diff(A,B)
                print "B:",diff(B,A)
                print "A/B:"
                result=getch()
                if result in ["a","A"]:
                    next=True
                elif result in ["b","B"]:
                    rules.rules[k]=B
                    next=True
                else:
                    print "Enter A or B. Try again."
if __name__ == '__main__':
    r=Rules("/home/james/tmp/easyList/rules.r")
    
    # cats=["ChaosSpaceMarines.cat", "Dark_Angels_6th_FAQ_1-13-2013.cat", "Eldar - 2013.cat", "Eldar.cat", "Fortifications.cat", "Orks 6th Ed (2008).cat"]
    # prefix="/home/james/bin/battlescribe_/catalogues/"
    # for cat in cats:
        
    #     cat=prefix+cat
    #     #cat="/home/james/bin/battlescribe_/catalogues/Eldar.cat"
    #     loadHelper(r,cat)
    #     #break
    # print "-"    
    for i in r.rules:
        #try:
        sanitised=r.rules[i].encode("ASCII", errors='replace')
        print """[%s] %s \n"""%(i,sanitised)
        # except:
        #     print "WHOOPS!"
        print "-"*20

    # r.save("/home/james/tmp/rules.r")
    #print len(r.rules)
    #print r.rules[0].attributes["name"].value


            

#     from xml.dom import minidom
# xmldoc = minidom.parse('items.xml')
# itemlist = xmldoc.getElementsByTagName('item') 
# print len(itemlist)
# print itemlist[0].attributes['name'].value
# for s in itemlist :
#     print s.attributes['name'].value
