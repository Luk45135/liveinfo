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
  format = "other"; # we’re not using setuptools or flit

  src = ./.;

  nativeBuildInputs = with pkgs; [ makeWrapper ];

  dependencies = with pkgs.python3Packages; [
    humanfriendly
  ];

  # propagatedBuildInputs = with pkgs; [
  #     fastfetch
  #     glxinfo
  #     smartmontools
  #     clinfo
  #     f3
  #     fio
  #     libsForQt5.okular
  #     typst
  # ];


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
  '';

  meta.mainProgram = "fetchscript";
}

