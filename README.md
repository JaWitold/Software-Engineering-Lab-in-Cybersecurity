## Contract deployment

Before compiling and deploying your contract you need to create a `.env` file. 
See `.env.example` for this purpose.

Then, you can start the docker containers to create your development environment.
It includes a **ganache** instance and a **python+solidity** container to run the code, compile contracts etc.

```bash
docker compose up --build
```

If you don't use the docker containers, remember to change your environment variables, and the **ENV_PATH** variable in `python/deployment/utils.py`.

Once started, you should see something like this :

```txt
ganache  | Available Accounts
ganache  | ==================
ganache  | (0) 0x769D1239CF96C1B0897F3C2b41f3f449b4c5eF5F (1000 ETH)
ganache  | (1) 0xFFb5314640B4f0C6FdC912621EEB24B3dE45653A (1000 ETH)
ganache  | (2) 0xbC47a094D70Ebfdc1a7402A2C58974173E7238C2 (1000 ETH)
ganache  | (3) 0x99436b0c1B326BB43c080882a468ffF30956ef2b (1000 ETH)
ganache  | (4) 0x8Cc5a3b54d2f03CcCF218008b6d69860B284D5Cf (1000 ETH)
ganache  | (5) 0x53550C17640C6A08f991d27c1dE4c0Df017235F4 (1000 ETH)
ganache  | (6) 0x945A24Fc8C5842E6ed8B6e796f926d08E4E975Ee (1000 ETH)
ganache  | (7) 0xD68062B1A99d47699228691F232402563753885D (1000 ETH)
ganache  | (8) 0xc85e546174b8E7896977e957890689F38D6cff0E (1000 ETH)
ganache  | (9) 0x6aDd4030439b193334D75807D5900797dF2e6017 (1000 ETH)
ganache  | 
ganache  | Private Keys
ganache  | ==================
ganache  | (0) 0x63f813a78a415323b529723321be3fafc85125273f7e8d1250126553cfe0dab9
ganache  | (1) 0x59d14c9ed37e682bd2ac20b2f2799400fe65499b0a5760a1e5995ae213c474c2
ganache  | (2) 0x26a041e862c6e074194953895e81c0919c213c819de4fe7a2c4b11162cc7e486
ganache  | (3) 0xf02c3490c82c58c2154a1bce39c9ea939175784ea3e58ab769fd116956c02321
ganache  | (4) 0x2fe79349583ce3a826c5ab083768b67f46aa095966c6c9c083a6eab802e445a8
ganache  | (5) 0xe5cc1ac6fcc31f1c271387f6ff9934a027e39755d91b83f8582bea039ea409ca
ganache  | (6) 0x74783589d2bd7d80b0f8655d88cb98dd919be5d5433bebd9612e66a70f35d054
ganache  | (7) 0x45e430dece31518dc5fed5b1a2d5ac71b2b2d6a8c43280ad1d2f05d6cf2516e8
ganache  | (8) 0xf13d0f5cb5d635b7b73fe46b583835bc61ff2a740714643fc0daf2be1e909a1a
ganache  | (9) 0x54b57210f982a0e2c4c8db35c29d2db4cecd49aba33b544cab9e60ece5a15098
```

Choose one account and it's private key and replace it in the `.env` file.

> Note: It is not necessary to use Ganache, every other provider could be used, you juste need to change the `.env` variable **PROVIDER_URL**.

Open a shell in the python container :
```bash
docker compose exec -ti python /bin/bash
```

Now, you can compile and deploy your smart contracts :
```bash
python3 python/deployment/index.py
```

The contracts to be compiled must be provided in the `.env` variable **FILES_TO_COMPILE**, separated by `,`.
For example :
- `FILES_TO_COMPILE="NrVerify,SchnorrSignature"`


