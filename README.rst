====================================
Hierarchical Ring Signatures Revisited – Unconditionally and Perfectly Anonymous Schnorr Version - Student's implementation
====================================

Introduction
------------

This project aims to (briefly describe the purpose of your project, what problems it solves, and how). It incorporates Python for backend logic and Solidity for smart contract development, facilitating seamless interaction with the Ethereum blockchain.

The structure and methodologies are inspired by the concepts discussed in the paper "Hierarchical Ring Signatures Revisited – Unconditionally and Perfectly Anonymous Schnorr Version" by Łukasz Krzywiecki, Małgorzata Sulkowska, and Filip Zagórski, which can be accessed `here <https://link.springer.com/chapter/10.1007/978-3-319-24126-5_19>`_. Special acknowledgment to Prof. Krzywiecki for the foundational theories and frameworks utilized in this project. More about Prof. Krzywiecki's work can be found on his `web page <https://cs.pwr.edu.pl/krzywiecki/index.html>`_.

Getting Started
---------------

**Prerequisites**

- Python 3.10+
- pip (Python package manager)
- Docker

**Installation**

1. Clone the repository:

   .. code-block:: bash

       git clone https://github.com/JaWitold/Software-Engineering-Lab-in-Cybersecurity.git

2. Navigate to the project directory:

   .. code-block:: bash

       cd Software-Engineering-Lab-in-Cybersecurity

3. Setup virtual environment

   .. code-block:: bash

      virtualenv venv

4. Activate virtual environment

   .. code-block:: bash

      source .venv/bin/activate

5. Install the required Python dependencies from setup.cfg:

   .. code-block:: bash

       pip install -e .

Running the Python Code
-----------------------

To run the Python code, navigate to the src directory and execute:

.. code-block:: bash

    python main.py

Replace `main.py` with the actual entry point of your project.

Running Tests
-------------

This project uses `pytest` for testing. To run the tests, execute the following command:

.. code-block:: bash

    pytest

Or, if you're using `tox`, simply run:

.. code-block:: bash

    tox

Deploying the Solidity Contract
-------------------------------

.. todo:: TODO

**Local Ganache Setup**

1. Ensure Docker is installed and running on your machine.

2. Pull the Ganache Docker image:

   .. code-block:: bash

       docker pull trufflesuite/ganache-cli

3. Run Ganache:

   .. code-block:: bash

       docker run -d -p 8545:8545 trufflesuite/ganache-cli:latest

**Deploying Contract**

After setting up Ganache, deploy the Solidity contract by executing:

.. code-block:: bash

    truffle migrate --reset

(Ensure you have Truffle installed and your `truffle-config.js` is configured to connect to your Ganache instance.)

Project Structure
-----------------

- `src/`: Contains the Python code.
- `contracts/`: Solidity contracts.
- `tests/`: Python test cases.
- `docs/`: Project documentation.

References
----------

- "Hierarchical Ring Signatures Revisited – Unconditionally and Perfectly Anonymous Schnorr Version", accessible at https://link.springer.com/chapter/10.1007/978-3-319-24126-5_19
- Prof. Krzywiecki's web page: https://cs.pwr.edu.pl/krzywiecki/index.html

Contributing
------------

.. include:: ../CONTRIBUTING.rst

License
-------
.. include:: ../LICENSE.txt

Note
====

This project has been set up using PyScaffold 4.5. For details and usage
information on PyScaffold see https://pyscaffold.org/.
