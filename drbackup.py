# coding: latin1

import os
import sys
import os.path
from drtools import DradisTools

def main():
    print("[*] DrTools - Backup active Dradis projects")

    if len(sys.argv) != 2:
	conffile = "proj.conf"
    else:
	conffile = sys.argv[1]

    if not os.path.exists(conffile):
	print("[-] Use: %s <conffile>" % sys.argv[0])
	sys.exit(1)

    if not os.path.exists("projects"):
        os.makedirs("projects")

    with DradisTools(conffile) as dt:
        for p in dt.get_projects():
            projdir = os.path.join("projects", _sanitize(p["name"]))
            if not os.path.exists(projdir):
                os.makedirs(projdir)
            
            print("[+] Backing up Project %s (%s)" % (p["name"], p["id"]))

            for i in dt.get_issues(p["id"]):
                with open(os.path.join(projdir, "%s.textile" % _sanitize(i["name"])), "w", encoding="utf8") as f:
                    print("[+] Issue: %s (%s)" % (i["name"], i["id"]))
                    f.write(dt.get_issue_data(p["id"], i["id"]))

        
if __name__ == "__main__":
    main()
