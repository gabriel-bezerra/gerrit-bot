# Copyright 2014 Gabriel Assis Bezerra
#
# A parser for the input page from redmine with each wiki page, and their change_numbers and valid dates

from __future__ import print_function

def debug(message):
    pass
    #print(message)


class Row:
    def __init__(self, wiki_page, sprint, from_date, until_date, should_be_updated, review_numbers):
        self.wiki_page = wiki_page
        self.sprint = sprint
        self.from_date = from_date
        self.until_date = until_date
        self.should_be_updated = should_be_updated
        self.review_numbers = review_numbers

class ReviewTable:
    def __init__(self, wiki_text_with_CRLF):
        wiki_text = wiki_text_with_CRLF.replace('\r','')

        table_index = wiki_text.find('\ntable{') + 1 #remove the \n
        titles_row_index = wiki_text.find('|', table_index)
        first_row_index = wiki_text.find('\n|', titles_row_index) + 1 #remove the \n
        after_last_row_index = wiki_text.find('\n\n', first_row_index)

        column_titles_text = wiki_text[titles_row_index:first_row_index]
        rows_text = wiki_text[first_row_index:after_last_row_index]

        self.columns = self.__parse_columns_from(column_titles_text)
        debug("columns = {0}".format(repr(self.columns)))

        self.rows = self.__parse_rows_from(self.columns, rows_text)


    def __parse_columns_from(self, column_titles_text):
        raw_cols = column_titles_text.split('|')

        def clean_col_name(col_field):
            return col_field.partition('.')[2].split('(')[0].strip()

        return [clean_col_name(c) for c in raw_cols if c.strip()]

    def __parse_rows_from(self, columns, rows_text):
        raw_rows = [r for r in rows_text.split('\n') if r.strip()]

        def parse_row(raw_row):
            raw_row_without_leading_and_trailing_pipes = raw_row[1:-1]
            row_fields = [f.strip() for f in raw_row_without_leading_and_trailing_pipes.split('|')]
            debug("row_fields = {0}".format(repr(row_fields)))

            wiki_page = row_fields[columns.index('Wiki page')][2:-2].strip()  # to remove [[ and ]]
            sprint = row_fields[columns.index('Sprint')]
            from_date = row_fields[columns.index('From')]
            until_date = row_fields[columns.index('Until')]
            should_be_updated = row_fields[columns.index('Should be updated')].lower()
            review_numbers = row_fields[columns.index('Review numbers')]

            return Row(wiki_page, sprint, from_date, until_date, should_be_updated, review_numbers)

        return [parse_row(r) for r in raw_rows]

test_sample = \
u"""
h1. Code Reviews

some text

table{border:1px bordercolor:darkblue}.
|_{background:#ffa}.Wiki page|_{background:#ffa}.Sprint|_{background:#ffa}.From (YYYY-MM-DD)|_{background:#ffa}.Until (YYYY-MM-DD)|_{background:#ffa}.Should be updated (yes/no)|_{background:#ffa}.Review numbers (space separated list)|
| [[US904 - As a Dev I want to do code review on OpenStack code]] | #9 | 2014-04-28 | 2014-05-18 | YeS | 89220 90476 |
|[[US1004 - As a Dev I want to do code review on OpenStack code]]| #10 | 2014-05-19 | 2014-06-08 | nO | |
| [[US1104 - As a Dev I want to do code review on OpenStack code]] | #11 | | | | |
|||||||
| [[  ]] ||||yes||

more text
"""

review_table = ReviewTable(test_sample)
assert review_table.columns == ['Wiki page', 'Sprint', 'From', 'Until', 'Should be updated', 'Review numbers']

##| [[US904 - As a Dev I want to do code review on OpenStack code]] | #9 | 2014-04-28 | 2014-05-18 | yes | 89220 90476 |
assert review_table.rows[0].wiki_page == 'US904 - As a Dev I want to do code review on OpenStack code'
assert review_table.rows[0].sprint == '#9'
assert review_table.rows[0].from_date == '2014-04-28'
assert review_table.rows[0].until_date == '2014-05-18'
assert review_table.rows[0].should_be_updated == 'yes'
assert review_table.rows[0].review_numbers == '89220 90476'

#|[[US1004 - As a Dev I want to do code review on OpenStack code]]| #10 | 2014-05-19 | 2014-06-08 | no | |
assert review_table.rows[1].wiki_page == 'US1004 - As a Dev I want to do code review on OpenStack code'
assert review_table.rows[1].sprint == '#10'
assert review_table.rows[1].from_date == '2014-05-19'
assert review_table.rows[1].until_date == '2014-06-08'
assert review_table.rows[1].should_be_updated == 'no'
assert review_table.rows[1].review_numbers == ''

