# This is the Nix Flake which basically defines:
# the inputs: basically the nixpkgs github repo
# and the outputs: the ISO which can be flashed onto a USB and a devshell
# Documentation for Flakes can be found here: https://wiki.nixos.org/wiki/Flakes
# and here which has additional info for this specific use case: https://wiki.nixos.org/wiki/Creating_a_NixOS_live_CD
{
  description = "Minimal NixOS installation media";
  # This defines which release stream (channel branch) is used 25.05 is the latest stable channel
  # More on the different channels can be read here: https://wiki.nixos.org/wiki/Channel_branches
  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-25.05";
  outputs = { self, nixpkgs }: {
    packages.x86_64-linux.default = self.nixosConfigurations.exampleIso.config.system.build.isoImage;
    nixosConfigurations = {
      exampleIso = nixpkgs.lib.nixosSystem {
        system = "x86_64-linux";
        modules = [
          ({ pkgs, modulesPath, ... }: {
            imports = [ 
              # This defines everything we need for a live environment
              # and is defined here: https://github.com/NixOS/nixpkgs/blob/nixos-25.05/nixos/modules/installer/cd-dvd/installation-cd-minimal.nix
              (modulesPath + "/installer/cd-dvd/installation-cd-minimal.nix")
              # Here we import the custom config
              ./configuration.nix
            ];
          })
        ];
      };
    };
    # This defines the devshell a shell that contains all the dependencies needed for developing this project
    # To use it run `nix develop` or `nix develop -c zsh` if you want to use zsh anywhere in the project
    devShells.x86_64-linux.default = let
      pkgs = import nixpkgs {
        system = "x86_64-linux";
      };
    in pkgs.mkShell {
      buildInputs = with pkgs; [
        # Needed for script
        python3
        python3Packages.py-dmidecode
        python3Packages.pyside6
        qt6.full
        ## For infofetching
        fastfetch
        dmidecode
        glxinfo
        smartmontools
        clinfo
        f3
        fio
        ## For pdf stuff
        typst
      ];
    };
  };
}
