# 密码学课程设计：PKE与IBE体制的深度解析与实现

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-green.svg)
![Status](https://img.shields.io/badge/status-完成-brightgreen.svg)

## 📖 项目概述

本项目是一个完整的密码学课程设计实现，深入研究和对比了两种核心的公钥密码体制：**公钥加密（PKE）**和**基于身份的加密（IBE）**。项目不仅实现了多种经典加密方案，还提供了全面的性能评测、可视化分析和实际应用案例演示。

### 🎯 项目目标

1. **理论学习**：深入理解PKE和IBE的核心工作原理和数学基础
2. **实践实现**：编程实现6种具体的加密方案（3种PKE + 3种IBE）
3. **性能评测**：通过科学的实验设计，量化分析各方案的性能特点
4. **应用案例**：设计贴近真实场景的应用演示
5. **对比分析**：全面比较PKE和IBE在不同维度上的优劣

## ✨ 核心功能特性

### 🔐 PKE（公钥加密）方案实现

- **ECC (椭圆曲线加密)**
  - 基于椭圆曲线离散对数难题
  - 使用ECIES混合加密方案
  - 支持任意大小数据加密
  - 密钥长度短，安全性高

- **ElGamal加密**
  - 基于离散对数难题
  - 概率性加密，语义安全
  - 适合理论研究和小数据加密
  - 密钥生成相对较快

- **SM2国密算法**
  - 中国国家密码标准
  - 基于椭圆曲线密码体制
  - 综合性能优秀
  - 符合国产化要求

### 📊 性能评测系统

- **多维度性能指标**
  - 密钥生成时间
  - 加密/解密速度
  - 密文大小分析
  - 不同数据量的性能表现

- **可视化分析**
  - 密钥生成性能对比图
  - 加密性能对比图表
  - 综合性能热力图
  - 效率分析图表

- **统计分析**
  - 多次测试取平均值
  - 性能评分计算
  - CSV格式数据导出

### 🎮 应用案例演示

- **安全通信系统**
  - 模拟Alice与Bob的机密消息传输
  - 三种加密方案的实际应用对比
  - 消息完整性验证

- **文件加密保护**
  - 重要文档的加密存储
  - 不同方案的加密效果对比
  - 适用场景分析

- **多用户密钥管理**
  - 企业级多用户安全通信网络
  - 密钥分发和管理演示
  - 用户间安全消息传递

- **性能需求分析**
  - 不同应用场景的性能要求
  - 方案选择建议
  - 实时通信、文件传输、合规性等场景

## 🚀 快速开始

### 环境要求

- Python 3.8+
- Windows 10/11 (项目在Windows环境下开发和测试)
- 至少 2GB 可用内存
- 100MB 磁盘空间

### 安装步骤

1. **克隆项目**
```bash
git clone <项目地址>
cd practice
```

2. **激活虚拟环境**
```powershell
# Windows PowerShell
.\venv\Scripts\Activate.ps1
```

3. **验证依赖**
```powershell
python -m pip list
```

项目已预装所需依赖：
- `pycryptodome` - 密码学算法库
- `eciespy` - 椭圆曲线集成加密
- `gmssl` - 国密SM2算法
- `matplotlib` - 图表绘制
- `pandas` - 数据分析
- `numpy` - 数值计算

## 📋 使用指南

### 1. 运行完整性能测试

```powershell
# 激活虚拟环境
.\venv\Scripts\Activate.ps1

# 运行PKE性能基准测试
python experiments/pke_benchmark.py

# 生成性能分析图表
python experiments/performance_analysis.py
```

### 2. 运行应用案例演示

```powershell
# 运行完整的应用案例演示
python experiments/pke_application_demo.py
```

### 3. 单独测试各个方案

```powershell
# 测试SM2方案
python test_sm2.py

# 测试ECC方案
python -c "from src.pke import ecc_scheme; ecc_scheme.test_encryption()"

# 测试ElGamal方案
python -c "from src.pke import elgamal_scheme; elgamal_scheme.test_encryption()"
```

### 4. 查看测试结果

```powershell
# 查看生成的文件
ls results/

# 主要输出文件：
# - pke_performance.csv           # 性能数据
# - key_generation_comparison.png # 密钥生成对比
# - encryption_performance.png    # 加密性能对比
# - performance_heatmap.png       # 综合性能热力图
# - efficiency_analysis.png       # 效率分析图
```

## 📈 性能测试结果

### 综合性能对比

| 加密方案 | 密钥生成时间(秒) | 平均加密时间(秒) | 平均解密时间(秒) | 平均密文大小(字节) | 性能评分 |
|----------|------------------|------------------|------------------|-------------------|----------|
| **SM2**  | 0.000013         | 0.0003           | 0.00007          | 608               | ⭐⭐⭐⭐⭐ |
| **ECC**  | 0.212            | 0.0013           | 0.0008           | 673               | ⭐⭐⭐⭐ |
| **ElGamal** | 0.049         | 0.0031           | 0.0020           | 136               | ⭐⭐⭐ |

### 关键发现

1. **SM2国密算法**表现最优
   - 密钥生成速度极快（0.013毫秒）
   - 加解密速度优秀
   - 适合高频次密钥生成场景

2. **ECC椭圆曲线加密**通用性最强
   - 支持任意大小数据加密
   - 安全性高，应用广泛
   - 适合通用安全通信

3. **ElGamal加密**理论价值高
   - 密钥生成相对较快
   - 密文大小最小
   - 但受消息长度限制

### 适用场景建议

- **实时通信**：推荐 SM2（低延迟，高性能）
- **文件传输**：推荐 ECC（高安全性，支持大文件）
- **国密合规**：推荐 SM2（符合国家标准）
- **理论研究**：推荐 ElGamal（经典算法，教学价值高）

## 📁 项目结构

```
practice/
├── src/                          # 核心源代码
│   └── pke/                      # PKE方案实现
│       ├── ecc_scheme.py         # ECC椭圆曲线加密
│       ├── elgamal_scheme.py     # ElGamal加密
│       └── sm2_scheme.py         # SM2国密算法
├── experiments/                  # 实验和测试脚本
│   ├── pke_benchmark.py          # PKE性能基准测试
│   ├── performance_analysis.py   # 性能分析和可视化
│   └── pke_application_demo.py   # 应用案例演示
├── results/                      # 测试结果和图表
│   ├── pke_performance.csv       # 性能数据
│   ├── *.png                     # 可视化图表
│   └── performance_summary.csv   # 性能总结
├── venv/                         # Python虚拟环境
├── requirements.txt              # 依赖列表
├── test_sm2.py                   # SM2单独测试
├── 密码学课设最终报告.md         # 详细技术报告
└── README.md                     # 项目说明文档
```

## 🔧 开发指南

### 添加新的加密方案

1. 在 `src/pke/` 目录下创建新的方案文件
2. 实现标准接口：
   ```python
   def generate_keys():
       """生成密钥对"""
       pass
   
   def encrypt(public_key, message):
       """加密函数"""
       pass
   
   def decrypt(private_key, ciphertext):
       """解密函数"""
       pass
   ```

3. 在测试脚本中添加对应的评测函数

### 自定义性能测试

修改 `experiments/pke_benchmark.py` 中的参数：
```python
# 测试数据大小
DATA_SIZES = [16, 128, 1024, 1024 * 10]

# 测试迭代次数
NUM_ITERATIONS = 10
```

## 🐛 故障排除

### 常见问题

1. **ModuleNotFoundError: No module named 'ecies'**
   ```powershell
   # 解决方案：确保激活虚拟环境
   .\venv\Scripts\Activate.ps1
   ```

2. **ElGamal消息长度限制错误**
   ```
   ValueError: 消息太大，需要分块处理
   ```
   - 原因：ElGamal使用512位密钥，只能处理小于64字节的消息
   - 解决：使用更小的测试数据或增大密钥长度

3. **图表显示中文乱码**
   ```python
   # 已在代码中设置中文字体
   plt.rcParams['font.sans-serif'] = ['SimHei']
   ```

### 性能优化建议

1. **减少测试迭代次数**：修改 `NUM_ITERATIONS` 参数
2. **使用更小的密钥长度**：在测试环境中使用512位而非2048位
3. **并行测试**：可以考虑使用多线程进行性能测试

## 📚 技术文档

详细的技术实现和理论分析请参考：
- [`密码学课设最终报告.md`](密码学课设最终报告.md) - 完整的技术报告
- 各方案源代码中的详细注释
- `results/` 目录下的性能分析图表

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 👨‍💻 作者

- **项目作者** - 密码学课程设计
- **指导老师** - AI助手导师

## 🙏 致谢

- 感谢 `pycryptodome` 提供的密码学算法实现
- 感谢 `eciespy` 提供的椭圆曲线集成加密方案
- 感谢 `gmssl` 提供的国密算法支持
- 感谢所有开源贡献者的努力

## 📞 联系方式

如有问题或建议，请通过以下方式联系：
- 提交 GitHub Issue
- 发送邮件至项目维护者

---

**⚡ 快速开始命令**
```powershell
.\venv\Scripts\Activate.ps1
python experiments/pke_benchmark.py
python experiments/performance_analysis.py
python experiments/pke_application_demo.py
```

🎉 **祝你在密码学的学习之旅中收获满满！**
