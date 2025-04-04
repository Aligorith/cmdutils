@REM echo off

@REM Check which processes use a given path, locking it
@REM https://superuser.com/questions/117902/find-out-which-process-is-locking-a-file-or-folder-in-windows#comment2549849_1203347
@REM
@REM Requires: https://learn.microsoft.com/en-us/sysinternals/downloads/handle

handle.exe -u -nobanner -accepteula %*