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
        self.rules=self.xml.getElementsByTagName("rule")
if __name__ == '__main__':
    r=Rules("/home/james/bin/battlescribe_/catalogues/Eldar.cat")
    #print len(r.rules)
    #print r.rules[0].attributes["name"].value
    for i in r.rules:
        print i.attributes["name"].value
        for j in i.childNodes:
            if len( j.childNodes)!=0 and  j.childNodes[0].nodeType==j.TEXT_NODE:
                k=j.childNodes[0]
                print k.nodeValue

                print "\n","="*10


            

#     from xml.dom import minidom
# xmldoc = minidom.parse('items.xml')
# itemlist = xmldoc.getElementsByTagName('item') 
# print len(itemlist)
# print itemlist[0].attributes['name'].value
# for s in itemlist :
#     print s.attributes['name'].value
