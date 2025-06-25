# This file defines extra options for the custom SystemReport program
{ pkgs, ... }:

# The package definition for the SystemReport is called here and then added to systemPackages to install it
let
  fetchscript = pkgs.callPackage ./fetchscript/package.nix {};
in
{
  environment.systemPackages = [ fetchscript ];

  # This defines a custom user-service that automatically runs the program upon getting into the desktop Environment
  systemd.user.services.systemreport = {
    enable = true;
    after = [ "graphical-session.target" ];
    wantedBy = [ "graphical-session.target" ];
    description = "Erstellt einen übersichtlichen PDF-Bericht mit wichtigen Informationen zum System und zur Hardware.";
    serviceConfig = {
      ExecStart = "${fetchscript}/bin/fetchscript";
      Environment = [
        "DISPLAY=:0"
        "XAUTHORITY=%h/.Xauthority"
      ];
    };
  };
  
  # SystemRepoprt makes use of these programs, but they need sudo priviledges
  # This makes these programs executable with sudo priviledges without a password
  # The user shouldn't need to input the password or even know it
  security.sudo.extraRules = [
    {
      users = [ "nixos" ];
      commands = [
        {
          command = "/run/current-system/sw/bin/fio";
          options = [ "NOPASSWD" ];
        }
        {
          command = "/run/current-system/sw/bin/smartctl";
          options = [ "NOPASSWD" ];
        }
        {
          command = "/run/current-system/sw/bin/f3probe";
          options = [ "NOPASSWD" ];
        }
        {
          command = "/run/current-system/sw/bin/dmidecode";
          options = [ "NOPASSWD" ];
        }
      ];
    }
  ];
}
