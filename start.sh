#!/usr/bin/env bash

gunicorn pepysdiary.wsgi --bind 127.0.0.1:8000 --daemon --log-file ~/dev/logs/pepysdiary_gunicorn.log --workers=3
