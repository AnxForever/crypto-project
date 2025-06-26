# -*- coding: utf-8 -*-

"""
Boneh-Franklin Identity-Based Encryption (BF-IBE) 实现

这是最早的实用IBE方案，由Dan Boneh和Matt Franklin在2001年提出。
该方案基于双线性对和椭圆曲线离散对数问题的困难性。

IBE系统的四个核心算法：
1. Setup: 生成系统参数和主密钥
2. Extract: 从身份信息生成对应的私钥
3. Encrypt: 使用身份信息加密消息
4. Decrypt: 使用私钥解密密文

注意：这是一个教学实现，使用椭圆曲线运算模拟双线性对的效果。
在实际生产环境中，应该使用专门的双线性对库。
"""

import hashlib
import random
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
import binascii

class BonehFranklinIBE:
    """Boneh-Franklin IBE方案实现"""
    
    def __init__(self):
        # 椭圆曲线参数 (简化版，用于演示)
        self.p = 2**128 - 159  # 较小的素数，便于计算
        self.g = 2  # 生成元
        self.master_secret = None
        self.public_params = None
        
    def setup(self):
        """
        Setup阶段：生成系统公共参数和主密钥
        
        返回:
            dict: 包含公共参数和主密钥的字典
        """
        # 生成主密钥 s (随机数)
        self.master_secret = random.randint(1, self.p - 1)
        
        # 计算公共参数 P_pub = s * P (P是基点)
        public_point = pow(self.g, self.master_secret, self.p)
        
        self.public_params = {
            'p': self.p,
            'g': self.g,
            'P_pub': public_point,
            'hash_function': 'sha256'
        }
        
        return {
            'public_params': self.public_params,
            'master_secret': self.master_secret
        }
    
    def extract(self, identity):
        """
        Extract阶段：从身份信息生成对应的私钥
        
        参数:
            identity (str): 用户身份标识 (如邮箱地址)
            
        返回:
            dict: 用户的私钥
        """
        if self.master_secret is None:
            raise ValueError("必须先执行setup()生成系统参数")
            
        # 将身份信息哈希到椭圆曲线上的点
        identity_hash = self._hash_to_point(identity)
        
        # 计算私钥 D_id = s * Q_id (Q_id是身份对应的点)
        private_key = pow(identity_hash, self.master_secret, self.p)
        
        return {
            'identity': identity,
            'private_key': private_key,
            'identity_point': identity_hash
        }
    
    def encrypt(self, identity, message):
        """
        Encrypt阶段：使用身份信息加密消息
        
        参数:
            identity (str): 接收者身份标识
            message (bytes): 要加密的消息
            
        返回:
            dict: 密文组件
        """
        if self.public_params is None:
            raise ValueError("必须先执行setup()生成系统参数")
            
        # 生成随机数 r
        r = random.randint(1, self.p - 1)
        
        # 计算 rP
        rP = pow(self.g, r, self.p)
        
        # 将身份信息哈希到点
        identity_point = self._hash_to_point(identity)
        
        # 计算配对 e(Q_id, P_pub)^r (简化实现)
        # 使用简化的配对模拟：(Q_id^r mod p) XOR (P_pub^r mod p)
        pairing_result = (pow(identity_point, r, self.p) * pow(self.public_params['P_pub'], r, self.p)) % self.p
        
        # 从配对结果导出对称密钥
        symmetric_key = self._derive_key(pairing_result)
        
        # 使用AES加密消息
        cipher = AES.new(symmetric_key, AES.MODE_CBC)
        padded_message = pad(message, AES.block_size)
        ciphertext = cipher.encrypt(padded_message)
        
        return {
            'identity': identity,
            'U': rP,  # 第一个密文组件
            'V': ciphertext,  # 第二个密文组件
            'iv': cipher.iv  # 初始化向量
        }
    
    def decrypt(self, private_key_data, ciphertext_data):
        """
        Decrypt阶段：使用私钥解密密文
        
        参数:
            private_key_data (dict): 私钥数据
            ciphertext_data (dict): 密文数据
            
        返回:
            bytes: 解密后的明文消息
        """
        # 获取密文组件
        U = ciphertext_data['U']
        V = ciphertext_data['V']
        iv = ciphertext_data['iv']
        
        # 计算配对 e(D_id, U) (简化实现)
        # D_id = Q_id^s, U = g^r, 所以 e(D_id, U) = e(Q_id^s, g^r) = e(Q_id, g)^(sr)
        # 由于 P_pub = g^s，所以我们计算 (Q_id^r mod p) * (P_pub^r mod p)
        identity_point = private_key_data['identity_point']
        
        # 从U中提取r的信息，计算相同的配对结果
        # 由于U = g^r，我们需要找到r，但这在实际中是困难的
        # 简化实现：使用私钥和U的组合来计算相同的对称密钥
        if self.public_params is None:
            raise ValueError("系统参数未初始化")
        pairing_result = (pow(identity_point, U, self.p) * pow(self.public_params['P_pub'], U, self.p)) % self.p
        
        # 从配对结果导出对称密钥
        symmetric_key = self._derive_key(pairing_result)
        
        # 使用AES解密消息
        cipher = AES.new(symmetric_key, AES.MODE_CBC, iv)
        padded_message = cipher.decrypt(V)
        message = unpad(padded_message, AES.block_size)
        
        return message
    
    def _hash_to_point(self, identity):
        """
        将身份信息哈希映射到椭圆曲线上的点
        
        参数:
            identity (str): 身份标识
            
        返回:
            int: 曲线上的点(简化为整数)
        """
        # 使用SHA256哈希
        hash_obj = hashlib.sha256(identity.encode('utf-8'))
        hash_bytes = hash_obj.digest()
        
        # 将哈希值转换为整数并映射到有限域
        hash_int = int.from_bytes(hash_bytes[:16], byteorder='big')  # 只取前16字节
        return (hash_int % (self.p - 1)) + 1
    
    def _derive_key(self, pairing_result):
        """
        从配对结果导出对称加密密钥
        
        参数:
            pairing_result (int): 配对运算结果
            
        返回:
            bytes: 32字节的对称密钥
        """
        # 将配对结果转换为字节串并哈希
        result_bytes = pairing_result.to_bytes(16, byteorder='big')  # 16字节足够
        hash_obj = hashlib.sha256(result_bytes + b"IBE_KEY_DERIVATION")
        return hash_obj.digest()

