# pip install cryptography

from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.backends import default_backend
import sqlite3

# Public key (Python 애플리케이션에 저장됨)
public_key_pem = b"""
-----BEGIN PUBLIC KEY-----
...Your Public Key Here...
-----END PUBLIC KEY-----
"""

# Primary key (리눅스 서버에 저장됨)
private_key_pem = b"""
-----BEGIN PRIVATE KEY-----
...Your Private Key Here...
-----END PRIVATE KEY-----
"""

# Public Key 로드
public_key = serialization.load_pem_public_key(
    public_key_pem,
    backend=default_backend()
)

# Private Key 로드
private_key = serialization.load_pem_private_key(
    private_key_pem,
    password=None,
    backend=default_backend()
)

# SQLite DB 연결 및 테이블 생성
conn = sqlite3.connect('example.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS data
             (id INTEGER PRIMARY KEY AUTOINCREMENT, encrypted_data BLOB)''')
conn.commit()


def encrypt_and_store_data(data: str):
    # 데이터를 바이트로 변환
    data_bytes = data.encode('utf-8')

    # 데이터를 Public Key로 암호화
    encrypted_data = public_key.encrypt(
        data_bytes,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    # 암호화된 데이터를 SQLite DB에 저장
    c.execute("INSERT INTO data (encrypted_data) VALUES (?)", (encrypted_data,))
    conn.commit()


def retrieve_and_decrypt_data(data_id: int):
    # DB에서 암호화된 데이터 가져오기
    c.execute("SELECT encrypted_data FROM data WHERE id = ?", (data_id,))
    encrypted_data = c.fetchone()[0]

    # 데이터를 Private Key로 복호화
    decrypted_data = private_key.decrypt(
        encrypted_data,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    # 바이트 데이터를 문자열로 변환하여 반환
    return decrypted_data.decode('utf-8')


# 예제 사용
encrypt_and_store_data("Hello, Secure World!")
decrypted_message = retrieve_and_decrypt_data(1)
print("Decrypted message:", decrypted_message)

# DB 연결 닫기
conn.close()
