# This file defines the bulk of the configuration of the live OS
# Documentation for the options used here can be found at: https://search.nixos.org/options?
{pkgs, ...}: {
  # This imports more configuration file that were split for organizing reasons
  imports = [
    ./modules/fetch.nix
    ./modules/printing.nix
  ];

  # This is the only option not found at the above mentioned site.
  # This option defines what compression algorithm is used for building the iso and speeds up build times by a huge factor
  # This was taken from: https://wiki.nixos.org/wiki/Creating_a_NixOS_live_CD#Building_faster
  # This specific compression algorithm was chosen for it's balance between build-speed and filesize
  isoImage.squashfsCompression = "gzip -Xcompression-level 1";

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

  # This is where additional packages/programs are defined
  # Package names can be found at: https://search.nixos.org/packages?
  environment.systemPackages = with pkgs; [
    firefox
    snapshot

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
