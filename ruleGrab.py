from xml.dom import minidom
class Rules(object):
    """
    """
    
    def __init__(self, filename):
        """
        
        Arguments:
        - `filename`:
        """
        self._filename = filename
        self.xml=minidom.parse(self._filename)
        self.rulesXML=self.xml.getElementsByTagName("rule")
        self.rules={}
        for i in self.rulesXML:
            for j in i.childNodes:
                if len( j.childNodes)!=0 and  j.childNodes[0].nodeType==j.TEXT_NODE:
                    r= i.attributes["name"].value
                    b="??"
                    try:
                        b=i.attributes["book"].value
                    except KeyError:
                        pass
                    k=j.childNodes[0].nodeValue+"(Source: %s)"%b
                    self.rules[r]=k

if __name__ == '__main__':
    r=Rules("/home/james/bin/battlescribe_/catalogues/Eldar.cat")
    for i in r.rules:
        print """[%s] %s \n"""%(i,r.rules[i])
    #print len(r.rules)
    #print r.rules[0].attributes["name"].value


            

#     from xml.dom import minidom
# xmldoc = minidom.parse('items.xml')
# itemlist = xmldoc.getElementsByTagName('item') 
# print len(itemlist)
# print itemlist[0].attributes['name'].value
# for s in itemlist :
#     print s.attributes['name'].value
