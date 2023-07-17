#!/bin/bash

while true; do
    # Execute your command here
    python sample_frames.py ../datasets/DFDC/ 20

    # Wait for an hour (3600 seconds)
    sleep 3600
done