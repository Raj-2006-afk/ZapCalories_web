#!/bin/bash
set -e

NODE_VERSION="v22.13.1"
ARCH="linux-x64"
INSTALL_DIR="/home/ranbir/node"

if [ -d "$INSTALL_DIR" ]; then
    echo "Node.js already installed in $INSTALL_DIR"
    exit 0
fi

echo "Downloading Node.js $NODE_VERSION..."
curl -O https://nodejs.org/dist/$NODE_VERSION/node-$NODE_VERSION-$ARCH.tar.xz

echo "Extracting..."
mkdir -p "$INSTALL_DIR"
tar -xJf node-$NODE_VERSION-$ARCH.tar.xz -C "$INSTALL_DIR" --strip-components=1

echo "Cleaning up..."
rm node-$NODE_VERSION-$ARCH.tar.xz

echo "Node.js installed successfully in $INSTALL_DIR"
echo "To use it, add $INSTALL_DIR/bin to your PATH:"
echo "export PATH=\$INSTALL_DIR/bin:\$PATH"
