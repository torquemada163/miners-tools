#!/bin/bash

GPU_COUNT=$(nvidia-smi --query-gpu=count --format=csv,noheader,nounits | tail -1)
for ((i=0; i < $GPU_COUNT; i++))
do
  nvidia-smi -i $i -pm 1
  nvidia-smi -i $i -pl 150
done

