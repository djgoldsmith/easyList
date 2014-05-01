import difflib
from ruleGrab import Rules

r=Rules("./rules.r")
rules=r.keys()

while True:
    lu=raw_input("Look up: ")
    poss= difflib.get_close_matches(lu,rules, cutoff=0.3)
    for i in poss:
        print i+"\n"+r[i]+"\n"+("-"*20)

