{ pkgs ? import <nixpkgs> {} }:

let
  # Fetch the image once, Nix will cache this
  computerbrockiImg = pkgs.fetchurl {
    url = "https://www.michael-nydegger.ch/computerbrocki.ch_transparent.png";
    hash = "sha256-6LuXzzMxGC74YtGZYVEFpMnTC+a+umuUUpjaBX5dca0=";
  };
in
pkgs.python3Packages.buildPythonApplication rec {
  pname = "fetchscript";
  version = "0.3.0";
  format = "other";

  src = ./.;

  nativeBuildInputs = with pkgs; [
    makeWrapper
    copyDesktopItems
  ];

  propagatedBuildInputs = with pkgs.python3Packages; [ 
    pyside6
    py-dmidecode
  ];

  installPhase = ''
    mkdir -p $out/lib/fetchscript
    cp src/*.py $out/lib/fetchscript
    chmod +x $out/lib/fetchscript/main.py

    wrapProgram $out/lib/fetchscript/main.py \
      --set FETCHSCRIPT_SHARE $out/share/fetchscript \
      --prefix PATH : /run/wrappers/bin:/run/current-system/sw/bin

    mkdir -p $out/bin
    ln -s $out/lib/fetchscript/main.py $out/bin/fetchscript

    mkdir -p $out/share/fetchscript
    cp assets/* $out/share/fetchscript
    cp ${computerbrockiImg} $out/share/fetchscript/computerbrocki.png

    runHook postInstall
  '';

  postInstall = ''
    install -Dm444 ./assets/search-list.png $out/share/icons/hicolor/256x256/apps/search-list.png
  '';

  desktopItems = [ (pkgs.makeDesktopItem {
    name = "Testprotokoll";
    genericName = pname;
    comment = "Generiert ein schönes Testprotokoll mit Systeminformationen.";
    desktopName = "Testprotokoll";
    exec = pname;
    icon = "search-list";
    type = "Application";
    terminal = true;
    categories = ["Utility"];
  }) ];

  meta.mainProgram = pname;
}

