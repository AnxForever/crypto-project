# -*- coding: utf-8 -*-

"""
PKE方案完整性能评测
对比ECC、ElGamal和SM2三种公钥加密方案的性能
"""

import sys
import os
import time
import pandas as pd

# 添加源代码路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

# 导入各个PKE方案
import pke.ecc_scheme as ecc
import pke.elgamal_scheme as elgamal
import pke.sm2_scheme as sm2

def benchmark_scheme(scheme_name, key_gen_func, encrypt_func, decrypt_func, iterations=3):
    """
    对单个加密方案进行性能评测
    
    :param scheme_name: 方案名称
    :param key_gen_func: 密钥生成函数
    :param encrypt_func: 加密函数
    :param decrypt_func: 解密函数
    :param iterations: 测试迭代次数
    :return: 性能数据列表
    """
    print(f"--- 开始评测 {scheme_name} ---")
    results = []
    
    # 测试数据大小
    test_sizes = [128, 1024]  # 字节
    
    try:
        # 1. 密钥生成性能测试
        print(f"正在测试 {scheme_name} 密钥生成...")
        key_gen_times = []
        
        for i in range(iterations):
            start_time = time.time()
            if scheme_name == "ElGamal":
                private_key, public_key = key_gen_func(key_size=512)  # ElGamal使用512位
            else:
                private_key, public_key = key_gen_func()
            end_time = time.time()
            key_gen_times.append(end_time - start_time)
        
        avg_key_gen_time = sum(key_gen_times) / len(key_gen_times)
        results.append({
            'scheme': scheme_name,
            'data_size': 0,
            'operation': 'key_gen',
            'time': avg_key_gen_time,
            'ciphertext_size': 0
        })
        print(f"密钥生成平均耗时: {avg_key_gen_time:.6f} 秒")
        
        # 2. 加密/解密性能测试
        for data_size in test_sizes:
            print(f"正在测试 {scheme_name} {data_size}B 数据处理...")
            
            # 准备测试数据
            test_data = b'A' * data_size
            
            # 调整消息大小以适应ElGamal
            if scheme_name == "ElGamal" and data_size > 50:
                test_data = b'A' * 50  # ElGamal限制消息大小
                print(f"  注意: ElGamal消息大小调整为50字节")
            
            encrypt_times = []
            decrypt_times = []
            ciphertext_sizes = []
            
            for i in range(iterations):
                # 加密测试
                start_time = time.time()
                ciphertext = encrypt_func(public_key, test_data)
                encrypt_time = time.time() - start_time
                encrypt_times.append(encrypt_time)
                ciphertext_sizes.append(len(ciphertext))
                
                # 解密测试
                start_time = time.time()
                decrypted = decrypt_func(private_key, ciphertext)
                decrypt_time = time.time() - start_time
                decrypt_times.append(decrypt_time)
                
                # 验证正确性
                if decrypted != test_data:
                    print(f"  警告: {scheme_name} 解密结果不正确")
            
            # 记录加密性能
            avg_encrypt_time = sum(encrypt_times) / len(encrypt_times)
            avg_ciphertext_size = sum(ciphertext_sizes) / len(ciphertext_sizes)
            results.append({
                'scheme': scheme_name,
                'data_size': data_size,
                'operation': 'encrypt',
                'time': avg_encrypt_time,
                'ciphertext_size': int(avg_ciphertext_size)
            })
            
            # 记录解密性能
            avg_decrypt_time = sum(decrypt_times) / len(decrypt_times)
            results.append({
                'scheme': scheme_name,
                'data_size': data_size,
                'operation': 'decrypt',
                'time': avg_decrypt_time,
                'ciphertext_size': int(avg_ciphertext_size)
            })
            
            print(f"数据大小: {data_size}B, 加密耗时: {avg_encrypt_time:.6f}s, "
                  f"解密耗时: {avg_decrypt_time:.6f}s, 密文大小: {int(avg_ciphertext_size)}B")
    
    except Exception as e:
        print(f"❌ {scheme_name} 评测失败: {e}")
        import traceback
        traceback.print_exc()
    
    return results

def main():
    """主函数，执行完整的PKE性能评测"""
    print("=== PKE方案完整性能评测 ===")
    print("对比 ECC、ElGamal、SM2 三种公钥加密方案")
    
    # 确保结果目录存在
    os.makedirs('results', exist_ok=True)
    
    all_results = []
    
    # 评测ECC (ECIES)
    ecc_results = benchmark_scheme(
        "ECC", 
        ecc.generate_keys, 
        ecc.encrypt, 
        ecc.decrypt,
        iterations=3
    )
    all_results.extend(ecc_results)
    
    # 评测ElGamal
    elgamal_results = benchmark_scheme(
        "ElGamal", 
        elgamal.generate_keys, 
        elgamal.encrypt, 
        elgamal.decrypt,
        iterations=2  # ElGamal较慢，减少迭代次数
    )
    all_results.extend(elgamal_results)
    
    # 评测SM2
    sm2_results = benchmark_scheme(
        "SM2", 
        sm2.generate_keys, 
        sm2.encrypt, 
        sm2.decrypt,
        iterations=3
    )
    all_results.extend(sm2_results)
    
    # 保存结果
    if all_results:
        df = pd.DataFrame(all_results)
        df.to_csv('results/pke_performance_complete.csv', index=False)
        
        print("\n完整评测完成！结果已保存到 results/pke_performance_complete.csv")
        
        # 显示结果预览
        print("\n--- 性能数据预览 ---")
        print(df.to_string(index=False))
        
        # 简单分析
        print("\n--- 性能对比分析 ---")
        
        # 密钥生成对比
        key_gen_data = df[df['operation'] == 'key_gen']
        print("密钥生成性能对比:")
        for _, row in key_gen_data.iterrows():
            print(f"  {row['scheme']}: {row['time']:.6f} 秒")
        
        # 加密性能对比（128字节）
        encrypt_128_data = df[(df['operation'] == 'encrypt') & (df['data_size'] == 128)]
        print("\n加密性能对比 (128字节数据):")
        for _, row in encrypt_128_data.iterrows():
            print(f"  {row['scheme']}: {row['time']:.6f} 秒, 密文大小: {row['ciphertext_size']} 字节")
        
        # 整体性能排名
        print("\n综合性能评分 (越低越好):")
        schemes = df['scheme'].unique()
        for scheme in schemes:
            scheme_data = df[df['scheme'] == scheme]
            key_gen_time = scheme_data[scheme_data['operation'] == 'key_gen']['time'].values[0]
            avg_encrypt_time = scheme_data[scheme_data['operation'] == 'encrypt']['time'].mean()
            avg_decrypt_time = scheme_data[scheme_data['operation'] == 'decrypt']['time'].mean()
            
            # 综合评分（密钥生成权重较低）
            score = key_gen_time * 0.1 + avg_encrypt_time * 0.45 + avg_decrypt_time * 0.45
            print(f"  {scheme}: {score:.6f}")
    else:
        print("❌ 没有成功获取任何评测结果")

if __name__ == '__main__':
    main() 