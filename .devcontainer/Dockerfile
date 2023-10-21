FROM mcr.microsoft.com/devcontainers/python:1-3.11-bullseye

RUN apt-get -qq update 
RUN sudo apt-get -qq install -y --no-install-recommends \
    git g++ gcc autoconf automake m4 libtool make swig \
    libcurl4-openssl-dev libcrypto++-dev libsqlite3-dev libc-ares-dev libsodium-dev \
    libnautilus-extension-dev libssl-dev libfreeimage-dev libboost-all-dev
RUN pip install ipykernel python-dotenv wheel