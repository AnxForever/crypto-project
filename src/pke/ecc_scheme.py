# -*- coding: utf-8 -*-

"""
本模块实现了基于椭圆曲线的集成加密方案（ECIES）。

ECIES (Elliptic Curve Integrated Encryption Scheme) 是一种混合加密方案，
它结合了ECC的非对称加密和对称加密算法（如AES）的优点。

- 非对称部分：使用接收方的ECC公钥和一个临时的ECC密钥对，通过椭圆曲线迪菲-赫尔曼密钥交换（ECDH）生成一个共享密钥。
- 对称部分：使用上一步生成的共享密钥，通过一个对称加密算法（如AES-GCM）来加密实际的消息。

这种方法既保证了安全性（只有私钥持有者能解密），又保证了效率（大块数据通过快速的对称算法加密）。

注意：pycryptodome库本身不提供直接的ECIES实现，我们将使用一个专门的库`eciespy`来完成，它底层依赖于`pycryptodome`。
我们已经安装了 `eciespy` 库。
"""
import ecies
import binascii

def generate_keys():
    """
    生成一对ECC密钥（公钥和私钥）。
    使用的是secp256k1曲线，比特币用的就是这个。

    :return: 一个元组 (private_key_hex, public_key_hex)，均为十六进制字符串。
    """
    # eciespy内部使用pycryptodome来生成密钥
    private_key = ecies.utils.generate_eth_key()
    private_key_hex = private_key.to_hex()
    public_key_hex = private_key.public_key.to_hex()
    return private_key_hex, public_key_hex

def encrypt(public_key_hex, message):
    """
    使用ECC公钥加密消息。

    :param public_key_hex: 接收方的公钥（十六进制字符串）。
    :param message: 需要加密的明文消息 (bytes)。
    :return: 加密后的密文 (bytes)。
    """
    # 移除'0x'前缀（如果存在）
    if public_key_hex.startswith('0x'):
        public_key_hex = public_key_hex[2:]
    
    # 确保hex字符串是偶数长度
    if len(public_key_hex) % 2 != 0:
        public_key_hex = '0' + public_key_hex
        
    public_key_bytes = binascii.unhexlify(public_key_hex)
    ciphertext = ecies.encrypt(public_key_bytes, message)
    return ciphertext

def decrypt(private_key_hex, ciphertext):
    """
    使用ECC私钥解密消息。

    :param private_key_hex: 接收方的私钥（十六进制字符串）。
    :param ciphertext: 需要解密的密文 (bytes)。
    :return: 解密后的明文消息 (bytes)。
    """
    # 移除'0x'前缀（如果存在）
    if private_key_hex.startswith('0x'):
        private_key_hex = private_key_hex[2:]

    # 确保hex字符串是偶数长度
    if len(private_key_hex) % 2 != 0:
        private_key_hex = '0' + private_key_hex

    private_key_bytes = binascii.unhexlify(private_key_hex)
    decrypted_message = ecies.decrypt(private_key_bytes, ciphertext)
    return decrypted_message

# === 测试代码 ===
if __name__ == '__main__':
    print("正在测试 ECIES (ECC) 加密方案...")

    # 1. 生成密钥
    priv_key_hex, pub_key_hex = generate_keys()
    print(f"密钥生成完毕。")
    print(f"私钥 (hex): {priv_key_hex}")
    print(f"公钥 (hex): {pub_key_hex}")

    # 2. 准备明文
    original_message = b"This is a much longer secret message for ECIES, which can handle large data!"
    print(f"原始明文: {original_message.decode()}")

    # 3. 加密
    encrypted_message = encrypt(pub_key_hex, original_message)
    print(f"加密后的密文 (hex): {encrypted_message.hex()}")

    # 4. 解密
    decrypted_message = decrypt(priv_key_hex, encrypted_message)
    print(f"解密后的明文: {decrypted_message.decode()}")

    # 5. 验证
    assert original_message == decrypted_message
    print("成功：解密后的明文与原始明文一致！") 