#!/bin/bash

GPUCLOCK=150
GPUMEM=-200
CMD='/usr/bin/nvidia-settings'

for NUM_GPU in {0..3}
  do
    ${CMD} -a [gpu:${NUM_GPU}]/GPUMemoryTransferRateOffset[3]=${GPUMEM}
    ${CMD} -a [gpu:${NUM_GPU}]/GPUGraphicsClockOffset[3]=${GPUCLOCK}
    ${CMD} -a [gpu:${NUM_GPU}]/GPUPowerMizerMode=1
    ${CMD} -a [gpu:${NUM_GPU}]/GPUFanControlState=1
  done

${CMD} -a [fan:0]/GPUTargetFanSpeed=80
${CMD} -a [fan:1]/GPUTargetFanSpeed=80
${CMD} -a [fan:2]/GPUTargetFanSpeed=80
${CMD} -a [fan:3]/GPUTargetFanSpeed=80


exit 0
