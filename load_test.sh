#!/usr/bin/bash

wrk -t32 -c256 -d40s -s wrk.lua http://127.0.0.1:8000/shorten_url
