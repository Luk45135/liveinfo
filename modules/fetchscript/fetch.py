#!/usr/bin/env python3

import os
from pathlib import Path
import subprocess
import shlex
from csv import writer
import json
from dataclasses import dataclass
import humanfriendly
from dmidecode import DMIParse



def run(cmd: str, shell: bool = False) -> str:
    result = subprocess.run(
        cmd if shell else shlex.split(cmd),
        capture_output=True,
        text=True,
        shell=shell
    )
    if result.returncode != 0:
        print(f"Command failed: {cmd}\n{result.stderr}")
    return result.stdout.strip()

def get_fio_read_json(filename: str, runtime: int = 20, jobname: str = "read_test") -> dict:
    fio_read_json_cmd = f"sudo fio --direct=1 --rw=randread --bs=4k --ioengine=libaio --iodepth=256 --runtime={runtime} --numjobs=4 --time_based --group_reporting --eta-newline=1 --readonly --output-format=json --filename={filename} --name={jobname}"
    return json.loads(run(fio_read_json_cmd))


@dataclass
class Disk:
    disk_type: str # SDD / HDD
    size_str: str # 931.5G or 1.00TB depending on if f3 is used
    size_bytes: float # parsed disk size used for sorting
    model: str
    power_on_hours: str
    written_data: str
    read_speed: str
    # write_speed: str
    smart_status: str

def get_disks():
    # Run lsblk and get raw output
    lsblk_json = json.loads(run("lsblk -d -o PATH,ROTA,TYPE,SIZE,TRAN,MODEL --noheading -J"))

    disks = []

    for device in lsblk_json.get("blockdevices", []):
        if device["type"] != "disk":
            continue # Skip if it isnt a disk
        if device.get("tran") == "usb":
            continue # Skip if it's attached via USB

        path = device.get("path") # Get disk path like /dev/sda
        disk_type = "HDD" if device.get("rota") else "SSD" # If it's a ROTAting disk its a HDD else its a SSD

        smartctl_json = json.loads(run(f"sudo smartctl -a -j {path}")) # Get SMART info for disk

        # size_str = device.get("size") # for testing
        print(f"Verifying real disk size of {path}")
        size_str = run(f"sudo f3probe {path} | awk -F: '/Module/ {{gsub(/^ +| +$/, \"\", $2); split($2, a, \" \"); print a[1], a[2]}}'", shell=True)

        power_on_hours = str(smartctl_json.get("power_on_time", {}).get("hours")) + "h" # This is the same on nvme ssd, sata ssd and sata hdd

        logical_block_size = smartctl_json.get("logical_block_size", 512) # Used for calculating total disk writes
        parsed_written_data = None # Initialize var for later
        fio_runtime = 20 # Initialize var for later

        if device.get("tran") == "nvme":
            raw_written_value = smartctl_json.get("nvme_smart_health_information_log", {}).get("data_units_written")
            if raw_written_value is not None:
                parsed_written_data = (raw_written_value * (logical_block_size * 1000)) / (1024 ** 3) # NVMEs use 512'000 as block size
                fio_runtime = 5
        elif device.get("tran") == "sata":
            raw_written_value = None
            for entry in smartctl_json.get("ata_smart_attributes", {}).get("table", []):
                if entry.get("id") == 241: # ID 241 stores info about total data written
                    raw_written_value = entry.get("raw", {}).get("value")
                    break
            if raw_written_value is not None:
                if disk_type == "SSD":
                    parsed_written_data = raw_written_value # SATA SSDs store this in GB
                    fio_runtime = 10
                else:
                    parsed_written_data = (raw_written_value * logical_block_size) / (1024 ** 3) # Other disks store it as logical block sizes written
                    fio_runtime = 30

        if parsed_written_data is not None:
            written_data = f"{parsed_written_data:.2f} GiB"
        else:
            written_data = "Unbekannt"

        print(f"Testing the random read speed of: {device.get("model")} at {path}")
        # fio_runtime = 5 # for testing
        fio_job = get_fio_read_json(path, fio_runtime)["jobs"][0]
        read_speed = str(round(fio_job.get("read", {}).get("bw") / 1024, 2)) + "MB/s" # bw = bandwidth in KB/s

        smart_status = "PASSED" if smartctl_json.get("smart_status").get("passed") else "FAILED"

        disks.append(Disk(
            disk_type = disk_type,
            size_str = size_str,
            size_bytes = humanfriendly.parse_size(device.get("size")), # only for sorting
            model = device.get("model", "Unknown"),
            power_on_hours = power_on_hours,
            written_data = written_data,
            read_speed = read_speed,
            # write_speed = write_speed,
            smart_status = smart_status
        ))

    return sorted(disks, key=lambda d: (d.disk_type != "SSD", -d.size_bytes))


