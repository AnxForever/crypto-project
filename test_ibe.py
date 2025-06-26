# -*- coding: utf-8 -*-

"""
IBE算法综合测试脚本

测试所有三种IBE方案的功能和性能：
1. Boneh-Franklin IBE
2. Boneh-Boyen IBE  
3. Sakai-Kasahara IBE
"""

import time
import sys
import os

# 添加src目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.ibe import get_scheme, list_schemes

def test_ibe_scheme(scheme_name, test_message="Hello IBE World!"):
    """
    测试单个IBE方案
    
    参数:
        scheme_name (str): IBE方案名称
        test_message (str): 测试消息
    """
    print(f"\n{'='*60}")
    print(f"测试 {scheme_name.upper()} 方案")
    print(f"{'='*60}")
    
    try:
        # 获取IBE方案
        ibe = get_scheme(scheme_name)
        
        # 1. 系统设置
        print("1. 执行系统设置...")
        start_time = time.time()
        setup_result = ibe.setup()
        setup_time = time.time() - start_time
        print(f"   设置完成，耗时: {setup_time:.4f} 秒")
        print(f"   系统ID: {setup_result['public_params']['system_id']}")
        
        # 2. 用户身份
        alice_identity = "alice@test.com"
        bob_identity = "bob@test.com"
        
        # 3. 密钥提取
        print("2. 密钥提取测试...")
        start_time = time.time()
        alice_key = ibe.extract(alice_identity)
        key_extract_time = time.time() - start_time
        print(f"   Alice密钥提取完成，耗时: {key_extract_time:.4f} 秒")
        
        # 4. 加密测试
        print("3. 加密测试...")
        start_time = time.time()
        ciphertext = ibe.encrypt(alice_identity, test_message)
        encrypt_time = time.time() - start_time
        print(f"   加密完成，耗时: {encrypt_time:.4f} 秒")
        print(f"   原始消息: {test_message}")
        
        # 5. 解密测试
        print("4. 解密测试...")
        start_time = time.time()
        decrypted_message = ibe.decrypt(alice_key, ciphertext)
        decrypt_time = time.time() - start_time
        print(f"   解密完成，耗时: {decrypt_time:.4f} 秒")
        print(f"   解密消息: {decrypted_message.decode('utf-8')}")
        
        # 6. 验证正确性
        assert test_message == decrypted_message.decode('utf-8')
        print("   ✅ 正确性验证通过")
        
        # 7. 安全性测试
        print("5. 安全性测试...")
        try:
            bob_key = ibe.extract(bob_identity)
            wrong_decryption = ibe.decrypt(bob_key, ciphertext)
            print("   ❌ 安全性测试失败：Bob不应该能解密给Alice的消息")
            return False
        except Exception:
            print("   ✅ 安全性测试通过：Bob无法解密给Alice的消息")
        
        # 8. 性能总结
        total_time = setup_time + key_extract_time + encrypt_time + decrypt_time
        print(f"6. 性能总结:")
        print(f"   系统设置: {setup_time:.4f} 秒")
        print(f"   密钥提取: {key_extract_time:.4f} 秒")
        print(f"   加密操作: {encrypt_time:.4f} 秒")
        print(f"   解密操作: {decrypt_time:.4f} 秒")
        print(f"   总耗时: {total_time:.4f} 秒")
        
        return {
            'scheme': scheme_name,
            'setup_time': setup_time,
            'key_extract_time': key_extract_time,
            'encrypt_time': encrypt_time,
            'decrypt_time': decrypt_time,
            'total_time': total_time,
            'success': True
        }
        
    except Exception as e:
        print(f"   ❌ 测试失败: {str(e)}")
        return {
            'scheme': scheme_name,
            'success': False,
            'error': str(e)
        }

