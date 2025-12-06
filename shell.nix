let
  pkgs = import <nixpkgs> {};
in pkgs.mkShell {
  packages = [
    pkgs.python313
    pkgs.python313Packages.venvShellHook
    pkgs.python313Packages.ruff
  ];

  venvDir = "./.venv";
  postVenvCreation = ''
    pip install -r requirements.txt
  '';
}
