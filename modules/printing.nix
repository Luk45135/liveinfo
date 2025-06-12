{pkgs, ...}:
{
  services = {
    printing = {
      enable = true;
      drivers = with pkgs; [
        gutenprintBin
        hplipWithPlugin
        postscript-lexmark
        samsung-unified-linux-driver
        splix
        brlaser
        brgenml1lpr
        epson-escpr
        epson-escpr2
      ];
    };
    avahi = {
      enable = true;
      nssmdns4 = true;
      openFirewall = true;
    };
  };
  systemd.services.enable-discovered-printers = {
    description = "Enable discovered printers once available";
    after = [ "network-online.target" "cups.service" "avahi-daemon.service" ];
    wants = [ "network-online.target" ];
    wantedBy = [ "multi-user.target" ];
    path = with pkgs; [ cups gawk ];
    serviceConfig = {
      Type = "simple";
      ExecStart = pkgs.writeShellScript "enable-discovered-printers" ''
        found=0
        for p in $(lpstat -p | awk '{print $2}'); do
          lpadmin -p "$p" -E
          cupsaccept "$p"
          found=1
        done
        [ "$found" -eq 1 ]
      '';
      Restart = "on-failure";
      RestartSec = 10;
    };
  };
}
