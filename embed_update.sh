#!/bin/bash
cd /var/www/qvantify-back
/usr/local/bin/pipenv run python /var/www/qvantify-back/async_analyze.py embed_records
