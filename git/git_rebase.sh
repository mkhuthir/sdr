#!/bin/sh

git checkout --orphan latest_branch  #Checkout/create orphan branch
git add -A #Add all the files to the newly created branc
git commit -am "rebase!" #Commit the changes
git branch -D master #Delete main/master (default) branch
git branch -m master #Rename the current branch to main/master
git push -f origin master #Finally, all changes are completed on your local repository, and force update your remote repository





