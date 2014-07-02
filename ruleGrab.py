from xml.dom import minidom
import pickle
from termcolor import colored
from getch import getch
#TODO: Turn this into a rules database with functions to update it from BS files.  Use sqlite? Or just serialisation?
#TODO: sanitise latex output more sensibly. What if it's already escaped, for ex.
def sanitiseCSV(s):
    return s.replace(",","&COMMA").replace(u'\u2022',"").replace(u'\u2019',"").replace("\n","&CRLF")

def reverseCSV(s):
    return s.replace("&CRLF","\n").replace("&COMMA",",")
class Rules(object):
    """
    """
    
    def __init__(self,fn=None, data=None, sanitiseLatex=True):
        """
        
        Arguments:
        - `filename`:
        """
        self.rules={}
        self.fn=fn
        if fn!=None:
            self.rules=pickle.load(open(fn,"r"))
        if data!=None:
            self.rules=data
        self.sanitiseLatex=sanitiseLatex
    def save(self,fn=None):
        if fn==None and self.fn!=None:
            fn=self.fn
        else:
            raise Exception("No filename given")
        f=open(fn,"w")
        pickle.dump(self.rules,f)
        f.close()
    def importCSV(self,fn):
        """Import rules from CSV file"""
        f=open(fn,"r")
        for l in f.readlines():
            #print l, len(l.split(",")),l.split(",")
            k,r=l[:-1].split(",")
            k=reverseCSV(k)
            r=reverseCSV(r)
            #print k,r
            self.rules[k]=r
        f.close()
    def exportCSV(self,fn):
        """ Exports rules as CSV file"""
        keys=self.rules.keys()
        keys.sort()
        f=open(fn,"w")

        for k in keys:
            # for c in self.rules[k]:
            #     try:
            #         print ord(c),c,
            #         rule+=c
            #     except:
            #         print 0,0,
            #         rule+="?"

            #print
            f.write( "%s, %s\n"%(sanitiseCSV(k), sanitiseCSV(self.rules[k])))
        f.close()

    def keys(self):
        return self.rules.keys()
    def __iter__(self, ):
        """
        """
        return self.rules.__iter__()

    def __getitem__(self,key):
        if self.rules.has_key(key):
            val=self.rules[key].encode("ASCII", errors='replace')
            val=val.replace("&","\\&")
            return val
        else:
            return "Unknown rule"
    def __setitem__(self, key,value):
        """
        
        Arguments:
        - `key`:
        - `value`:
        """
        self.rules[key]=value

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
    r=Rules("./rules.r")

    #r.exportCSV("rules.csv")
    #r.importCSV("rules.csv")
    #r.save()


    # r["Assault"]="A weapon that can be fired in the shooting phase without preventing the firer from assaulting in the assault phase"
    # r.save()
    # cats=["ChaosSpaceMarines.cat", "Dark_Angels_6th_FAQ_1-13-2013.cat", "Eldar - 2013.cat", "Eldar.cat", "Fortifications.cat", "Orks 6th Ed (2008).cat"]
    # prefix="/home/james/bin/battlescribe_/catalogues/"
    # for cat in cats:
        
    #     cat=prefix+cat
    #     #cat="/home/james/bin/battlescribe_/catalogues/Eldar.cat"
    #     loadHelper(r,cat)
    #     #break
    # print "-"
    #    print r["Assault"]
    #loadHelper(r,"/home/james/bin/battlescribe_/previous_version/catalogues/Eldar.cat")
    # for i in r:
        
    #     print """[%s] %s \n"""%(i,r[i])
    #     print "-"*20

    # r.save()
    #print len(r.rules)
    #print r.rules[0].attributes["name"].value


            

#     from xml.dom import minidom
# xmldoc = minidom.parse('items.xml')
# itemlist = xmldoc.getElementsByTagName('item') 
# print len(itemlist)
# print itemlist[0].attributes['name'].value
# for s in itemlist :
#     print s.attributes['name'].value
