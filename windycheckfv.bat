@echo off
setlocal

cd C:\Program Files\Windows Defender
MpCmdRun -Scan -ScanType 3 -File %1

endlocal
