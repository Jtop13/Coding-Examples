#!/bin/bash

# Create the .gitignore file
touch .gitignore

# Add rules to the .gitignore file
echo "*.out" >> .gitignore
echo "*.log" >> .gitignore
echo "*.o" >> .gitignore
echo "*.exe" >> .gitignore
echo "tmp/" >> .gitignore

echo ".gitignore created."

