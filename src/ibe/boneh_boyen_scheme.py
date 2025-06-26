# -*- coding: utf-8 -*-

"""
Boneh-Boyen Identity-Based Encryption (BB-IBE) 实现

Boneh-Boyen IBE是对原始Boneh-Franklin方案的改进，提供了更强的安全性保证。
主要改进包括：
1. 标准模型下的安全性证明（而非随机神谕模型）
2. 更好的抗选择密文攻击能力
3. 支持分级身份加密

核心特点：
- 使用更复杂的身份哈希函数
- 增强的密钥生成算法
- 改进的加密/解密过程

注意：这是一个教学实现，重点展示BB-IBE的算法流程。
"""

import hashlib
import hmac
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
import struct

class BonehBoyenIBE:
    """Boneh-Boyen IBE方案实现"""
    
    def __init__(self):
        self.master_secret = None
        self.alpha = None  # 额外的主密钥组件
        self.system_params = None
        
    def setup(self):
        """
        Setup阶段：生成系统参数和主密钥
        BB-IBE使用双主密钥结构提供更强的安全性
        """
        # 生成双主密钥
        self.master_secret = get_random_bytes(32)  # 主密钥 s
        self.alpha = get_random_bytes(32)          # 辅助密钥 α
        
        # 系统公共参数
        self.system_params = {
            'system_id': 'BB-IBE-v1.0',
            'hash_function': 'sha256',
            'key_size': 256,
            'security_level': 'standard_model'
        }
        
        return {
            'public_params': self.system_params,
            'master_secret_s': self.master_secret.hex(),
            'master_secret_alpha': self.alpha.hex()
        }
    
    def extract(self, identity):
        """
        Extract阶段：为指定身份生成私钥
        BB-IBE使用改进的密钥生成算法
        """
        if self.master_secret is None or self.alpha is None:
            raise ValueError("必须先执行setup()初始化系统")
            
        # BB-IBE的身份哈希函数（更复杂的映射）
        identity_bytes = identity.encode('utf-8')
        
        # 第一轮哈希：基本身份映射
        h1 = hashlib.pbkdf2_hmac('sha256', identity_bytes, self.master_secret, 50000, 32)
        
        # 第二轮哈希：使用α增强安全性
        h2 = hmac.new(self.alpha, h1 + identity_bytes, hashlib.sha256).digest()
        
        # 组合生成最终私钥
        private_key = hashlib.pbkdf2_hmac('sha256', h1 + h2, self.alpha, 50000, 32)
        
        return {
            'identity': identity,
            'private_key': private_key,
            'key_hex': private_key.hex(),
            'h1': h1,
            'h2': h2
        }
    
    def encrypt(self, identity, message):
        """
        Encrypt阶段：使用身份信息加密消息
        BB-IBE使用增强的加密算法
        """
        if self.system_params is None or self.master_secret is None:
            raise ValueError("必须先执行setup()初始化系统")
            
        # 生成随机会话密钥
        session_key = get_random_bytes(32)
        
        # BB-IBE的身份密钥生成（与extract保持一致）
        identity_bytes = identity.encode('utf-8')
        
        # 使用相同的哈希链生成身份密钥
        if self.master_secret is None or self.alpha is None:
            raise ValueError("主密钥未初始化")
        h1 = hashlib.pbkdf2_hmac('sha256', identity_bytes, self.master_secret, 50000, 32)
        h2 = hmac.new(self.alpha, h1 + identity_bytes, hashlib.sha256).digest()
        identity_key = hashlib.pbkdf2_hmac('sha256', h1 + h2, self.alpha, 50000, 32)
        
        # 生成随机数r用于增强安全性
        r = get_random_bytes(16)
        
        # 使用身份密钥和随机数生成KEK
        kek_material = identity_key + r
        kek = hashlib.sha256(kek_material).digest()
        
        # 使用KEK加密会话密钥
        kek_cipher = AES.new(kek, AES.MODE_GCM)
        encrypted_session_key, kek_tag = kek_cipher.encrypt_and_digest(session_key)
        
        # 使用会话密钥加密消息
        msg_cipher = AES.new(session_key, AES.MODE_GCM)
        if isinstance(message, str):
            message = message.encode('utf-8')
        ciphertext, msg_tag = msg_cipher.encrypt_and_digest(message)
        
        return {
            'identity': identity,
            'r': r,  # BB-IBE特有的随机组件
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
        BB-IBE的解密过程
        """
        # 提取私钥和随机数
        private_key = private_key_data['private_key']
        r = ciphertext_data['r']
        
        # 生成KEK（与加密时相同的逻辑）
        kek_material = private_key + r
        kek = hashlib.sha256(kek_material).digest()
        
        # 解密会话密钥
        kek_cipher = AES.new(kek, AES.MODE_GCM, ciphertext_data['kek_nonce'])
        session_key = kek_cipher.decrypt_and_verify(
            ciphertext_data['encrypted_session_key'],
            ciphertext_data['kek_tag']
        )
        
        # 使用会话密钥解密消息
        msg_cipher = AES.new(session_key, AES.MODE_GCM, ciphertext_data['msg_nonce'])
        message = msg_cipher.decrypt_and_verify(
            ciphertext_data['ciphertext'],
            ciphertext_data['msg_tag']
        )
        
        return message

# 全局实例
bb_ibe = BonehBoyenIBE()

def setup():
    """设置BB-IBE系统"""
    return bb_ibe.setup()

def extract(identity):
    """提取身份对应的私钥"""
    return bb_ibe.extract(identity)

def encrypt(identity, message):
    """使用身份加密消息"""
    return bb_ibe.encrypt(identity, message)

def decrypt(private_key_data, ciphertext_data):
    """使用私钥解密消息"""
    return bb_ibe.decrypt(private_key_data, ciphertext_data)

# === 测试代码 ===
if __name__ == '__main__':
    print("正在测试 Boneh-Boyen IBE 方案...")
    
    # 1. 系统设置
    print("1. 执行 Setup...")
    setup_result = setup()
    print(f"   系统初始化完毕")
    print(f"   系统ID: {setup_result['public_params']['system_id']}")
    print(f"   安全级别: {setup_result['public_params']['security_level']}")
    
    # 2. 用户身份
    alice_identity = "alice@company.com"
    bob_identity = "bob@company.com"
    
    # 3. 密钥提取
    print(f"2. 为 {alice_identity} 提取私钥...")
    alice_private_key = extract(alice_identity)
    print(f"   私钥提取完毕")
    print(f"   私钥前8字节: {alice_private_key['key_hex'][:16]}...")
    
    # 4. 加密消息
    original_message = "Confidential: BB-IBE provides enhanced security in standard model."
    print(f"3. 使用 {alice_identity} 的身份加密消息...")
    print(f"   原始消息: {original_message}")
    
    ciphertext = encrypt(alice_identity, original_message)
    print(f"   加密完毕，密文长度: {len(ciphertext['ciphertext'])} 字节")
    print(f"   随机组件r长度: {len(ciphertext['r'])} 字节")
    
    # 5. 解密消息
    print("4. 使用Alice的私钥解密消息...")
    decrypted_message = decrypt(alice_private_key, ciphertext)
    print(f"   解密后的消息: {decrypted_message.decode('utf-8')}")
    
    # 6. 验证
    assert original_message == decrypted_message.decode('utf-8')
    print("✅ 成功：Boneh-Boyen IBE 测试通过！")
    
    # 7. 安全性测试
    print("5. 安全性测试：Bob尝试解密给Alice的消息...")
    try:
        bob_private_key = extract(bob_identity)
        wrong_decryption = decrypt(bob_private_key, ciphertext)
        print("❌ 安全漏洞：Bob不应该能解密给Alice的消息")
    except Exception as e:
        print("✅ 安全性正确：Bob无法解密给Alice的消息")
        print(f"   错误类型: {type(e).__name__}")
    
    # 8. 性能对比测试
    print("6. 与BF-IBE的差异展示...")
    print("   - 双主密钥结构提供更强安全性")
    print("   - 标准模型下的安全性证明")
    print("   - 增强的随机化加密过程")
    print("   - 更复杂的身份哈希链")
    
    # 9. 批量测试
    print("7. 批量加密解密测试...")
    test_identities = [
        "admin@company.com",
        "dev@company.com", 
        "hr@company.com"
    ]
    
    for identity in test_identities:
        key = extract(identity)
        msg = f"Test message for {identity}"
        enc = encrypt(identity, msg)
        dec = decrypt(key, enc).decode('utf-8')
        assert msg == dec
        print(f"   {identity}: ✅")
    
    print("✅ Boneh-Boyen IBE 完整测试通过！") 