#! /bin/sh
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
cd ../../../aiomega
cat << EOF > __init__.py
from .aiomega import AsyncMegaApi
from .mega import *
EOF