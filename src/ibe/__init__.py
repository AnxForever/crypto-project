# -*- coding: utf-8 -*-

"""
Identity-Based Encryption (IBE) 算法包

这个包实现了三种主要的IBE方案：
1. Boneh-Franklin IBE (BF-IBE) - 最早的实用IBE方案
2. Boneh-Boyen IBE (BB-IBE) - 标准模型下的安全IBE方案
3. Sakai-Kasahara IBE (SK-IBE) - 高效的IBE方案

每个方案都提供统一的接口：
- setup(): 系统设置，生成主密钥
- extract(identity): 身份密钥提取
- encrypt(identity, message): 基于身份的加密
- decrypt(private_key, ciphertext): 解密

使用示例：
    from src.ibe import boneh_franklin_scheme as bf
    
    # 设置系统
    setup_result = bf.setup()
    
    # 为用户生成私钥
    alice_key = bf.extract("alice@example.com")
    
    # 加密消息
    ciphertext = bf.encrypt("alice@example.com", "Hello Alice!")
    
    # 解密消息
    plaintext = bf.decrypt(alice_key, ciphertext)
"""

# 导入三种IBE方案
from . import boneh_franklin_scheme_simple as boneh_franklin
from . import boneh_boyen_scheme as boneh_boyen
from . import sakai_kasahara_scheme as sakai_kasahara

# 定义支持的IBE方案
SUPPORTED_SCHEMES = {
    'boneh_franklin': boneh_franklin,
    'bf': boneh_franklin,  # 简写
    'boneh_boyen': boneh_boyen,
    'bb': boneh_boyen,  # 简写
    'sakai_kasahara': sakai_kasahara,
    'sk': sakai_kasahara  # 简写
}

def get_scheme(scheme_name):
    """
    获取指定的IBE方案
    
    参数:
        scheme_name (str): 方案名称，支持：
            - 'boneh_franklin' 或 'bf'
            - 'boneh_boyen' 或 'bb' 
            - 'sakai_kasahara' 或 'sk'
    
    返回:
        module: IBE方案模块
    """
    scheme_name = scheme_name.lower()
    if scheme_name not in SUPPORTED_SCHEMES:
        raise ValueError(f"不支持的IBE方案: {scheme_name}. 支持的方案: {list(SUPPORTED_SCHEMES.keys())}")
    
    return SUPPORTED_SCHEMES[scheme_name]

def list_schemes():
    """
    列出所有支持的IBE方案
    
    返回:
        list: 支持的方案列表
    """
    return list(SUPPORTED_SCHEMES.keys())

# 为了向后兼容，直接导出常用方案
bf_ibe = boneh_franklin
bb_ibe = boneh_boyen
sk_ibe = sakai_kasahara

__all__ = [
    'boneh_franklin',
    'boneh_boyen', 
    'sakai_kasahara',
    'bf_ibe',
    'bb_ibe',
    'sk_ibe',
    'get_scheme',
    'list_schemes',
    'SUPPORTED_SCHEMES'
] 