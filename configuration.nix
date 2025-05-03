{pkgs, ...}: {

  services = {
    printing.enable = true;
    avahi = {
      enable = true;
      nssmdns4 = true;
      openFirewall = true;
    };

    pipewire = {
      enable = true;
      pulse.enable = true;
    };

    xserver = {
      enable = true;
      xkb.layout = "ch";
      displayManager.lightdm = {
        enable = true;
        autoLogin = {
          enable = true;
          user = "nixos";
        };
      };
      desktopManager.mate.enable = true;
    };
  };

  networking = {
    wireless.enable = true;
  };

  environment.systemPackages = with pkgs; [
    alacritty
    tmux
    neovim
    firefox
    dmidecode
    fastfetch
    pciutils
    ripgrep
    libsForQt5.okular
    typst
  ];

  
  fonts = {
    enableDefaultPackages = true;
    packages = with pkgs; [
      fira-code-nerdfont
    ];
  };
}
