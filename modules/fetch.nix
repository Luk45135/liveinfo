{ pkgs, ... }:

let
  fetchscript = pkgs.callPackage ./fetchscript/package.nix {};
in
{
  environment.systemPackages = [ fetchscript ];

  systemd.user.services.testprotokoll = {
    enable = true;
    after = [ "graphical-session.target" ];
    wantedBy = [ "default.target" ];
    description = "Generiert ein schönes Testprotokoll mit diversen Systeminformationen.";
    # script = ''
    #   cd /etc/fetchscript
    #   python fetch.py
    # '';
    serviceConfig = {
      ExecStart = "${fetchscript}/bin/fetchscript";
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
      ];
    }
  ];
}
