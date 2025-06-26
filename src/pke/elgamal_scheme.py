# -*- coding: utf-8 -*-

"""
本模块实现了ElGamal公钥加密方案。

ElGamal加密基于离散对数难题，支持语义安全的概率加密。
使用较小的参数以提高性能，适合演示和测试。
"""

import random
import hashlib
from Crypto.Util.number import getPrime, inverse, long_to_bytes, bytes_to_long

class ElGamalKey:
    """ElGamal密钥类"""
    def __init__(self, p=None, g=None, y=None, x=None):
        self.p = p  # 大素数
        self.g = g  # 生成元
        self.y = y  # 公钥 y = g^x mod p
        self.x = x  # 私钥

def generate_keys(key_size=512):
    """
    生成ElGamal密钥对。
    为了提高演示性能，使用较小的密钥长度。

    :param key_size: 密钥长度（比特）
    :return: (private_key, public_key) - ElGamalKey对象
    """
    print(f"正在生成 {key_size} 位 ElGamal 密钥...")
    
    # 生成大素数 p
    p = getPrime(key_size)
    
    # 选择生成元 g (简单选择，实际应用中需要验证)
    g = 2
    while pow(g, (p-1)//2, p) == 1:  # 确保g是生成元
        g += 1
        if g > 100:  # 避免无限循环
            g = random.randint(2, p-1)
            break
    
    # 生成私钥 x
    x = random.randint(2, p-2)
    
    # 计算公钥 y = g^x mod p
    y = pow(g, x, p)
    
    private_key = ElGamalKey(p, g, y, x)
    public_key = ElGamalKey(p, g, y, None)
    
    print(f"密钥生成完成。p={p} (len={p.bit_length()}), g={g}")
    
    return private_key, public_key

def encrypt(public_key, message):
    """
    使用ElGamal公钥加密消息。

    :param public_key: ElGamalKey对象（公钥）
    :param message: 待加密的消息 (bytes)
    :return: 密文元组 (c1, c2)，以bytes形式返回
    """
    p, g, y = public_key.p, public_key.g, public_key.y
    
    # 将消息转换为整数
    m = bytes_to_long(message)
    
    # 如果消息太大，需要分块处理
    if m >= p:
        raise ValueError(f"消息太大，需要分块处理。消息长度: {m.bit_length()}, 模数长度: {p.bit_length()}")
    
    # 选择随机数 k
    k = random.randint(2, p-2)
    
    # 计算密文
    c1 = pow(g, k, p)  # c1 = g^k mod p
    s = pow(y, k, p)   # s = y^k mod p
    c2 = (m * s) % p   # c2 = m * s mod p
    
    # 将整数密文转换为字节
    c1_bytes = long_to_bytes(c1)
    c2_bytes = long_to_bytes(c2)
    
    # 返回密文长度 + 密文内容的格式
    c1_len = len(c1_bytes).to_bytes(4, 'big')
    c2_len = len(c2_bytes).to_bytes(4, 'big')
    
    return c1_len + c1_bytes + c2_len + c2_bytes

def decrypt(private_key, ciphertext):
    """
    使用ElGamal私钥解密消息。

    :param private_key: ElGamalKey对象（私钥）
    :param ciphertext: 密文 (bytes)
    :return: 解密后的明文消息 (bytes)
    """
    p, x = private_key.p, private_key.x
    
    # 解析密文格式
    c1_len = int.from_bytes(ciphertext[:4], 'big')
    c1_bytes = ciphertext[4:4+c1_len]
    c2_len = int.from_bytes(ciphertext[4+c1_len:8+c1_len], 'big')
    c2_bytes = ciphertext[8+c1_len:8+c1_len+c2_len]
    
    # 转换为整数
    c1 = bytes_to_long(c1_bytes)
    c2 = bytes_to_long(c2_bytes)
    
    # 解密
    s = pow(c1, x, p)         # s = c1^x mod p
    s_inv = inverse(s, p)     # s的模逆
    m = (c2 * s_inv) % p      # m = c2 * s^(-1) mod p
    
    # 转换回字节
    try:
        message = long_to_bytes(m)
        return message
    except Exception as e:
        # 如果转换失败，可能是填充问题
        m_bytes = m.to_bytes((m.bit_length() + 7) // 8, 'big')
        return m_bytes

# === 测试代码 ===
if __name__ == '__main__':
    print("正在测试 ElGamal 加密方案（优化版）...")

    # 1. 生成密钥（使用较小参数以提高速度）
    private_key, public_key = generate_keys(key_size=512)  # 使用512位密钥确保能处理消息
    print(f"密钥生成完毕。")

    # 2. 准备明文
    original_message = b"ElGamal test message."
    print(f"原始明文: {original_message.decode('utf-8', errors='ignore')}")

    # 3. 加密
    print("正在加密...")
    try:
        encrypted_message = encrypt(public_key, original_message)
        print(f"加密成功。密文长度: {len(encrypted_message)} 字节")
        print(f"密文 (hex): {encrypted_message.hex()[:128]}...（已截断）")

        # 4. 解密
        print("正在解密...")
        decrypted_message = decrypt(private_key, encrypted_message)
        print(f"解密后的明文: {decrypted_message.decode('utf-8', errors='ignore')}")

        # 5. 验证
        if original_message == decrypted_message:
            print("✅ 成功：解密后的明文与原始明文一致！")
        else:
            print("❌ 错误：解密后的明文与原始明文不一致！")
            print(f"原始: {original_message}")
            print(f"解密: {decrypted_message}")
    
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc() 