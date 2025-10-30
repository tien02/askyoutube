ARG BASE_IMAGE=pytorch/pytorch:2.9.0-cuda13.0-cudnn9-runtime

FROM ${BASE_IMAGE}

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Etc/UTC

RUN apt-get update && apt-get install -y \
    git curl build-essential cmake yasm nasm pkg-config autoconf automake \
    libtool libv4l-dev libgl1 libglib2.0-0 libsm6 libxrender1 libxext6 \
    libmp3lame-dev librtmp-dev libfdk-aac-dev && \
    rm -rf /var/lib/apt/lists/*

# Build and install x264 (shared)
RUN git clone --branch stable https://code.videolan.org/videolan/x264.git && \
    cd x264 && \
    ./configure --prefix=/usr/local --enable-pic --enable-shared && \
    make -j"$(nproc)" && \
    make install && \
    cd .. && rm -rf x264

RUN git clone https://git.ffmpeg.org/ffmpeg.git ffmpeg && \
    cd ffmpeg && \
    ./configure \
        --prefix=/usr/local \
        --enable-gpl \
        --enable-nonfree \
        --enable-libx264 \
        --enable-libmp3lame \
        --enable-librtmp \
        --enable-libfdk-aac \
        --enable-shared && \
    make -j"$(nproc)" && \
    make install && \
    ldconfig && \
    cd .. && rm -rf ffmpeg

WORKDIR /module

COPY ./requirements.txt ./

RUN pip install -r requirements.txt

COPY ./app/main.py /module/main.py
COPY ./app/config /module/config
COPY ./app/schema /module/schema
COPY ./app/src /module/src
COPY ./app/utils /module/utils
