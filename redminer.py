# Copyright 2014 Gabriel Assis Bezerra
#
# Script to fetch changes from Gerrit according to a wiki page on Redmine and generate report wiki pages

from __future__ import print_function

import time
import argparse
from os import environ as env
from redmine import Redmine

from gerriter import ChangeParser
from inputparser import ParsedInputPage


# Wiki and Report abstraction

class ReportPage:
    def __init__(self, report_item, changes, page_timestamp):
        self.report_item = report_item
        self.title = report_item.wiki_page

        self.changes = changes

        self.page_timestamp = page_timestamp

    def wiki_text(self):
        return self.__crlf_ed(self.__template_with(self.title, self.__change_rows(), self.page_timestamp))

    def __change_rows(self):
        def review_filter(review):
            return review.author.email.endswith("@lsd.ufcg.edu.br") and \
                    (self.report_item.from_date <= review.timestamp if self.report_item.from_date != None else True) and \
                    (review.timestamp <= self.report_item.until_date  if self.report_item.until_date != None else True)

        change_rows = []
        for change in self.changes:
            for revision in change.revisions:
                for review in revision.reviews:
                    if review_filter(review):
                        #| Reviewer | Review | Project | Patch | Revision score | Comment |
                        reviewer = review.author.name.split()[0]
                        rev = '"'+change.title()+'":'+change.permalink()
                        project = change.project
                        patch = str(revision.number)
                        score = review.vote()
                        comment = review.message_without_vote().replace('\n', ' ')

                        change_rows.append("|"+ reviewer +"|"+ rev +"|"+ project +"|"+ patch +"|"+ score +"|"+ comment +"|")

        return change_rows

    def __template_with(self, title, change_rows, page_timestamp):
        time_string = time.strftime("%Y-%m-%d %H:%M:%S %Z", page_timestamp)
        template = \
"""h1. $title$

table{border:1px bordercolor:darkblue}.
|_{background:#ffa}.Reviewer|_{background:#ffa}.Review|_{background:#ffa}.Project|_{background:#ffa}.Patch|_{background:#ffa}.Revision score|_{background:#ffa}.Comment|
$change_rows$

Last updated on: $page_timestamp$"""
        return template.replace('$title$', title).replace('$change_rows$', '\n'.join(change_rows)).replace('$page_timestamp$', time_string)

    def __crlf_ed(self, text):
        return text.replace('\n', '\r\n')


class RedmineWiki:
    def __init__(self, redmine, project_name):
        self.redmine = redmine

        project = self.redmine.project.get(project_name)
        self.project_id = project.id

    def create_or_update(self, title, wiki_text):
        return self.redmine.wiki_page.update(title, text=wiki_text, project_id=self.project_id)

    def get(self, title):
        return self.redmine.wiki_page.get(title, project_id=self.project_id)


# Action

redmine_address = env['REDMINE_ADDRESS']
redmine_key = env['REDMINE_KEY']
project_name = env['REDMINE_PROJECT']
input_page_name = env['REDMINE_INPUT_PAGE']

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument('-n', '--dry-run', action='store_true', help='does not write reports back to Redmine')
arg_parser.add_argument('-s', '--std-out', action='store_true', help='prints reports on standard output')
arg_parser.add_argument('-I', '--ignore-should-be-updated', action='store_true', help='ignores "Should be updated" column of input table and updates all reports. USE WITH CAUTION!')
args = arg_parser.parse_args()

wiki = RedmineWiki(Redmine(redmine_address, key=redmine_key), project_name)

print("Fetching input page from Redmine.")
input_page = wiki.get(input_page_name)

print("Parsing input page.")
parsed_input_page = ParsedInputPage(input_page.text)

print("Start updating the report of code reviews.")
change_parser = ChangeParser()
for report_item in parsed_input_page.report_items:
    if report_item.should_be_updated or args.ignore_should_be_updated:
        print("Fetching: {0}".format(report_item.wiki_page))
        timestamp = time.localtime()
        changes = change_parser.changes(report_item.review_numbers)

        report_page = ReportPage(report_item, changes, timestamp)
        page_title = report_page.title
        page_text = report_page.wiki_text()

        if args.std_out:
            print('"{0}"\'s text:\n{1}'.format(page_title, page_text))

        if args.dry_run:
            print("Would update {0} on Redmine".format(page_title))
        else:
            print("Updating {0} on Redmine".format(page_title))
            if wiki.create_or_update(page_title, page_text):
                print("Done updating {0} on Redmine".format(page_title))
            else:
                print("Failed updating {0} on Redmine".format(page_title))
    else:
        print("Skipping: {0}".format(report_item.wiki_page))

print("Done.")
