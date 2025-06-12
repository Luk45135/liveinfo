{pkgs, ...}: {
  imports = [
    ./modules/fetch.nix
  ];

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

    pipewire = {
      enable = true;
      pulse.enable = true;
    };

    displayManager.autoLogin = {
      enable = true;
      user = "nixos";
    };
    xserver = {
      enable = true;
      xkb.layout = "ch";
      displayManager.lightdm.enable = true;
      desktopManager.cinnamon.enable = true;
    };
  };

  hardware.enableAllFirmware = true;

  networking = {
    networkmanager.enable = true;
    wireless.enable = false;
  };
  users.users.nixos = {
    isNormalUser = true;
    shell = pkgs.zsh;
    extraGroups = [
      "wheel"
      "networkmanager"
    ];
  };
  programs.zsh = {
    enable = true;
    autosuggestions.enable = true;
    syntaxHighlighting.enable = true;
  };

  environment.systemPackages = with pkgs; [
    firefox

    # Tools for reading out systeminfo
    pciutils
    furmark
    hardinfo2
    cpu-x
    sysbench
    glmark2

    # Other useful tools
    gnome-disk-utility
    gparted

    # Needed for script
    # python3
    # python3Packages.humanfriendly
    ## For infofetching
    fastfetch
    dmidecode
    glxinfo
    smartmontools
    clinfo
    f3
    fio
    ## For pdf stuff
    libsForQt5.okular
    typst
  ];

  nixpkgs.config.allowUnfree = true;
  
  fonts = {
    enableDefaultPackages = true;
    packages = with pkgs; [
      noto-fonts
      roboto
      nerd-fonts.jetbrains-mono
    ];
    fontconfig = {
      enable = true;
      defaultFonts.monospace = [ "JetBrainsMono NFM" ];
    };
  };
}
