# This file defines the SystemReport package which is basically a installation script
# Documentation can be found here: https://wiki.nixos.org/wiki/Python#Package_a_Python_application
# and way more in depth here: https://nixos.org/manual/nixpkgs/stable/#building-packages-and-applications
{ pkgs ? import <nixpkgs> {} }:

# This downloads the logo visible in the resulting PDF
let
  # Fetch the image once, Nix will cache this
  logo = pkgs.fetchurl {
    url = "https://www.michael-nydegger.ch/computerbrocki.ch_transparent.png";
    hash = "sha256-6LuXzzMxGC74YtGZYVEFpMnTC+a+umuUUpjaBX5dca0=";
  };
in
pkgs.python3Packages.buildPythonApplication rec {
  # Basic program info like name and version
  pname = "fetchscript";
  version = "0.3.4";
  format = "other"; # other because this doesnt use a pyproject.toml or setup.py for installation

  src = ./.;

  # Libraries needed for wrapping the program and installing the desktop item
  nativeBuildInputs = with pkgs; [
    makeWrapper
    copyDesktopItems
  ];

  # Define the needed python dependencies
  propagatedBuildInputs = with pkgs.python3Packages; [ 
    pyside6
    py-dmidecode
  ];

  # Install the programm and assets
  installPhase = ''
    install -Dm755 src/* -t $out/lib/fetchscript

    install -Dm644 assets/* -t $out/share/fetchscript
    install -Dm644 ${logo} $out/share/fetchscript/logo.png

    install -Dm755 src/main.py $out/bin/fetchscript

    # Sets needed environment variables for the program
    wrapProgram $out/bin/fetchscript \
      --set PYTHONPATH $out/lib \
      --set FETCHSCRIPT_SHARE $out/share/fetchscript \
      --prefix PATH : /run/wrappers/bin:/run/current-system/sw/bin

    runHook postInstall
  '';

  # Install the icon to the correct directory fot the desktop item
  postInstall = ''
    install -Dm444 ./assets/search-list.png $out/share/icons/hicolor/256x256/apps/search-list.png
  '';

  # This creates the desktop item for the program (e.g. the nice icon you can click on)
  desktopItems = [ (pkgs.makeDesktopItem {
    name = "SystemReport";
    genericName = pname;
    comment = "Erstellt einen übersichtlichen PDF-Bericht mit wichtigen Informationen zum System und zur Hardware.";
    desktopName = "SystemReport";
    exec = pname;
    icon = "search-list";
    type = "Application";
    terminal = false;
    categories = ["Utility"];
  }) ];

  meta.mainProgram = pname;
}

