# LiveInfo

LiveInfo is a [NixOS](https://nixos.org/) configuration that lets you create a bootable ISO with pre-installed tools to help you gather information about the system and create a PDF which you can then print.

# Usage

## Build

Make sure that you have ample free storage space available on your Linux machine. (16/32GB should be enough. (not tested))

Download the .zip or .tar.gz and extract it into a directory of your choice and navigate to it in your Terminal of choice.

Run `./build.sh`.
The script will do the following automatically:
- Install nix if it wasn't installed already.
- Edit the nix configuration in `$HOME/.config/nix/nix.conf` to allow the usage of nix-commands and flakes if this wasn't configured before.
- Build the ISO by running `nix build .

If you encounter a permission denied error add the executable flag to build.sh by running `chmod +x build.sh`.

After building you will find the ISO in `./result/iso/nixos-XX.XX.XXXXXXXX.xxxxxxx-x86_64-linux.iso`

## Flash

If you have a way to boot into an ISO like with a Ventoy drive or a Zalman ZM-VE350 you can put the ISO onto the device and skip the rest of this step.

Flash the ISO onto a USB drive that is at least 8GB in size with a tool like [Fedora Media Writer](https://github.com/FedoraQt/MediaWriter) or [Popsicle](https://github.com/pop-os/popsicle).

If you don't already have a tool to Flash a USB you can temporarily install/run it like this:
- `nix run nixpkgs#mediawriter`
	- This will directly run the app.
- `nix shell nixpkpgs#popsicle`
	- This will give you a shell that has the app installed which you can then run through the terminal like this: `popsicle-gtk`

## Boot

When booting make sure that your USB drive is first in the boot order and that Secureboot is disabled.

## Updating

In a shell with nix installed, navigate to the extracted liveinfo directory and run:

`nix run nixpkgs#git pull` and then `nix build .`

or you can just repeat the [Build](#build) process

# Develop

## DevShell

> This project also provides a nix devshell which when activated installs all the needed development dependencies temporarily in that shell.

In a shell with nix installed, navigate to the extracted liveinfo directory and run:

`nix develop` or if you don't like Bash: `nix develop -c zsh`

## Test

In a shell with nix installed, navigate to the extracted liveinfo directory.

Running `nix run .#testVm` will temporarily install [QEMU](https://www.qemu.org/) and directly run the liveiso NixOS configuration in a Virtual Machine.

