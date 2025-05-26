

host=$(fastfetch --logo none --key-type none --structure host)
cpu=$(fastfetch --logo none --key-type none --structure cpu --cpu-format "{1} ({3}c/{4}t) @ {7} ")$(getconf LONG_BIT)-bit
# sysbench_score=$(sysbench --threads="$(nproc)" cpu run | awk '/events per second:/ {print $4}')
bootmgr=$(fastfetch --logo none --key-type none --structure bootmgr --bootmgr-format "{1}")
memory=$(lsmem | awk '/Total online memory:/ {print $4}')
gpu=$(fastfetch --logo none --key-type none --structure gpu --gpu-format "{2}")$(glxinfo -B | awk -F: '/Dedicated video memory/ { print $2 }')
gpu_clock=$(clinfo --prop CL_DEVICE_MAX_CLOCK_FREQUENCY | awk '{print $NF " MHz"}')
# glmark2_score=$(glmark2 | awk '/glmark2 Score:/ {print $NF}')


echo $host
echo $cpu
# echo $sysbench_score
echo $bootmgr
echo $memory
echo $gpu $gpu_clock
# echo $glmark2_score
