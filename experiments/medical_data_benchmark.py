# -*- coding: utf-8 -*-

"""
基于真实医疗数据的加密性能测试

本脚本使用真实的医疗数据格式和内容来测试PKE和IBE算法的性能，
替代之前基于随机数据的测试，提供更真实的应用场景评估。
"""

import time
import os
import pandas as pd
import sys
import json
from datetime import datetime, timedelta
import random

# 将项目根目录添加到Python路径中
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

# 导入算法模块
from src.pke import ecc_scheme, elgamal_scheme, sm2_scheme
from src.ibe import get_scheme as get_ibe_scheme

# === 真实医疗数据生成器 ===

class MedicalDataGenerator:
    """生成符合真实医疗标准的测试数据"""
    
    def __init__(self):
        self.patient_names = [
            "张三", "李四", "王五", "赵六", "陈七", "刘八", "杨九", "黄十",
            "周一", "吴二", "郑三", "王四", "冯五", "陈六", "褚七", "卫八"
        ]
        
        self.diagnoses = [
            "高血压", "糖尿病", "冠心病", "脑梗塞", "肺炎", "胃炎", 
            "肝炎", "肾炎", "关节炎", "骨折", "白内障", "阑尾炎"
        ]
        
        self.medications = [
            "阿司匹林", "美托洛尔", "硝苯地平", "二甲双胍", "胰岛素",
            "阿托伐他汀", "氯吡格雷", "培哚普利", "氨氯地平", "瑞舒伐他汀"
        ]
        
        self.departments = [
            "心内科", "内分泌科", "神经内科", "呼吸内科", "消化内科",
            "肾内科", "骨科", "眼科", "普外科", "急诊科"
        ]

    def generate_patient_id(self):
        """生成患者ID（16字节）"""
        return f"P{random.randint(100000000000, 999999999999)}"
    
    def generate_doctor_identity(self):
        """生成医生身份标识（用于IBE）"""
        dept = random.choice(self.departments)
        doc_id = f"DOC{random.randint(1000, 9999)}"
        return f"{doc_id}@{dept}.hospital.com"
    
    def generate_prescription_data(self, size_category="small"):
        """生成处方数据"""
        data = {
            "prescription_id": f"RX{random.randint(100000, 999999)}",
            "patient_id": self.generate_patient_id(),
            "doctor_id": f"DOC{random.randint(1000, 9999)}",
            "department": random.choice(self.departments),
            "date": (datetime.now() - timedelta(days=random.randint(0, 365))).strftime("%Y-%m-%d"),
            "medications": []
        }
        
        # 根据大小类别添加不同数量的药物
        if size_category == "small":  # ~100-500字节
            med_count = random.randint(1, 3)
        elif size_category == "medium":  # ~500-2000字节
            med_count = random.randint(3, 8)
        else:  # large, ~2000-5000字节
            med_count = random.randint(8, 15)
        
        for _ in range(med_count):
            medication = {
                "name": random.choice(self.medications),
                "dosage": f"{random.randint(25, 500)}mg",
                "frequency": f"每日{random.randint(1, 3)}次",
                "duration": f"{random.randint(3, 30)}天",
                "instructions": "饭后服用" if random.random() > 0.5 else "空腹服用"
            }
            data["medications"].append(medication)
        
        return json.dumps(data, ensure_ascii=False).encode('utf-8')
    
    def generate_lab_report(self, size_category="medium"):
        """生成检验报告数据"""
        data = {
            "report_id": f"LAB{random.randint(100000, 999999)}",
            "patient_id": self.generate_patient_id(),
            "test_date": (datetime.now() - timedelta(days=random.randint(0, 30))).strftime("%Y-%m-%d %H:%M:%S"),
            "test_type": "血常规检查",
            "results": {}
        }
        
        # 基础检验项目
        basic_tests = {
            "白细胞计数": f"{random.uniform(4.0, 10.0):.1f} (×10^9/L)",
            "红细胞计数": f"{random.uniform(3.5, 5.5):.2f} (×10^12/L)",
            "血红蛋白": f"{random.randint(110, 180)} g/L",
            "血小板计数": f"{random.randint(100, 450)} (×10^9/L)",
            "血糖": f"{random.uniform(3.9, 6.1):.1f} mmol/L"
        }
        
        if size_category == "small":  # ~200-800字节
            selected_tests = dict(list(basic_tests.items())[:3])
        elif size_category == "medium":  # ~800-3000字节
            selected_tests = basic_tests.copy()
            # 添加生化指标
            selected_tests.update({
                "总胆固醇": f"{random.uniform(3.1, 5.7):.2f} mmol/L",
                "甘油三酯": f"{random.uniform(0.5, 1.7):.2f} mmol/L",
                "肌酐": f"{random.randint(44, 133)} μmol/L",
                "尿素氮": f"{random.uniform(2.5, 7.1):.1f} mmol/L"
            })
        else:  # large, ~3000-10000字节
            selected_tests = basic_tests.copy()
            # 添加完整生化面板
            for i in range(20):
                test_name = f"检验项目_{i+1}"
                selected_tests[test_name] = f"{random.uniform(10, 100):.2f} {random.choice(['mmol/L', 'g/L', 'U/L'])}"
        
        data["results"] = selected_tests
        data["interpretation"] = "检验结果在正常范围内" if random.random() > 0.3 else "部分指标异常，建议复查"
        
        return json.dumps(data, ensure_ascii=False).encode('utf-8')
    
    def generate_medical_image_metadata(self, size_category="large"):
        """生成医疗影像元数据（模拟）"""
        data = {
            "image_id": f"IMG{random.randint(100000, 999999)}",
            "patient_id": self.generate_patient_id(),
            "study_date": (datetime.now() - timedelta(days=random.randint(0, 180))).strftime("%Y-%m-%d"),
            "modality": random.choice(["CT", "MRI", "X-Ray", "Ultrasound"]),
            "body_part": random.choice(["胸部", "腹部", "头部", "四肢"]),
            "clinical_info": f"患者主诉{random.choice(['胸痛', '腹痛', '头痛', '关节疼痛'])}"
        }
        
        # 模拟影像报告文本
        if size_category == "medium":  # ~1-5KB
            report_text = "影像学检查显示：器官结构清晰，未见明显异常密度影。" * random.randint(10, 50)
        else:  # large, ~5-20KB
            report_text = """
            详细影像学报告：
            1. 扫描技术：采用高分辨率CT扫描，层厚1.25mm，重建间隔1.0mm
            2. 图像质量：图像清晰，对比度良好，无运动伪影
            3. 观察结果：各器官结构显示清楚，密度均匀，轮廓规整
            4. 测量数据：肝脏大小正常，脾脏无肿大，肾脏形态正常
            5. 对比剂使用：碘对比剂增强扫描，动脉期、静脉期及延迟期图像
            """ * random.randint(5, 20)
        
        data["report"] = report_text
        return json.dumps(data, ensure_ascii=False).encode('utf-8')

