import sqlite3
from datetime import datetime
from typing import List
from random import randint
from py_ecc.bn128 import multiply, G1, curve_order


class PKI:
    def __init__(self, db_name="pki_database.db"):
        self.conn = sqlite3.connect(db_name)
        self.database_init()
            
    def database_init(self):
        with self.conn:
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS keys (
                    key_id INTEGER PRIMARY KEY,
                    private_key TEXT NOT NULL,
                    creation_date DATETIME NOT NULL,
                    owner_id INT NOT NULL,
                    owner_name TEXT NOT NULL,
                    CONSTRAINT unique_key_id UNIQUE (key_id),
                    CONSTRAINT unique_owner_key_id UNIQUE (owner_id)
                )
            ''')
            
            self.conn.execute('CREATE INDEX IF NOT EXISTS idx_creation_date ON keys (creation_date)')
            self.conn.execute('CREATE INDEX IF NOT EXISTS idx_owner_id ON keys (owner_id)')
            self.conn.execute('CREATE INDEX IF NOT EXISTS idx_private_key ON keys (private_key)')
         
    def generate_key_for_user(self, owner_id: int, owner_name: str):
        private_key = randint(1, curve_order)
                
        with self.conn:
            self.conn.execute('''
                INSERT INTO keys (private_key, creation_date, owner_id, owner_name)
                VALUES (?, ?, ?, ?)
            ''', (str(private_key),  datetime.now(), owner_id, owner_name))

    def insert_key(self, private_key: int, owner_id: int, owner_name: str):
        with self.conn:
            self.conn.execute('''
                INSERT INTO keys (private_key, creation_date, owner_id, owner_name)
                VALUES (?, ?, ?, ?)
            ''', (private_key,  datetime.now(), owner_id, owner_name))
            
    def get_public_key_by_ids(self, ids: List[int]):
        with self.conn:
            cursor = self.conn.execute(f"""
                        SELECT private_key FROM keys WHERE key_id IN ({','.join('?' for _ in ids)})
                    """, ids)

            return [multiply(G1, int(private_key[0])) for private_key in cursor.fetchall()]
        
    def get_public_key_by_owner_ids(self, ids: List[int]):
        with self.conn:
            cursor = self.conn.execute(f"""
                        SELECT private_key FROM keys WHERE owner_id IN ({','.join('?' for _ in ids)})
                    """, ids)

            return [multiply(G1, int(private_key[0])) for private_key in cursor.fetchall()]
    
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
    
    pki.insert_key(123, 66, "test66")
    assert pki.get_number_of_keys() == 3
    
    print(pki.get_public_key_by_ids([2]))
    print(pki.get_public_key_by_owner_ids([3]))