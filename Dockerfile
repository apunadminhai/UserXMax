# We're using Alpine Edge
FROM alpine:edge

# install ca-certificates so that HTTPS works consistently
RUN apk add --no-cache ca-certificates

# Installing Packages
RUN apk add --no-cache --update \
    bash \
    build-base \
    python2 \
    python2-dev \
    python3 \
    python3-dev \
    py3-pip \
    bzip2-dev \
    curl \
    coreutils \
    gcc \
    g++ \
    git \
    util-linux \
    libevent \
    libjpeg-turbo-dev \
    figlet \
    jpeg-dev \
    jpeg \
    libc-dev \
    aria2 \
    libffi-dev \
    libpq \
    libwebp-dev \
    libxml2-dev \
    libxslt-dev \
    linux-headers \
    musl-dev \
    openssl-dev \
    postgresql \
    postgresql-client \
    postgresql-dev \
    openssl \
    pv \
    neofetch \
    jq \
    wget \
    readline-dev \
    ffmpeg \
    sqlite-dev \
    sudo \
    zlib-dev \
    zip \
    unrar

#
# Clone repo and prepare working directory
#
RUN git clone 'https://github.com/noobvishal/UserXMax.git' /root/userbot
RUN mkdir /root/userbot/bin/
WORKDIR /root/userbot/

#
# Copies session and config (if it exists)
#
COPY ./sample_config.env ./userbot.session* ./config.env* /root/userbot/

#
# Install requirements
#
RUN pip3 install --no-cache-dir -r requirements.txt
CMD ["python3","-m","userbot"]
