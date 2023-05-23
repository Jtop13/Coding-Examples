#!/bin/bash

# write out current crontab
crontab -l > mycron

# echo new cron into cron file
echo "0 0 * * * /public_html/wsgi/updateStock.py" >> mycron

# install new cron file
crontab mycron
rm mycron
