{
  description = "Minimal NixOS installation media";
  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-24.11";
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
  };
}
