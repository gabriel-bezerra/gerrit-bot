gerrit-bot
==========

`gerrit-bot` is a tool to generate Gerrit code review reports on Redmine wiki pages.

## Dependencies

To run gerrit-bot you will need:
* Python 2.7
* [virtualenv][virtualenv]
* A Redmine API key.

On Ubuntu:
```no-highlight
sudo apt-get install python-virtualenv
```

## Quick Start

### Input page

Create a page on your project's wiki where `gerrit-bot` will look for its input parameters.
This page must contain a table with the following format:
```
table{border:1px bordercolor:darkblue}.
|_{background:#ffa}.Wiki page|_{background:#ffa}.Sprint|_{background:#ffa}.From (YYYY-MM-DD)|_{background:#ffa}.Until (YYYY-MM-DD)|_{background:#ffa}.Should be updated (yes/no)|_{background:#ffa}.Review numbers (space separated list)|
| [[Sprint1 - Code review report]] | #1 |  |  | no | 79411 57492 78658 |
| [[Sprint2 - Code review report]] | #2 | 2014-05-01 | 2014-05-14  | yes | 89220 90476 |
```
Where:
* **Wiki page**: an internal link of the wiki;
* **Sprint**: _(optional)_ sprint number;
* **From**: _(optional)_ date from which the reviews of the report will be filtered;
* **Until**: _(optional)_ date until which the reviews of the report will be filtered;
* **Should be updated**: if it contains "yes", `gerrit-bot` will update this page, otherwise it will skip it;
* **Review numbers**: a space separated list of Gerrit's change numbers to be used in the report.

### Install and configure it

Clone this repository:
```no-highlight
git clone https://github.com/gabriel-bezerra/gerrit-bot.git && cd gerrit-bot
```

Copy the sample configuration script and set its permissions:
```no-highlight
cp gerrit-bot-rc{.sample,} && chmod 600 gerrit-bot-rc
```

Edit your configuration file with your Redmine project information. The sample should be self explaining.
You can find your Redmine API key on your Account Settings page.

### Run

```no-highlight
./run-in-venv.sh
```

On the first run, it will create a virtualenv on $VENV_DIR and install [python-redmine][python-redmine] in it.

```bash
$ ./run-in-venv.sh
Installing virtual environment and dependencies
New python executable in venv/bin/python
Installing distribute.............................................................................................................................................................................................done.
Installing pip...............done.
Downloading/unpacking python-redmine
  Downloading python-redmine-0.8.1.tar.gz
  Running setup.py egg_info for package python-redmine

Downloading/unpacking requests>=0.12.1 (from python-redmine)
  Downloading requests-2.2.1.tar.gz (421Kb): 421Kb downloaded
  Running setup.py egg_info for package requests

Installing collected packages: python-redmine, requests
  Running setup.py install for python-redmine

  Running setup.py install for requests

Successfully installed python-redmine requests
Cleaning up...
Done.
Running Gerrit Bot
Fetching input page from Redmine.
Parsing input page.
Start updating the report of code reviews.
Skipping: Sprint1 - Code review report
Fetching: Sprint2 - Code review report
[Gerrit] Fetching: https://review.openstack.org/changes/89220?o=all_revisions&o=messages
[Gerrit] Fetching: https://review.openstack.org/changes/89220/revisions/5288a167912a1a335047f3bad4e63625b44af4b7/review
[Gerrit] Fetching: https://review.openstack.org/changes/89220/revisions/aa02e440b91c3cf1058ad82e03e698cee1d023ab/review
[Gerrit] Fetching: https://review.openstack.org/changes/89220/revisions/532dc2b47a0d2c79995232803ab25886eedba62f/review
[Gerrit] Fetching: https://review.openstack.org/changes/89220/revisions/59b94d3c75e1068356b9f04407ecf68d99dd339a/review
[Gerrit] Fetching: https://review.openstack.org/changes/89220/revisions/9eb54a98b6700d86636e8b8a13cfb35466c688ef/review
[Gerrit] Fetching: https://review.openstack.org/changes/89220/revisions/9bac24a3b0676ce83b1f2b9949efc61db3a8831c/review
[Gerrit] Fetching: https://review.openstack.org/changes/89220/revisions/cc3848d04ed916603bca759b8e5265f9b2031826/review
[Gerrit] Fetching: https://review.openstack.org/changes/89220/revisions/289b85ed080275707311e658105d7cc56cb9fec5/review
[Gerrit] Fetching: https://review.openstack.org/changes/89220/revisions/8eaaac6f05a942ff08ccd20064feef19ea3091b7/review
[Gerrit] Fetching: https://review.openstack.org/changes/89220/revisions/f62cddc261e7e54a9731e4ce02197aed71f65393/review
[Gerrit] Fetching: https://review.openstack.org/changes/89220/revisions/86747e1cb900526e38cb6fda9a9ac992cb6c5175/review
[Gerrit] Fetching: https://review.openstack.org/changes/89220/revisions/687745c175bec31cf1010a433ceb66960267013c/review
[Gerrit] Fetching: https://review.openstack.org/changes/89220/revisions/bb7c6cce990228c825cfffaa6509278d269fa816/review
[Gerrit] Fetching: https://review.openstack.org/changes/90476?o=all_revisions&o=messages
[Gerrit] Fetching: https://review.openstack.org/changes/90476/revisions/f6cb493f3fd579fe65c0cfca42c79369bfe60a1c/review
[Gerrit] Fetching: https://review.openstack.org/changes/90476/revisions/a8c54c26179ae9fc619dbbbb3ce1bb3aafcb4926/review
[Gerrit] Fetching: https://review.openstack.org/changes/90476/revisions/31c2667c24a44cfc976d5a6119b1b45fe62fcd02/review
[Gerrit] Fetching: https://review.openstack.org/changes/90476/revisions/ebe1162c2c381f69454e200ce875ac8d6e8a86e2/review
[Gerrit] Fetching: https://review.openstack.org/changes/90476/revisions/ba1bba8257716c2f5aa668e496173e96a80f0e43/review
[Gerrit] Fetching: https://review.openstack.org/changes/90476/revisions/be6fc247251883317e02d188e662b1f142fcc043/review
Updating Sprint2 - Code review report on Redmine
Done updating Sprint2 - Code review report on Redmine
Done.
Done
```