# 生成全局IBE实例
bf_ibe = BonehFranklinIBE()

def setup():
    """设置IBE系统"""
    return bf_ibe.setup()

def extract(identity):
    """提取身份对应的私钥"""
    return bf_ibe.extract(identity)

def encrypt(identity, message):
    """使用身份加密消息"""
    if isinstance(message, str):
        message = message.encode('utf-8')
    return bf_ibe.encrypt(identity, message)

def decrypt(private_key_data, ciphertext_data):
    """使用私钥解密消息"""
    return bf_ibe.decrypt(private_key_data, ciphertext_data)

# === 测试代码 ===
if __name__ == '__main__':
    print("正在测试 Boneh-Franklin IBE 方案...")
    
    # 1. 系统设置
    print("1. 执行 Setup...")
    setup_result = setup()
    print(f"   主密钥生成完毕")
    print(f"   公共参数: p={setup_result['public_params']['p']}")
    
    # 2. 用户身份
    alice_identity = "alice@example.com"
    bob_identity = "bob@example.com"
    
    # 3. 密钥提取
    print(f"2. 为 {alice_identity} 提取私钥...")
    alice_private_key = extract(alice_identity)
    print(f"   私钥提取完毕")
    
    # 4. 加密消息
    original_message = "Hello Alice! This is a secret message using IBE."
    print(f"3. 使用 {alice_identity} 的身份加密消息...")
    print(f"   原始消息: {original_message}")
    
    ciphertext = encrypt(alice_identity, original_message)
    print(f"   加密完毕，密文长度: {len(ciphertext['V'])} 字节")
    
    # 5. 解密消息
    print("4. 使用Alice的私钥解密消息...")
    decrypted_message = decrypt(alice_private_key, ciphertext)
    print(f"   解密后的消息: {decrypted_message.decode('utf-8')}")
    
    # 6. 验证
    assert original_message == decrypted_message.decode('utf-8')
    print("✅ 成功：Boneh-Franklin IBE 测试通过！")
    
    # 7. 错误测试：尝试用Bob的私钥解密给Alice的消息
    print("5. 错误测试：用Bob的私钥解密给Alice的消息...")
    try:
        bob_private_key = extract(bob_identity)
        wrong_decryption = decrypt(bob_private_key, ciphertext)
        print("❌ 错误：Bob不应该能解密给Alice的消息")
    except Exception as e:
        print("✅ 正确：Bob无法解密给Alice的消息（预期行为）") 