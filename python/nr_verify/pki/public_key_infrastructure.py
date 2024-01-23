"""
Module: public_key_infrastructure
This module introduces PKI database class.
"""

import sqlite3
from datetime import datetime
from typing import List, Tuple, Any
from random import randint
import pickle as pkl
from py_ecc.bn128 import multiply, G1, curve_order


class PKI:
    """
    Implements sqlite PKI database with some access functions.
    """

    def __init__(self, db_name="pki_database.db"):
        self.conn = sqlite3.connect(db_name)
        self.database_init()

    @staticmethod
    def _serialize_key(key: Any):
        return pkl.dumps(key)

    @staticmethod
    def _deserialize_key(data: bytes):
        return pkl.loads(data)

    @staticmethod
    def _validate_keys_pair(public_key: Tuple[int, int], private_key: int):
        return multiply(G1, private_key) == public_key

    def database_init(self):
        """
        This function initialize table in database.
        """
        with self.conn:
            self.conn.execute(
                """
                CREATE TABLE IF NOT EXISTS keys (
                    key_id INTEGER PRIMARY KEY,
                    private_key BLOB NOT NULL,
                    creation_date DATETIME NOT NULL,
                    owner_id INT NOT NULL,
                    owner_name TEXT NOT NULL,
                    CONSTRAINT unique_key_id UNIQUE (key_id),
                    CONSTRAINT unique_owner_key_id UNIQUE (owner_id)
                )
            """
            )

            self.conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_creation_date ON keys (creation_date)"
            )
            self.conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_owner_id ON keys (owner_id)"
            )
            self.conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_private_key ON keys (private_key)"
            )

    def insert_key(
        self,
        public_key: Tuple[int, int],
        private_key: int,
        owner_id: int,
        owner_name: str,
    ):
        """
        This function inserts private key with assosiated metadata to database.
        It also verifies if user is in possesion of corresponding key.

        Args:
            private_key (int): User private key.
            owner_id (int): ID of user.
            owner_name (str): Name of user.
        """
        if self._validate_keys_pair(public_key, private_key):
            with self.conn:
                self.conn.execute(
                    """
                    INSERT INTO keys (private_key, creation_date, owner_id, owner_name)
                    VALUES (?, ?, ?, ?)
                """,
                    (
                        self._serialize_key(private_key),
                        datetime.now(),
                        owner_id,
                        owner_name,
                    ),
                )
        else:
            raise ValueError("Private key is not correspondig to public key")

    def generate_key_for_user(self, owner_id: int, owner_name: str) -> int:
        """
        This function generates private_key for user and insert it into database.

        Args:
            owner_id (int): ID of user.
            owner_name (str): Name of user.

        Returns:
            int: Private key for user.
        """
        private_key = randint(1, curve_order)

        with self.conn:
            self.conn.execute(
                """
                INSERT INTO keys (private_key, creation_date, owner_id, owner_name)
                VALUES (?, ?, ?, ?)
            """,
                (
                    self._serialize_key(private_key),
                    datetime.now(),
                    owner_id,
                    owner_name,
                ),
            )

        return private_key

    def get_public_key_by_ids(self, ids: List[int]) -> List[Tuple[int, int]]:
        """
        This function returns public keys by ids.

        Args:
            ids (List): IDs of keys.

        Returns:
            List[Tuple[int, int]]: Public keys.
        """
        with self.conn:
            cursor = self.conn.execute(
                f"""
                        SELECT private_key FROM keys WHERE key_id IN ({','.join('?' for _ in ids)})
                    """,
                ids,
            )

            return [
                multiply(G1, self._deserialize_key(private_key[0]))
                for private_key in cursor.fetchall()
            ]

    def get_public_key_by_owner_ids(self, ids: List[int]) -> List[Tuple[int, int]]:
        """
        This function returns public keys by user ids.

        Args:
            ids (List): IDs of users.

        Returns:
            List[Tuple[int, int]]: Public keys.
        """
        with self.conn:
            cursor = self.conn.execute(
                f"""
                    SELECT private_key FROM keys WHERE owner_id IN ({','.join('?' for _ in ids)})
                    """,
                ids,
            )

            return [
                multiply(G1, self._deserialize_key(private_key[0]))
                for private_key in cursor.fetchall()
            ]

    def get_number_of_keys(self) -> int:
        """
        This function returns number of keys in database.

        Returns:
            int: Number of keys.
        """
        with self.conn:
            cursor = self.conn.execute(
                """
                SELECT COUNT(*) FROM keys
            """
            )

            return cursor.fetchone()[0]

    def clear_database(self):
        """
        This function delete everything from database.
        """
        with self.conn:
            self.conn.execute(
                """
                DELETE FROM keys
            """
            )


if __name__ == "__main__":
    # Example usage
    pki = PKI()
    pki.clear_database()

    pki.generate_key_for_user(5, "test5")
    sk = randint(1, curve_order)
    pk = multiply(G1, sk)

    pki.insert_key(pk, sk, 32, "test32")

    print(pki.get_public_key_by_ids([1]))
    print(pki.get_public_key_by_owner_ids([32]))
    print(pki.get_number_of_keys())
