# Copyright 2014 Gabriel Assis Bezerra
#
# Script to fetch and parse changes from Gerrit

from __future__ import print_function
from datetime import datetime

import json
import urllib2

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
        url = "https://review.openstack.org/changes/" + str(change_number) + "?o=all_revisions&o=messages"
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
        stripped_message = self.message.strip()
        return stripped_message.partition('\n\n')[2].strip() if len(stripped_message.split('\n')) > 1 else stripped_message.partition(':')[2].strip()

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

            # In some abandoned changes, the "Code-Review" label is not present, so we fallback to an empty one.
            code_reviews = revision["labels"].get("Code-Review", { "all": [] })["all"]
            for code_review in code_reviews:
                #debug(change["messages"])
                author = Author(code_review.get("username", ""), code_review["name"], code_review.get("email", ""))
                debug(author)

                value = code_review["value"]

                messages_of_this_revision_of_this_author = [m for m in messages_of_this_revision if m["author"]["name"] == author.name]
                #debug(messages_of_this_revision_of_this_author)

                for message in messages_of_this_revision_of_this_author:
                    message_text = message["message"]
                    #debug(message)

                    # Timestamps are given in UTC and have the format "yyyy-mm-dd hh:mm:ss.fffffffff" where "ffffffffff" indicates the nanoseconds.
                    timestamp = datetime.strptime(message["date"].rpartition('.')[0]+" UTC", "%Y-%m-%d %H:%M:%S %Z")

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

