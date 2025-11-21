#!/bin/bash
# Install dependencies for Phase 3

echo "Installing Cobaya..."
python3 -m pip install --user cobaya

echo "Installing Planck Likelihoods (might take a while)..."
# cobaya-install will be run later

echo "Building CLASS python wrapper..."
cd ../phase2/class
# Ensure clean build
rm -rf build

# Setup C++ flags for macOS
# Explicitly include C++ headers
export SDKROOT=$(xcrun --show-sdk-path)
export CXXFLAGS="-isysroot $SDKROOT -I$SDKROOT/usr/include -I/Library/Developer/CommandLineTools/SDKs/MacOSX.sdk/usr/include/c++/v1 -std=c++11 -stdlib=libc++"
export CFLAGS="-isysroot $SDKROOT -I$SDKROOT/usr/include"
export LDFLAGS="-isysroot $SDKROOT"

echo "Using SDKROOT: $SDKROOT"

# Use setup.py directly to ensure flags are passed
python3 setup.py build_ext --inplace
python3 setup.py install --user

echo "Done."