The next time you run it, it will reuse the previously created virtualenv.
```bash
$ ./run-in-venv.sh
Running Gerrit Bot
Fetching input page from Redmine.
Parsing input page.
Start updating the report of code reviews.
Skipping: Sprint1 - Code review report
Fetching: Sprint2 - Code review report
[Gerrit] Fetching: https://review.openstack.org/changes/89220?o=all_revisions&o=messages
[Gerrit] Fetching: https://review.openstack.org/changes/89220/revisions/5288a167912a1a335047f3bad4e63625b44af4b7/review
[Gerrit] Fetching: https://review.openstack.org/changes/89220/revisions/aa02e440b91c3cf1058ad82e03e698cee1d023ab/review
[Gerrit] Fetching: https://review.openstack.org/changes/89220/revisions/532dc2b47a0d2c79995232803ab25886eedba62f/review
[Gerrit] Fetching: https://review.openstack.org/changes/89220/revisions/59b94d3c75e1068356b9f04407ecf68d99dd339a/review
[Gerrit] Fetching: https://review.openstack.org/changes/89220/revisions/9eb54a98b6700d86636e8b8a13cfb35466c688ef/review
[Gerrit] Fetching: https://review.openstack.org/changes/89220/revisions/9bac24a3b0676ce83b1f2b9949efc61db3a8831c/review
[Gerrit] Fetching: https://review.openstack.org/changes/89220/revisions/cc3848d04ed916603bca759b8e5265f9b2031826/review
[Gerrit] Fetching: https://review.openstack.org/changes/89220/revisions/289b85ed080275707311e658105d7cc56cb9fec5/review
[Gerrit] Fetching: https://review.openstack.org/changes/89220/revisions/8eaaac6f05a942ff08ccd20064feef19ea3091b7/review
[Gerrit] Fetching: https://review.openstack.org/changes/89220/revisions/f62cddc261e7e54a9731e4ce02197aed71f65393/review
[Gerrit] Fetching: https://review.openstack.org/changes/89220/revisions/86747e1cb900526e38cb6fda9a9ac992cb6c5175/review
[Gerrit] Fetching: https://review.openstack.org/changes/89220/revisions/687745c175bec31cf1010a433ceb66960267013c/review
[Gerrit] Fetching: https://review.openstack.org/changes/89220/revisions/bb7c6cce990228c825cfffaa6509278d269fa816/review
[Gerrit] Fetching: https://review.openstack.org/changes/90476?o=all_revisions&o=messages
[Gerrit] Fetching: https://review.openstack.org/changes/90476/revisions/f6cb493f3fd579fe65c0cfca42c79369bfe60a1c/review
[Gerrit] Fetching: https://review.openstack.org/changes/90476/revisions/a8c54c26179ae9fc619dbbbb3ce1bb3aafcb4926/review
[Gerrit] Fetching: https://review.openstack.org/changes/90476/revisions/31c2667c24a44cfc976d5a6119b1b45fe62fcd02/review
[Gerrit] Fetching: https://review.openstack.org/changes/90476/revisions/ebe1162c2c381f69454e200ce875ac8d6e8a86e2/review
[Gerrit] Fetching: https://review.openstack.org/changes/90476/revisions/ba1bba8257716c2f5aa668e496173e96a80f0e43/review
[Gerrit] Fetching: https://review.openstack.org/changes/90476/revisions/be6fc247251883317e02d188e662b1f142fcc043/review
Updating Sprint2 - Code review report on Redmine
Done updating Sprint2 - Code review report on Redmine
Done.
Done
```

[virtualenv]: http://www.virtualenv.org/
[python-redmine]: https://github.com/maxtepkeev/python-redmine
