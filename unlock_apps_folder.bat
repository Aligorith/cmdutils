@echo off

@REM Unlock "C:\Apps" folder that all software gets installed to
@REM See https://superuser.com/a/653955/728363

attrib -r -h "c:\Apps\*.*" /s /d

