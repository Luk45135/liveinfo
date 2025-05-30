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

        logical_block_size = smartctl_json.get("logical_block_size", 512) # Used for calculating total disk writes
        power_on_hours = str(smartctl_json.get("power_on_time", {}).get("hours")) + "h" # This is the same on nvme ssd, sata ssd and sata hdd

        written_data = 0 # Initialize var for later
        fio_runtime = 20 # Initialize var for later

        if device.get("tran") == "nvme":
            raw_written_value = smartctl_json.get("nvme_smart_health_information_log", {}).get("data_units_written")
            written_data = (raw_written_value * (logical_block_size * 1000)) / (1024 ** 3) # NVMEs use 512'000 as block size

            fio_runtime = 5
        elif device.get("tran") == "sata":
            raw_written_value = 0
            for entry in smartctl_json.get("ata_smart_attributes", {}).get("table", []):
                if entry.get("id") == 241: # ID 241 stores info about total data written
                    raw_written_value = entry.get("raw", {}).get("value")
                    # print(raw_written_value)
                    break
            if disk_type == "SSD":
                written_data = raw_written_value # SATA SSDs store this in GB

                fio_runtime = 10
            else:
                written_data = (raw_written_value * logical_block_size) / (1024 ** 3) # Other disks store it as logical block sizes written

                fio_runtime = 30

        written_data = str(round(written_data, 2)) + " GiB"

        print(f"Testing the random read speed of: {device.get("model")} at {path}")
        fio_job = get_fio_read_json(path, fio_runtime)["jobs"][0]
        read_speed = str(round(fio_job.get("read", {}).get("bw") / 1024, 2)) + "MB/s" # bw = bandwidth in KB/s

        smart_status = "PASSED" if smartctl_json.get("smart_status").get("passed") else "FAILED"

        disks.append(Disk(
            disk_type = disk_type,
            size_str = device.get("size"),
            # size_str = run(f"sudo f3probe {disk[3]} | awk -F: '/Module/ {{gsub(/^ +| +$/, \"\", $2); split($2, a, \" \"); print a[1], a[2]}}'", shell=True),
            size_bytes = humanfriendly.parse_size(device.get("size")),
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
    ["Preissegment", "☐ Hobby   ☐ Klein   ☐ Mittel   ☐ Gross"],
    ["Hersteller", ""]
]

# Fastfetch default settings
ff = "fastfetch --logo none --key-type none " # ending space to make following commands cleaner

# Host
host = run(ff + "--structure host")
sys.append(["Modell", host])

# CPU
cpu = run(ff + "--structure cpu --cpu-format '{1} ({3}c/{4}t) @ {7}'")
arch = run("getconf LONG_BIT") + "-bit"
sys.append(["Prozessor", f"{cpu} {arch}"])

# Boot Manager
bootmgr = run(ff + "--structure bootmgr --bootmgr-format '{1}'")
sys.append(["UEFI/Legacy", bootmgr])

# TPM?
tpm = run(ff + "--structure tpm")
sys.append(["TPM", tpm])

# Memory
memory = run("lsmem | awk '/Total online memory:/ {print $4}'", shell=True)
sys.append(["Arbeitsspeicher", memory])

# GPU
gpu = run(ff + "--structure gpu --gpu-format '{2}'")
gpu_mem = run("glxinfo -B | awk -F: '/Dedicated video memory/ { print $2 }'", shell=True)
gpu_clock = run("clinfo --prop CL_DEVICE_MAX_CLOCK_FREQUENCY | awk '{print $NF}'", shell=True).strip() + " MHz" # only works if gpu supports opencl
sys.append(["Grafikkarte", f"{gpu} {gpu_mem} {gpu_clock}".strip()]) # strip because gpu_mem or gpu_clock might not work


with open("system_info.csv", "w", newline="") as csvfile:
    csv_writer = writer(csvfile)
    csv_writer.writerows(sys)
    print("Written general info")
# print(sys)



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


with open("disks.csv", "w", newline="") as csvfile:
    csv_writer = writer(csvfile)
    csv_writer.writerows(disks)
    print("Written disk info")
# print(disks)




run("typst compile testprotokoll.typ info.pdf")
run("okular info.pdf")
