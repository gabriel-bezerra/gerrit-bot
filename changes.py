# Copyright 2014 Gabriel Assis Bezerra
#
# Script to fetch changes from Gerrit and generate the proper Redmine wiki page

from __future__ import print_function
import json
import urllib2

def debug(msg):
    pass
    #print(msg)


#change_numbers = [90771, 90476]
change_numbers = [87406, 86250, 85199, 79112, 64103, 87861, 79411, 57492, 78658, 90476]

def reviewer_author_filter(author):
    return author.email.endswith("@lsd.ufcg.edu.br")


# Gerrit

class Gerrit:
    """Gerrit interface that returns interpreted JSON collections
    """

    def fetch_change(self, change_number):
        url = "https://review.openstack.org/changes/" + str(change_number) + "?o=all_revisions&o=messages"
        return self.__fetch_json(url)

    def fetch_revision(self, change_number, revision_id):
        url = "https://review.openstack.org/changes/" + str(change_number) + "/revisions/" + str(revision_id) + "/review"
        return self.__fetch_json(url)

    def __fetch_json(self, url):
        debug("Fetching: " + url)
        response_body = urllib2.urlopen(url).read()
        sanitized_body = response_body.partition("'")[2]
        return json.loads(sanitized_body)


# Domain model

class Change:
    def __init__(self, number, id, subject, project):
        self.number = number
        self.id = id
        self.subject = subject
        self.project = project
        self.revisions = []

    def title(self):
        return "Change "+self.id[0:9]+": "+self.subject

    def permalink(self):
        return "https://review.openstack.org/"+str(self.number)

    def __repr__(self):
        return "Change("+repr(self.number)+", "+repr(self.id)+", "+repr(self.subject)+", "+repr(self.project)+", "+repr(self.revisions)+")"

class Revision:
    def __init__(self, id, number):
        self.id = id
        self.number = number
        self.reviews = []

    def __repr__(self):
        return "Revision("+repr(self.number)+", "+repr(self.id)+", "+repr(self.reviews)+")"

class Review:
    def __init__(self, value, author, message):
        self.value = value
        self.author = author
        self.message = message

    def vote(self):
        return "{0:+d}".format(self.value) if self.value != 0 else str(0)

    def message_without_vote(self):
        return self.message.partition('\n\n')[2]

    def __repr__(self):
        return "Review("+repr(self.vote())+", "+repr(self.author)+", "+repr(self.message)+")"

class Author:
    def __init__(self, username, name, email):
        self.username = username
        self.name = name
        self.email = email

    def __repr__(self):
        return "Author("+repr(self.username)+", "+repr(self.name)+", "+repr(self.email)+")"


# Action

def changes(change_numbers):
    gerrit = Gerrit()

    changes = []
    for change_number in change_numbers:
        change = gerrit.fetch_change(change_number)

        debug(change["subject"])
        ch = Change(change["_number"], change["change_id"], change["subject"], change["project"])

        revision_ids = change["revisions"].keys()
        debug("==========")
        for revision_id in revision_ids:
            revision = gerrit.fetch_revision(change_number, revision_id)
            #debug(revision)

            r = Revision(revision["id"], revision["revisions"].values()[0]["_number"])
            debug("Revision: " + str(r.number))

            messages_of_this_revision = [m for m in change["messages"] if m["_revision_number"] == r.number]
            #debug(messages_of_this_revision)

            code_reviews = revision["labels"]["Code-Review"]["all"]
            for code_review in code_reviews:
                #debug(change["messages"])
                author = Author(code_review.get("username", ""), code_review["name"], code_review.get("email", ""))
                debug(author)

                value = code_review["value"]

                messages_of_this_revision_of_this_author = [m for m in messages_of_this_revision if m["author"]["name"] == author.name]
                #debug(messages_of_this_revision_of_this_author)

                if messages_of_this_revision_of_this_author: #is not empty
                    message = messages_of_this_revision_of_this_author[0]["message"]
                    #debug(message)

                    review = Review(value, author, message)
                    r.reviews.append(review)
                    debug(review)

            #debug(code_reviews)
            debug("==========")
            ch.revisions.append(r)
            debug(r)

        changes.append(ch)
        debug(ch)

    return changes

def report_page_from_changes(changes):
    """
    h1. US904 - As a Dev I want to do code review on OpenStack code

    table{border:1px bordercolor:darkblue}.
    |_{background:#ffa}.Reviewer|_{background:#ffa}.Review|_{background:#ffa}.Project|_{background:#ffa}.Patch|_{background:#ffa}.Revision
    score|_{background:#ffa}.Comment|
    |||||||
    """

    wiki_page_name = "h1. US904 - As a Dev I want to do code review on OpenStack code"
    header = wiki_page_name+"""

    table{border:1px bordercolor:darkblue}.
    |_{background:#ffa}.Reviewer|_{background:#ffa}.Review|_{background:#ffa}.Project|_{background:#ffa}.Patch|_{background:#ffa}.Revision
    score|_{background:#ffa}.Comment|"""
    print(header)

    for change in changes:
        for revision in change.revisions:
            for review in revision.reviews:
                #Reviewer    Review  Project Patch   Revision score  Comment
                reviewer = review.author.name
                rev = '"'+change.title()+'":'+change.permalink()
                project = change.project
                patch = str(revision.number)
                score = review.vote()
                comment = review.message_without_vote().replace('\n', ' ')
                if reviewer_author_filter(review.author):
                    print("|"+ reviewer +"|"+ rev +"|"+ project +"|"+ patch +"|"+ score +"|"+ comment +"|")

if __name__ == '__main__':
    changes = changes(change_numbers)
    report_page_from_changes(changes)

