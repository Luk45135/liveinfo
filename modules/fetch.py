import subprocess
import shlex
from csv import writer
import json
from dataclasses import dataclass
import humanfriendly


def run(cmd: str, shell: bool = False) -> str:
    result = subprocess.run(
        cmd if shell else shlex.split(cmd),
        capture_output=True,
        text=True,
        shell=shell
    )
    return result.stdout.strip()

@dataclass
class Disk:
    disk_type: str # SDD / HDD
    size_str: str # 931.5G or 1.00TB depending on if f3 is used
    size_bytes: float # parsed disk size used for sorting
    model: str
    power_on_hours: str
    # written_data: str
    # read_speed: str
    # write_speed: str
    # smart_status: str

def get_disks():
    # Run lsblk and get raw output
    lsblk_json = json.loads(run("lsblk -d -o PATH,ROTA,TYPE,SIZE,TRAN,MODEL --noheading -J"))

    disks = []

    for device in lsblk_json.get("blockdevices", []):
        if device["type"] != "disk":
            continue # Skip if it isnt a disk
        if device.get("tran") == "usb":
            continue # Skip if it's attached via USB

        


        if device.get("tran") == "nvme":
            power_on_hours = run(f"sudo smartctl --all {device.get("path")} | awk -F: '/Power On Hours/ {{print $2}}'".strip(), shell=True) + "h"
        else:
            power_on_hours= run(f"sudo smartctl --all {device.get("path")} | awk '/Power_On_Hours/ {{for (i=1; i<NF; i++) if ($i == \"-\") print $(i+1)}}'", shell=True) + "h"

        disks.append(Disk(
            disk_type = "SSD" if not device.get("rota") else "HDD",
            size_str = device.get("size"),
            # size_str = run(f"sudo f3probe {disk[3]} | awk -F: '/Module/ {{gsub(/^ +| +$/, \"\", $2); split($2, a, \" \"); print a[1], a[2]}}'", shell=True),
            size_bytes = humanfriendly.parse_size(device.get("size")),
            model = device.get("model", "Unknown"),
            power_on_hours = power_on_hours,
            # written_data = written_data,
            # read_speed = read_speed,
            # write_speed = write_speed,
            # smart_status = smart_status
        ))

    return sorted(disks, key=lambda d: (d.disk_type != "SSD", -d.size_bytes))

    # for line in lsblk_out.strip().splitlines():
    #     parts = line.split(None, 5)  # Split into max 4 parts
    #     if len(parts) < 6 or parts[2] != "disk":
    #         continue  # Skip if not a full line or not a disk
    #     path, rota, _type, size_str, model, tran = parts
    #
    #
    #     print(tran)
    #     if tran == "usb": # If the disk is attached via USB dont include it in the list
    #         continue
    #
    #     size_parsed = humanfriendly.parse_size(size_str)
    #
    #     disk_type = "SSD" if rota == "0" else "HDD"

        # disks.append((size_parsed, [disk_type, size_str, model, path, tran]))

    # Sort using size_gb (from tuple[0]), then discard it
    # return [entry for _, entry in sorted(disks, key=lambda x: (x[1][0] != "SSD", -x[0]))]


# List that will become csv
csv = []

# Fastfetch default settings
ff = "fastfetch --logo none --key-type none " # ending space to make following commands cleaner

# Host
host = run(ff + "--structure host")
csv.append(["Modell", host])

# CPU
cpu = run(ff + "--structure cpu --cpu-format '{1} ({3}c/{4}t) @ {7}'")
arch = run("getconf LONG_BIT") + "-bit"
csv.append(["Prozessor", f"{cpu} {arch}"])

# Boot Manager
bootmgr = run(ff + "--structure bootmgr --bootmgr-format '{1}'")
csv.append(["UEFI/Legacy", bootmgr])

# TPM?
tpm = run(ff + "--structure tpm")
csv.append(["TPM", tpm])

# Memory
memory = run("lsmem | awk '/Total online memory:/ {print $4}'", shell=True)
csv.append(["Arbeitsspeicher", memory])

# GPU
gpu = run(ff + "--structure gpu --gpu-format '{2}'")
gpu_mem = run("glxinfo -B | awk -F: '/Dedicated video memory/ { print $2 }'", shell=True)
gpu_clock = run("clinfo --prop CL_DEVICE_MAX_CLOCK_FREQUENCY | awk '{print $NF}'", shell=True).strip() + " MHz" # only works if gpu supports opencl
csv.append(["Grafikkarte", f"{gpu} {gpu_mem} {gpu_clock}".strip()]) # strip because gpu_mem or gpu_clock might not work

# Disks
for disk in get_disks():
    csv.append([disk.disk_type, disk.model])
    csv.append(["Grösse", disk.size_str])
    csv.append(["Betriebsstunden", disk.power_on_hours])
    # csv.append(["Geschriebene Daten", disk.written_data])
    # csv.append(["Lesegeschwindigkeit", disk.read_speed])
    # csv.append(["Schreibgeschwindigkeit", disk.write_speed])
    # csv.append(["SMART-Status", disk.smart_status])



with open("system_info.csv", "w", newline="") as csvfile:
    csv_writer = writer(csvfile)
    csv_writer.writerows(csv)

# run("okular system_info.csv")
    
print(csv)

# print(get_disks())



