{pkgs, ...}: {
  imports = [
    ./modules/fetch.nix
    ./modules/printing.nix
  ];

  services = {
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

  i18n.defaultLocale = "de_CH.UTF-8";
  time.timeZone = "Europe/Zurich";

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
