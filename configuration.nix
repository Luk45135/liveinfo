# This file defines the bulk of the configuration of the live OS
# Documentation for the options used here can be found at: https://search.nixos.org/options?
{pkgs, lib, ...}: 
let
  f3-qt = pkgs.callPackage ./modules/f3qt.nix {};
in
{
  # This imports more configuration files that were split up to organize
  imports = [
    ./modules/fetch.nix
    ./modules/printing.nix
  ];

  # This is the only option not found at the above mentioned site.
  # This option defines what compression algorithm is used for the filesystem on the iso and speeds up build times by a huge factor
  # This was taken from: https://wiki.nixos.org/wiki/Creating_a_NixOS_live_CD#Building_faster
  # This specific compression algorithm was chosen for it's balance between build-speed and filesize
  isoImage.squashfsCompression = "gzip -Xcompression-level 1";

  services = {
    # Enables the soundserver pipewire with support for the older pulseaudio
    pipewire = {
      enable = true;
      pulse.enable = true;
    };
    # Configures auto login so that it completely skips the login prompt
    displayManager.autoLogin = {
      enable = true;
      user = "nixos";
    };
    xserver = {
      enable = true;
      # Sets the keyboard layout to swiss german
      # Usually the 2-letter country code is used, for a full list run `localectl list-x11-keymap-layouts`
      xkb.layout = "ch"; 
      # Sets the desktop environment and the login manager to the one used by Mint Cinnamon
      displayManager.lightdm.enable = true;
      desktopManager.cinnamon.enable = true;
    };
  };
  # This sets the default locale to swissgerman which is typically defined in the form of language_territory.UTF-8
  # For more info check the arch wiki: https://wiki.archlinux.org/title/Locale#Generating_locales
  i18n.defaultLocale = "de_CH.UTF-8";
  time.timeZone = "Europe/Zurich";

  # Enables all firmware regardless of license
  hardware.enableAllFirmware = true;

  # Enable networking and and wireless support
  networking = {
    networkmanager.enable = true;
    wireless.enable = false;
  };
  # Sets up the user, sets the default shell to zsh and adds it to some groups
  # for sudo access and access to networkmanager
  users.users.nixos = {
    # Set the password of the nixos user to 1234
    initialPassword = "1234";
    # Force the initialHashedPassword value to be null
    # because it is set to "" in the installation cd module
    initialHashedPassword = lib.mkForce null;
    isNormalUser = true;
    shell = pkgs.fish;
    extraGroups = [
      "wheel"
      "networkmanager"
    ];
  };
  programs.fish.enable = true;

  # This is where additional packages/programs are defined
  # Package names can be found at: https://search.nixos.org/packages?
  environment.systemPackages = with pkgs; [
    firefox
    snapshot
    audacity

    # Tools for reading out systeminfo
    pciutils
    furmark
    hardinfo2
    cpu-x
    sysbench
    glmark2

    # Other useful tools
    gnome-disk-utility
    nwipe
    hdparm
    nvme-cli
    f3-qt

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

  # Allow for non-opensource software to be installed like furmark
  nixpkgs.config.allowUnfree = true;
  
  # Install some usefull and needed fonts also sets a nice terminal font
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
