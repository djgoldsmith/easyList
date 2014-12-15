from mod_python import apache, util


import difflib
from ruleGrab import Rules

r=Rules("/home/james/public_html/whrules/rules.r")
rules=r.keys()


def auth(req,user,password):
    if user == 'blah' and password == 'blah':
        return 1
    else:
        return 0


def index(req):
    def __auth__(req, user, password):
        return auth(req,user,password)


    req.content_type = 'text/html'
    out="aaa"
    #TODO: FIX
    return out

  

def grab(req):
    req.content_type = 'text/html'
    out=""
    pairs = dict(util.parse_qsl(req.args))
    if pairs.has_key("refresh"):
        out+="<p style='background-color: #DDFFEE'>Refresh</p>"
    if pairs.has_key("str"):
        poss= difflib.get_close_matches(pairs["str"],rules, cutoff=0.3)
        out+="<dl>\n"
        for i in poss:
            out+= "<dt>%s</dt><dd>%s</dd>\n"%(i,r[i])
        out+="</dl>\n"
        return out

        
    else:
        return "NO"