# List that will become system_info.csv
sys = [
    ["Preissegment", "☐ Hobby   ☐ Klein   ☐ Mittel   ☐ Gross"]
]

# Parsed dmidecode
raw_dmi = run("sudo dmidecode")
dmi = DMIParse(raw_dmi)

# Manufacturer
sys.append(["Hersteller", dmi.manufacturer()])

# Fastfetch default settings
ff = "fastfetch --logo none --key-type none " # ending space to make following commands cleaner

# Host
host = run(ff + "--structure host")
sys.append(["Modell", host])

# CPU
cpu = run(ff + "--structure cpu --cpu-format '{1} ({3}c/{4}t) @ {7}'")
sys.append(["Prozessor", cpu])

# Architecture
arch = run("getconf LONG_BIT") + "-bit"
sys.append(["Architektur", arch])

# Boot Manager
uefi = False
bios = False
if "UEFI is supported" in raw_dmi:
    uefi = True   
if "BIOS boot specification is supported" in raw_dmi:
    bios = True

bootmgr = "/".join([x for x, cond in [("UEFI", uefi), ("BIOS", bios)] if cond]) or "Unbekannt"
# bootmgr = run(ff + "--structure bootmgr --bootmgr-format '{1}'")
sys.append(["UEFI/Legacy", bootmgr])

# TPM?
ff_tpm = run(ff + "--structure tpm")
tpm = ff_tpm if ff_tpm != "" else "TPM wird nicht unterstützt (überprüfe BIOS einstellungen)"
sys.append(["TPM", tpm])

# Memory
memory = str(dmi.total_ram()) + " GB"
sys.append(["Arbeitsspeicher", memory])


# GPU
gpu = run(ff + "--structure gpu --gpu-format '{1} {2}'")
glxinfo_output = run("glxinfo -B")
if "Unified memory: yes" in glxinfo_output:
    print("VRAM is shared")
    gpu_mem = run(f"echo '{glxinfo_output}' | awk -F: '/Video memory/ {{print $NF}}'", shell=True) + "(shared)"
else:
    print("VRAM is dedicated")
    gpu_mem = run(f"echo '{glxinfo_output}' | awk -F: '/Dedicated video memory/ {{print $NF}}'", shell=True)

gpu_clock = run("clinfo --prop CL_DEVICE_MAX_CLOCK_FREQUENCY | awk '{print $NF}'", shell=True) # only works on some GPUs
if gpu_clock != "":
    gpu_clock += " MHz" # Only append MHz if we actually get the max clock
else:
    print("GPU does not show max clock frequency in clinfo")
    gpu_clock = ""

gpu_string = f"{gpu} {gpu_mem} {gpu_clock}".strip()
sys.append(["Grafikkarte", gpu_string]) # strip because gpu_mem or gpu_clock might not work


# List that will become disks.csv
disks = []

# Disks
for disk in get_disks():
    disks.append([disk.disk_type, disk.model])
    disks.append(["Grösse", disk.size_str])
    disks.append(["Betriebsstunden", disk.power_on_hours])
    disks.append(["Geschriebene Daten", disk.written_data])
    disks.append(["Lesegeschwindigkeit", disk.read_speed])
    # disks.append(["Schreibgeschwindigkeit", disk.write_speed])
    disks.append(["SMART-Status", disk.smart_status])




asset_dir = Path(os.getenv("FETCHSCRIPT_SHARE", "/run/current-system/sw/share/fetchscript"))
work_dir = Path.home() / "Documents" / "fetchscript"
work_dir.mkdir(parents=True, exist_ok=True)

for asset in asset_dir.iterdir():
    target = work_dir / asset.name
    if not target.exists():
        print(f"Copying {asset.name} to {work_dir}")
        target.write_bytes(asset.read_bytes())


with open(work_dir / "system_info.csv", "w", newline="") as csvfile:
    csv_writer = writer(csvfile)
    csv_writer.writerows(sys)
    print("Written general info")

with open(work_dir / "disks.csv", "w", newline="") as csvfile:
    csv_writer = writer(csvfile)
    csv_writer.writerows(disks)
    print("Written disk info")

print("Compiling Document")
run(f"typst compile {work_dir}/testprotokoll.typ {work_dir}/info.pdf")
run(f"okular {work_dir}/info.pdf")
