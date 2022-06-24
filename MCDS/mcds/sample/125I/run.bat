@echo off
cls

ECHO MCDS Simulation for 125I
set MCDS=..\..\bin\mcds.exe

%MCDS% I125.inp

set MCDS=