# === 医疗数据测试函数 ===

def benchmark_pke_with_medical_data():
    """使用医疗数据测试PKE算法性能"""
    print("=== PKE算法医疗数据性能测试 ===")
    
    generator = MedicalDataGenerator()
    results = []
    
    # 测试数据类型定义
    test_cases = [
        ("患者ID", "small", lambda: generator.generate_patient_id().encode('utf-8')),
        ("小处方", "small", lambda: generator.generate_prescription_data("small")),
        ("检验报告", "medium", lambda: generator.generate_lab_report("medium")),
        ("影像报告", "large", lambda: generator.generate_medical_image_metadata("large"))
    ]
    
    algorithms = [
        ("SM2", sm2_scheme),
        ("ECC", ecc_scheme),
        ("ElGamal", elgamal_scheme)
    ]
    
    for algo_name, algo_module in algorithms:
        print(f"\n--- 测试 {algo_name} 算法 ---")
        
        # 密钥生成测试
        start_time = time.perf_counter()
        if algo_name == "ElGamal":
            priv_key, pub_key = algo_module.generate_keys()
        else:
            priv_key, pub_key = algo_module.generate_keys()
        end_time = time.perf_counter()
        key_gen_time = end_time - start_time
        
        results.append({
            'algorithm': algo_name,
            'data_type': '密钥生成',
            'data_category': 'system',
            'data_size': 0,
            'operation': 'key_gen',
            'time': key_gen_time,
            'success': True
        })
        
        # 测试不同类型的医疗数据
        for data_type, category, data_generator in test_cases:
            if algo_name == "ElGamal" and category in ["medium", "large"]:
                # ElGamal有大小限制，跳过大数据测试
                continue
            
            try:
                medical_data = data_generator()
                data_size = len(medical_data)
                
                # 加密测试
                start_time = time.perf_counter()
                ciphertext = algo_module.encrypt(pub_key, medical_data)
                end_time = time.perf_counter()
                encrypt_time = end_time - start_time
                
                # 解密测试
                start_time = time.perf_counter()
                decrypted_data = algo_module.decrypt(priv_key, ciphertext)
                end_time = time.perf_counter()
                decrypt_time = end_time - start_time
                
                # 验证数据完整性
                success = decrypted_data == medical_data
                
                results.extend([
                    {
                        'algorithm': algo_name,
                        'data_type': data_type,
                        'data_category': category,
                        'data_size': data_size,
                        'operation': 'encrypt',
                        'time': encrypt_time,
                        'success': success
                    },
                    {
                        'algorithm': algo_name,
                        'data_type': data_type,
                        'data_category': category,
                        'data_size': data_size,
                        'operation': 'decrypt',
                        'time': decrypt_time,
                        'success': success
                    }
                ])
                
                print(f"  {data_type} ({data_size}B): 加密 {encrypt_time*1000:.3f}ms, 解密 {decrypt_time*1000:.3f}ms")
                
            except Exception as e:
                print(f"  {data_type}: 测试失败 - {str(e)}")
                results.append({
                    'algorithm': algo_name,
                    'data_type': data_type,
                    'data_category': category,
                    'data_size': 0,
                    'operation': 'error',
                    'time': 0,
                    'success': False
                })
    
    return results

