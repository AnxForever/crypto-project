# -*- coding: utf-8 -*-

"""
PKE方案应用案例演示
展示ECC、ElGamal和SM2在不同场景下的实际应用
"""

import sys
import os
import time
import json

# 添加源代码路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

# 导入各个PKE方案
import pke.ecc_scheme as ecc
import pke.elgamal_scheme as elgamal
import pke.sm2_scheme as sm2

class SecureMessageSystem:
    """安全消息传输系统演示"""
    
    def __init__(self, crypto_scheme):
        self.scheme_name = crypto_scheme.__name__.split('.')[-1].upper()
        self.generate_keys = crypto_scheme.generate_keys
        self.encrypt = crypto_scheme.encrypt
        self.decrypt = crypto_scheme.decrypt
        
        print(f"🔐 初始化 {self.scheme_name} 安全消息系统")
        
        # 生成密钥对
        if 'elgamal' in crypto_scheme.__name__:
            self.private_key, self.public_key = self.generate_keys(key_size=512)
        else:
            self.private_key, self.public_key = self.generate_keys()
    
    def send_message(self, message, recipient_name="Alice"):
        """发送加密消息"""
        print(f"\n📤 {recipient_name} 发送消息 (使用 {self.scheme_name})")
        
        # ElGamal消息长度限制处理
        if 'ELGAMAL' in self.scheme_name and len(message.encode('utf-8')) > 50:
            original_message = message
            message = "机密文件摘要：新产品计划"
            print(f"原始消息: {original_message}")
            print(f"⚠️  ElGamal消息长度限制，使用简化消息: {message}")
        else:
            print(f"原始消息: {message}")
        
        start_time = time.time()
        ciphertext = self.encrypt(self.public_key, message.encode('utf-8'))
        encrypt_time = time.time() - start_time
        
        print(f"✅ 加密完成，耗时: {encrypt_time:.6f}秒")
        print(f"密文长度: {len(ciphertext)} 字节")
        print(f"密文预览: {ciphertext.hex()[:64]}...")
        
        return ciphertext, message  # 返回消息用于验证
    
    def receive_message(self, ciphertext, recipient_name="Bob"):
        """接收并解密消息"""
        print(f"\n📥 {recipient_name} 接收消息 (使用 {self.scheme_name})")
        
        start_time = time.time()
        try:
            plaintext = self.decrypt(self.private_key, ciphertext)
            decrypt_time = time.time() - start_time
            
            message = plaintext.decode('utf-8')
            print(f"✅ 解密成功，耗时: {decrypt_time:.6f}秒")
            print(f"解密消息: {message}")
            return message
        except Exception as e:
            print(f"❌ 解密失败: {e}")
            return None

def scenario_1_secure_communication():
    """场景1: 安全通信演示"""
    print("="*60)
    print("🔥 场景1: 安全通信系统演示")
    print("模拟Alice向Bob发送机密文件的场景")
    print("="*60)
    
    message = "机密文件：新产品发布计划 - 绝密级别信息，请勿外传！"
    
    # 使用三种不同的加密方案
    schemes = [
        ("ECC (ECIES)", ecc),
        ("SM2 (国密)", sm2),
        ("ElGamal", elgamal)
    ]
    
    for scheme_name, scheme_module in schemes:
        print(f"\n🚀 使用 {scheme_name} 进行安全通信:")
        
        # 创建消息系统
        msg_system = SecureMessageSystem(scheme_module)
        
        # Alice发送消息
        result = msg_system.send_message(message, "Alice")
        if isinstance(result, tuple):
            ciphertext, actual_message = result
        else:
            ciphertext, actual_message = result, message
        
        # Bob接收消息
        received_msg = msg_system.receive_message(ciphertext, "Bob")
        
        # 验证消息完整性
        if received_msg == actual_message:
            print("🎉 消息传输成功，完整性验证通过！")
        else:
            print("❌ 消息传输失败或数据损坏！")

def scenario_2_file_encryption():
    """场景2: 文件加密演示"""
    print("\n" + "="*60)
    print("📁 场景2: 重要文件加密保护")
    print("模拟对敏感文档进行加密存储的场景")
    print("="*60)
    
    # 模拟文件内容
    file_content = {
        "document_type": "财务报表",
        "classification": "机密",
        "content": "公司Q4财务数据: 营收1.2亿，利润3000万",
        "access_level": "高级管理层",
        "create_time": "2024-01-15 14:30:00"
    }
    
    file_data = json.dumps(file_content, ensure_ascii=False, indent=2)
    print(f"📄 待加密文件内容:\n{file_data}")
    
    # 对比不同方案的加密效果
    schemes = [ecc, sm2, elgamal]
    scheme_names = ["ECC", "SM2", "ElGamal"]
    
    print(f"\n📊 加密方案对比:")
    print(f"{'方案':<10} {'加密时间':<12} {'密文大小':<12} {'解密时间':<12}")
    print("-" * 50)
    
    for scheme, name in zip(schemes, scheme_names):
        try:
            # 生成密钥
            if name == "ElGamal":
                private_key, public_key = scheme.generate_keys(key_size=512)
                # ElGamal消息长度限制，使用较短内容
                test_data = "财务数据:营收1.2亿"
            else:
                private_key, public_key = scheme.generate_keys()
                test_data = file_data
            
            # 加密测试
            start = time.time()
            ciphertext = scheme.encrypt(public_key, test_data.encode('utf-8'))
            encrypt_time = time.time() - start
            
            # 解密测试
            start = time.time()
            decrypted = scheme.decrypt(private_key, ciphertext)
            decrypt_time = time.time() - start
            
            print(f"{name:<10} {encrypt_time:<12.6f} {len(ciphertext):<12} {decrypt_time:<12.6f}")
            
        except Exception as e:
            print(f"{name:<10} {'错误':<12} {'N/A':<12} {'N/A':<12}")

