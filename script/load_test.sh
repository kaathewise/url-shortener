#!/bin/bash

wrk -t16 -c8 -d10s -s wrk.lua http://127.0.0.1:8000/shorten_url
