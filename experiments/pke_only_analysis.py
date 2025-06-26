# -*- coding: utf-8 -*-

"""
PKE算法专项性能分析和可视化脚本
专门针对ECC、ElGamal、SM2三种公钥加密算法的内部对比分析
设计时考虑前端美观显示需求
"""

import matplotlib
matplotlib.use('Agg')
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

# 设置中文字体和样式
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['figure.facecolor'] = 'white'
plt.rcParams['axes.facecolor'] = 'white'

# 前端友好的配色方案
PKE_COLORS = {
    'ECC': '#4A90E2',      # 专业蓝
    'ElGamal': '#7ED321',  # 活力绿  
    'SM2': '#F5A623'       # 温暖橙
}

def load_pke_data():
    """加载PKE性能数据"""
    data_file = 'results/pke_performance_complete.csv'
    
    if os.path.exists(data_file):
        print("📄 加载PKE性能数据")
        df = pd.read_csv(data_file)
        return df
    else:
        print(f"❌ 找不到PKE性能数据文件: {data_file}")
        return None

def create_pke_performance_overview(df):
    """
    创建PKE性能全景图 - 2x2布局
    针对前端显示优化：合理的图片尺寸、清晰的标签、美观的布局
    """
    # 使用前端友好的尺寸比例 (16:10)
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 10))
    fig.suptitle('PKE算法性能全景分析', fontsize=20, fontweight='bold', y=0.95)
    
    schemes = df['scheme'].unique()
    colors = [PKE_COLORS[scheme] for scheme in schemes]
    
    # 子图1: 密钥生成性能对比
    key_gen_data = df[df['operation'] == 'key_gen']
    times = key_gen_data['time'].values * 1000  # 转换为毫秒
    
    bars1 = ax1.bar(schemes, times, color=colors, alpha=0.8, edgecolor='white', linewidth=2)
    ax1.set_title('密钥生成性能', fontsize=14, fontweight='bold', pad=15)
    ax1.set_ylabel('时间 (毫秒)', fontsize=12)
    ax1.grid(True, alpha=0.3, axis='y')
    ax1.set_facecolor('#FAFAFA')
    
    # 添加数值标签
    for bar, time in zip(bars1, times):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2, height + max(times)*0.02,
                f'{time:.2f}ms', ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    # 子图2: 加密性能对比（双数据大小）
    data_sizes = [128, 1024]
    x = np.arange(len(schemes))
    width = 0.35
    
    for i, size in enumerate(data_sizes):
        encrypt_data = df[(df['operation'] == 'encrypt') & (df['data_size'] == size)]
        times = [encrypt_data[encrypt_data['scheme'] == scheme]['time'].values[0] * 1000 
                for scheme in schemes]
        
        bars = ax2.bar(x + i*width, times, width, 
                      label=f'{size}B数据', alpha=0.8, edgecolor='white', linewidth=1)
        
        # 为每个数据大小使用不同的透明度
        for j, bar in enumerate(bars):
            bar.set_color(colors[j])
            bar.set_alpha(0.9 if i == 0 else 0.6)
    
    ax2.set_title('加密性能对比', fontsize=14, fontweight='bold', pad=15)
    ax2.set_ylabel('时间 (毫秒)', fontsize=12)
    ax2.set_xticks(x + width/2)
    ax2.set_xticklabels(schemes)
    ax2.legend(loc='upper right')
    ax2.grid(True, alpha=0.3, axis='y')
    ax2.set_facecolor('#FAFAFA')
    
    # 子图3: 解密性能对比（双数据大小）
    for i, size in enumerate(data_sizes):
        decrypt_data = df[(df['operation'] == 'decrypt') & (df['data_size'] == size)]
        times = [decrypt_data[decrypt_data['scheme'] == scheme]['time'].values[0] * 1000 
                for scheme in schemes]
        
        bars = ax3.bar(x + i*width, times, width, 
                      label=f'{size}B数据', alpha=0.8, edgecolor='white', linewidth=1)
        
        for j, bar in enumerate(bars):
            bar.set_color(colors[j])
            bar.set_alpha(0.9 if i == 0 else 0.6)
    
    ax3.set_title('解密性能对比', fontsize=14, fontweight='bold', pad=15)
    ax3.set_ylabel('时间 (毫秒)', fontsize=12)
    ax3.set_xticks(x + width/2)
    ax3.set_xticklabels(schemes)
    ax3.legend(loc='upper right')
    ax3.grid(True, alpha=0.3, axis='y')
    ax3.set_facecolor('#FAFAFA')
    
    # 子图4: 综合性能雷达图
    categories = ['密钥生成', '加密速度', '解密速度', '密文效率', '整体性能']
    
    # 计算性能评分（越高越好）
    scheme_scores = {}
    
    for scheme in schemes:
        scores = []
        
        # 密钥生成评分（时间越短评分越高）
        key_gen_time = df[(df['scheme'] == scheme) & (df['operation'] == 'key_gen')]['time'].values[0]
        key_gen_score = min(100 / (key_gen_time * 1000 + 0.1), 100)
        scores.append(key_gen_score)
        
        # 加密速度评分（使用128B数据）
        encrypt_time = df[(df['scheme'] == scheme) & (df['operation'] == 'encrypt') & (df['data_size'] == 128)]['time'].values[0]
        encrypt_score = min(100 / (encrypt_time * 1000 + 0.1), 100)
        scores.append(encrypt_score)
        
        # 解密速度评分
        decrypt_time = df[(df['scheme'] == scheme) & (df['operation'] == 'decrypt') & (df['data_size'] == 128)]['time'].values[0]
        decrypt_score = min(100 / (decrypt_time * 1000 + 0.1), 100)
        scores.append(decrypt_score)
        
        # 密文效率评分（密文大小越小评分越高）
        cipher_size = df[(df['scheme'] == scheme) & (df['operation'] == 'encrypt') & (df['data_size'] == 128)]['ciphertext_size'].values[0]
        cipher_score = min(1000 / (cipher_size + 1), 100)
        scores.append(cipher_score)
        
        # 整体性能评分（综合前面各项）
        overall_score = np.mean(scores)
        scores.append(overall_score)
        
        scheme_scores[scheme] = scores
    
    # 绘制雷达图
    angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
    angles += angles[:1]  # 闭合图形
    
    ax4 = plt.subplot(2, 2, 4, projection='polar')
    ax4.set_facecolor('#FAFAFA')
    
    for i, scheme in enumerate(schemes):
        values = scheme_scores[scheme]
        values += values[:1]  # 闭合图形
        
        ax4.plot(angles, values, 'o-', linewidth=2.5, label=scheme, 
                color=colors[i], markersize=6)
        ax4.fill(angles, values, alpha=0.25, color=colors[i])
    
    ax4.set_xticks(angles[:-1])
    ax4.set_xticklabels(categories, fontsize=10)
    ax4.set_ylim(0, 100)
    ax4.set_title('综合性能雷达图', fontsize=14, fontweight='bold', pad=20)
    ax4.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0))
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('results/pke_only_performance_overview.png', dpi=300, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    plt.close()
    print("✅ PKE性能全景图已保存: results/pke_only_performance_overview.png")

def create_pke_efficiency_analysis(df):
    """
    创建PKE效率分析图 - 2x2布局
    重点关注实用性指标，适合前端卡片式展示
    """
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 10))
    fig.suptitle('PKE算法效率深度分析', fontsize=20, fontweight='bold', y=0.95)
    
    schemes = df['scheme'].unique()
    colors = [PKE_COLORS[scheme] for scheme in schemes]
    
    # 子图1: 密文膨胀率对比
    data_sizes = [128, 1024]
    x = np.arange(len(schemes))
    width = 0.35
    
    for i, size in enumerate(data_sizes):
        encrypt_data = df[(df['operation'] == 'encrypt') & (df['data_size'] == size)]
        expansion_rates = []
        
        for scheme in schemes:
            scheme_data = encrypt_data[encrypt_data['scheme'] == scheme]
            cipher_size = scheme_data['ciphertext_size'].values[0]
            expansion_rate = ((cipher_size / size) - 1) * 100
            expansion_rates.append(expansion_rate)
        
        bars = ax1.bar(x + i*width, expansion_rates, width, 
                      label=f'{size}B原文', alpha=0.8, edgecolor='white', linewidth=1)
        
        for j, bar in enumerate(bars):
            bar.set_color(colors[j])
            bar.set_alpha(0.9 if i == 0 else 0.6)
    
    ax1.set_title('密文膨胀率对比', fontsize=14, fontweight='bold', pad=15)
    ax1.set_ylabel('膨胀率 (%)', fontsize=12)
    ax1.set_xticks(x + width/2)
    ax1.set_xticklabels(schemes)
    ax1.legend()
    ax1.grid(True, alpha=0.3, axis='y')
    ax1.set_facecolor('#FAFAFA')
    
    # 子图2: 加密吞吐量对比
    throughput_data = []
    labels = []
    
    for scheme in schemes:
        for size in data_sizes:
            encrypt_data = df[(df['scheme'] == scheme) & (df['operation'] == 'encrypt') & (df['data_size'] == size)]
            if not encrypt_data.empty:
                time = encrypt_data['time'].values[0]
                throughput = size / time  # 字节/秒
                throughput_data.append(throughput)
                labels.append(f'{scheme}\n{size}B')
    
    # 重新组织数据用于分组显示
    throughput_128 = []
    throughput_1024 = []
    
    for scheme in schemes:
        # 128B吞吐量
        encrypt_128 = df[(df['scheme'] == scheme) & (df['operation'] == 'encrypt') & (df['data_size'] == 128)]
        time_128 = encrypt_128['time'].values[0]
        throughput_128.append(128 / time_128)
        
        # 1024B吞吐量
        encrypt_1024 = df[(df['scheme'] == scheme) & (df['operation'] == 'encrypt') & (df['data_size'] == 1024)]
        time_1024 = encrypt_1024['time'].values[0]
        throughput_1024.append(1024 / time_1024)
    
    x = np.arange(len(schemes))
    bars1 = ax2.bar(x - width/2, throughput_128, width, label='128B数据', alpha=0.8, edgecolor='white', linewidth=1)
    bars2 = ax2.bar(x + width/2, throughput_1024, width, label='1024B数据', alpha=0.8, edgecolor='white', linewidth=1)
    
    for i, (bar1, bar2) in enumerate(zip(bars1, bars2)):
        bar1.set_color(colors[i])
        bar2.set_color(colors[i])
        bar1.set_alpha(0.9)
        bar2.set_alpha(0.6)
    
    ax2.set_title('加密吞吐量对比', fontsize=14, fontweight='bold', pad=15)
    ax2.set_ylabel('吞吐量 (字节/秒)', fontsize=12)
    ax2.set_xticks(x)
    ax2.set_xticklabels(schemes)
    ax2.legend()
    ax2.grid(True, alpha=0.3, axis='y')
    ax2.set_facecolor('#FAFAFA')
    
    # 子图3: 解密吞吐量对比
    decrypt_throughput_128 = []
    decrypt_throughput_1024 = []
    
    for scheme in schemes:
        # 128B解密吞吐量
        decrypt_128 = df[(df['scheme'] == scheme) & (df['operation'] == 'decrypt') & (df['data_size'] == 128)]
        time_128 = decrypt_128['time'].values[0]
        decrypt_throughput_128.append(128 / time_128)
        
        # 1024B解密吞吐量
        decrypt_1024 = df[(df['scheme'] == scheme) & (df['operation'] == 'decrypt') & (df['data_size'] == 1024)]
        time_1024 = decrypt_1024['time'].values[0]
        decrypt_throughput_1024.append(1024 / time_1024)
    
    bars1 = ax3.bar(x - width/2, decrypt_throughput_128, width, label='128B数据', alpha=0.8, edgecolor='white', linewidth=1)
    bars2 = ax3.bar(x + width/2, decrypt_throughput_1024, width, label='1024B数据', alpha=0.8, edgecolor='white', linewidth=1)
    
    for i, (bar1, bar2) in enumerate(zip(bars1, bars2)):
        bar1.set_color(colors[i])
        bar2.set_color(colors[i])
        bar1.set_alpha(0.9)
        bar2.set_alpha(0.6)
    
    ax3.set_title('解密吞吐量对比', fontsize=14, fontweight='bold', pad=15)
    ax3.set_ylabel('吞吐量 (字节/秒)', fontsize=12)
    ax3.set_xticks(x)
    ax3.set_xticklabels(schemes)
    ax3.legend()
    ax3.grid(True, alpha=0.3, axis='y')
    ax3.set_facecolor('#FAFAFA')
    
    # 子图4: 算法效率热力图
    operations = ['密钥生成', '加密(128B)', '解密(128B)', '加密(1024B)', '解密(1024B)']
    
    # 准备热力图数据
    heatmap_data = []
    
    for scheme in schemes:
        row = []
        
        # 密钥生成效率
        key_gen_time = df[(df['scheme'] == scheme) & (df['operation'] == 'key_gen')]['time'].values[0]
        key_gen_efficiency = min(100 / (key_gen_time * 1000 + 0.1), 100)
        row.append(key_gen_efficiency)
        
        # 加密效率 (128B)
        encrypt_128_time = df[(df['scheme'] == scheme) & (df['operation'] == 'encrypt') & (df['data_size'] == 128)]['time'].values[0]
        encrypt_128_efficiency = min(100 / (encrypt_128_time * 1000 + 0.1), 100)
        row.append(encrypt_128_efficiency)
        
        # 解密效率 (128B)
        decrypt_128_time = df[(df['scheme'] == scheme) & (df['operation'] == 'decrypt') & (df['data_size'] == 128)]['time'].values[0]
        decrypt_128_efficiency = min(100 / (decrypt_128_time * 1000 + 0.1), 100)
        row.append(decrypt_128_efficiency)
        
        # 加密效率 (1024B)
        encrypt_1024_time = df[(df['scheme'] == scheme) & (df['operation'] == 'encrypt') & (df['data_size'] == 1024)]['time'].values[0]
        encrypt_1024_efficiency = min(100 / (encrypt_1024_time * 1000 + 0.1), 100)
        row.append(encrypt_1024_efficiency)
        
        # 解密效率 (1024B)
        decrypt_1024_time = df[(df['scheme'] == scheme) & (df['operation'] == 'decrypt') & (df['data_size'] == 1024)]['time'].values[0]
        decrypt_1024_efficiency = min(100 / (decrypt_1024_time * 1000 + 0.1), 100)
        row.append(decrypt_1024_efficiency)
        
        heatmap_data.append(row)
    
    heatmap_array = np.array(heatmap_data)
    
    im = ax4.imshow(heatmap_array, cmap='RdYlGn', aspect='auto', vmin=0, vmax=100)
    
    # 设置标签
    ax4.set_xticks(range(len(operations)))
    ax4.set_xticklabels(operations, rotation=45, ha='right')
    ax4.set_yticks(range(len(schemes)))
    ax4.set_yticklabels(schemes)
    ax4.set_title('算法效率热力图', fontsize=14, fontweight='bold', pad=15)
    
    # 添加颜色条
    cbar = plt.colorbar(im, ax=ax4, shrink=0.8)
    cbar.set_label('效率评分', rotation=270, labelpad=15)
    
    # 添加数值标签
    for i in range(len(schemes)):
        for j in range(len(operations)):
            ax4.text(j, i, f'{heatmap_array[i, j]:.1f}',
                    ha='center', va='center', color='black', fontweight='bold', fontsize=9)
    
    plt.tight_layout()
    plt.savefig('results/pke_only_efficiency_analysis.png', dpi=300, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()
    print("✅ PKE效率分析图已保存: results/pke_only_efficiency_analysis.png")

def create_pke_scalability_analysis(df):
    """
    创建PKE规模适应性分析
    展示算法在不同数据大小下的性能变化趋势
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    fig.suptitle('PKE算法数据规模适应性分析', fontsize=18, fontweight='bold', y=0.95)
    
    schemes = df['scheme'].unique()
    colors = [PKE_COLORS[scheme] for scheme in schemes]
    data_sizes = [128, 1024]
    
    # 子图1: 加密性能随数据大小变化
    for i, scheme in enumerate(schemes):
        encrypt_times = []
        for size in data_sizes:
            encrypt_data = df[(df['scheme'] == scheme) & (df['operation'] == 'encrypt') & (df['data_size'] == size)]
            time = encrypt_data['time'].values[0] * 1000  # 转换为毫秒
            encrypt_times.append(time)
        
        ax1.plot(data_sizes, encrypt_times, 'o-', linewidth=3, markersize=8,
                label=scheme, color=colors[i], alpha=0.8)
        
        # 添加数值标签
        for x, y in zip(data_sizes, encrypt_times):
            ax1.annotate(f'{y:.3f}ms', (x, y), textcoords="offset points", 
                        xytext=(0,10), ha='center', fontsize=10, fontweight='bold')
    
    ax1.set_title('加密性能vs数据大小', fontsize=14, fontweight='bold', pad=15)
    ax1.set_xlabel('数据大小 (字节)', fontsize=12)
    ax1.set_ylabel('加密时间 (毫秒)', fontsize=12)
    ax1.set_xscale('log')
    ax1.set_yscale('log')
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    ax1.set_facecolor('#FAFAFA')
    
    # 子图2: 解密性能随数据大小变化
    for i, scheme in enumerate(schemes):
        decrypt_times = []
        for size in data_sizes:
            decrypt_data = df[(df['scheme'] == scheme) & (df['operation'] == 'decrypt') & (df['data_size'] == size)]
            time = decrypt_data['time'].values[0] * 1000  # 转换为毫秒
            decrypt_times.append(time)
        
        ax2.plot(data_sizes, decrypt_times, 'o-', linewidth=3, markersize=8,
                label=scheme, color=colors[i], alpha=0.8)
        
        # 添加数值标签
        for x, y in zip(data_sizes, decrypt_times):
            ax2.annotate(f'{y:.3f}ms', (x, y), textcoords="offset points", 
                        xytext=(0,10), ha='center', fontsize=10, fontweight='bold')
    
    ax2.set_title('解密性能vs数据大小', fontsize=14, fontweight='bold', pad=15)
    ax2.set_xlabel('数据大小 (字节)', fontsize=12)
    ax2.set_ylabel('解密时间 (毫秒)', fontsize=12)
    ax2.set_xscale('log')
    ax2.set_yscale('log')
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    ax2.set_facecolor('#FAFAFA')
    
    plt.tight_layout()
    plt.savefig('results/pke_only_scalability_analysis.png', dpi=300, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()
    print("✅ PKE规模适应性分析图已保存: results/pke_only_scalability_analysis.png")

def generate_pke_summary_report(df):
    """生成PKE算法详细性能报告"""
    print("\n" + "="*70)
    print("PKE算法专项性能分析报告")
    print("="*70)
    
    schemes = df['scheme'].unique()
    
    for scheme in schemes:
        print(f"\n🔐 {scheme} 详细分析:")
        
        # 密钥生成性能
        key_gen_time = df[(df['scheme'] == scheme) & (df['operation'] == 'key_gen')]['time'].values[0] * 1000
        print(f"  密钥生成: {key_gen_time:.3f} 毫秒")
        
        # 加密性能分析
        encrypt_128 = df[(df['scheme'] == scheme) & (df['operation'] == 'encrypt') & (df['data_size'] == 128)]
        encrypt_1024 = df[(df['scheme'] == scheme) & (df['operation'] == 'encrypt') & (df['data_size'] == 1024)]
        
        if not encrypt_128.empty and not encrypt_1024.empty:
            encrypt_time_128 = encrypt_128['time'].values[0] * 1000
            encrypt_time_1024 = encrypt_1024['time'].values[0] * 1000
            cipher_size_128 = encrypt_128['ciphertext_size'].values[0]
            cipher_size_1024 = encrypt_1024['ciphertext_size'].values[0]
            
            print(f"  加密(128B): {encrypt_time_128:.3f} 毫秒, 密文: {cipher_size_128} 字节")
            print(f"  加密(1024B): {encrypt_time_1024:.3f} 毫秒, 密文: {cipher_size_1024} 字节")
            
            # 计算吞吐量
            throughput_128 = 128 / (encrypt_time_128 / 1000)  # 字节/秒
            throughput_1024 = 1024 / (encrypt_time_1024 / 1000)
            print(f"  加密吞吐量: {throughput_128:.0f} B/s (128B), {throughput_1024:.0f} B/s (1024B)")
        
        # 解密性能分析
        decrypt_128 = df[(df['scheme'] == scheme) & (df['operation'] == 'decrypt') & (df['data_size'] == 128)]
        decrypt_1024 = df[(df['scheme'] == scheme) & (df['operation'] == 'decrypt') & (df['data_size'] == 1024)]
        
        if not decrypt_128.empty and not decrypt_1024.empty:
            decrypt_time_128 = decrypt_128['time'].values[0] * 1000
            decrypt_time_1024 = decrypt_1024['time'].values[0] * 1000
            
            print(f"  解密(128B): {decrypt_time_128:.3f} 毫秒")
            print(f"  解密(1024B): {decrypt_time_1024:.3f} 毫秒")
            
            # 计算解密吞吐量
            decrypt_throughput_128 = 128 / (decrypt_time_128 / 1000)
            decrypt_throughput_1024 = 1024 / (decrypt_time_1024 / 1000)
            print(f"  解密吞吐量: {decrypt_throughput_128:.0f} B/s (128B), {decrypt_throughput_1024:.0f} B/s (1024B)")
    
    print(f"\n🎯 PKE算法选择建议:")
    print(f"  • SM2: 国产标准，整体性能优异，推荐用于国内商业项目")
    print(f"  • ElGamal: 密文紧凑，解密快速，适合存储空间敏感的应用")
    print(f"  • ECC: 加密强度高，适合高安全等级要求的政府和金融场景")
    
    print(f"\n📊 前端显示建议:")
    print(f"  • 图表尺寸: 16:10比例，适合现代显示器")
    print(f"  • 配色方案: 蓝色(ECC)、绿色(ElGamal)、橙色(SM2)")
    print(f"  • 布局方式: 2x2网格布局，便于卡片式展示")
    print(f"  • 交互建议: 支持点击查看详细数据，悬停显示具体数值")

def main():
    """主函数，执行PKE专项性能分析"""
    print("=== PKE算法专项性能分析 ===")
    
    # 加载数据
    df = load_pke_data()
    if df is None:
        return
    
    # 确保结果目录存在
    os.makedirs('results', exist_ok=True)
    
    print("\n🎨 生成PKE专项分析图表...")
    
    # 生成各种PKE专项图表
    create_pke_performance_overview(df)
    create_pke_efficiency_analysis(df)
    create_pke_scalability_analysis(df)
    
    # 生成分析报告
    generate_pke_summary_report(df)
    
    print(f"\n🎉 PKE专项分析完成！")
    print(f"生成的图表:")
    print(f"  • pke_only_performance_overview.png - PKE性能全景图 (2x2布局)")
    print(f"  • pke_only_efficiency_analysis.png - PKE效率分析图 (2x2布局)")  
    print(f"  • pke_only_scalability_analysis.png - PKE规模适应性分析 (1x2布局)")
    print(f"\n💡 前端集成提示:")
    print(f"  • 所有图表采用16:10或16:6比例，适合响应式设计")
    print(f"  • 使用统一配色方案，便于用户识别不同算法")
    print(f"  • 图表背景为白色，便于在各种主题下显示")

if __name__ == '__main__':
    main() 