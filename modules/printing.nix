# This defines all the live OS configurations related to printing
{pkgs, ...}:
{
  # This installs a nice GUI app for adding and configuring printers
  environment.systemPackages = with pkgs; [ system-config-printer ];
  services = {
    # This installs the printing system CUPS
    printing = {
      enable = true;
      # This installs every additional printer-driver available in NixOS
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
    # This installs the avahi service which automatically adds network printers that are compatible with Apple's Bonjour
    avahi = {
      enable = true;
      nssmdns4 = true;
      openFirewall = true;
    };
  };
  # This defines a system-service that automatically accepts printers
  # CUPS by default doesn't accept printers for security reasons which is why this workaround is needed
  systemd.services.enable-discovered-printers = {
    description = "Enable discovered printers once available";
    after = [ "network-online.target" "cups.service" "avahi-daemon.service" ];
    wants = [ "network-online.target" ];
    wantedBy = [ "multi-user.target" ];
    path = with pkgs; [ cups gawk ];
    serviceConfig = {
      Type = "simple";
      ExecStart = pkgs.writeShellScript "enable-discovered-printers" ''
        for p in $(lpstat -p | awk '{print $2}'); do
          lpadmin -p "$p" -E
          cupsaccept "$p"
        done
      '';
      Restart = "always";
      RestartSec = 30;
    };
  };
}
