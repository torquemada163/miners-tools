#!/bin/bash

CMD_AMD='/home/klondike163ld/custom_services/custom_scripts/ohgodatool'

for NUM_AMD in {0..10}
  do
    if GPU_TEMP=$(sudo $CMD_AMD -i ${NUM_AMD} --show-temp) && GPU_FAN=$(sudo $CMD_AMD -i ${NUM_AMD} --show-fanspeed); then
      echo "GPU: $NUM_AMD TEMP: $GPU_TEMP FAN: $GPU_FAN"
    else
      true
    fi
  done

exit 0
