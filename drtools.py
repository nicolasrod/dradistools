# coding: latin1

import requests
import json
from codecs import open
from bs4 import BeautifulSoup as parse_html

# TODO: Check // in URL
# TODO: Check for config keys
# TODO: Error checking!

def _sanitize(s):
    for c in [":", " ", ";", "&", "/", "\\", "|"]:
        s = s.replace(c, "_")
    return s

class DradisTools(object):

    def __init__(self, configfile):
        with open(configfile, "rb") as f:
            self.config = json.load(f)

        self.session = requests.Session()
        self.login()

    def url(self, *args):
	return "%s/%s" % (self.config["server"], "/".join(args))

    def login(self):
	r = self.session.get(self.url("pro", "login"))
	token = self.get_token(r.text)

	r = self.session.post(self.url("pro", "session"),
	    data={"authenticity_token": token, "login": self.config["username"], "password": self.config["password"]})

    def get_projects(self):
	r = self.session.get(self.url("pro", "projects"))
	soup = parse_html(r.text, "html.parser")
    
        for item in soup.find_all("div"):
	    if item.has_attr("class"):
	        if item["class"] == ["project", "active-project"]:
		    a = item.div.h4.a
                    yield {"name": a.text, "url": self.url(a["href"]), "id": a["href"].split("/")[-1]}


    def get_issues(self, pid):
        r = self.session.get(self.url("pro", "projects", pid))
        r = self.session.get(self.url("pro", "issues"))
        soup = parse_html(r.text, "html.parser")

        for item in soup.find_all("div"):
            pid = item.get("id", "")
            
            if pid.startswith("issue_") and not pid.startswith("issue_summary"):
                a = item.div.a
                yield {"url": a["href"], "name": a.text.strip(), "id": a["href"].split("/")[-1]}


    def get_issue_data(self, pid, iid):
        r = self.session.get(self.url("pro", "projects", pid))
        r = self.session.get(self.url("pro", "issues", iid, "edit"))
        soup = parse_html(r.text, "html.parser")

        for item in soup.find_all("textarea"):
            if item.get("id", "") == "issue_text":
                return item.text.strip().replace("\r\n", "\n")

    def get_token(self, html):
        soup = parse_html(html, "html.parser")
        for i in soup.find_all("input"):
	    if i["name"] == "authenticity_token":
	        return i["value"]

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, tb):
        if self.session is not None:
            self.session.close()
