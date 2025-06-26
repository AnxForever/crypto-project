from gmssl.sm2 import CryptSM2
import os

# 测试方法1：尝试查看CryptSM2的构造函数需要什么参数
print("测试gmssl的SM2库...")

try:
    # 生成一个私钥
    private_key = os.urandom(32)
    private_key_hex = private_key.hex()
    
    print("私钥hex:", private_key_hex)
    
    # 创建一个虚拟的公钥（128个字符）
    dummy_public_key = "00" * 128
    
    # 创建SM2对象
    sm2 = CryptSM2(private_key_hex, dummy_public_key)
    print("SM2对象创建成功!")
    
    # 测试基本功能 - 先看看对象内部的信息
    print("私钥属性:", hasattr(sm2, 'private_key'))
    print("公钥属性:", hasattr(sm2, 'public_key'))
    
    if hasattr(sm2, 'private_key'):
        print("对象中的私钥:", sm2.private_key if isinstance(sm2.private_key, str) else sm2.private_key.hex())
    
    if hasattr(sm2, 'public_key'):
        print("对象中的公钥:", sm2.public_key if isinstance(sm2.public_key, str) else sm2.public_key.hex())
    
    # 尝试加密一个简单的消息
    print("\n测试加密功能...")
    message = b"Hello SM2!"
    print("原始消息:", message)
    
    ciphertext = sm2.encrypt(message)
    print("加密成功! 密文长度:", len(ciphertext))
    
    # 尝试解密
    print("测试解密功能...")
    decrypted = sm2.decrypt(ciphertext)
    print("解密成功! 解密结果:", decrypted)
    print("解密正确?", message == decrypted)
    
except Exception as e:
    print(f"错误: {e}")
    import traceback
    traceback.print_exc() 