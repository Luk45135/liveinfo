{ pkgs, ... }:

let
  fetchscript = pkgs.callPackage ./fetchscript/package.nix {};
in
{
  environment.systemPackages = [ fetchscript ];

  systemd.user.services.testprotokoll = {
    enable = true;
    after = [ "graphical-session.target" ];
    wantedBy = [ "graphical-session.target" ];
    description = "Generiert ein schönes Testprotokoll mit diversen Systeminformationen.";
    serviceConfig = {
      ExecStart = "${fetchscript}/bin/fetchscript";
      Environment = [
        "DISPLAY=:0"
        "XAUTHORITY=%h/.Xauthority"
      ];
    };
  };
  
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
