#!/bin/bash

# Get the current version from PyPI
current_version=$(pip install ava-mosaic-ai==invalid 2>&1 | grep -oP "(?<=\(from versions: ).*(?=\))" | awk '{print $NF}')

# Get the latest git tag
latest_tag=$(git describe --tags --abbrev=0)

# Remove the 'v' prefix if it exists
latest_tag=${latest_tag#v}

# Compare versions
if [ "$current_version" = "$latest_tag" ]; then
    echo "Error: Version $latest_tag already exists on PyPI. Please increment the git tag before publishing."
    exit 1
else
    echo "Version check passed. Current PyPI version: $current_version, New version: $latest_tag"
    exit 0
fi