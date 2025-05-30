{
  description = "Minimal NixOS installation media";
  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-25.05";
  outputs = { self, nixpkgs }: {
    packages.x86_64-linux.default = self.nixosConfigurations.exampleIso.config.system.build.isoImage;
    nixosConfigurations = {
      exampleIso = nixpkgs.lib.nixosSystem {
        system = "x86_64-linux";
        modules = [
          ({ pkgs, modulesPath, ... }: {
            imports = [ 
              (modulesPath + "/installer/cd-dvd/installation-cd-minimal.nix") 
              ./configuration.nix
            ];
          })
        ];
      };
    };
    devShells.x86_64-linux.default = let
      pkgs = import nixpkgs {
        system = "x86_64-linux";
      };
    in pkgs.mkShell {
      buildInputs = with pkgs; [
        # Needed for script
        python3
        python3Packages.humanfriendly
        ## For infofetching
        fastfetch
        glxinfo
        smartmontools
        clinfo
        f3
        fio
        ## For pdf stuff
        libsForQt5.okular
        typst
      ];
    };
  };
}
