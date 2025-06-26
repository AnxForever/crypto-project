# -*- coding: utf-8 -*-

"""
IBE方案性能分析和可视化脚本
生成多种图表展示Boneh-Franklin、Boneh-Boyen、Sakai-Kasahara的性能对比
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

def load_ibe_performance_data():
    """加载IBE性能评测数据"""
    data_file = 'results/ibe_performance_complete.csv'
    
    if os.path.exists(data_file):
        print("📄 加载IBE性能数据")
        df = pd.read_csv(data_file)
        return df
    else:
        print(f"错误：找不到IBE性能数据文件: {data_file}")
        return None

def create_ibe_setup_comparison(df):
    """创建IBE系统设置性能对比图"""
    setup_data = df[df['operation'] == 'setup']
    
    plt.figure(figsize=(10, 6))
    schemes = setup_data['scheme'].values
    times = setup_data['time'].values * 1000  # 转换为毫秒
    
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1']
    bars = plt.bar(schemes, times, color=colors, alpha=0.8)
    
    plt.title('IBE方案系统设置性能对比', fontsize=16, fontweight='bold')
    plt.ylabel('时间 (毫秒)', fontsize=12)
    plt.xlabel('IBE方案', fontsize=12)
    
    # 添加数值标签
    for bar, time in zip(bars, times):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(times)*0.01,
                f'{time:.3f}ms', ha='center', va='bottom', fontsize=10)
    
    plt.tight_layout()
    plt.savefig('results/ibe_setup_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✅ IBE系统设置对比图已保存: results/ibe_setup_comparison.png")

def create_ibe_key_extraction_comparison(df):
    """创建IBE密钥提取性能对比图"""
    extract_data = df[df['operation'] == 'extract']
    
    # 计算每个方案的平均密钥提取时间
    schemes = extract_data['scheme'].unique()
    avg_times = []
    
    for scheme in schemes:
        scheme_data = extract_data[extract_data['scheme'] == scheme]
        avg_time = scheme_data['time'].mean() * 1000  # 转换为毫秒
        avg_times.append(avg_time)
    
    plt.figure(figsize=(10, 6))
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1']
    bars = plt.bar(schemes, avg_times, color=colors, alpha=0.8)
    
    plt.title('IBE方案密钥提取性能对比', fontsize=16, fontweight='bold')
    plt.ylabel('平均时间 (毫秒)', fontsize=12)
    plt.xlabel('IBE方案', fontsize=12)
    
    # 添加数值标签
    for bar, time in zip(bars, avg_times):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(avg_times)*0.01,
                f'{time:.2f}ms', ha='center', va='bottom', fontsize=10)
    
    plt.tight_layout()
    plt.savefig('results/ibe_key_extraction_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✅ IBE密钥提取对比图已保存: results/ibe_key_extraction_comparison.png")

def create_ibe_encryption_performance_chart(df):
    """创建IBE加密性能对比图"""
    encrypt_data = df[df['operation'] == 'encrypt']
    
    if encrypt_data.empty:
        print("⚠️ 没有找到加密性能数据，跳过加密性能图表生成")
        return
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # 子图1: 加密时间对比
    schemes = encrypt_data['scheme'].unique()
    message_types = encrypt_data['message_type'].unique()
    
    x = np.arange(len(message_types))
    width = 0.35
    
    for i, scheme in enumerate(schemes):
        scheme_data = encrypt_data[encrypt_data['scheme'] == scheme]
        times = []
        for msg_type in message_types:
            msg_data = scheme_data[scheme_data['message_type'] == msg_type]
            if not msg_data.empty:
                times.append(msg_data['time'].values[0] * 1000)  # 转换为毫秒
            else:
                times.append(0)
        
        ax1.bar(x + i*width, times, width, label=scheme, alpha=0.8)
    
    ax1.set_title('IBE加密时间对比', fontsize=14, fontweight='bold')
    ax1.set_ylabel('时间 (毫秒)', fontsize=12)
    ax1.set_xlabel('消息类型', fontsize=12)
    ax1.set_xticks(x + width/2)
    ax1.set_xticklabels(message_types)
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 子图2: 解密时间对比
    decrypt_data = df[df['operation'] == 'decrypt']
    for i, scheme in enumerate(schemes):
        scheme_data = decrypt_data[decrypt_data['scheme'] == scheme]
        times = []
        for msg_type in message_types:
            msg_data = scheme_data[scheme_data['message_type'] == msg_type]
            if not msg_data.empty:
                times.append(msg_data['time'].values[0] * 1000)  # 转换为毫秒
            else:
                times.append(0)
        
        ax2.bar(x + i*width, times, width, label=scheme, alpha=0.8)
    
    ax2.set_title('IBE解密时间对比', fontsize=14, fontweight='bold')
    ax2.set_ylabel('时间 (毫秒)', fontsize=12)
    ax2.set_xlabel('消息类型', fontsize=12)
    ax2.set_xticks(x + width/2)
    ax2.set_xticklabels(message_types)
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('results/ibe_encryption_performance.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✅ IBE加密解密性能对比图已保存: results/ibe_encryption_performance.png")

def create_ibe_comprehensive_radar_chart(df):
    """创建IBE综合性能雷达图"""
    schemes = df['scheme'].unique()
    
    # 过滤掉没有加密数据的方案
    valid_schemes = []
    for scheme in schemes:
        encrypt_data = df[(df['scheme'] == scheme) & (df['operation'] == 'encrypt')]
        if not encrypt_data.empty:
            valid_schemes.append(scheme)
    
    if len(valid_schemes) < 2:
        print("⚠️ 有效的IBE方案数量不足，跳过雷达图生成")
        return
    
    # 准备雷达图数据
    categories = ['系统设置', '密钥提取', '加密速度', '解密速度', '整体效率']
    
    # 计算性能评分（越高越好，所以用倒数）
    scheme_scores = {}
    
    for scheme in valid_schemes:
        scores = []
        
        # 系统设置性能（越快越好）
        setup_time = df[(df['scheme'] == scheme) & (df['operation'] == 'setup')]['time'].values[0]
        setup_score = 1 / (setup_time * 1000 + 0.001)  # 避免除零
        scores.append(min(setup_score, 100))  # 限制最大值
        
        # 密钥提取性能
        extract_data = df[(df['scheme'] == scheme) & (df['operation'] == 'extract')]
        if not extract_data.empty:
            extract_time = extract_data['time'].mean()
            extract_score = 1 / (extract_time * 10 + 0.001)
            scores.append(min(extract_score, 100))
        else:
            scores.append(0)
        
        # 加密性能
        encrypt_data = df[(df['scheme'] == scheme) & (df['operation'] == 'encrypt')]
        if not encrypt_data.empty:
            encrypt_time = encrypt_data['time'].mean()
            encrypt_score = 1 / (encrypt_time * 10 + 0.001)
            scores.append(min(encrypt_score, 100))
        else:
            scores.append(0)
        
        # 解密性能
        decrypt_data = df[(df['scheme'] == scheme) & (df['operation'] == 'decrypt')]
        if not decrypt_data.empty:
            decrypt_time = decrypt_data['time'].mean()
            decrypt_score = 1 / (decrypt_time * 100 + 0.001)
            scores.append(min(decrypt_score, 100))
        else:
            scores.append(0)
        
        # 整体效率（综合评分）
        overall_score = np.mean(scores)
        scores.append(overall_score)
        
        scheme_scores[scheme] = scores
    
    # 创建雷达图
    angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
    angles += angles[:1]  # 闭合图形
    
    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
    
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1']
    
    for i, scheme in enumerate(valid_schemes):
        values = scheme_scores[scheme]
        values += values[:1]  # 闭合图形
        
        ax.plot(angles, values, 'o-', linewidth=2, label=scheme, color=colors[i])
        ax.fill(angles, values, alpha=0.25, color=colors[i])
    
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories)
    ax.set_ylim(0, 100)
    ax.set_title('IBE方案综合性能雷达图', fontsize=16, fontweight='bold', pad=20)
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0))
    ax.grid(True)
    
    plt.tight_layout()
    plt.savefig('results/ibe_comprehensive_radar.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✅ IBE综合性能雷达图已保存: results/ibe_comprehensive_radar.png")

def create_ibe_efficiency_analysis(df):
    """创建IBE效率分析图"""
    # 过滤有效数据
    encrypt_data = df[df['operation'] == 'encrypt']
    if encrypt_data.empty:
        print("⚠️ 没有加密数据，跳过效率分析图")
        return
    
    schemes = encrypt_data['scheme'].unique()
    
    plt.figure(figsize=(12, 8))
    
    # 创建2x2子图
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
    
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1']
    
    # 子图1: 加密吞吐量 (字节/秒)
    for i, scheme in enumerate(schemes):
        scheme_encrypt = encrypt_data[encrypt_data['scheme'] == scheme]
        if not scheme_encrypt.empty:
            data_sizes = scheme_encrypt['data_size'].values
            times = scheme_encrypt['time'].values
            throughput = data_sizes / times  # 字节/秒
            
            ax1.bar([f'{scheme}\n{size}B' for size in data_sizes], throughput, 
                   color=colors[i], alpha=0.7, label=scheme)
    
    ax1.set_title('IBE加密吞吐量对比', fontweight='bold')
    ax1.set_ylabel('吞吐量 (字节/秒)')
    ax1.tick_params(axis='x', rotation=45)
    
    # 子图2: 解密吞吐量
    decrypt_data = df[df['operation'] == 'decrypt']
    for i, scheme in enumerate(schemes):
        scheme_decrypt = decrypt_data[decrypt_data['scheme'] == scheme]
        if not scheme_decrypt.empty:
            data_sizes = scheme_decrypt['data_size'].values
            times = scheme_decrypt['time'].values
            throughput = data_sizes / times
            
            ax2.bar([f'{scheme}\n{size}B' for size in data_sizes], throughput, 
                   color=colors[i], alpha=0.7, label=scheme)
    
    ax2.set_title('IBE解密吞吐量对比', fontweight='bold')
    ax2.set_ylabel('吞吐量 (字节/秒)')
    ax2.tick_params(axis='x', rotation=45)
    
    # 子图3: 密钥提取效率
    extract_data = df[df['operation'] == 'extract']
    for i, scheme in enumerate(schemes):
        scheme_extract = extract_data[extract_data['scheme'] == scheme]
        if not scheme_extract.empty:
            avg_time = scheme_extract['time'].mean() * 1000  # 毫秒
            ax3.bar(scheme, 1000/avg_time, color=colors[i], alpha=0.7)  # 密钥/秒
    
    ax3.set_title('IBE密钥提取效率', fontweight='bold')
    ax3.set_ylabel('密钥提取率 (密钥/秒)')
    ax3.tick_params(axis='x', rotation=45)
    
    # 子图4: 综合性能评分
    overall_scores = []
    scheme_names = []
    
    for i, scheme in enumerate(schemes):
        # 计算综合评分
        setup_data = df[(df['scheme'] == scheme) & (df['operation'] == 'setup')]
        extract_avg = extract_data[extract_data['scheme'] == scheme]['time'].mean() if not extract_data[extract_data['scheme'] == scheme].empty else 0
        encrypt_avg = encrypt_data[encrypt_data['scheme'] == scheme]['time'].mean() if not encrypt_data[encrypt_data['scheme'] == scheme].empty else 0
        decrypt_avg = decrypt_data[decrypt_data['scheme'] == scheme]['time'].mean() if not decrypt_data[decrypt_data['scheme'] == scheme].empty else 0
        
        if not setup_data.empty and encrypt_avg > 0:
            setup_time = setup_data['time'].values[0]
            # 综合评分（时间越短评分越高）
            score = 1000 / (setup_time * 0.1 + extract_avg * 0.2 + encrypt_avg * 0.35 + decrypt_avg * 0.35 + 0.001)
            overall_scores.append(score)
            scheme_names.append(scheme)
    
    if overall_scores:
        bars = ax4.bar(scheme_names, overall_scores, color=colors[:len(scheme_names)], alpha=0.7)
        ax4.set_title('IBE综合性能评分', fontweight='bold')
        ax4.set_ylabel('综合评分 (越高越好)')
        ax4.tick_params(axis='x', rotation=45)
        
        # 添加数值标签
        for bar, score in zip(bars, overall_scores):
            ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(overall_scores)*0.01,
                    f'{score:.1f}', ha='center', va='bottom', fontsize=10)
    
    plt.tight_layout()
    plt.savefig('results/ibe_efficiency_analysis.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✅ IBE效率分析图已保存: results/ibe_efficiency_analysis.png")

def generate_ibe_performance_summary(df):
    """生成IBE性能总结报告"""
    print("\n" + "="*60)
    print("IBE性能分析总结报告")
    print("="*60)
    
    schemes = df['scheme'].unique()
    
    for scheme in schemes:
        print(f"\n📊 {scheme} 性能总结:")
        
        # 系统设置
        setup_data = df[(df['scheme'] == scheme) & (df['operation'] == 'setup')]
        if not setup_data.empty:
            setup_time = setup_data['time'].values[0] * 1000
            print(f"  系统设置: {setup_time:.3f} 毫秒")
        
        # 密钥提取
        extract_data = df[(df['scheme'] == scheme) & (df['operation'] == 'extract')]
        if not extract_data.empty:
            avg_extract = extract_data['time'].mean() * 1000
            print(f"  密钥提取: {avg_extract:.2f} 毫秒 (平均)")
        
        # 加密性能
        encrypt_data = df[(df['scheme'] == scheme) & (df['operation'] == 'encrypt')]
        if not encrypt_data.empty:
            avg_encrypt = encrypt_data['time'].mean() * 1000
            print(f"  加密性能: {avg_encrypt:.2f} 毫秒 (平均)")
        
        # 解密性能
        decrypt_data = df[(df['scheme'] == scheme) & (df['operation'] == 'decrypt')]
        if not decrypt_data.empty:
            avg_decrypt = decrypt_data['time'].mean() * 1000
            print(f"  解密性能: {avg_decrypt:.2f} 毫秒 (平均)")
    
    print(f"\n🎯 推荐使用场景:")
    print(f"  • Boneh-Franklin: 教学和原型开发")
    print(f"  • Boneh-Boyen: 需要标准模型安全性的场景")
    print(f"  • Sakai-Kasahara: 高性能生产环境")

def main():
    """主函数，执行IBE性能分析和可视化"""
    print("=== IBE性能分析和可视化 ===")
    
    # 加载数据
    df = load_ibe_performance_data()
    if df is None:
        return
    
    # 确保结果目录存在
    os.makedirs('results', exist_ok=True)
    
    print("\n🎨 生成IBE性能对比图表...")
    
    # 生成各种图表
    create_ibe_setup_comparison(df)
    create_ibe_key_extraction_comparison(df)
    create_ibe_encryption_performance_chart(df)
    create_ibe_comprehensive_radar_chart(df)
    create_ibe_efficiency_analysis(df)
    
    # 生成总结报告
    generate_ibe_performance_summary(df)
    
    print(f"\n🎉 IBE性能分析完成！")
    print(f"所有图表已保存到 results/ 目录")
    print(f"生成的图表:")
    print(f"  • ibe_setup_comparison.png - 系统设置性能对比")
    print(f"  • ibe_key_extraction_comparison.png - 密钥提取性能对比")
    print(f"  • ibe_encryption_performance.png - 加密解密性能对比")
    print(f"  • ibe_comprehensive_radar.png - 综合性能雷达图")
    print(f"  • ibe_efficiency_analysis.png - 效率分析图")

if __name__ == '__main__':
    main() 