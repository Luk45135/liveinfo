{ pkgs, lib, ... }:

let  
  # fetchscript = pkgs.writeShellScriptBin "fetchscript" (builtins.readFile ./fetch.py);
  fetchscript = pkgs.writers.writePython3Bin "fetchscript" {
    libraries = [pkgs.python3Packages.humanfriendly];
    flakeIgnore = [ "E501" "E261" "E303" "E302" "E251" ];
  } ./fetch.py;
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
      WorkingDirectory = "/etc/fetchscript";
      ExecStart = "${fetchscript}/bin/fetchscript";
    };
  };
  
  environment.etc = {
    "fetchscript/fetch.py".source = ./fetch.py;
    "fetchscript/testprotokoll.typ".source = ./testprotokoll.typ;
    "fetchscript/computerbrocki.png".source = pkgs.fetchurl {
      url = "https://www.michael-nydegger.ch/computerbrocki.ch_transparent.png";
      hash = "sha256-6LuXzzMxGC74YtGZYVEFpMnTC+a+umuUUpjaBX5dca0=";
    };
  };


}
