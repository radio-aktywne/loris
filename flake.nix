{
  inputs = {
    nixpkgs = {
      url = "github:NixOS/nixpkgs/nixpkgs-unstable";
    };

    flake-parts = {
      url = "github:hercules-ci/flake-parts";
    };
  };

  outputs = inputs:
    inputs.flake-parts.lib.mkFlake {inherit inputs;} {
      # Import local override if it exists
      imports = [
        (
          if builtins.pathExists ./local.nix
          then ./local.nix
          else {}
        )
      ];

      # Sensible defaults
      systems = [
        "x86_64-linux"
        "i686-linux"
        "aarch64-linux"
        "x86_64-darwin"
        "aarch64-darwin"
      ];

      perSystem = {
        config,
        pkgs,
        system,
        ...
      }: let
        node = pkgs.nodejs;
        python = pkgs.python312.withPackages (ps: [ps.gst-python]);
        nil = pkgs.nil;
        task = pkgs.go-task;
        coreutils = pkgs.coreutils;
        trunk = pkgs.trunk-io;
        poetry = pkgs.poetry;
        cacert = pkgs.cacert;
        copier = pkgs.copier;
        glib = pkgs.glib;
        gstreamer = pkgs.gst_all_1.gstreamer;
        gstreamer-plugins-base = pkgs.gst_all_1.gst-plugins-base;
        gstreamer-plugins-good = pkgs.gst_all_1.gst-plugins-good;
        gstreamer-plugins-bad = pkgs.gst_all_1.gst-plugins-bad;
        gstreamer-plugins-ugly = pkgs.gst_all_1.gst-plugins-ugly;
        gstreamer-plugins-rs = pkgs.gst_all_1.gst-plugins-rs;
        libnice = pkgs.libnice;
        tini = pkgs.tini;
        su-exec = pkgs.su-exec;
      in {
        # Override pkgs argument
        _module.args.pkgs = import inputs.nixpkgs {
          inherit system;
          config = {
            # Allow packages with non-free licenses
            allowUnfree = true;
            # Allow packages with broken dependencies
            allowBroken = true;
            # Allow packages with unsupported system
            allowUnsupportedSystem = true;
          };
        };

        # Set which formatter should be used
        formatter = pkgs.alejandra;

        # Define multiple development shells for different purposes
        devShells = {
          default = pkgs.mkShell {
            name = "dev";

            packages = [
              node
              python
              nil
              task
              coreutils
              trunk
              poetry
              cacert
              copier
              glib
              gstreamer
              gstreamer-plugins-base
              gstreamer-plugins-good
              gstreamer-plugins-bad
              gstreamer-plugins-ugly
              gstreamer-plugins-rs
              libnice
            ];

            EXTRAPYTHONPATH = "${python}/${python.sitePackages}";

            # These are needed for custom GStreamer plugins
            GI_TYPELIB_PATH = "${glib.out}/lib/girepository-1.0:${gstreamer.out}/lib/girepository-1.0:${gstreamer-plugins-base}/lib/girepository-1.0:${gstreamer-plugins-good}/lib/girepository-1.0:${gstreamer-plugins-bad}/lib/girepository-1.0:${gstreamer-plugins-ugly}/lib/girepository-1.0:${gstreamer-plugins-rs}/lib/girepository-1.0:${libnice.out}/lib/girepository-1.0";
            GST_PLUGIN_PATH = "${python}/lib/gstreamer-1.0:plugins";

            shellHook = ''
              export TMPDIR=/tmp
            '';
          };

          package = pkgs.mkShell {
            name = "package";

            packages = [
              python
              task
              coreutils
              poetry
              cacert
            ];

            shellHook = ''
              export TMPDIR=/tmp
            '';
          };

          runtime = pkgs.mkShell {
            name = "runtime";

            packages = [
              python
              poetry
              cacert
              glib
              gstreamer
              gstreamer-plugins-base
              gstreamer-plugins-good
              gstreamer-plugins-bad
              gstreamer-plugins-ugly
              gstreamer-plugins-rs
              libnice
              tini
              su-exec
            ];

            EXTRAPYTHONPATH = "${python}/${python.sitePackages}";

            # These are needed for custom GStreamer plugins
            GI_TYPELIB_PATH = "${glib.out}/lib/girepository-1.0:${gstreamer.out}/lib/girepository-1.0:${gstreamer-plugins-base}/lib/girepository-1.0:${gstreamer-plugins-good}/lib/girepository-1.0:${gstreamer-plugins-bad}/lib/girepository-1.0:${gstreamer-plugins-ugly}/lib/girepository-1.0:${gstreamer-plugins-rs}/lib/girepository-1.0:${libnice.out}/lib/girepository-1.0";
            GST_PLUGIN_PATH = "${python}/lib/gstreamer-1.0:plugins";

            shellHook = ''
              export TMPDIR=/tmp
            '';
          };

          template = pkgs.mkShell {
            name = "template";

            packages = [
              task
              coreutils
              copier
            ];

            shellHook = ''
              export TMPDIR=/tmp
            '';
          };

          lint = pkgs.mkShell {
            name = "lint";

            packages = [
              node
              task
              coreutils
              trunk
            ];

            shellHook = ''
              export TMPDIR=/tmp
            '';
          };

          test = pkgs.mkShell {
            name = "test";

            packages = [
              python
              task
              coreutils
              poetry
              cacert
              glib
              gstreamer
              gstreamer-plugins-base
              gstreamer-plugins-good
              gstreamer-plugins-bad
              gstreamer-plugins-ugly
              gstreamer-plugins-rs
              libnice
            ];

            EXTRAPYTHONPATH = "${python}/${python.sitePackages}";

            # These are needed for custom GStreamer plugins
            GI_TYPELIB_PATH = "${glib.out}/lib/girepository-1.0:${gstreamer.out}/lib/girepository-1.0:${gstreamer-plugins-base}/lib/girepository-1.0:${gstreamer-plugins-good}/lib/girepository-1.0:${gstreamer-plugins-bad}/lib/girepository-1.0:${gstreamer-plugins-ugly}/lib/girepository-1.0:${gstreamer-plugins-rs}/lib/girepository-1.0:${libnice.out}/lib/girepository-1.0";
            GST_PLUGIN_PATH = "${python}/lib/gstreamer-1.0:plugins";

            shellHook = ''
              export TMPDIR=/tmp
            '';
          };

          docs = pkgs.mkShell {
            name = "docs";

            packages = [
              node
              task
              coreutils
            ];

            shellHook = ''
              export TMPDIR=/tmp
            '';
          };
        };
      };
    };
}
