#!/bin/bash

# Check if the branch "new-branch" exists
if git show-ref --verify --quiet "refs/heads/new-branch"; then
    echo "Branch 'new-branch' already exists."
else
    # Create the branch "new-branch"
    git checkout -b new-branch
    echo "Branch 'new-branch' created."
fi
git add .
git commit -m "added to new brnach"
git push origin HEAD:new-beanch --force

