#!/bin/bash
curl -s "http://localhost:8008/weather?city=Seattle&state=WA" | python3 -m json.tool
