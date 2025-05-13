{pkgs, ...}: {
  imports = [
    ./modules/fetch.nix
  ];

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
      displayManager = {
        autoLogin = {
          enable = true;
          user = "nixos";
        };
        lightdm.enable = true;
      };
      desktopManager.cinnamon.enable = true;
    };
  };

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
  programs.zsh.enable = true;

  environment.systemPackages = with pkgs; [
    alacritty
    tmux
    neovim
    firefox

    dmidecode
    fastfetch
    pciutils
    glxinfo
    smartmontools
    ripgrep
    furmark

    libsForQt5.okular
    typst
  ];

  nixpkgs.config.allowUnfree = true;
  
  fonts = {
    enableDefaultPackages = true;
    packages = with pkgs; [
      fira-code-nerdfont
    ];
    fontconfig = {
      enable = true;
      defaultFonts.monospace = ["FiraCode Nerd Font Mono"];
    };
  };
}
