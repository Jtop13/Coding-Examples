#!/bin/bash

echo "Enter subnet for scan: "
read subnet

outputFile="networkScanResult.txt"

#run nmap scan
nmap -sV -O -sS -Pn -p- --script=default,discovery,vuln,version -oN $outputFile $subnet

echo "Scan completed check $outputFile file for results."
