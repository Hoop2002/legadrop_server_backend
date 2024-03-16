#! /usr/bin/env bash

celery -A legadrop beat --loglevel=INFO -S django