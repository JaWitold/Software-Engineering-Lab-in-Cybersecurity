FROM node:slim as base

RUN apt-get update && \
    apt-get install --no-install-recommends -y \
        build-essential \
        python3 && \
    rm -fr /var/lib/apt/lists/* && \
    rm -rf /etc/apt/sources.list.d/*

RUN npm install --global --quiet truffle ganache

FROM base as truffle

RUN mkdir -p /home/app
WORKDIR /home/app

COPY package.json /home/app
COPY package-lock.json /home/app

RUN npm install --quiet

COPY truffle-config.js /home/app
COPY contracts /home/app/contracts
COPY migrations /home/app/migrations/
COPY test /home/app/test/

CMD ["truffle", "version"]

FROM base as ganache

RUN mkdir -p /home/accounts
WORKDIR /home
EXPOSE 8545

ENTRYPOINT ganache -h 0.0.0.0 \
                   --wallet.accountKeysPath /home/accounts/accounts.json \
                   --wallet.mnemonic "major arrive swarm best hungry lake amateur team float exotic sell fresh" \
                   --wallet.defaultBalance 1000000000
