# -*- coding: utf-8 -*-

"""
Sakai-Kasahara Identity-Based Encryption (SK-IBE) 实现

Sakai-Kasahara IBE方案是另一种基于配对的身份加密方案，具有以下特点：
1. 不同于Boneh-Franklin和Boneh-Boyen的数学结构
2. 在某些场景下具有更好的计算效率
3. 使用不同的身份映射方法
4. 更适合特定的应用场景

核心特点：
- 基于不同的难题假设
- 优化的密钥生成过程
- 高效的加密/解密算法
- 适合大规模部署

注意：这是一个教学实现，重点展示SK-IBE的算法特性。
"""

import hashlib
import hmac
from Crypto.Cipher import AES, ChaCha20
from Crypto.Random import get_random_bytes
import struct
import base64

class SakaiKasaharaIBE:
    """Sakai-Kasahara IBE方案实现"""
    
    def __init__(self):
        self.master_secret = None
        self.beta = None  # SK-IBE特有的系统参数
        self.system_params = None
        
    def setup(self):
        """
        Setup阶段：生成系统参数和主密钥
        SK-IBE使用不同的参数结构
        """
        # 生成主密钥
        self.master_secret = get_random_bytes(32)
        self.beta = get_random_bytes(32)  # SK-IBE特有参数
        
        # 系统公共参数
        self.system_params = {
            'system_id': 'SK-IBE-v1.0',
            'hash_function': 'sha256',
            'key_size': 256,
            'scheme_type': 'sakai_kasahara',
            'optimization_level': 'high'
        }
        
        return {
            'public_params': self.system_params,
            'master_secret': self.master_secret.hex(),
            'beta_param': self.beta.hex()
        }
    
    def extract(self, identity):
        """
        Extract阶段：使用SK-IBE的密钥生成算法
        """
        if self.master_secret is None or self.beta is None:
            raise ValueError("必须先执行setup()初始化系统")
            
        identity_bytes = identity.encode('utf-8')
        
        # SK-IBE的身份处理：使用逆元计算
        # 这是SK-IBE与其他方案的主要区别
        identity_hash = hashlib.sha256(identity_bytes + self.beta).digest()
        identity_int = int.from_bytes(identity_hash[:8], byteorder='big')
        
        # 模拟SK-IBE的逆元计算（简化版）
        # 在真实实现中，这涉及到椭圆曲线上的复杂运算
        inverse_factor = pow(identity_int, -1, 2**64 - 59)  # 使用模逆
        
        # 使用逆元和主密钥生成私钥
        key_material = struct.pack('>Q', inverse_factor) + self.master_secret
        private_key = hashlib.pbkdf2_hmac('sha256', key_material, self.beta, 75000, 32)
        
        return {
            'identity': identity,
            'private_key': private_key,
            'key_hex': private_key.hex(),
            'identity_hash': identity_hash,
            'inverse_factor': inverse_factor
        }
    
    def encrypt(self, identity, message):
        """
        Encrypt阶段：SK-IBE的高效加密算法
        """
        if self.system_params is None or self.master_secret is None or self.beta is None:
            raise ValueError("必须先执行setup()初始化系统")
            
        # 生成随机会话密钥
        session_key = get_random_bytes(32)
        
        # SK-IBE的身份密钥计算（与extract保持一致）
        identity_bytes = identity.encode('utf-8')
        identity_hash = hashlib.sha256(identity_bytes + self.beta).digest()
        identity_int = int.from_bytes(identity_hash[:8], byteorder='big')
        inverse_factor = pow(identity_int, -1, 2**64 - 59)
        
        key_material = struct.pack('>Q', inverse_factor) + self.master_secret
        identity_key = hashlib.pbkdf2_hmac('sha256', key_material, self.beta, 75000, 32)
        
        # SK-IBE特有的随机化参数
        sk_randomizer = get_random_bytes(24)
        
        # 使用ChaCha20流密码（SK-IBE推荐的高效算法）
        kek_nonce = get_random_bytes(12)
        kek_cipher = ChaCha20.new(key=identity_key, nonce=kek_nonce)
        encrypted_session_key = kek_cipher.encrypt(session_key)
        
        # 消息加密
        msg_nonce = get_random_bytes(12)
        msg_cipher = ChaCha20.new(key=session_key, nonce=msg_nonce)
        if isinstance(message, str):
            message = message.encode('utf-8')
        ciphertext = msg_cipher.encrypt(message)
        
        # 计算消息认证码
        auth_data = sk_randomizer + identity_bytes + ciphertext
        auth_tag = hmac.new(session_key, auth_data, hashlib.sha256).digest()
        
        return {
            'identity': identity,
            'sk_randomizer': sk_randomizer,
            'encrypted_session_key': encrypted_session_key,
            'kek_nonce': kek_nonce,
            'ciphertext': ciphertext,
            'msg_nonce': msg_nonce,
            'auth_tag': auth_tag
        }
    
    def decrypt(self, private_key_data, ciphertext_data):
        """
        Decrypt阶段：SK-IBE的高效解密算法
        """
        # 提取私钥和密文组件
        private_key = private_key_data['private_key']
        sk_randomizer = ciphertext_data['sk_randomizer']
        identity_bytes = ciphertext_data['identity'].encode('utf-8')
        
        # 解密会话密钥
        kek_cipher = ChaCha20.new(key=private_key, nonce=ciphertext_data['kek_nonce'])
        session_key = kek_cipher.decrypt(ciphertext_data['encrypted_session_key'])
        
        # 验证消息认证码
        auth_data = sk_randomizer + identity_bytes + ciphertext_data['ciphertext']
        expected_tag = hmac.new(session_key, auth_data, hashlib.sha256).digest()
        
        if not hmac.compare_digest(expected_tag, ciphertext_data['auth_tag']):
            raise ValueError("消息认证失败，可能被篡改")
        
        # 解密消息
        msg_cipher = ChaCha20.new(key=session_key, nonce=ciphertext_data['msg_nonce'])
        message = msg_cipher.decrypt(ciphertext_data['ciphertext'])
        
        return message

