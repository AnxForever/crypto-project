# -*- coding: utf-8 -*-

"""
本脚本用于对PKE（公钥加密）的三种方案进行性能评测。
评测维度包括：密钥生成时间、加密时间、解密时间、密文大小。
"""

import time
import os
import pandas as pd
import sys

# 将项目根目录添加到Python路径中，这样才能找到src模块
# D:\Mima\practice\crypto_project
# 我们需要的是 D:\Mima\practice
# 所以需要向上两级
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

# 导入我们自己实现的三个PKE方案
from src.pke import ecc_scheme, elgamal_scheme, sm2_scheme

# 定义要测试的数据大小 (bytes)
DATA_SIZES = [16, 128, 1024, 1024 * 10]
# ElGamal特殊数据大小（受密钥长度限制）
ELGAMAL_DATA_SIZES = [16, 32]  # ElGamal使用512位密钥，只能处理小消息
# 定义每个测试的重复次数，以获得更稳定的平均值
NUM_ITERATIONS = 10

def benchmark_elgamal():
    """评测ElGamal方案的性能"""
    print("--- 开始评测 ElGamal ---")
    results = []

    # 1. 评测密钥生成
    # ElGamal密钥生成非常耗时，我们减少迭代次数以避免长时间等待
    key_gen_iterations = 1
    start_time = time.perf_counter()
    for _ in range(key_gen_iterations):
        priv_key, pub_key = elgamal_scheme.generate_keys()
    end_time = time.perf_counter()
    key_gen_time = (end_time - start_time) / key_gen_iterations
    print(f"密钥生成平均耗时: {key_gen_time:.6f} 秒")
    results.append({'scheme': 'ElGamal', 'data_size': 0, 'operation': 'key_gen', 'time': key_gen_time, 'ciphertext_size': 0})

    # 生成一对密钥用于后续的加解密测试
    priv_key, pub_key = elgamal_scheme.generate_keys()

    # 2. 评测不同数据大小的加解密（ElGamal使用受限的数据大小）
    for size in ELGAMAL_DATA_SIZES:
        message = os.urandom(size)
        
        # 加密评测
        start_time = time.perf_counter()
        for _ in range(NUM_ITERATIONS):
            ciphertext = elgamal_scheme.encrypt(pub_key, message)
        end_time = time.perf_counter()
        encrypt_time = (end_time - start_time) / NUM_ITERATIONS
        
        # 解密评测
        start_time = time.perf_counter()
        for _ in range(NUM_ITERATIONS):
            elgamal_scheme.decrypt(priv_key, ciphertext)
        end_time = time.perf_counter()
        decrypt_time = (end_time - start_time) / NUM_ITERATIONS

        # 记录密文大小 (ElGamal密文是bytes格式)
        ciphertext_size = len(ciphertext)
        
        print(f"数据大小: {size}B, 加密耗时: {encrypt_time:.6f}s, 解密耗时: {decrypt_time:.6f}s, 密文大小: {ciphertext_size}B")
        results.append({'scheme': 'ElGamal', 'data_size': size, 'operation': 'encrypt', 'time': encrypt_time, 'ciphertext_size': ciphertext_size})
        results.append({'scheme': 'ElGamal', 'data_size': size, 'operation': 'decrypt', 'time': decrypt_time, 'ciphertext_size': ciphertext_size})
        
    return results

