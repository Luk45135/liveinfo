{ pkgs ? import <nixpkgs> {} }:

let
  # Fetch the image once, Nix will cache this
  computerbrockiImg = pkgs.fetchurl {
    url = "https://www.michael-nydegger.ch/computerbrocki.ch_transparent.png";
    hash = "sha256-6LuXzzMxGC74YtGZYVEFpMnTC+a+umuUUpjaBX5dca0=";
  };
in
pkgs.python3Packages.buildPythonApplication {
  pname = "fetchscript";
  version = "0.1.0";
  format = "other";

  src = ./.;

  nativeBuildInputs = with pkgs; [
    makeWrapper
    copyDesktopItems
  ];

  dependencies = with pkgs.python3Packages; [
    humanfriendly
    py-dmidecode
    pyside6
  ];

  installPhase = ''
    mkdir -p $out/bin
    cp fetch.py $out/bin/fetchscript
    chmod +x $out/bin/fetchscript

    mkdir -p $out/share/fetchscript
    cp testprotokoll.typ $out/share/fetchscript/testprotokoll.typ
    cp ${computerbrockiImg} $out/share/fetchscript/computerbrocki.png

    wrapProgram $out/bin/fetchscript \
      --set FETCHSCRIPT_SHARE $out/share/fetchscript \
      --prefix PATH : /run/wrappers/bin:/run/current-system/sw/bin

    runHook postInstall
  '';

  postInstall = ''
    install -Dm444 ./search-list.png $out/share/icons/hicolor/256x256/apps/search-list.png
  '';

  desktopItems = [ (pkgs.makeDesktopItem {
    name = "Testprotokoll";
    genericName = "fetchscript";
    comment = "Generiert ein schönes Testprotokoll mit Systeminformationen.";
    desktopName = "Testprotokoll";
    exec = "fetchscript";
    icon = "search-list";
    type = "Application";
    terminal = true;
    categories = ["Utility"];
  }) ];


  meta.mainProgram = "fetchscript";
}