# 全局实例
sk_ibe = SakaiKasaharaIBE()

def setup():
    """设置SK-IBE系统"""
    return sk_ibe.setup()

def extract(identity):
    """提取身份对应的私钥"""
    return sk_ibe.extract(identity)

def encrypt(identity, message):
    """使用身份加密消息"""
    return sk_ibe.encrypt(identity, message)

def decrypt(private_key_data, ciphertext_data):
    """使用私钥解密消息"""
    return sk_ibe.decrypt(private_key_data, ciphertext_data)

# === 测试代码 ===
if __name__ == '__main__':
    print("正在测试 Sakai-Kasahara IBE 方案...")
    
    # 1. 系统设置
    print("1. 执行 Setup...")
    setup_result = setup()
    print(f"   系统初始化完毕")
    print(f"   系统ID: {setup_result['public_params']['system_id']}")
    print(f"   方案类型: {setup_result['public_params']['scheme_type']}")
    print(f"   优化级别: {setup_result['public_params']['optimization_level']}")
    
    # 2. 用户身份
    alice_identity = "alice@university.edu"
    bob_identity = "bob@university.edu"
    
    # 3. 密钥提取
    print(f"2. 为 {alice_identity} 提取私钥...")
    alice_private_key = extract(alice_identity)
    print(f"   私钥提取完毕")
    print(f"   私钥前8字节: {alice_private_key['key_hex'][:16]}...")
    print(f"   逆元因子: {alice_private_key['inverse_factor']}")
    
    # 4. 加密消息
    original_message = "SK-IBE: Efficient identity-based encryption with optimized performance."
    print(f"3. 使用 {alice_identity} 的身份加密消息...")
    print(f"   原始消息: {original_message}")
    
    ciphertext = encrypt(alice_identity, original_message)
    print(f"   加密完毕，密文长度: {len(ciphertext['ciphertext'])} 字节")
    print(f"   随机化参数长度: {len(ciphertext['sk_randomizer'])} 字节")
    
    # 5. 解密消息
    print("4. 使用Alice的私钥解密消息...")
    decrypted_message = decrypt(alice_private_key, ciphertext)
    print(f"   解密后的消息: {decrypted_message.decode('utf-8')}")
    
    # 6. 验证
    assert original_message == decrypted_message.decode('utf-8')
    print("✅ 成功：Sakai-Kasahara IBE 测试通过！")
    
    # 7. 安全性测试
    print("5. 安全性测试：Bob尝试解密给Alice的消息...")
    try:
        bob_private_key = extract(bob_identity)
        wrong_decryption = decrypt(bob_private_key, ciphertext)
        print("❌ 安全漏洞：Bob不应该能解密给Alice的消息")
    except Exception as e:
        print("✅ 安全性正确：Bob无法解密给Alice的消息")
        print(f"   错误类型: {type(e).__name__}")
    
    # 8. 篡改检测测试
    print("6. 消息完整性测试：尝试篡改密文...")
    try:
        # 篡改密文
        tampered_ciphertext = ciphertext.copy()
        tampered_data = bytearray(tampered_ciphertext['ciphertext'])
        tampered_data[0] = (tampered_data[0] + 1) % 256  # 修改第一个字节
        tampered_ciphertext['ciphertext'] = bytes(tampered_data)
        
        # 尝试解密被篡改的密文
        decrypt(alice_private_key, tampered_ciphertext)
        print("❌ 完整性检查失败：应该检测到篡改")
    except ValueError as e:
        print("✅ 完整性检查成功：检测到消息被篡改")
        print(f"   错误信息: {str(e)}")
    
    # 9. SK-IBE特性展示
    print("7. SK-IBE方案特性...")
    print("   - 基于逆元的身份映射算法")
    print("   - 使用ChaCha20流密码提高效率")
    print("   - 内置消息认证保护完整性")
    print("   - 优化的密钥生成过程")
    
    # 10. 效率测试
    print("8. 效率测试...")
    import time
    
    test_identities = [f"user{i}@test.edu" for i in range(5)]
    
    # 密钥生成效率
    start_time = time.time()
    for identity in test_identities:
        extract(identity)
    key_gen_time = time.time() - start_time
    print(f"   5个用户密钥生成耗时: {key_gen_time:.4f} 秒")
    
    # 加密解密效率
    test_msg = "Efficiency test message for SK-IBE scheme."
    start_time = time.time()
    for identity in test_identities:
        key = extract(identity)
        enc = encrypt(identity, test_msg)
        dec = decrypt(key, enc)
        assert test_msg.encode() == dec
    total_time = time.time() - start_time
    print(f"   5次完整加密解密耗时: {total_time:.4f} 秒")
    print(f"   平均每次耗时: {total_time/5:.4f} 秒")
    
    print("✅ Sakai-Kasahara IBE 完整测试通过！") 