def benchmark_ibe_with_medical_data():
    """使用医疗数据测试IBE算法性能"""
    print("\n=== IBE算法医疗数据性能测试 ===")
    
    generator = MedicalDataGenerator()
    results = []
    
    # IBE身份标识测试用例
    identities = [
        ("患者身份证", "330106199001011234"),
        ("医生工号", generator.generate_doctor_identity()),
        ("科室代码", "CARDIO_DEPT_001@hospital.com"),
        ("病历编号", f"MR{random.randint(100000, 999999)}@archive.com")
    ]
    
    # 医疗数据测试用例
    medical_messages = [
        ("处方单", generator.generate_prescription_data("small")),
        ("检验结果", generator.generate_lab_report("small")),
        ("诊断报告", generator.generate_lab_report("medium"))
    ]
    
    schemes = ["sakai_kasahara", "boneh_boyen"]  # 使用正确的方案名称
    
    for scheme_name in schemes:
        display_name = scheme_name.replace("_", "-").title()
        print(f"\n--- 测试 {display_name} 方案 ---")
        
        try:
            scheme = get_ibe_scheme(scheme_name)()
            
            # 系统设置
            start_time = time.perf_counter()
            master_key, public_params = scheme.setup()
            end_time = time.perf_counter()
            setup_time = end_time - start_time
            
            results.append({
                'scheme': scheme_name,
                'identity_type': '系统设置',
                'message_type': 'system',
                'data_size': 0,
                'operation': 'setup',
                'time': setup_time,
                'success': True
            })
            
            # 测试不同身份的密钥提取
            for identity_type, identity in identities:
                start_time = time.perf_counter()
                private_key = scheme.extract(master_key, public_params, identity)
                end_time = time.perf_counter()
                extract_time = end_time - start_time
                
                results.append({
                    'scheme': scheme_name,
                    'identity_type': identity_type,
                    'message_type': 'key_extract',
                    'data_size': len(identity.encode('utf-8')),
                    'operation': 'extract',
                    'time': extract_time,
                    'success': True
                })
                
                # 使用该身份测试医疗数据加密
                for msg_type, medical_data in medical_messages:
                    try:
                        data_size = len(medical_data)
                        
                        # 加密
                        start_time = time.perf_counter()
                        ciphertext = scheme.encrypt(public_params, identity, medical_data)
                        end_time = time.perf_counter()
                        encrypt_time = end_time - start_time
                        
                        # 解密
                        start_time = time.perf_counter()
                        decrypted_data = scheme.decrypt(private_key, ciphertext)
                        end_time = time.perf_counter()
                        decrypt_time = end_time - start_time
                        
                        # 验证
                        success = decrypted_data == medical_data
                        
                        results.extend([
                            {
                                'scheme': scheme_name,
                                'identity_type': identity_type,
                                'message_type': msg_type,
                                'data_size': data_size,
                                'operation': 'encrypt',
                                'time': encrypt_time,
                                'success': success
                            },
                            {
                                'scheme': scheme_name,
                                'identity_type': identity_type,
                                'message_type': msg_type,
                                'data_size': data_size,
                                'operation': 'decrypt',
                                'time': decrypt_time,
                                'success': success
                            }
                        ])
                        
                        print(f"  {identity_type} -> {msg_type} ({data_size}B): 加密 {encrypt_time*1000:.3f}ms, 解密 {decrypt_time*1000:.3f}ms")
                        
                    except Exception as e:
                        print(f"  {identity_type} -> {msg_type}: 失败 - {str(e)}")
                        break  # 如果一个消息失败，跳过该身份的其他消息
                        
        except Exception as e:
            print(f"  {scheme_name} 初始化失败: {str(e)}")
    
    return results

