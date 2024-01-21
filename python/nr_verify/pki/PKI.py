import sqlite3
from datetime import datetime
from typing import List, Tuple, Any
from random import randint
import pickle as pkl
from py_ecc.bn128 import multiply, G1, curve_order


class PKI:
    def __init__(self, db_name="pki_database.db"):
        self.conn = sqlite3.connect(db_name)
        self.database_init()
        
    def _serialize_key(self, key: Any):
        return pkl.dumps(key)
    
    def _deserialize_key(self, data: bytes):
        return pkl.loads(data)
    
    def _validate_keys_pair(self, public_key: Tuple[int, int], private_key: int):
        return multiply(G1, private_key) == public_key
    
    def database_init(self):
        with self.conn:
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS keys (
                    key_id INTEGER PRIMARY KEY,
                    public_key BLOB NOT NULL,
                    creation_date DATETIME NOT NULL,
                    owner_id INT NOT NULL,
                    owner_name TEXT NOT NULL,
                    CONSTRAINT unique_key_id UNIQUE (key_id),
                    CONSTRAINT unique_owner_key_id UNIQUE (owner_id)
                )
            ''')
            
            self.conn.execute('CREATE INDEX IF NOT EXISTS idx_creation_date ON keys (creation_date)')
            self.conn.execute('CREATE INDEX IF NOT EXISTS idx_owner_id ON keys (owner_id)')
            self.conn.execute('CREATE INDEX IF NOT EXISTS idx_public_key ON keys (public_key)')
    

    def insert_key(self, public_key: Tuple[int, int], private_key: int, owner_id: int, owner_name: str):
        if self._validate_keys_pair(public_key, private_key):
            with self.conn:
                self.conn.execute('''
                    INSERT INTO keys (public_key, creation_date, owner_id, owner_name)
                    VALUES (?, ?, ?, ?)
                ''', (self._serialize_key(public_key),  datetime.now(), owner_id, owner_name))
        else:
            raise ValueError("Private key is not correspondig to public key")
         
    def generate_key_for_user(self, owner_id: int, owner_name: str):
        private_key = randint(1, curve_order)
        public_key = multiply(G1, private_key)
                
        with self.conn:
            self.conn.execute('''
                INSERT INTO keys (public_key, creation_date, owner_id, owner_name)
                VALUES (?, ?, ?, ?)
            ''', (self._serialize_key(public_key),  datetime.now(), owner_id, owner_name))
            
        return private_key
 
    def get_public_key_by_ids(self, ids: List[int]):
        with self.conn:
            cursor = self.conn.execute(f"""
                        SELECT public_key FROM keys WHERE key_id IN ({','.join('?' for _ in ids)})
                    """, ids)

            return [self._deserialize_key(public_key[0])for public_key in cursor.fetchall()]
        
    def get_public_key_by_owner_ids(self, ids: List[int]):
        with self.conn:
            cursor = self.conn.execute(f"""
                        SELECT public_key FROM keys WHERE owner_id IN ({','.join('?' for _ in ids)})
                    """, ids)

            return [self._deserialize_key(public_key[0])for public_key in cursor.fetchall()]
    
    def get_number_of_keys(self) -> int:
        with self.conn:
            cursor = self.conn.execute("""
                SELECT COUNT(*) FROM keys
            """)

            return cursor.fetchone()[0]
        
    def clear_database(self):
        with self.conn:
            self.conn.execute("""
                DELETE FROM keys
            """)
        
           
if __name__ == '__main__':
    # Example usage
    pki = PKI()
    pki.clear_database()
    
    pki.generate_key_for_user(5, "test5")
    assert pki.get_number_of_keys() == 1
    
    pki.generate_key_for_user(3, "test3")
    assert pki.get_number_of_keys() == 2
    
    private_key = randint(1, curve_order)
    public_key = multiply(G1, private_key)
    
    pki.insert_key(public_key, private_key, 32, "test32")
    assert pki.get_number_of_keys() == 3
    
    print(pki.get_public_key_by_ids([1]))
    print(pki.get_public_key_by_owner_ids([32]))
    
    private_key = pki.generate_key_for_user(111, "test111")
    public_key = pki.get_public_key_by_owner_ids([111])[0]
    
    assert(multiply(G1, private_key) == public_key)