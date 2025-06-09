#!/usr/bin/env python3

import os
from pathlib import Path
from filecmp import cmp
import subprocess
import shlex
from csv import writer
import json
from dataclasses import dataclass
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



class Prepare():
    def __init__(self) -> None:
        self.asset_dir = Path(os.getenv("FETCHSCRIPT_SHARE", "/run/current-system/sw/share/fetchscript"))
        self.work_dir = Path.home() / "Documents" / "fetchscript"
        self.work_dir.mkdir(parents=True, exist_ok=True)

        self.prepare_work_dir()


    def prepare_work_dir(self):
        for asset in self.asset_dir.iterdir():
            target = self.work_dir / asset.name
            if not target.exists() or not cmp(asset, target, shallow=False):
                print(f"Copying {asset.name} to {self.work_dir}")
                target.write_bytes(asset.read_bytes())
            else:
                print(f"Skipping {asset.name}, identical asset already exists in {self.work_dir}")



class SystemInfo():
    def __init__(self) -> None:
        # List that will become system_info.csv
        self.sys = [
            ["Preissegment", "☐ Hobby   ☐ Klein   ☐ Mittel   ☐ Gross"]
        ]

    def get_system_info(self):
        # Parsed dmidecode
        raw_dmi = run("sudo dmidecode")
        dmi = DMIParse(raw_dmi)
        
        # Manufacturer
        self.sys.append(["Hersteller", dmi.manufacturer()])
        
        # Fastfetch default settings
        ff = "fastfetch --logo none --key-type none " # ending space to make following commands cleaner
        
        # Host
        host = run(ff + "--structure host")
        self.sys.append(["Modell", host])
        
        # CPU
        cpu = run(ff + "--structure cpu --cpu-format '{1} ({3}c/{4}t) @ {7}'")
        self.sys.append(["Prozessor", cpu])
        
        # Architecture
        arch = run("getconf LONG_BIT") + "-bit"
        self.sys.append(["Architektur", arch])
        
        # Boot Manager
        uefi = False
        bios = False
        if "UEFI is supported" in raw_dmi:
            uefi = True   
        if "BIOS boot specification is supported" in raw_dmi:
            bios = True
        
        bootmgr = "/".join([x for x, cond in [("UEFI", uefi), ("BIOS", bios)] if cond]) or "Unbekannt"
        # bootmgr = run(ff + "--structure bootmgr --bootmgr-format '{1}'")
        self.sys.append(["UEFI/Legacy", bootmgr])
        
        # TPM?
        ff_tpm = run(ff + "--structure tpm")
        tpm = ff_tpm if ff_tpm != "" else "TPM wird nicht unterstützt (überprüfe BIOS einstellungen)"
        self.sys.append(["TPM", tpm])
        
        # Memory
        memory = str(dmi.total_ram()) + " GB"
        self.sys.append(["Arbeitsspeicher", memory])
        
        
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
        self.sys.append(["Grafikkarte", gpu_string]) # strip because gpu_mem or gpu_clock might not work


    def write_system_info(self):

        self.get_system_info()

        with open(prepare.work_dir / "system_info.csv", "w", newline="") as csvfile:
            csv_writer = writer(csvfile)
            csv_writer.writerows(self.sys)
            print("Written general info")



@dataclass
class Disk:
    disk_type: str # SSD / HDD
    size_str: str # 931.5G or 1.00TB depending on if f3 is used
    model: str
    power_on_hours: str
    written_data: str
    read_speed: str
    # write_speed: str
    smart_status: str

