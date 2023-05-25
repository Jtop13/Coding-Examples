#!/bin/bash

touch .gitignore

echo "*.out" >> .gitignore
echo "*.log" >> .gitignore
echo "*.o" >> .gitignore
echo "*.exe" >> .gitignore
echo "tmp/" >> .gitignore

echo ".gitignore created."

