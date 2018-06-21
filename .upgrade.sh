#!/bin/bash -e

SYMLINK=/usr/bin/pkgs-update-local
sudo ln -sf $(realpath $0) $SYMLINK

sudo apt update
sudo apt upgrade
sudo snap refresh
sudo flatpak update