def main():
    """主函数"""
    print("🏥 基于真实医疗数据的加密算法性能测试")
    print("=" * 60)
    
    # 创建结果目录
    results_dir = "results"
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)
    
    # PKE测试
    pke_results = benchmark_pke_with_medical_data()
    pke_df = pd.DataFrame(pke_results)
    pke_output = os.path.join(results_dir, "pke_medical_performance.csv")
    pke_df.to_csv(pke_output, index=False, encoding='utf-8-sig')
    print(f"\n✅ PKE医疗数据测试结果保存到: {pke_output}")
    
    # IBE测试
    ibe_results = benchmark_ibe_with_medical_data()
    ibe_df = pd.DataFrame(ibe_results)
    ibe_output = os.path.join(results_dir, "ibe_medical_performance.csv")
    ibe_df.to_csv(ibe_output, index=False, encoding='utf-8-sig')
    print(f"✅ IBE医疗数据测试结果保存到: {ibe_output}")
    
    # 生成总结报告
    print("\n" + "=" * 60)
    print("📊 医疗数据加密性能总结")
    print("=" * 60)
    
    # PKE总结
    print("\n🔐 PKE算法在医疗数据上的表现:")
    successful_pke = pke_df[pke_df['success'] == True]
    for algo in successful_pke['algorithm'].unique():
        algo_data = successful_pke[successful_pke['algorithm'] == algo]
        avg_encrypt = algo_data[algo_data['operation'] == 'encrypt']['time'].mean() * 1000
        avg_decrypt = algo_data[algo_data['operation'] == 'decrypt']['time'].mean() * 1000
        print(f"  {algo}: 平均加密 {avg_encrypt:.3f}ms, 平均解密 {avg_decrypt:.3f}ms")
    
    # IBE总结
    print("\n🆔 IBE算法在医疗数据上的表现:")
    successful_ibe = ibe_df[ibe_df['success'] == True]
    for scheme in successful_ibe['scheme'].unique():
        scheme_data = successful_ibe[successful_ibe['scheme'] == scheme]
        avg_encrypt = scheme_data[scheme_data['operation'] == 'encrypt']['time'].mean() * 1000
        avg_decrypt = scheme_data[scheme_data['operation'] == 'decrypt']['time'].mean() * 1000
        print(f"  {scheme}: 平均加密 {avg_encrypt:.3f}ms, 平均解密 {avg_decrypt:.3f}ms")
    
    print(f"\n🎉 医疗数据加密测试完成！")
    print(f"💡 下一步: 可以运行 medical_data_analysis.py 生成可视化分析")

if __name__ == '__main__':
    main() 