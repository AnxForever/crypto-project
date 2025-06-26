# -*- coding: utf-8 -*-

"""
IBE算法专项性能分析和可视化脚本
专门针对Boneh-Franklin、Boneh-Boyen、Sakai-Kasahara三种IBE算法的内部对比分析
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

# 前端友好的IBE配色方案
IBE_COLORS = {
    'Boneh-Franklin': '#E74C3C',     # 经典红
    'Boneh-Boyen': '#3498DB',       # 天空蓝
    'Sakai-Kasahara': '#2ECC71'     # 翠绿色
}

def load_ibe_data():
    """加载IBE性能数据"""
    data_file = 'results/ibe_performance_complete.csv'
    
    if os.path.exists(data_file):
        print("📄 加载IBE性能数据")
        df = pd.read_csv(data_file)
        return df
    else:
        print(f"❌ 找不到IBE性能数据文件: {data_file}")
        return None

def create_ibe_performance_overview(df):
    """
    创建IBE性能全景图 - 2x2布局
    针对前端显示优化：合理的图片尺寸、清晰的标签、美观的布局
    """
    # 使用前端友好的尺寸比例 (16:10)
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 10))
    fig.suptitle('IBE算法性能全景分析', fontsize=20, fontweight='bold', y=0.95)
    
    schemes = df['scheme'].unique()
    colors = [IBE_COLORS[scheme] for scheme in schemes]
    
    # 子图1: 系统设置性能对比
    setup_data = df[df['operation'] == 'setup']
    if not setup_data.empty:
        setup_schemes = setup_data['scheme'].values
        setup_times = setup_data['time'].values * 1000  # 转换为毫秒
        setup_colors = [IBE_COLORS[scheme] for scheme in setup_schemes]
        
        bars1 = ax1.bar(setup_schemes, setup_times, color=setup_colors, alpha=0.8, 
                       edgecolor='white', linewidth=2)
        ax1.set_title('系统设置性能', fontsize=14, fontweight='bold', pad=15)
        ax1.set_ylabel('时间 (毫秒)', fontsize=12)
        ax1.grid(True, alpha=0.3, axis='y')
        ax1.set_facecolor('#FAFAFA')
        
        # 添加数值标签
        for bar, time in zip(bars1, setup_times):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2, height + max(setup_times)*0.02,
                    f'{time:.3f}ms', ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    # 子图2: 密钥提取性能对比
    extract_data = df[df['operation'] == 'extract']
    if not extract_data.empty:
        # 计算每个方案的平均密钥提取时间
        extract_schemes = extract_data['scheme'].unique()
        avg_times = []
        
        for scheme in extract_schemes:
            scheme_data = extract_data[extract_data['scheme'] == scheme]
            avg_time = scheme_data['time'].mean() * 1000  # 转换为毫秒
            avg_times.append(avg_time)
        
        extract_colors = [IBE_COLORS[scheme] for scheme in extract_schemes]
        
        bars2 = ax2.bar(extract_schemes, avg_times, color=extract_colors, alpha=0.8,
                       edgecolor='white', linewidth=2)
        ax2.set_title('密钥提取性能', fontsize=14, fontweight='bold', pad=15)
        ax2.set_ylabel('平均时间 (毫秒)', fontsize=12)
        ax2.grid(True, alpha=0.3, axis='y')
        ax2.set_facecolor('#FAFAFA')
        
        # 添加数值标签
        for bar, time in zip(bars2, avg_times):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2, height + max(avg_times)*0.02,
                    f'{time:.2f}ms', ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    # 子图3: 加密性能对比（多消息类型）
    encrypt_data = df[df['operation'] == 'encrypt']
    if not encrypt_data.empty:
        encrypt_schemes = encrypt_data['scheme'].unique()
        message_types = encrypt_data['message_type'].unique()
        
        x = np.arange(len(message_types))
        width = 0.25
        
        for i, scheme in enumerate(encrypt_schemes):
            scheme_data = encrypt_data[encrypt_data['scheme'] == scheme]
            times = []
            for msg_type in message_types:
                msg_data = scheme_data[scheme_data['message_type'] == msg_type]
                if not msg_data.empty:
                    times.append(msg_data['time'].values[0] * 1000)  # 转换为毫秒
                else:
                    times.append(0)
            
            bars = ax3.bar(x + i*width, times, width, label=scheme, 
                          alpha=0.8, color=IBE_COLORS[scheme], edgecolor='white', linewidth=1)
        
        ax3.set_title('加密性能对比', fontsize=14, fontweight='bold', pad=15)
        ax3.set_ylabel('时间 (毫秒)', fontsize=12)
        ax3.set_xlabel('消息类型', fontsize=12)
        ax3.set_xticks(x + width)
        ax3.set_xticklabels(message_types)
        ax3.legend(loc='upper left')
        ax3.grid(True, alpha=0.3, axis='y')
        ax3.set_facecolor('#FAFAFA')
    
    # 子图4: 解密性能对比（多消息类型）
    decrypt_data = df[df['operation'] == 'decrypt']
    if not decrypt_data.empty:
        decrypt_schemes = decrypt_data['scheme'].unique()
        
        for i, scheme in enumerate(decrypt_schemes):
            scheme_data = decrypt_data[decrypt_data['scheme'] == scheme]
            times = []
            for msg_type in message_types:
                msg_data = scheme_data[scheme_data['message_type'] == msg_type]
                if not msg_data.empty:
                    times.append(msg_data['time'].values[0] * 1000)  # 转换为毫秒
                else:
                    times.append(0)
            
            bars = ax4.bar(x + i*width, times, width, label=scheme, 
                          alpha=0.8, color=IBE_COLORS[scheme], edgecolor='white', linewidth=1)
        
        ax4.set_title('解密性能对比', fontsize=14, fontweight='bold', pad=15)
        ax4.set_ylabel('时间 (毫秒)', fontsize=12)
        ax4.set_xlabel('消息类型', fontsize=12)
        ax4.set_xticks(x + width)
        ax4.set_xticklabels(message_types)
        ax4.legend(loc='upper left')
        ax4.grid(True, alpha=0.3, axis='y')
        ax4.set_facecolor('#FAFAFA')
    
    plt.tight_layout()
    plt.savefig('results/ibe_only_performance_overview.png', dpi=300, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    plt.close()
    print("✅ IBE性能全景图已保存: results/ibe_only_performance_overview.png")

def create_ibe_efficiency_analysis(df):
    """
    创建IBE效率分析图 - 2x2布局
    重点关注实用性指标，适合前端卡片式展示
    """
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 10))
    fig.suptitle('IBE算法效率深度分析', fontsize=20, fontweight='bold', y=0.95)
    
    schemes = df['scheme'].unique()
    colors = [IBE_COLORS[scheme] for scheme in schemes]
    
    # 子图1: 密钥提取效率（密钥/秒）
    extract_data = df[df['operation'] == 'extract']
    if not extract_data.empty:
        extract_rates = []
        extract_schemes = []
        
        for scheme in schemes:
            scheme_data = extract_data[extract_data['scheme'] == scheme]
            if not scheme_data.empty:
                avg_time = scheme_data['time'].mean()  # 秒
                extract_rate = 1 / avg_time  # 密钥/秒
                extract_rates.append(extract_rate)
                extract_schemes.append(scheme)
        
        scheme_colors = [IBE_COLORS[scheme] for scheme in extract_schemes]
        
        bars1 = ax1.bar(extract_schemes, extract_rates, color=scheme_colors, alpha=0.8,
                       edgecolor='white', linewidth=2)
        ax1.set_title('密钥提取效率', fontsize=14, fontweight='bold', pad=15)
        ax1.set_ylabel('密钥提取率 (密钥/秒)', fontsize=12)
        ax1.grid(True, alpha=0.3, axis='y')
        ax1.set_facecolor('#FAFAFA')
        
        # 添加数值标签
        for bar, rate in zip(bars1, extract_rates):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2, height + max(extract_rates)*0.02,
                    f'{rate:.1f}', ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    # 子图2: 加密吞吐量对比（不同消息长度）
    encrypt_data = df[df['operation'] == 'encrypt']
    if not encrypt_data.empty:
        encrypt_schemes = encrypt_data['scheme'].unique()
        message_types = encrypt_data['message_type'].unique()
        
        x = np.arange(len(encrypt_schemes))
        width = 0.25
        
        for i, msg_type in enumerate(message_types):
            throughputs = []
            for scheme in encrypt_schemes:
                scheme_data = encrypt_data[(encrypt_data['scheme'] == scheme) & 
                                         (encrypt_data['message_type'] == msg_type)]
                if not scheme_data.empty:
                    time = scheme_data['time'].values[0]
                    data_size = scheme_data['data_size'].values[0]
                    throughput = data_size / time  # 字节/秒
                    throughputs.append(throughput)
                else:
                    throughputs.append(0)
            
            bars = ax2.bar(x + i*width, throughputs, width, label=msg_type, 
                          alpha=0.8, edgecolor='white', linewidth=1)
        
        ax2.set_title('加密吞吐量对比', fontsize=14, fontweight='bold', pad=15)
        ax2.set_ylabel('吞吐量 (字节/秒)', fontsize=12)
        ax2.set_xticks(x + width)
        ax2.set_xticklabels(encrypt_schemes, rotation=45)
        ax2.legend()
        ax2.grid(True, alpha=0.3, axis='y')
        ax2.set_facecolor('#FAFAFA')
    
    # 子图3: 解密吞吐量对比
    decrypt_data = df[df['operation'] == 'decrypt']
    if not decrypt_data.empty:
        decrypt_schemes = decrypt_data['scheme'].unique()
        
        for i, msg_type in enumerate(message_types):
            throughputs = []
            for scheme in decrypt_schemes:
                scheme_data = decrypt_data[(decrypt_data['scheme'] == scheme) & 
                                         (decrypt_data['message_type'] == msg_type)]
                if not scheme_data.empty:
                    time = scheme_data['time'].values[0]
                    data_size = scheme_data['data_size'].values[0]
                    throughput = data_size / time  # 字节/秒
                    throughputs.append(throughput)
                else:
                    throughputs.append(0)
            
            bars = ax3.bar(x + i*width, throughputs, width, label=msg_type, 
                          alpha=0.8, edgecolor='white', linewidth=1)
        
        ax3.set_title('解密吞吐量对比', fontsize=14, fontweight='bold', pad=15)
        ax3.set_ylabel('吞吐量 (字节/秒)', fontsize=12)
        ax3.set_xticks(x + width)
        ax3.set_xticklabels(decrypt_schemes, rotation=45)
        ax3.legend()
        ax3.grid(True, alpha=0.3, axis='y')
        ax3.set_facecolor('#FAFAFA')
    
    # 子图4: IBE综合性能雷达图
    valid_schemes = []
    scheme_scores = {}
    
    # 过滤有效方案（有加密数据的）
    for scheme in schemes:
        encrypt_scheme_data = encrypt_data[encrypt_data['scheme'] == scheme]
        if not encrypt_scheme_data.empty:
            valid_schemes.append(scheme)
    
    if len(valid_schemes) >= 2:
        categories = ['系统设置', '密钥提取', '加密速度', '解密速度', '整体效率']
        
        for scheme in valid_schemes:
            scores = []
            
            # 系统设置性能（时间越短评分越高）
            setup_data = df[(df['scheme'] == scheme) & (df['operation'] == 'setup')]
            if not setup_data.empty:
                setup_time = setup_data['time'].values[0]
                setup_score = min(100 / (setup_time * 1000 + 0.001), 100)
                scores.append(setup_score)
            else:
                scores.append(50)
            
            # 密钥提取性能
            extract_scheme_data = df[(df['scheme'] == scheme) & (df['operation'] == 'extract')]
            if not extract_scheme_data.empty:
                extract_time = extract_scheme_data['time'].mean()
                extract_score = min(100 / (extract_time * 10 + 0.001), 100)
                scores.append(extract_score)
            else:
                scores.append(0)
            
            # 加密性能
            encrypt_scheme_data = df[(df['scheme'] == scheme) & (df['operation'] == 'encrypt')]
            if not encrypt_scheme_data.empty:
                encrypt_time = encrypt_scheme_data['time'].mean()
                encrypt_score = min(100 / (encrypt_time * 10 + 0.001), 100)
                scores.append(encrypt_score)
            else:
                scores.append(0)
            
            # 解密性能
            decrypt_scheme_data = df[(df['scheme'] == scheme) & (df['operation'] == 'decrypt')]
            if not decrypt_scheme_data.empty:
                decrypt_time = decrypt_scheme_data['time'].mean()
                decrypt_score = min(100 / (decrypt_time * 100 + 0.001), 100)
                scores.append(decrypt_score)
            else:
                scores.append(0)
            
            # 整体效率（综合评分）
            overall_score = np.mean(scores)
            scores.append(overall_score)
            
            scheme_scores[scheme] = scores
        
        # 创建雷达图
        angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
        angles += angles[:1]  # 闭合图形
        
        ax4 = plt.subplot(2, 2, 4, projection='polar')
        ax4.set_facecolor('#FAFAFA')
        
        for i, scheme in enumerate(valid_schemes):
            values = scheme_scores[scheme]
            values += values[:1]  # 闭合图形
            
            ax4.plot(angles, values, 'o-', linewidth=2.5, label=scheme, 
                    color=IBE_COLORS[scheme], markersize=6)
            ax4.fill(angles, values, alpha=0.25, color=IBE_COLORS[scheme])
        
        ax4.set_xticks(angles[:-1])
        ax4.set_xticklabels(categories, fontsize=10)
        ax4.set_ylim(0, 100)
        ax4.set_title('综合性能雷达图', fontsize=14, fontweight='bold', pad=20)
        ax4.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0))
        ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('results/ibe_only_efficiency_analysis.png', dpi=300, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()
    print("✅ IBE效率分析图已保存: results/ibe_only_efficiency_analysis.png")

def create_ibe_message_scalability(df):
    """
    创建IBE消息长度适应性分析
    展示不同消息类型下的性能变化
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    fig.suptitle('IBE算法消息规模适应性分析', fontsize=18, fontweight='bold', y=0.95)
    
    encrypt_data = df[df['operation'] == 'encrypt']
    decrypt_data = df[df['operation'] == 'decrypt']
    
    if not encrypt_data.empty and not decrypt_data.empty:
        schemes = encrypt_data['scheme'].unique()
        message_types = encrypt_data['message_type'].unique()
        colors = [IBE_COLORS[scheme] for scheme in schemes]
        
        # 获取消息大小作为X轴
        message_sizes = []
        for msg_type in message_types:
            size_data = encrypt_data[encrypt_data['message_type'] == msg_type]['data_size'].values
            if len(size_data) > 0:
                message_sizes.append(size_data[0])
            else:
                message_sizes.append(0)
        
        # 子图1: 加密性能随消息大小变化
        for i, scheme in enumerate(schemes):
            encrypt_times = []
            for msg_type in message_types:
                scheme_msg_data = encrypt_data[(encrypt_data['scheme'] == scheme) & 
                                             (encrypt_data['message_type'] == msg_type)]
                if not scheme_msg_data.empty:
                    time = scheme_msg_data['time'].values[0] * 1000  # 转换为毫秒
                    encrypt_times.append(time)
                else:
                    encrypt_times.append(0)
            
            ax1.plot(message_sizes, encrypt_times, 'o-', linewidth=3, markersize=8,
                    label=scheme, color=colors[i], alpha=0.8)
            
            # 添加数值标签
            for x, y in zip(message_sizes, encrypt_times):
                if y > 0:
                    ax1.annotate(f'{y:.1f}ms', (x, y), textcoords="offset points", 
                                xytext=(0,10), ha='center', fontsize=9, fontweight='bold')
        
        ax1.set_title('加密性能vs消息大小', fontsize=14, fontweight='bold', pad=15)
        ax1.set_xlabel('消息大小 (字节)', fontsize=12)
        ax1.set_ylabel('加密时间 (毫秒)', fontsize=12)
        ax1.grid(True, alpha=0.3)
        ax1.legend()
        ax1.set_facecolor('#FAFAFA')
        
        # 子图2: 解密性能随消息大小变化
        for i, scheme in enumerate(schemes):
            decrypt_times = []
            for msg_type in message_types:
                scheme_msg_data = decrypt_data[(decrypt_data['scheme'] == scheme) & 
                                             (decrypt_data['message_type'] == msg_type)]
                if not scheme_msg_data.empty:
                    time = scheme_msg_data['time'].values[0] * 1000  # 转换为毫秒
                    decrypt_times.append(time)
                else:
                    decrypt_times.append(0)
            
            ax2.plot(message_sizes, decrypt_times, 'o-', linewidth=3, markersize=8,
                    label=scheme, color=colors[i], alpha=0.8)
            
            # 添加数值标签
            for x, y in zip(message_sizes, decrypt_times):
                if y > 0:
                    ax2.annotate(f'{y:.3f}ms', (x, y), textcoords="offset points", 
                                xytext=(0,10), ha='center', fontsize=9, fontweight='bold')
        
        ax2.set_title('解密性能vs消息大小', fontsize=14, fontweight='bold', pad=15)
        ax2.set_xlabel('消息大小 (字节)', fontsize=12)
        ax2.set_ylabel('解密时间 (毫秒)', fontsize=12)
        ax2.grid(True, alpha=0.3)
        ax2.legend()
        ax2.set_facecolor('#FAFAFA')
    
    plt.tight_layout()
    plt.savefig('results/ibe_only_message_scalability.png', dpi=300, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()
    print("✅ IBE消息适应性分析图已保存: results/ibe_only_message_scalability.png")

def generate_ibe_summary_report(df):
    """生成IBE算法详细性能报告"""
    print("\n" + "="*70)
    print("IBE算法专项性能分析报告")
    print("="*70)
    
    schemes = df['scheme'].unique()
    
    for scheme in schemes:
        print(f"\n🔐 {scheme} 详细分析:")
        
        # 系统设置性能
        setup_data = df[(df['scheme'] == scheme) & (df['operation'] == 'setup')]
        if not setup_data.empty:
            setup_time = setup_data['time'].values[0] * 1000
            print(f"  系统设置: {setup_time:.3f} 毫秒")
        
        # 密钥提取性能
        extract_data = df[(df['scheme'] == scheme) & (df['operation'] == 'extract')]
        if not extract_data.empty:
            avg_extract = extract_data['time'].mean() * 1000
            extract_rate = 1000 / avg_extract  # 密钥/秒
            print(f"  密钥提取: {avg_extract:.2f} 毫秒 (平均), 提取率: {extract_rate:.1f} 密钥/秒")
        
        # 加密解密性能
        encrypt_data = df[(df['scheme'] == scheme) & (df['operation'] == 'encrypt')]
        decrypt_data = df[(df['scheme'] == scheme) & (df['operation'] == 'decrypt')]
        
        if not encrypt_data.empty:
            avg_encrypt = encrypt_data['time'].mean() * 1000
            print(f"  加密性能: {avg_encrypt:.2f} 毫秒 (平均)")
            
            # 计算各消息类型的吞吐量
            message_types = encrypt_data['message_type'].unique()
            for msg_type in message_types:
                msg_data = encrypt_data[encrypt_data['message_type'] == msg_type]
                if not msg_data.empty:
                    time = msg_data['time'].values[0]
                    size = msg_data['data_size'].values[0]
                    throughput = size / time
                    print(f"    {msg_type}吞吐量: {throughput:.0f} 字节/秒")
        
        if not decrypt_data.empty:
            avg_decrypt = decrypt_data['time'].mean() * 1000
            print(f"  解密性能: {avg_decrypt:.3f} 毫秒 (平均)")
    
    print(f"\n🎯 IBE算法选择建议:")
    print(f"  • Sakai-Kasahara: 性能最优，适合高性能生产环境")
    print(f"  • Boneh-Boyen: 标准模型安全，适合高安全等级需求")
    print(f"  • Boneh-Franklin: 经典方案，适合教学研究和原型开发")
    
    print(f"\n📊 前端显示建议:")
    print(f"  • 图表尺寸: 16:10比例，适合现代显示器")
    print(f"  • 配色方案: 红色(Boneh-Franklin)、蓝色(Boneh-Boyen)、绿色(Sakai-Kasahara)")
    print(f"  • 布局方式: 2x2网格布局，便于卡片式展示")
    print(f"  • 交互建议: 支持消息类型筛选，悬停显示详细指标")

def main():
    """主函数，执行IBE专项性能分析"""
    print("=== IBE算法专项性能分析 ===")
    
    # 加载数据
    df = load_ibe_data()
    if df is None:
        return
    
    # 确保结果目录存在
    os.makedirs('results', exist_ok=True)
    
    print("\n🎨 生成IBE专项分析图表...")
    
    # 生成各种IBE专项图表
    create_ibe_performance_overview(df)
    create_ibe_efficiency_analysis(df)
    create_ibe_message_scalability(df)
    
    # 生成分析报告
    generate_ibe_summary_report(df)
    
    print(f"\n🎉 IBE专项分析完成！")
    print(f"生成的图表:")
    print(f"  • ibe_only_performance_overview.png - IBE性能全景图 (2x2布局)")
    print(f"  • ibe_only_efficiency_analysis.png - IBE效率分析图 (2x2布局)")  
    print(f"  • ibe_only_message_scalability.png - IBE消息适应性分析 (1x2布局)")
    print(f"\n💡 前端集成提示:")
    print(f"  • 所有图表采用16:10或16:6比例，适合响应式设计")
    print(f"  • 使用统一配色方案，便于用户识别不同算法")
    print(f"  • 图表背景为白色，便于在各种主题下显示")

if __name__ == '__main__':
    main() 