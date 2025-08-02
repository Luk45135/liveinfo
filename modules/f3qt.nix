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
    rev = "c8ee27be78d6f3697d1ffe1f9c8fbf0950118831";
    hash = "sha256-1xxl8X2ebk+JU1sgI0bYxbHvoxKHEhaR8KmcY7Vie54";
  };

  nativeBuildInputs = with pkgs.qt6Packages; [ qmake wrapQtAppsHook ];
  buildInputs = [ pkgs.qt6Packages.qtbase ];

  dontUseCmakeConfigure = true;
  enableParallelBuilding = true;

  installPhase = ''
    install -Dm755 f3-qt $out/bin/f3-qt

    install -Dm644 f3-qt.desktop $out/share/applications/f3-qt.desktop
  '';
}
