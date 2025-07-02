# This is the package definition of F3-Qt
# Documentation for packaging Qt apps: https://nixos.org/manual/nixpkgs/stable/#sec-language-qt
{ pkgs ? import <nixpkgs> {} }:

pkgs.stdenv.mkDerivation rec {
  pname = "f3-qt";
  version = "git";
  # The latest git revision is used because the latest tagged release doesn't have a .desktop file
  src = pkgs.fetchFromGitHub {
    owner = "zwpwjwtz";
    repo = pname;
    rev = "511093975f8605d17a53b29d9861798f28f63ef0";
    hash = "sha256-Bw7bGddzS4RRvSU9umu6L7drT41qqcpTWXbTIBsCyy0";
  };

  nativeBuildInputs = with pkgs.libsForQt5; [ qmake wrapQtAppsHook ];
  buildInputs = [ pkgs.libsForQt5.qt5.full ];

  dontUseCmakeConfigure = true;
  enableParallelBuilding = true;

  installPhase = ''
    install -Dm755 f3-qt $out/bin/f3-qt

    install -Dm644 f3-qt.desktop $out/share/applications/f3-qt.desktop
  '';
}
