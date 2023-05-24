#!/bin/bash

#get current date
DATE=$(date +%Y-%m-%d-%H-%M)

#source directory to be backed up
SRC_DIR="/home/jtopper/Downloads"

#destination directory
DEST_DIR="/home/jtopper/Downloads"

#create backup
zip -r $DEST_DIR/backup-$DATE.zip $SRC_DIR

echo "Backup for $SRC_DIR created at $DEST_DIR/backup-$DATE.zip"

