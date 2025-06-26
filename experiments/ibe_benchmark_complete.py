# -*- coding: utf-8 -*-

"""
IBE方案完整性能评测
对比Boneh-Franklin、Boneh-Boyen、Sakai-Kasahara三种基于身份加密方案的性能
"""

import sys
import os
import time
import pandas as pd

# 添加源代码路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

# 导入各个IBE方案
from ibe import boneh_franklin_scheme, boneh_boyen_scheme, sakai_kasahara_scheme

def benchmark_ibe_scheme(scheme_name, scheme_module, iterations=3):
    """
    对单个IBE方案进行性能评测
    
    :param scheme_name: 方案名称
    :param scheme_module: IBE方案模块
    :param iterations: 测试迭代次数
    :return: 性能数据列表
    """
    print(f"--- 开始评测 {scheme_name} ---")
    results = []
    
    # 测试消息大小
    test_messages = [
        ("短消息", "Hello IBE!"),
        ("中等消息", "This is a medium length message for IBE performance testing. " * 2),
        ("长消息", "This is a longer message for comprehensive IBE performance evaluation. " * 5)
    ]
    
    # 测试身份
    test_identities = [
        "alice@company.com",
        "bob@department.org", 
        "charlie@university.edu"
    ]
    
    try:
        # 1. 系统设置性能测试
        print(f"正在测试 {scheme_name} 系统设置...")
        setup_times = []
        
        for i in range(iterations):
            start_time = time.time()
            setup_result = scheme_module.setup()
            end_time = time.time()
            setup_times.append(end_time - start_time)
        
        avg_setup_time = sum(setup_times) / len(setup_times)
        results.append({
            'scheme': scheme_name,
            'operation': 'setup',
            'message_type': 'system',
            'time': avg_setup_time,
            'data_size': 0
        })
        print(f"系统设置平均耗时: {avg_setup_time:.6f} 秒")
        
        # 2. 密钥提取性能测试
        print(f"正在测试 {scheme_name} 密钥提取...")
        for identity in test_identities:
            extract_times = []
            
            for i in range(iterations):
                start_time = time.time()
                private_key = scheme_module.extract(identity)
                end_time = time.time()
                extract_times.append(end_time - start_time)
            
            avg_extract_time = sum(extract_times) / len(extract_times)
            results.append({
                'scheme': scheme_name,
                'operation': 'extract',
                'message_type': 'key_extract',
                'time': avg_extract_time,
                'data_size': len(identity.encode('utf-8'))
            })
        
        avg_extract_time = sum([r['time'] for r in results if r['operation'] == 'extract']) / len(test_identities)
        print(f"密钥提取平均耗时: {avg_extract_time:.6f} 秒")
        
        # 3. 加密/解密性能测试
        test_identity = test_identities[0]  # 使用第一个身份进行加密解密测试
        private_key = scheme_module.extract(test_identity)
        
        for msg_type, message in test_messages:
            print(f"正在测试 {scheme_name} {msg_type}处理...")
            
            encrypt_times = []
            decrypt_times = []
            message_size = len(message.encode('utf-8'))
            
            for i in range(iterations):
                # 加密测试
                start_time = time.time()
                ciphertext = scheme_module.encrypt(test_identity, message)
                encrypt_time = time.time() - start_time
                encrypt_times.append(encrypt_time)
                
                # 解密测试
                start_time = time.time()
                decrypted = scheme_module.decrypt(private_key, ciphertext)
                decrypt_time = time.time() - start_time
                decrypt_times.append(decrypt_time)
                
                # 验证正确性
                if decrypted.decode('utf-8') != message:
                    print(f"  警告: {scheme_name} 解密结果不正确")
            
            # 记录加密性能
            avg_encrypt_time = sum(encrypt_times) / len(encrypt_times)
            results.append({
                'scheme': scheme_name,
                'operation': 'encrypt',
                'message_type': msg_type,
                'time': avg_encrypt_time,
                'data_size': message_size
            })
            
            # 记录解密性能
            avg_decrypt_time = sum(decrypt_times) / len(decrypt_times)
            results.append({
                'scheme': scheme_name,
                'operation': 'decrypt',
                'message_type': msg_type,
                'time': avg_decrypt_time,
                'data_size': message_size
            })
            
            print(f"消息类型: {msg_type}, 大小: {message_size}B, "
                  f"加密耗时: {avg_encrypt_time:.6f}s, 解密耗时: {avg_decrypt_time:.6f}s")
    
    except Exception as e:
        print(f"❌ {scheme_name} 评测失败: {e}")
        import traceback
        traceback.print_exc()
    
    return results

