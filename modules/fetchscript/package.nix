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
  version = "0.3.1";
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

    install -Dm644 assets/* -t $out/share/fetchscript
    install -Dm644 ${computerbrockiImg} $out/share/fetchscript/computerbrocki.png

    install -Dm755 src/main.py $out/bin/fetchscript

    wrapProgram $out/bin/fetchscript \
      --set PYTHONPATH $out/lib \
      --set FETCHSCRIPT_SHARE $out/share/fetchscript \
      --prefix PATH : /run/wrappers/bin:/run/current-system/sw/bin

    runHook postInstall
  '';

  postInstall = ''
    install -Dm444 ./assets/search-list.png $out/share/icons/hicolor/256x256/apps/search-list.png
  '';

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