def benchmark_ecc():
    """评测ECC (ECIES)方案的性能"""
    print("--- 开始评测 ECC (ECIES) ---")
    results = []

    # 1. 评测密钥生成
    start_time = time.perf_counter()
    for _ in range(NUM_ITERATIONS):
        priv_key_hex, pub_key_hex = ecc_scheme.generate_keys()
    end_time = time.perf_counter()
    key_gen_time = (end_time - start_time) / NUM_ITERATIONS
    print(f"密钥生成平均耗时: {key_gen_time:.6f} 秒")
    results.append({'scheme': 'ECC', 'data_size': 0, 'operation': 'key_gen', 'time': key_gen_time, 'ciphertext_size': 0})

    priv_key_hex, pub_key_hex = ecc_scheme.generate_keys()

    # 2. 评测不同数据大小的加解密
    for size in DATA_SIZES:
        message = os.urandom(size)
        
        start_time = time.perf_counter()
        for _ in range(NUM_ITERATIONS):
            ciphertext = ecc_scheme.encrypt(pub_key_hex, message)
        end_time = time.perf_counter()
        encrypt_time = (end_time - start_time) / NUM_ITERATIONS
        
        start_time = time.perf_counter()
        for _ in range(NUM_ITERATIONS):
            ecc_scheme.decrypt(priv_key_hex, ciphertext)
        end_time = time.perf_counter()
        decrypt_time = (end_time - start_time) / NUM_ITERATIONS
        
        ciphertext_size = len(ciphertext)
        
        print(f"数据大小: {size}B, 加密耗时: {encrypt_time:.6f}s, 解密耗时: {decrypt_time:.6f}s, 密文大小: {ciphertext_size}B")
        results.append({'scheme': 'ECC', 'data_size': size, 'operation': 'encrypt', 'time': encrypt_time, 'ciphertext_size': ciphertext_size})
        results.append({'scheme': 'ECC', 'data_size': size, 'operation': 'decrypt', 'time': decrypt_time, 'ciphertext_size': ciphertext_size})

    return results

def benchmark_sm2():
    """评测SM2方案的性能"""
    print("--- 开始评测 SM2 ---")
    results = []

    # 1. 评测密钥生成
    start_time = time.perf_counter()
    for _ in range(NUM_ITERATIONS):
        priv_key_hex, pub_key_hex = sm2_scheme.generate_keys()
    end_time = time.perf_counter()
    key_gen_time = (end_time - start_time) / NUM_ITERATIONS
    print(f"密钥生成平均耗时: {key_gen_time:.6f} 秒")
    results.append({'scheme': 'SM2', 'data_size': 0, 'operation': 'key_gen', 'time': key_gen_time, 'ciphertext_size': 0})
    
    priv_key_hex, pub_key_hex = sm2_scheme.generate_keys()
    
    # 2. 评测不同数据大小的加解密
    for size in DATA_SIZES:
        message = os.urandom(size)
        
        start_time = time.perf_counter()
        for _ in range(NUM_ITERATIONS):
            ciphertext = sm2_scheme.encrypt(pub_key_hex, message)
        end_time = time.perf_counter()
        encrypt_time = (end_time - start_time) / NUM_ITERATIONS
        
        start_time = time.perf_counter()
        for _ in range(NUM_ITERATIONS):
            sm2_scheme.decrypt(priv_key_hex, ciphertext)
        end_time = time.perf_counter()
        decrypt_time = (end_time - start_time) / NUM_ITERATIONS
        
        ciphertext_size = len(ciphertext)
        
        print(f"数据大小: {size}B, 加密耗时: {encrypt_time:.6f}s, 解密耗时: {decrypt_time:.6f}s, 密文大小: {ciphertext_size}B")
        results.append({'scheme': 'SM2', 'data_size': size, 'operation': 'encrypt', 'time': encrypt_time, 'ciphertext_size': ciphertext_size})
        results.append({'scheme': 'SM2', 'data_size': size, 'operation': 'decrypt', 'time': decrypt_time, 'ciphertext_size': ciphertext_size})

    return results


if __name__ == '__main__':
    all_results = []
    
    # 运行所有评测
    all_results.extend(benchmark_elgamal())
    all_results.extend(benchmark_ecc())
    all_results.extend(benchmark_sm2())

    # 将结果保存到DataFrame中
    df = pd.DataFrame(all_results)
    
    # 确保results目录存在
    if not os.path.exists('results'):
        os.makedirs('results')
        
    # 保存到CSV文件
    output_path = 'results/pke_performance.csv'
    df.to_csv(output_path, index=False)
    
    print(f"\n评测完成！所有结果已保存到 {output_path}")

    # 打印部分结果看看
    print("\n--- 性能数据预览 (前5行) ---")
    print(df.head())
    print("\n--- 性能数据预览 (后5行) ---")
    print(df.tail()) 