def main():
    """主函数，执行完整的IBE性能评测"""
    print("=== IBE方案完整性能评测 ===")
    print("对比 Boneh-Franklin、Boneh-Boyen、Sakai-Kasahara 三种基于身份加密方案")
    
    # 确保结果目录存在
    results_dir = os.path.join(os.path.dirname(__file__), 'results')
    os.makedirs(results_dir, exist_ok=True)
    
    all_results = []
    
    # 评测Boneh-Franklin IBE
    bf_results = benchmark_ibe_scheme(
        "Boneh-Franklin", 
        boneh_franklin_scheme,
        iterations=3
    )
    all_results.extend(bf_results)
    
    # 评测Boneh-Boyen IBE
    bb_results = benchmark_ibe_scheme(
        "Boneh-Boyen", 
        boneh_boyen_scheme,
        iterations=3
    )
    all_results.extend(bb_results)
    
    # 评测Sakai-Kasahara IBE
    sk_results = benchmark_ibe_scheme(
        "Sakai-Kasahara", 
        sakai_kasahara_scheme,
        iterations=3
    )
    all_results.extend(sk_results)
    
    # 保存结果
    if all_results:
        df = pd.DataFrame(all_results)
        output_file = os.path.join(results_dir, 'ibe_performance_complete.csv')
        df.to_csv(output_file, index=False)
        
        print(f"\n完整评测完成！结果已保存到 {output_file}")
        
        # 显示结果预览
        print("\n--- IBE性能数据预览 ---")
        print(df.to_string(index=False))
        
        # 简单分析
        print("\n--- IBE性能对比分析 ---")
        
        # 系统设置对比
        setup_data = df[df['operation'] == 'setup']
        print("系统设置性能对比:")
        for _, row in setup_data.iterrows():
            print(f"  {row['scheme']}: {row['time']:.6f} 秒")
        
        # 密钥提取对比
        extract_data = df[df['operation'] == 'extract']
        print("\n密钥提取性能对比:")
        schemes = extract_data['scheme'].unique()
        for scheme in schemes:
            scheme_data = extract_data[extract_data['scheme'] == scheme]
            avg_time = scheme_data['time'].mean()
            print(f"  {scheme}: {avg_time:.6f} 秒")
        
        # 加密性能对比（短消息）
        encrypt_short_data = df[(df['operation'] == 'encrypt') & (df['message_type'] == '短消息')]
        print("\n加密性能对比 (短消息):")
        for _, row in encrypt_short_data.iterrows():
            print(f"  {row['scheme']}: {row['time']:.6f} 秒")
        
        # 整体性能排名
        print("\nIBE综合性能评分 (越低越好):")
        schemes = df['scheme'].unique()
        for scheme in schemes:
            scheme_data = df[df['scheme'] == scheme]
            setup_time = scheme_data[scheme_data['operation'] == 'setup']['time'].values[0]
            avg_extract_time = scheme_data[scheme_data['operation'] == 'extract']['time'].mean()
            avg_encrypt_time = scheme_data[scheme_data['operation'] == 'encrypt']['time'].mean()
            avg_decrypt_time = scheme_data[scheme_data['operation'] == 'decrypt']['time'].mean()
            
            # 综合评分（越低越好）
            # 权重：系统设置10%，密钥提取20%，加密35%，解密35%
            score = setup_time * 0.1 + avg_extract_time * 0.2 + avg_encrypt_time * 0.35 + avg_decrypt_time * 0.35
            print(f"  {scheme}: {score:.6f} 秒")
        
        print(f"\n🎉 IBE性能评测完成！")
        print(f"数据文件: {output_file}")
        print(f"下一步可以运行 ibe_performance_analysis.py 生成可视化图表")
    
    else:
        print("❌ 没有收集到任何性能数据")

if __name__ == '__main__':
    main() 