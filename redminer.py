from __future__ import print_function

from redmine import Redmine
from os import environ as env

from changes import ChangeParser
from inputparser import ParsedInputPage


# Wiki and Report abstraction

class ReportPage:
    def __init__(self, title, changes):
        self.title = title
        self.changes = changes

    def wiki_text(self):
        return self.__crlf_ed(self.__template_with(self.title, self.__change_rows()))

    def __change_rows(self):
        def review_filter(review):
            #TODO: filter by date
            return review.author.email.endswith("@lsd.ufcg.edu.br")

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

    def __template_with(self, title, change_rows):
        template = \
"""h1. $title$

table{border:1px bordercolor:darkblue}.
|_{background:#ffa}.Reviewer|_{background:#ffa}.Review|_{background:#ffa}.Project|_{background:#ffa}.Patch|_{background:#ffa}.Revision score|_{background:#ffa}.Comment|
$change_rows$"""
        return template.replace('$title$', title).replace('$change_rows$', '\n'.join(change_rows))

    def __crlf_ed(self, text):
        return text.replace('\n', '\r\n')


class RedmineWiki:
    def __init__(self, address, key, project_name):
        self.redmine = Redmine(address, key=key)

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

input_page_name = 'Code Reviews'

print("Fetching input page from Redmine.")
wiki = RedmineWiki(redmine_address, redmine_key, project_name)
input_page = wiki.get(input_page_name)

print("Parsing input page.")
parsed_input_page = ParsedInputPage(input_page.text)

print("Start updating the report of code reviews.")
change_parser = ChangeParser()
for report_item in parsed_input_page.report_items:
    if report_item.should_be_updated:
        print("Fetching: {0}".format(report_item.wiki_page))
        changes = change_parser.changes(report_item.review_numbers)

        report_page = ReportPage(report_item.wiki_page, changes)
        page_title = report_page.title

        print("Updating {0} on Redmine".format(page_title))
        if wiki.create_or_update(page_title, report_page.wiki_text()):
            print("Done updating {0} on Redmine".format(page_title))
        else:
            print("Failed updating {0} on Redmine".format(page_title))
    else:
        print("Skipping: {0}".format(report_item.wiki_page))

print("Done.")