class DiskInfo():
    def __init__(self) -> None:
        # List that will become disks.csv
        self.disks = []
    

    def get_fio_read_json(self, filename: str, runtime: int = 20, jobname: str = "read_test") -> dict:
        fio_read_json_cmd = f"sudo fio --direct=1 --rw=randread --bs=4k --ioengine=libaio --iodepth=256 --runtime={runtime} --numjobs=4 --time_based --group_reporting --eta-newline=1 --readonly --output-format=json --filename={filename} --name={jobname}"
        return json.loads(run(fio_read_json_cmd))

    
    def get_disks(self):
        # Run lsblk and get raw output
        lsblk_json = json.loads(run("lsblk -d -o PATH,ROTA,TYPE,SIZE,TRAN,MODEL --noheading -J"))
    
        disks = []
    
        for device in lsblk_json.get("blockdevices", []):
            if device["type"] != "disk":
                continue # Skip if it isnt a disk
            if device.get("tran") == "usb":
                continue # Skip if it's attached via USB
    
            path = device.get("path") # Get disk path like /dev/sda
    
            disk_type = "" # Enumeration for disk_type
            if device.get("tran") == "nvme":
                disk_type = "NVMe SSD"
            elif device.get("tran") == "sata":
                if device.get("rota"):
                    disk_type = "HDD"
                else:
                    disk_type = "SATA SSD"
    
    
            smartctl_json = json.loads(run(f"sudo smartctl -a -j {path}")) # Get SMART info for disk
    
            # size_str = device.get("size") # for testing
            print(f"Verifying real disk size of {path}")
            size_str = run(f"sudo f3probe {path} | awk -F: '/Module/ {{gsub(/^ +| +$/, \"\", $2); split($2, a, \" \"); print a[1], a[2]}}'", shell=True)
    
            power_on_hours = str(smartctl_json.get("power_on_time", {}).get("hours")) + "h" # This is the same on nvme ssd, sata ssd and sata hdd
    
            logical_block_size = smartctl_json.get("logical_block_size", 512) # Used for calculating total disk writes
            parsed_written_data = None # Initialize var for later
            fio_runtime = 20 # Initialize var for later
    
    
            raw_written_value = None
            match disk_type:
                case "NVMe SSD":
                    fio_runtime = 5
                    raw_written_value = smartctl_json.get("nvme_smart_health_information_log", {}).get("data_units_written")
                    if raw_written_value is not None:
                        parsed_written_data = (raw_written_value * (logical_block_size * 1000)) / (1024 ** 3) # NVMEs use 512'000 as block size
                case "SATA SSD":
                    fio_runtime = 10
                    for entry in smartctl_json.get("ata_smart_attributes", {}).get("table", []):
                        if entry.get("id") == 241: # ID 241 stores info about total data written
                            raw_written_value = entry.get("raw", {}).get("value")
                            break
                    if raw_written_value is not None:
                        parsed_written_data = raw_written_value # SATA SSDs store this in GB
                case "HDD":
                    fio_runtime = 30
                    for entry in smartctl_json.get("ata_smart_attributes", {}).get("table", []):
                        if entry.get("id") == 241: # ID 241 stores info about total data written
                            raw_written_value = entry.get("raw", {}).get("value")
                            break
                    if raw_written_value is not None:
                        parsed_written_data = (raw_written_value * logical_block_size) / (1024 ** 3) # Most HDD's store it as logical block sizes written
                case _:
                    fio_runtime = 30
    
            if parsed_written_data is not None:
                written_data = f"{parsed_written_data:.2f} GiB"
            else:
                written_data = "Unbekannt"
    
            print(f"Testing the random read speed of: {device.get("model")} at {path}")
            # fio_runtime = 5 # for testing
            fio_job = self.get_fio_read_json(path, fio_runtime)["jobs"][0]
            read_speed = str(round(fio_job.get("read", {}).get("bw") / 1024, 2)) + "MB/s" # bw = bandwidth in KB/s
    
            smart_status = "PASSED" if smartctl_json.get("smart_status").get("passed") else "FAILED"
    
            disks.append(Disk(
                disk_type = disk_type,
                size_str = size_str,
                model = device.get("model", "Unknown"),
                power_on_hours = power_on_hours,
                written_data = written_data,
                read_speed = read_speed,
                # write_speed = write_speed,
                smart_status = smart_status
            ))
    
        return sorted(disks, key=lambda d: (-float(d.read_speed[:-4])))

    def get_disk_info(self):
        for disk in self.get_disks():
            self.disks.append(["Festplattentyp", disk.disk_type])
            self.disks.append(["Modell", disk.model])
            self.disks.append(["Grösse", disk.size_str])
            self.disks.append(["Betriebsstunden", disk.power_on_hours])
            self.disks.append(["Geschriebene Daten", disk.written_data])
            self.disks.append(["Lesegeschwindigkeit", disk.read_speed])
            # self.disks.append(["Schreibgeschwindigkeit", disk.write_speed])
            self.disks.append(["SMART-Status", disk.smart_status])


    def write_disk_info(self):

        self.get_disk_info()
        
        with open(prepare.work_dir / "disks.csv", "w", newline="") as csvfile:
            csv_writer = writer(csvfile)
            csv_writer.writerows(self.disks)
            print("Written disk info")



prepare = Prepare()


DiskInfo().write_disk_info()

SystemInfo().write_system_info()

print("Compiling Document")
run(f"typst compile {prepare.work_dir}/testprotokoll.typ {prepare.work_dir}/info.pdf")
run(f"okular {prepare.work_dir}/info.pdf")