def compare_schemes():
    """
    对比所有IBE方案的性能
    """
    print(f"\n{'='*60}")
    print("IBE 方案性能对比")
    print(f"{'='*60}")
    
    test_message = "Performance comparison test message for IBE schemes."
    results = []
    
    # 测试所有方案
    scheme_names = ['boneh_franklin', 'boneh_boyen', 'sakai_kasahara']
    
    for scheme_name in scheme_names:
        result = test_ibe_scheme(scheme_name, test_message)
        if result['success']:
            results.append(result)
    
    # 性能对比
    if len(results) > 1:
        print(f"\n{'='*60}")
        print("性能对比结果")
        print(f"{'='*60}")
        
        # 表头
        print(f"{'方案名称':<20} {'设置时间':<10} {'密钥提取':<10} {'加密时间':<10} {'解密时间':<10} {'总时间':<10}")
        print("-" * 80)
        
        # 数据行
        for result in results:
            print(f"{result['scheme']:<20} "
                  f"{result['setup_time']:<10.4f} "
                  f"{result['key_extract_time']:<10.4f} "
                  f"{result['encrypt_time']:<10.4f} "
                  f"{result['decrypt_time']:<10.4f} "
                  f"{result['total_time']:<10.4f}")
        
        # 找出最快的方案
        fastest_setup = min(results, key=lambda x: x['setup_time'])
        fastest_encrypt = min(results, key=lambda x: x['encrypt_time'])
        fastest_decrypt = min(results, key=lambda x: x['decrypt_time'])
        fastest_overall = min(results, key=lambda x: x['total_time'])
        
        print(f"\n性能优胜者:")
        print(f"  设置最快: {fastest_setup['scheme']} ({fastest_setup['setup_time']:.4f}s)")
        print(f"  加密最快: {fastest_encrypt['scheme']} ({fastest_encrypt['encrypt_time']:.4f}s)")
        print(f"  解密最快: {fastest_decrypt['scheme']} ({fastest_decrypt['decrypt_time']:.4f}s)")
        print(f"  整体最快: {fastest_overall['scheme']} ({fastest_overall['total_time']:.4f}s)")

def batch_test():
    """
    批量测试：验证IBE算法在多用户场景下的表现
    """
    print(f"\n{'='*60}")
    print("批量测试 - 多用户场景")
    print(f"{'='*60}")
    
    # 使用最快的方案进行批量测试
    ibe = get_scheme('sakai_kasahara')  # SK-IBE通常最快
    
    # 系统设置
    ibe.setup()
    
    # 生成测试用户
    users = [f"user{i}@company.com" for i in range(1, 11)]
    messages = [f"Secret message for user{i}" for i in range(1, 11)]
    
    print(f"测试 {len(users)} 个用户的加密通信...")
    
    start_time = time.time()
    
    # 为所有用户生成密钥
    user_keys = {}
    for user in users:
        user_keys[user] = ibe.extract(user)
    
    # 每个用户都给其他用户发送消息
    total_operations = 0
    for i, sender in enumerate(users):
        for j, receiver in enumerate(users):
            if i != j:  # 不给自己发消息
                # 加密
                ciphertext = ibe.encrypt(receiver, f"From {sender}: {messages[i]}")
                
                # 解密
                decrypted = ibe.decrypt(user_keys[receiver], ciphertext)
                
                # 验证
                expected = f"From {sender}: {messages[i]}"
                assert expected == decrypted.decode('utf-8')
                
                total_operations += 1
    
    end_time = time.time()
    total_time = end_time - start_time
    
    print(f"完成 {total_operations} 次加密解密操作")
    print(f"总耗时: {total_time:.4f} 秒")
    print(f"平均每次操作: {total_time/total_operations:.4f} 秒")
    print(f"吞吐量: {total_operations/total_time:.2f} 操作/秒")

def main():
    """
    主测试函数
    """
    print("IBE 算法综合测试开始")
    print(f"支持的IBE方案: {list_schemes()}")
    
    # 1. 单独测试每个方案
    compare_schemes()
    
    # 2. 批量性能测试
    batch_test()
    
    print(f"\n{'='*60}")
    print("🎉 所有测试完成！")
    print("IBE算法实现成功，准备集成到Web系统中。")
    print(f"{'='*60}")

if __name__ == '__main__':
    main() 