{
  description = "Development shell for testing webui with pytest, selenium and chromedriver";
  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
    poetry2nix.url = "github:nix-community/poetry2nix";
  };
  outputs = { self, nixpkgs, poetry2nix, ... }:
    let
      system = "x86_64-linux";
      pkgs = import nixpkgs { 
        system = system;
        config = {
          allowUnfree = true;
        }; 
      };
      inherit (poetry2nix.lib.mkPoetry2Nix { inherit pkgs; }) mkPoetryApplication;
      webuiTestingApp = mkPoetryApplication { 
        projectDir = ./.;
        python = pkgs.python3;
        pyproject = ./pyproject.toml;
        poetryLock = ./poetry.lock; 
      };
    in {
      devShells.x86_64-linux.default = pkgs.mkShell {
        LD_LIBRARY_PATH = "${pkgs.stdenv.cc.cc.lib}/lib";
        buildInputs = with pkgs; [
          webuiTestingApp
          chromedriver
          google-chrome
        ];
        shellHook = ''
          export CHROME_PATH=${pkgs.google-chrome}/bin/google-chrome-stable
        '';
      };
  };
}