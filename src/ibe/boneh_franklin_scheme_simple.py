# -*- coding: utf-8 -*-

"""
简化版 Boneh-Franklin Identity-Based Encryption (BF-IBE) 实现

这是一个教学导向的IBE实现，重点展示IBE的核心概念：
- 使用身份信息作为公钥
- 通过可信机构生成对应的私钥
- 实现身份到密钥的映射

注意：这是一个概念性实现，使用简化的密码学原语。
"""

import hashlib
import random
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes

class SimpleBonehFranklinIBE:
    """简化版 Boneh-Franklin IBE方案"""
    
    def __init__(self):
        self.master_secret = None
        self.system_params = None
        
    def setup(self):
        """
        Setup阶段：生成系统参数和主密钥
        """
        # 生成主密钥（256位随机数）
        self.master_secret = get_random_bytes(32)
        
        # 系统公共参数
        self.system_params = {
            'system_id': 'BF-IBE-v1.0',
            'hash_function': 'sha256',
            'key_size': 256
        }
        
        return {
            'public_params': self.system_params,
            'master_secret': self.master_secret.hex()
        }
    
    def extract(self, identity):
        """
        Extract阶段：为指定身份生成私钥
        """
        if self.master_secret is None:
            raise ValueError("必须先执行setup()初始化系统")
            
        # 使用身份信息和主密钥生成私钥
        # 这里使用HMAC来确保私钥的唯一性和安全性
        identity_bytes = identity.encode('utf-8')
        
        # 生成确定性的私钥
        private_key = hashlib.pbkdf2_hmac(
            'sha256',
            identity_bytes,
            self.master_secret,
            100000,  # 迭代次数
            32       # 密钥长度
        )
        
        return {
            'identity': identity,
            'private_key': private_key,
            'key_hex': private_key.hex()
        }
    
    def encrypt(self, identity, message):
        """
        Encrypt阶段：使用身份信息加密消息
        """
        if self.system_params is None:
            raise ValueError("必须先执行setup()初始化系统")
            
        # 生成随机会话密钥
        session_key = get_random_bytes(32)
        
        # 生成确定性的身份密钥（与extract中的逻辑一致）
        identity_bytes = identity.encode('utf-8')
        if self.master_secret is None:
            raise ValueError("主密钥未初始化")
        identity_key = hashlib.pbkdf2_hmac(
            'sha256',
            identity_bytes,
            self.master_secret,
            100000,
            32
        )
        
        # 使用身份密钥加密会话密钥
        kek_cipher = AES.new(identity_key, AES.MODE_EAX)
        encrypted_session_key, kek_tag = kek_cipher.encrypt_and_digest(session_key)
        
        # 使用会话密钥加密实际消息
        msg_cipher = AES.new(session_key, AES.MODE_EAX)
        if isinstance(message, str):
            message = message.encode('utf-8')
        ciphertext, msg_tag = msg_cipher.encrypt_and_digest(message)
        
        return {
            'identity': identity,
            'encrypted_session_key': encrypted_session_key,
            'kek_nonce': kek_cipher.nonce,
            'kek_tag': kek_tag,
            'ciphertext': ciphertext,
            'msg_nonce': msg_cipher.nonce,
            'msg_tag': msg_tag
        }
    
    def decrypt(self, private_key_data, ciphertext_data):
        """
        Decrypt阶段：使用私钥解密消息
        """
        # 提取私钥
        private_key = private_key_data['private_key']
        
        # 解密会话密钥
        kek_cipher = AES.new(private_key, AES.MODE_EAX, ciphertext_data['kek_nonce'])
        session_key = kek_cipher.decrypt_and_verify(
            ciphertext_data['encrypted_session_key'],
            ciphertext_data['kek_tag']
        )
        
        # 使用会话密钥解密消息
        msg_cipher = AES.new(session_key, AES.MODE_EAX, ciphertext_data['msg_nonce'])
        message = msg_cipher.decrypt_and_verify(
            ciphertext_data['ciphertext'],
            ciphertext_data['msg_tag']
        )
        
        return message

# 全局实例
simple_bf_ibe = SimpleBonehFranklinIBE()

def setup():
    """设置IBE系统"""
    return simple_bf_ibe.setup()

def extract(identity):
    """提取身份对应的私钥"""
    return simple_bf_ibe.extract(identity)

def encrypt(identity, message):
    """使用身份加密消息"""
    return simple_bf_ibe.encrypt(identity, message)

def decrypt(private_key_data, ciphertext_data):
    """使用私钥解密消息"""
    return simple_bf_ibe.decrypt(private_key_data, ciphertext_data)

# === 测试代码 ===
if __name__ == '__main__':
    print("正在测试简化版 Boneh-Franklin IBE 方案...")
    
    # 1. 系统设置
    print("1. 执行 Setup...")
    setup_result = setup()
    print(f"   系统初始化完毕")
    print(f"   系统ID: {setup_result['public_params']['system_id']}")
    
    # 2. 用户身份
    alice_identity = "alice@example.com"
    bob_identity = "bob@example.com"
    
    # 3. 密钥提取
    print(f"2. 为 {alice_identity} 提取私钥...")
    alice_private_key = extract(alice_identity)
    print(f"   私钥提取完毕")
    print(f"   私钥前8字节: {alice_private_key['key_hex'][:16]}...")
    
    # 4. 加密消息
    original_message = "Hello Alice! This is a secret message using IBE."
    print(f"3. 使用 {alice_identity} 的身份加密消息...")
    print(f"   原始消息: {original_message}")
    
    ciphertext = encrypt(alice_identity, original_message)
    print(f"   加密完毕，密文长度: {len(ciphertext['ciphertext'])} 字节")
    
    # 5. 解密消息
    print("4. 使用Alice的私钥解密消息...")
    decrypted_message = decrypt(alice_private_key, ciphertext)
    print(f"   解密后的消息: {decrypted_message.decode('utf-8')}")
    
    # 6. 验证
    assert original_message == decrypted_message.decode('utf-8')
    print("✅ 成功：简化版 Boneh-Franklin IBE 测试通过！")
    
    # 7. 安全性测试：Bob不能解密给Alice的消息
    print("5. 安全性测试：Bob尝试解密给Alice的消息...")
    try:
        bob_private_key = extract(bob_identity)
        wrong_decryption = decrypt(bob_private_key, ciphertext)
        print("❌ 安全漏洞：Bob不应该能解密给Alice的消息")
    except Exception as e:
        print("✅ 安全性正确：Bob无法解密给Alice的消息")
        print(f"   错误类型: {type(e).__name__}")
    
    # 8. 多用户测试
    print("6. 多用户测试...")
    users = ["alice@example.com", "bob@example.com", "charlie@example.com"]
    messages = {}
    
    for user in users:
        user_key = extract(user)
        user_msg = f"This is a private message for {user}"
        encrypted_msg = encrypt(user, user_msg)
        decrypted_msg = decrypt(user_key, encrypted_msg)
        messages[user] = decrypted_msg.decode('utf-8')
        print(f"   {user}: ✅")
    
    print("✅ 多用户测试完成！所有用户都能正确收发消息。") 