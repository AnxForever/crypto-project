# -*- coding: utf-8 -*-

"""
本脚本是PKE性能评测的简化版本，专注于快速获得可用的对比结果。
由于ElGamal方案的性能评测过于耗时，本版本暂时跳过ElGamal，
只对ECC和SM2两种方案进行性能对比。
"""

import time
import os
import pandas as pd
import sys

# 将项目根目录添加到Python路径中
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

# 导入我们自己实现的PKE方案
from src.pke import ecc_scheme, sm2_scheme

# 简化的测试参数
DATA_SIZES = [128, 1024]  # 只测试两种数据大小
NUM_ITERATIONS = 3  # 减少重复次数

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
    print("=== PKE性能评测 (简化版) ===")
    print("注意：由于ElGamal方案评测耗时过长，本次测试暂时跳过ElGamal，")
    print("只对ECC和SM2两种方案进行快速性能对比。")
    print()
    
    all_results = []
    
    # 运行评测
    all_results.extend(benchmark_ecc())
    all_results.extend(benchmark_sm2())

    # 将结果保存到DataFrame中
    df = pd.DataFrame(all_results)
    
    # 确保results目录存在
    if not os.path.exists('results'):
        os.makedirs('results')
        
    # 保存到CSV文件
    output_path = 'results/pke_performance_simple.csv'
    df.to_csv(output_path, index=False)
    
    print(f"\n简化版评测完成！结果已保存到 {output_path}")

    # 打印结果预览
    print("\n--- 性能数据预览 ---")
    print(df.to_string(index=False))
    
    # 生成简单的性能对比分析
    print("\n--- 性能对比分析 ---")
    
    # 密钥生成对比
    key_gen_data = df[df['operation'] == 'key_gen']
    print("密钥生成性能对比:")
    for _, row in key_gen_data.iterrows():
        print(f"  {row['scheme']}: {row['time']:.6f} 秒")
    
    # 加密性能对比 (以128字节数据为例)
    encrypt_128_data = df[(df['operation'] == 'encrypt') & (df['data_size'] == 128)]
    print("\n加密性能对比 (128字节数据):")
    for _, row in encrypt_128_data.iterrows():
        print(f"  {row['scheme']}: {row['time']:.6f} 秒, 密文大小: {row['ciphertext_size']} 字节") 