FROM ethereum/solc:0.8.22-alpine as base

RUN apk upgrade --update

RUN apk add --no-cache \
  python3 && \
  python3 -m ensurepip

RUN pip3 install --no-cache --upgrade pip setuptools

RUN apk add --no-cache \
  libffi-dev \
  openssl-dev \
  build-base \
  git \
  make \
  cmake \
  g++ \
  gcc \
  musl-dev \
  linux-headers \
  python3-dev \
  vim \
  curl \
  bash \
  gmp-dev \
  nodejs \
  npm \
  libc6-compat

RUN npm install -g --quiet npm ganache

FROM base as ganache

RUN mkdir -p /app
WORKDIR /app
EXPOSE 8545

ENTRYPOINT ["ganache", "-h 0.0.0.0"]

FROM base as python

WORKDIR /app
COPY . .
# web3, solcx python wrappers
RUN pip install -r python/requirements.txt
RUN mkdir -p /root/.solcx/ && cp /usr/local/bin/solc /root/.solcx/solc-v0.8.22

ENTRYPOINT ["python3"]
