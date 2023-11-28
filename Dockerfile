FROM ethereum/solc:0.8.22-alpine 

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
    npm

WORKDIR /app
COPY . .

RUN npm install -g pnpm

# web3, solcx python wrappers
RUN pip install -r requirements.txt
RUN mkdir -p /root/.solcx/ && cp /usr/local/bin/solc /root/.solcx/solc-v0.8.22

ENTRYPOINT ["python3"]
