#!/usr/bin/env bash

BOT_RC=gerrit-bot-rc

if [ ! -f $BOT_RC ]; then
    echo $BOT_RC not found. Run: cp $BOT_RC{.sample,}
    echo and adapt it to your context. Aborting.
    exit 1
fi

if [ -z $(stat -c %A $BOT_RC | grep '^...-------$') ]; then
    echo For security reasons, $BOT_RC should have 600 permissions.
    echo To fix it, run: chmod 600 $BOT_RC
    echo Aborting.
    exit 1
fi

source $BOT_RC

set -e

if [ -z $VENV_DIR ]; then
    echo '$VENV_DIR' is not set. You must set it in $BOT_RC. Aborting.
    exit 1
fi

if [ ! -d $VENV_DIR ]; then
    echo Installing virtual environment and dependencies
    virtualenv $VENV_DIR
    source $VENV_DIR/bin/activate

    pip install python-redmine

    deactivate
    echo Done.
fi

echo Running Gerrit Bot
source $VENV_DIR/bin/activate

python redminer.py

deactivate
echo Done
