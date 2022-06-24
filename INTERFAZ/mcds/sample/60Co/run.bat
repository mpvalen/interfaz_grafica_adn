@echo off
cls

ECHO MCDS Simulation for 60Co 
set MCDS=..\..\bin\mcds.exe

%MCDS% Co60(park).inp
%MCDS% Co60(hsaio).inp

set MCDS=