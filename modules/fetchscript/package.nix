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

    mkdir -p $out/bin
    cat > $out/bin/fetchscript <<EOF
    #!${pkgs.runtimeShell}
    exec ${pkgs.python3.interpreter} $out/lib/fetchscript/main.py "\$@"
    EOF
    chmod +x $out/bin/fetchscript

    mkdir -p $out/share/fetchscript
    cp assets/* $out/share/fetchscript
    cp ${computerbrockiImg} $out/share/fetchscript/computerbrocki.png

    wrapProgram $out/bin/fetchscript \
      --set FETCHSCRIPT_SHARE $out/share/fetchscript \
      --prefix PATH : /run/wrappers/bin:/run/current-system/sw/bin

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

