# Copyright 2014 Gabriel Assis Bezerra
#
# Script to fetch and parse changes from Gerrit

from __future__ import print_function
from datetime import datetime

import json
import urllib2
import re

def debug(msg):
    pass
    #print(msg)

def info(msg):
    #pass
    print(msg)


# Gerrit

class Gerrit:
    """Gerrit interface that returns interpreted JSON collections
    """

    def fetch_change(self, change_number):
        url = "https://review.openstack.org/changes/" + str(change_number) + "/detail?o=all_revisions&o=messages"
        return self.__fetch_json(url)

    def fetch_revision(self, change_number, revision_id):
        url = "https://review.openstack.org/changes/" + str(change_number) + "/revisions/" + str(revision_id) + "/review"
        return self.__fetch_json(url)

    def __fetch_json(self, url):
        info("[Gerrit] Fetching: " + url)
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
    def __init__(self, value, author, message, timestamp):
        self.value = value
        self.author = author
        self.message = message
        self.timestamp = timestamp

    def vote(self):
        return "{0:+d}".format(self.value) if self.value != 0 else str(0)

    def message_without_vote(self):
        message_text = self.message.strip()
        message_without_vote = ""

        matches_with_vote = re.match("^Patch Set [0-9]+: Code-Review([+-][12])($|\n\n.*)", message_text)
        matches_without_vote = re.match("^Patch Set [0-9]+:( |\n)+(.*)", message_text)

        if matches_with_vote is not None and matches_with_vote.group(2) is not None:
            message_without_vote = matches_with_vote.group(2).strip()
            debug("matches with vote")

        elif matches_without_vote is not None and matches_without_vote.group(2) is not None:
            message_without_vote = matches_without_vote.group(2).strip()
            debug("matches without vote")

        else:
            message_without_vote = message_text.strip()
            debug("matches with none")

        return message_without_vote

    def __repr__(self):
        return "Review("+repr(self.vote())+", "+repr(self.author)+", "+repr(self.message)+", "+repr(self.timestamp)+")"

review_with_single_line_message = Review(1, None, '\nPatch Set 9: (1 inline comment)\n', None)
assert review_with_single_line_message.vote() == '+1'
assert review_with_single_line_message.message_without_vote() == '(1 inline comment)'

review_with_multi_line_message = Review(0, None, '\nPatch Set 9:\n\n(1 comment)\n', None)
assert review_with_multi_line_message.vote() == '0'
assert review_with_multi_line_message.message_without_vote() == '(1 comment)'

class Author:
    def __init__(self, username, name, email):
        self.username = username
        self.name = name
        self.email = email

    def __repr__(self):
        return "Author("+repr(self.username)+", "+repr(self.name)+", "+repr(self.email)+")"


# Action

class ChangeParser:
    def __init__(self):
        self.gerrit = Gerrit()

    def change_with_number(self, change_number):
        change = self.gerrit.fetch_change(change_number)

        debug(change["subject"])
        ch = Change(change["_number"], change["change_id"], change["subject"], change["project"])

        revision_ids = change["revisions"].keys()
        debug("==========")
        for revision_id in revision_ids:
            revision = self.gerrit.fetch_revision(change_number, revision_id)
            #debug(revision)

            r = Revision(revision["id"], revision["revisions"].values()[0]["_number"])
            debug("Revision: " + str(r.number))

            messages_of_this_revision = [m for m in change["messages"] if m["_revision_number"] == r.number]
            #debug(messages_of_this_revision)

            for message in messages_of_this_revision:
                message_author = message["author"]
                author = Author(message_author.get("username", ""), message_author["name"], message_author.get("email", ""))
                debug(message)
                debug(author)

                message_text = message["message"]
                timestamp = datetime.strptime(message["date"].rpartition('.')[0]+" UTC", "%Y-%m-%d %H:%M:%S %Z")

                value = 0
                matches = re.match("^Patch Set [0-9]+: Code-Review([+-][12])($|\n\n)", message_text)
                if matches is not None:
                    debug("Vote match: " + matches.group(1))
                    value = int(matches.group(1))
                else:
                    debug("Vote did not match.")

                review = Review(value, author, message_text, timestamp)
                r.reviews.append(review)
                debug(review)

            #debug(code_reviews)
            debug("==========")
            ch.revisions.append(r)
            debug(r)

        debug(ch)
        return ch

    def changes(self, change_numbers):
        return [self.change_with_number(cn) for cn in change_numbers]


if __name__ == '__main__':
    #change_numbers = [90771, 90476]
    #change_numbers = [87406, 86250, 85199, 79112, 64103, 87861, 79411, 57492, 78658, 90476]
    #change_numbers = ['87406', '86250', '85199', '79112', '64103', '87861', '79411', '57492', '78658', '90476']
    #change_numbers = ['89220']
    change_numbers = ['168776']

    print(repr(change_numbers))

    change_parser = ChangeParser()
    changes = change_parser.changes(change_numbers)

    for change in changes:
        print(repr(change.title))
        for revision in change.revisions:
            print(repr(revision.number))
            for review in revision.reviews:
                print(repr(review))

                #| Reviewer | Review | Project | Patch | Revision score | Comment |
                reviewer = review.author.name.split()[0]
                rev = '"'+change.title()+'":'+change.permalink()
                project = change.project
                patch = str(revision.number)
                score = review.vote()
                comment = review.message_without_vote().replace('\n', ' ')

                #print("|"+ reviewer +"|"+ rev +"|"+ project +"|"+ patch +"|"+ score +"|"+ comment +"|")
        print('============')

