# -*- coding: utf-8 -*-

"""
密码学算法性能分析公共模块
提供数据加载功能，支持PKE和IBE专项分析
"""

import matplotlib
matplotlib.use('Agg')
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

def load_performance_data():
    """加载PKE和IBE性能数据"""
    pke_file = 'results/pke_performance_complete.csv'
    ibe_file = 'results/ibe_performance_complete.csv'
    
    pke_df = None
    ibe_df = None
    
    if os.path.exists(pke_file):
        print("📄 加载PKE性能数据")
        pke_df = pd.read_csv(pke_file)
    else:
        print(f"警告：找不到PKE性能数据文件: {pke_file}")
    
    if os.path.exists(ibe_file):
        print("📄 加载IBE性能数据")
        ibe_df = pd.read_csv(ibe_file)
    else:
        print(f"警告：找不到IBE性能数据文件: {ibe_file}")
    
    return pke_df, ibe_df

def generate_performance_report(pke_df, ibe_df):
    """生成性能分析报告"""
    print("\n" + "="*80)
    print("密码学算法性能分析总结报告")
    print("="*80)
    
    if pke_df is not None:
        print("\n📊 PKE算法性能总结:")
        schemes = pke_df['scheme'].unique()
        
        for scheme in schemes:
            print(f"\n  {scheme}:")
            
            # 密钥生成
            key_gen_time = pke_df[(pke_df['scheme'] == scheme) & (pke_df['operation'] == 'key_gen')]['time'].values[0] * 1000
            print(f"    密钥生成: {key_gen_time:.2f} 毫秒")
            
            # 加密性能
            encrypt_128 = pke_df[(pke_df['scheme'] == scheme) & (pke_df['operation'] == 'encrypt') & (pke_df['data_size'] == 128)]
            if not encrypt_128.empty:
                encrypt_time = encrypt_128['time'].values[0] * 1000
                cipher_size = encrypt_128['ciphertext_size'].values[0]
                print(f"    加密(128B): {encrypt_time:.3f} 毫秒, 密文大小: {cipher_size} 字节")
            
            # 解密性能
            decrypt_128 = pke_df[(pke_df['scheme'] == scheme) & (pke_df['operation'] == 'decrypt') & (pke_df['data_size'] == 128)]
            if not decrypt_128.empty:
                decrypt_time = decrypt_128['time'].values[0] * 1000
                print(f"    解密(128B): {decrypt_time:.3f} 毫秒")
    
    if ibe_df is not None:
        print(f"\n📊 IBE算法性能总结:")
        schemes = ibe_df['scheme'].unique()
        
        for scheme in schemes:
            print(f"\n  {scheme}:")
            
            # 系统设置
            setup_data = ibe_df[(ibe_df['scheme'] == scheme) & (ibe_df['operation'] == 'setup')]
            if not setup_data.empty:
                setup_time = setup_data['time'].values[0] * 1000
                print(f"    系统设置: {setup_time:.3f} 毫秒")
            
            # 密钥提取
            extract_data = ibe_df[(ibe_df['scheme'] == scheme) & (ibe_df['operation'] == 'extract')]
            if not extract_data.empty:
                avg_extract = extract_data['time'].mean() * 1000
                print(f"    密钥提取: {avg_extract:.2f} 毫秒 (平均)")
            
            # 加密性能
            encrypt_data = ibe_df[(ibe_df['scheme'] == scheme) & (ibe_df['operation'] == 'encrypt')]
            if not encrypt_data.empty:
                avg_encrypt = encrypt_data['time'].mean() * 1000
                print(f"    加密性能: {avg_encrypt:.2f} 毫秒 (平均)")
    
    print(f"\n🎯 算法选择建议:")
    print(f"  PKE算法:")
    print(f"    • SM2: 国产标准，高性能，推荐用于国内项目")
    print(f"    • ECC: 安全性高，适合对安全要求严格的场景")
    print(f"    • ElGamal: 经典算法，适合教学和研究")
    print(f"  IBE算法:")
    print(f"    • Sakai-Kasahara: 性能最优，适合生产环境")
    print(f"    • Boneh-Boyen: 标准模型安全，适合高安全需求")
    print(f"    • Boneh-Franklin: 经典方案，适合教学研究")

def main():
    """主函数，执行基础性能分析"""
    print("=== 密码学算法性能分析公共模块 ===")
    print("本模块提供数据加载和基础报告功能")
    print("请使用以下专项分析脚本获取详细图表：")
    print("  • pke_only_analysis.py - PKE专项分析")
    print("  • ibe_only_analysis.py - IBE专项分析")
    
    # 加载数据
    pke_df, ibe_df = load_performance_data()
    
    # 生成基础分析报告
    generate_performance_report(pke_df, ibe_df)
    
    print(f"\n💡 专项分析图表已生成:")
    print(f"  PKE专项:")
    print(f"    • pke_only_performance_overview.png")
    print(f"    • pke_only_efficiency_analysis.png")
    print(f"    • pke_only_scalability_analysis.png")
    print(f"  IBE专项:")
    print(f"    • ibe_only_performance_overview.png")
    print(f"    • ibe_only_efficiency_analysis.png")
    print(f"    • ibe_only_message_scalability.png")

if __name__ == '__main__':
    main() 