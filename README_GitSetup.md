### Starting out
1. In Git Bash or CMD, change directory to working folder
2. '*git init*' to make the folder into a local repository
3. *'git remote add **(name)** https://github.com/RasmusMeyer/SnowDepth'* to create a connection between this and local repository folder
4. *'git pull **(name)** main'* to pull all content from the remotely added repository (allows pushing)
5. *'git branch -M main'* to create a new local branch to push from (-M force overwrites in case a branch with the same name already exists)
6. *'git push -u **(name)** main'* with -u being used to connect the newly created local branch to the one furthest upstream (main) in **(name)**. This allows pushing and pulling without manually defining the repository and branch

### Adding, comitting and pushing new or modified files
1. *'git add **(filename)**'* or *"git add .*" to mark a either a single file or all files in the folder for inclusion in the next commit
2. *'git commit -m "message"'* to capture a snapshot of the added files, getting them ready to be pushed to the repository
3. *'git push'* to push the committed files to the repository
