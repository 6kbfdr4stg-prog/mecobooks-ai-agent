#!/bin/bash
pwd > diag.log
whoami >> diag.log
ls -la >> diag.log
python3 --version >> diag.log 2>&1
./cloudflared --version >> diag.log 2>&1
nohup python3 server.py > server.log 2>&1 &
echo "Server started: $!" >> diag.log
sleep 5
nohup ./cloudflared tunnel --url http://localhost:5001 > tunnel.log 2>&1 &
echo "Tunnel started: $!" >> diag.log
sleep 10
grep "trycloudflare.com" tunnel.log >> diag.log
