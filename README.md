# Build

Make sure that you have ample free storage space available on your Linux machine. (16/32GB should be enough. (not tested))

Download the .zip or .tar.gz and extract it into a directory of your choice and navigate to it in your Terminal of choice.

Run `./build.sh` and the script will take care of setting up nix for you.

If you encounter a permission denied error add the executeable flag to build.sh by running `chmod +x build.sh`.

After building you will find the ISO in `./result/iso/nixos-XX.XX.XXXXXXXX.xxxxxxx-x86_64-linux.iso`

# Usage

Flash the ISO onto a USD drive that is at least 8GB in size with a tool like Fedora Media Writer or Popsicle.

If you are in a shell with nix you can run it with `nix run nixpkgs#mediawriter` or you can create a shell with a program like this:

`nix shell nixpkpgs#popsicle` then you can run the program like if it was installed `popsicle-gtk`.

When booting make sure that your USB drive is first in the boot order and that Secureboot is disabled.

# Updating

In a shell with nix installed, navigate to the extracted liveinfo directory and run:

`nix run nixpkgs#git pull` and then `nix build .`

or you can just repeat the [Build](#build) process

# Test

In a shell with nix installed, navigate to the extracted liveinfo directory.

You can easily run this NixOS configuration in a qemu VM by running `nix run .#testVm`.

