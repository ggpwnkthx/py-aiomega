#! /bin/sh
sudo apt-get -qq update 
sudo apt-get -qq install -y --no-install-recommends \
    git g++ gcc autoconf automake m4 libtool make swig \
    libcurl4-openssl-dev libcrypto++-dev libsqlite3-dev libc-ares-dev libsodium-dev \
    libnautilus-extension-dev libssl-dev libfreeimage-dev libboost-all-dev
pip install wheel

rm -rf sdk
git clone https://github.com/meganz/sdk.git sdk
cd sdk || exit

autoupdate
./autogen.sh
./configure --disable-silent-rules --disable-examples --enable-python --with-python3 --with-sodium
make -j$(nproc --all)

cd bindings/python/ || exit
python3 setup.py bdist_wheel
cp -f build/lib/mega/* ../../../aiomega