def scenario_3_multi_user_system():
    """场景3: 多用户密钥管理演示"""
    print("\n" + "="*60)
    print("👥 场景3: 企业多用户密钥管理系统")
    print("模拟企业环境下多用户之间的安全通信")
    print("="*60)
    
    # 创建多个用户
    users = ["张三", "李四", "王五"]
    messages = {
        "张三": "项目进度报告：目前完成度85%",
        "李四": "预算申请：需要追加经费50万元",
        "王五": "技术方案：建议采用新的架构设计"
    }
    
    print("🔐 使用SM2国密算法建立企业安全通信网络")
    
    # 为每个用户生成密钥对
    user_keys = {}
    for user in users:
        private_key, public_key = sm2.generate_keys()
        user_keys[user] = {
            'private_key': private_key,
            'public_key': public_key
        }
        print(f"✅ 为用户 {user} 生成密钥对")
    
    print(f"\n📡 模拟用户间消息传递:")
    
    # 模拟消息传递
    for sender in users:
        for receiver in users:
            if sender != receiver:
                message = f"来自{sender}的消息: {messages[sender]}"
                
                # 发送方用接收方公钥加密
                ciphertext = sm2.encrypt(user_keys[receiver]['public_key'], message.encode('utf-8'))
                
                # 接收方用自己私钥解密
                decrypted = sm2.decrypt(user_keys[receiver]['private_key'], ciphertext)
                received_message = decrypted.decode('utf-8')
                
                print(f"📤 {sender} → {receiver}: 消息长度 {len(message)} → 密文 {len(ciphertext)}字节")
                break  # 每个发送方只演示一次传输

def scenario_4_performance_analysis():
    """场景4: 性能需求分析"""
    print("\n" + "="*60)
    print("⚡ 场景4: 不同应用场景的性能需求分析")
    print("分析三种方案在不同应用场景下的适用性")
    print("="*60)
    
    scenarios = [
        {
            "name": "实时通信",
            "requirements": "低延迟，中等安全性",
            "data_size": 100,
            "frequency": "高频",
            "priority": "速度"
        },
        {
            "name": "文件传输",
            "requirements": "高安全性，可接受延迟",
            "data_size": 1000,
            "frequency": "中频",
            "priority": "安全"
        },
        {
            "name": "国密合规",
            "requirements": "符合国家标准",
            "data_size": 500,
            "frequency": "低频",
            "priority": "合规"
        }
    ]
    
    for scenario in scenarios:
        print(f"\n📋 场景: {scenario['name']}")
        print(f"   需求: {scenario['requirements']}")
        print(f"   数据量: ~{scenario['data_size']}字节")
        print(f"   使用频率: {scenario['frequency']}")
        
        # 给出推荐方案
        if scenario["priority"] == "速度":
            print(f"   🏆 推荐方案: SM2 (密钥生成快，解密快)")
        elif scenario["priority"] == "安全":
            print(f"   🏆 推荐方案: ECC (成熟技术，广泛应用)")
        elif scenario["priority"] == "合规":
            print(f"   🏆 推荐方案: SM2 (国密标准，政府推荐)")

def main():
    """主函数"""
    print("🚀 PKE公钥加密方案应用案例演示")
    print("本演示将展示ECC、ElGamal、SM2在实际场景中的应用")
    
    try:
        # 场景1: 安全通信
        scenario_1_secure_communication()
        
        # 场景2: 文件加密
        scenario_2_file_encryption()
        
        # 场景3: 多用户系统
        scenario_3_multi_user_system()
        
        # 场景4: 性能分析
        scenario_4_performance_analysis()
        
        print("\n" + "="*60)
        print("🎉 所有应用案例演示完成！")
        print("📊 总结:")
        print("   • ECC: 适用于通用安全通信，技术成熟")
        print("   • SM2: 适用于国密合规场景，性能优秀")  
        print("   • ElGamal: 适用于理论研究，消息长度有限制")
        print("="*60)
        
    except Exception as e:
        print(f"❌ 演示过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main() 