#| [[US1104 - As a Dev I want to do code review on OpenStack code]] | #11 | | | | |
assert review_table.rows[2].wiki_page == 'US1104 - As a Dev I want to do code review on OpenStack code'
assert review_table.rows[2].sprint == '#11'
assert review_table.rows[2].from_date == ''
assert review_table.rows[2].until_date == ''
assert review_table.rows[2].should_be_updated == ''
assert review_table.rows[2].review_numbers == ''

#|||||||
assert review_table.rows[3].wiki_page == ''
assert review_table.rows[3].sprint == ''
assert review_table.rows[3].from_date == ''
assert review_table.rows[3].until_date == ''
assert review_table.rows[3].should_be_updated == ''
assert review_table.rows[3].review_numbers == ''

#| [[  ]] ||||yes||
assert review_table.rows[4].wiki_page == ''
assert review_table.rows[4].sprint == ''
assert review_table.rows[4].from_date == ''
assert review_table.rows[4].until_date == ''
assert review_table.rows[4].should_be_updated == 'yes'
assert review_table.rows[4].review_numbers == ''


#TODO: Add tzinfo
from datetime import datetime, date, time

def parse_date(date_str):
    return datetime.strptime(date_str, '%Y-%m-%d')

assert parse_date('2014-04-28') == datetime.combine(date(year=2014, month=4, day=28), time.min)
assert parse_date('2014-04-28') == parse_date('2014-04-28')
assert parse_date('2014-04-27') < parse_date('2014-04-28')
assert parse_date('2014-04-29') > parse_date('2014-04-28')

class ReviewReportItem:
    def __init__(self, row):
        self.wiki_page = row.wiki_page
        self.sprint = row.sprint

        self.from_date = parse_date(row.from_date) if row.from_date else None
        self.until_date = parse_date(row.until_date) if row.from_date else None

        self.should_be_updated = bool(self.wiki_page) and (row.should_be_updated == 'yes')

        self.review_numbers = row.review_numbers.split()

    def __repr__(self):
        return 'ReviewReportItem({0}, {1}, {2}, {3}, {4}, {5})'.format(repr(self.wiki_page), repr(self.sprint), repr(self.from_date), \
                repr(self.until_date), repr(self.should_be_updated), repr(self.review_numbers))

report_items = [ReviewReportItem(r) for r in review_table.rows]

##| [[US904 - As a Dev I want to do code review on OpenStack code]] | #9 | 2014-04-28 | 2014-05-18 | yes | 89220 90476 |
assert report_items[0].wiki_page == 'US904 - As a Dev I want to do code review on OpenStack code'
assert report_items[0].sprint == '#9'
assert report_items[0].from_date == parse_date('2014-04-28')
assert report_items[0].until_date == parse_date('2014-05-18')
assert report_items[0].should_be_updated == True
assert report_items[0].review_numbers == ['89220', '90476']

#| [[US1004 - As a Dev I want to do code review on OpenStack code]] | #10 | 2014-05-19 | 2014-06-08 | no | |
assert report_items[1].wiki_page == 'US1004 - As a Dev I want to do code review on OpenStack code'
assert report_items[1].sprint == '#10'
assert report_items[1].from_date == parse_date('2014-05-19')
assert report_items[1].until_date == parse_date('2014-06-08')
assert report_items[1].should_be_updated == False
assert report_items[1].review_numbers == []

#| [[US1104 - As a Dev I want to do code review on OpenStack code]] | #11 | | | | |
assert report_items[2].wiki_page == 'US1104 - As a Dev I want to do code review on OpenStack code'
assert report_items[2].sprint == '#11'
assert report_items[2].from_date == None
assert report_items[2].until_date == None
assert report_items[2].should_be_updated == False
assert report_items[2].review_numbers == []

#|||||||
assert report_items[3].wiki_page == ''
assert report_items[3].sprint == ''
assert report_items[3].from_date == None
assert report_items[3].until_date == None
assert report_items[3].should_be_updated == False
assert report_items[3].review_numbers == []

#| [[  ]] ||||yes||
assert report_items[4].wiki_page == ''
assert report_items[4].sprint == ''
assert report_items[4].from_date == None
assert report_items[4].until_date == None
assert report_items[4].should_be_updated == False
assert report_items[4].review_numbers == []


class ParsedInputPage:
    def __init__(self, wiki_text):
        self.review_table = ReviewTable(wiki_text)
        self.report_items = [ReviewReportItem(r) for r in self.review_table.rows]

    def __repr__(self):
        return 'ParsedInputPage({0})'.format(repr(self.report_items))

