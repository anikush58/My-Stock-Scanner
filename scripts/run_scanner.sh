#!/bin/bash

curl -s http://localhost:8000/scanner/run >> /home/ubuntu/my-stock-scanner/scanner.log

echo "" >> /home/ubuntu/my-stock-scanner/scanner.log
echo "======================================" >> /home/ubuntu/my-stock-scanner/scanner.log
echo "$(date)" >> /home/ubuntu/my-stock-scanner/scanner.log
echo "======================================" >> /home/ubuntu/my-stock-scanner/scanner.log
