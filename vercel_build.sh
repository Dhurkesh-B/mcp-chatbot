#!/bin/bash

# Create a symbolic link for the mcp package
ln -s /var/task/mcp /var/task/app/mcp

# Install requirements
pip install -r requirements.txt 