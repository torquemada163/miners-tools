#!/bin/bash

GPUCLOCK=-100
GPUMEM=1200
CMD='/usr/bin/nvidia-settings'
CMD_AMD='/home/klondike163ld/custom_services/custom_scripts/ohgodatool'

for NUM_GPU in {0..4}
  do
    ${CMD} -a [gpu:${NUM_GPU}]/GPUMemoryTransferRateOffset[3]=${GPUMEM}
    ${CMD} -a [gpu:${NUM_GPU}]/GPUGraphicsClockOffset[3]=${GPUCLOCK}
    ${CMD} -a [gpu:${NUM_GPU}]/GPUPowerMizerMode=1
    ${CMD} -a [gpu:${NUM_GPU}]/GPUFanControlState=1
  done

${CMD} -a [gpu:1]/GPUMemoryTransferRateOffset[1]=1800
${CMD} -a [gpu:1]/GPUGraphicsClockOffset[1]=-100

${CMD} -a [fan:0]/GPUTargetFanSpeed=100
${CMD} -a [fan:1]/GPUTargetFanSpeed=100
${CMD} -a [fan:2]/GPUTargetFanSpeed=100
${CMD} -a [fan:3]/GPUTargetFanSpeed=100
${CMD} -a [fan:4]/GPUTargetFanSpeed=100


#{CMD} -a [gpu:2]/GPUGraphicsClockOffset[3]=150

for NUM_AMD in {0..10}
  do
    sudo ${CMD_AMD} -i ${NUM_AMD} --set-fanspeed 90 --core-state 4 --mem-state 2 --mem-clock 2200
  done

#sudo /home/klondike163ld/custom_services/custom_scripts/ohgodatool -i 0 --set-fanspeed 90 --core-state 4 --mem-state 2 --mem-clock 2200
#sudo /home/klondike163ld/custom_services/custom_scripts/ohgodatool -i 2 --set-fanspeed 90 --core-state 4 --mem-state 2 --mem-clock 2200
#sudo /home/klondike163ld/custom_services/custom_scripts/ohgodatool -i 5 --set-fanspeed 90 --core-state 4 --mem-state 2 --mem-clock 2200

exit 0
