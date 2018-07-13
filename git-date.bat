@echo off
@REM git show -s --format=%ci <commit-id>

echo git-date [commit-id]
git show "%1" -s --format=%%ci 
