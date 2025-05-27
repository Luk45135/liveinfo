import subprocess
import shlex
from csv import writer
import humanfriendly


def run(cmd: str, shell: bool = False) -> str:
    result = subprocess.run(
        cmd if shell else shlex.split(cmd),
        capture_output=True,
        text=True,
        shell=shell
    )
    return result.stdout.strip()


def get_disks():
    # Run lsblk and get raw output
    result = run("lsblk -d -o NAME,ROTA,TYPE,SIZE,MODEL --noheading")

    disks = []

    for line in result.strip().splitlines():
        parts = line.split(None, 4)  # Split into max 4 parts
        if len(parts) < 5 or parts[2] != "disk":
            continue  # Skip if not a full line or not a disk
        name, rota, _type, size_str, model = parts
        path = f"/dev/{name}"

        bus_info = run(f"udevadm info --query=property --name={path}")
        if "ID_BUS=usb" in bus_info: # If the disk is a USB stick dont include it in the list
            continue

        size_parsed = humanfriendly.parse_size(size_str)

        disk_type = "SSD" if rota == "0" else "HDD"

        disks.append((size_parsed, [disk_type, size_str, model, path]))

    # Sort using size_gb (from tuple[0]), then discard it
    return [entry for _, entry in sorted(disks, key=lambda x: (x[1][0] != "SSD", -x[0]))]


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
    csv.append([disk[0], disk[2]]) # SSD/HDD Modellname
    csv.append(["Grösse", disk[1]])






with open("system_info.csv", "w", newline="") as csvfile:
    csv_writer = writer(csvfile)
    csv_writer.writerows(csv)

# run("okular system_info.csv")
    
print(csv)

# print(get_disks())



