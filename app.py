# -*- coding: utf-8 -*-

"""
密码学工具Web应用 - 主应用文件

这是一个完整的密码学工具Web应用，提供：
1. PKE加密工具 (ECC, ElGamal, SM2)
2. IBE加密工具 (Boneh-Franklin, Boneh-Boyen, Sakai-Kasahara)
3. 性能分析和对比
4. 应用案例演示

技术栈：Flask + HTML5 + CSS3 + JavaScript + Chart.js
"""

from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import sys
import traceback
import json
from flask.json.provider import JSONProvider
from datetime import datetime
import pandas as pd
import numpy as np

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# 导入算法模块
from src.pke import ecc_scheme, elgamal_scheme, sm2_scheme
from src.ibe import get_scheme as get_ibe_scheme, list_schemes as list_ibe_schemes
from src.utils.dataset_manager import DatasetManager

# --- 最终修复：正确的自定义JSON序列化 ---
class CustomJSONProvider(JSONProvider):
    def dumps(self, obj, **kwargs):
        """Dumps an object to a JSON string."""
        if 'default' not in kwargs:
            kwargs['default'] = self.default
        return json.dumps(obj, **kwargs)

    def loads(self, s, **kwargs):
        """Loads a JSON string to an object."""
        return json.loads(s, **kwargs)

    @staticmethod
    def default(o):
        """The default function for JSON serialization."""
        if isinstance(o, (datetime, pd.Timestamp)):
            return o.isoformat()
        if isinstance(o, np.integer):
            return int(o)
        if isinstance(o, np.floating):
            return float(o)
        if isinstance(o, np.ndarray):
            return o.tolist()
        if isinstance(o, bytes):
            return o.hex()
        raise TypeError(
            f"Object of type {type(o).__name__} is not JSON serializable"
        )

# 创建Flask应用
app = Flask(__name__)
app.json = CustomJSONProvider(app) # 应用自定义的JSON Provider
CORS(app)  # 允许跨域请求

# 配置
app.config['SECRET_KEY'] = 'cryptography_tools_secret_key_2024'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 最大文件大小16MB

# 全局变量存储系统状态
pke_systems = {}
ibe_systems = {}

# 全局数据集管理器
dataset_manager = DatasetManager()

@app.route('/')
def index():
    """主页 - 项目概述"""
    return render_template('index.html')

@app.route('/pke-tool')
def pke_tool():
    """PKE加密工具页面"""
    return render_template('pke_tool.html')

@app.route('/ibe-tool')
def ibe_tool():
    """IBE加密工具页面"""
    return render_template('ibe_tool.html')

@app.route('/pke-demo')
def pke_demo():
    """PKE应用演示页面"""
    return render_template('pke_demo.html')

@app.route('/ibe-demo')
def ibe_demo():
    """IBE应用演示页面"""
    return render_template('ibe_demo.html')

@app.route('/pke-analysis')
def pke_analysis():
    """PKE性能分析页面"""
    return render_template('pke_analysis.html')

@app.route('/ibe-analysis')
def ibe_analysis():
    """IBE性能分析页面"""
    return render_template('ibe_analysis.html')

@app.route('/pke-application')
def pke_application():
    """PKE应用演示页面 - 基于真实数据集"""
    return render_template('pke_application_demo.html')



# === API路由 ===

@app.route('/api/pke/schemes')
def get_pke_schemes():
    """获取支持的PKE方案列表"""
    return jsonify({
        'schemes': ['ECC', 'ElGamal', 'SM2'],
        'status': 'success'
    })

@app.route('/api/ibe/schemes')
def get_ibe_schemes():
    """获取支持的IBE方案列表"""
    return jsonify({
        'schemes': list_ibe_schemes(),
        'status': 'success'
    })

@app.route('/api/pke/performance-data')
def get_pke_performance_data():
    """获取PKE性能分析数据"""
    try:
        import pandas as pd
        
        # 优先使用完整数据，如果不存在则使用简化数据
        complete_file = 'results/pke_performance_complete.csv'
        simple_file = 'results/pke_performance_simple.csv'
        
        if os.path.exists(complete_file):
            df = pd.read_csv(complete_file)
        elif os.path.exists(simple_file):
            df = pd.read_csv(simple_file)
        else:
            return jsonify({'error': '性能数据文件不存在'}), 404
        
        # 按算法分组处理数据
        schemes = df['scheme'].unique().tolist()
        
        # 密钥生成数据
        key_gen_data = df[df['operation'] == 'key_gen']
        key_generation = {
            'schemes': key_gen_data['scheme'].tolist(),
            'times': (key_gen_data['time'] * 1000).tolist()  # 转换为毫秒
        }
        
        # 加密性能数据
        encrypt_data = df[df['operation'] == 'encrypt']
        encryption_performance = {}
        for size in pd.unique(encrypt_data['data_size']):
            size_data = encrypt_data[encrypt_data['data_size'] == size]
            encryption_performance[f'{size}B'] = {
                'schemes': size_data['scheme'].tolist(),
                'times': (size_data['time'] * 1000).tolist(),  # 转换为毫秒
                'sizes': size_data['ciphertext_size'].tolist()
            }
        
        # 解密性能数据
        decrypt_data = df[df['operation'] == 'decrypt']
        decryption_performance = {}
        for size in pd.unique(decrypt_data['data_size']):
            size_data = decrypt_data[decrypt_data['data_size'] == size]
            decryption_performance[f'{size}B'] = {
                'schemes': size_data['scheme'].tolist(),
                'times': (size_data['time'] * 1000).tolist()  # 转换为毫秒
            }
        
        # 综合性能评分
        performance_scores = []
        for scheme in schemes:
            scheme_data = df[df['scheme'] == scheme]
            key_gen_time = scheme_data[scheme_data['operation'] == 'key_gen']['time'].iloc[0]
            avg_encrypt_time = scheme_data[scheme_data['operation'] == 'encrypt']['time'].mean()
            avg_decrypt_time = scheme_data[scheme_data['operation'] == 'decrypt']['time'].mean()
            
            # 综合评分（越低越好）
            score = key_gen_time * 0.1 + avg_encrypt_time * 0.45 + avg_decrypt_time * 0.45
            performance_scores.append(score * 1000)  # 转换为毫秒
        
        return jsonify({
            'status': 'success',
            'data': {
                'schemes': schemes,
                'key_generation': key_generation,
                'encryption_performance': encryption_performance,
                'decryption_performance': decryption_performance,
                'performance_scores': {
                    'schemes': schemes,
                    'scores': performance_scores
                }
            }
        })
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': f'获取性能数据失败: {str(e)}'}), 500

@app.route('/api/pke/generate-keys', methods=['POST'])
def pke_generate_keys():
    """PKE密钥生成API"""
    try:
        data = request.get_json()
        scheme = data.get('scheme', '').upper()
        
        if scheme == 'ECC':
            private_key, public_key = ecc_scheme.generate_keys()
            result = {
                'private_key': private_key,
                'public_key': public_key
            }
        elif scheme == 'ELGAMAL':
            private_key, public_key = elgamal_scheme.generate_keys()
            result = {
                'private_key': {
                    'p': str(private_key.p),
                    'g': str(private_key.g),
                    'x': str(private_key.x),
                    'y': str(private_key.y)
                },
                'public_key': {
                    'p': str(public_key.p),
                    'g': str(public_key.g),
                    'y': str(public_key.y)
                }
            }
        elif scheme == 'SM2':
            private_key, public_key = sm2_scheme.generate_keys()
            result = {
                'private_key': private_key,
                'public_key': public_key
            }
        else:
            return jsonify({'error': f'不支持的PKE方案: {scheme}'}), 400
            
        return jsonify({
            'status': 'success',
            'scheme': scheme,
            'keys': result
        })
        
    except Exception as e:
        return jsonify({'error': f'密钥生成失败: {str(e)}'}), 500

@app.route('/api/pke/encrypt', methods=['POST'])
def pke_encrypt():
    """PKE加密API"""
    try:
        data = request.get_json()
        scheme = data.get('scheme', '').upper()
        message = data.get('message', '')
        public_key = data.get('public_key')
        
        if not message:
            return jsonify({'error': '消息不能为空'}), 400
            
        if scheme == 'ECC':
            # ECC需要处理字符串到bytes的转换
            message_bytes = message.encode('utf-8') if isinstance(message, str) else message
            # --- 健壮性修复：预处理公钥 ---
            if isinstance(public_key, str) and len(public_key) % 2 != 0:
                public_key = '0' + public_key
            result = ecc_scheme.encrypt(public_key, message_bytes)
            # 将bytes结果转换为hex字符串以便JSON传输
            result = result.hex()
        elif scheme == 'ELGAMAL':
            # ElGamal需要处理字符串到bytes的转换和密钥对象重构
            message_bytes = message.encode('utf-8') if isinstance(message, str) else message
            # 重构ElGamal公钥对象
            elgamal_public_key = elgamal_scheme.ElGamalKey(
                p=int(public_key['p']),
                g=int(public_key['g']),
                y=int(public_key['y']),
                x=None
            )
            result = elgamal_scheme.encrypt(elgamal_public_key, message_bytes)
            # 将bytes结果转换为hex字符串以便JSON传输
            result = result.hex()
        elif scheme == 'SM2':
            # SM2需要处理字符串到bytes的转换
            message_bytes = message.encode('utf-8') if isinstance(message, str) else message
            # --- 健壮性修复：预处理公钥 ---
            if isinstance(public_key, str) and len(public_key) % 2 != 0:
                public_key = '0' + public_key
            result = sm2_scheme.encrypt(public_key, message_bytes)
            # 将bytes结果转换为hex字符串以便JSON传输
            result = result.hex()
        else:
            return jsonify({'error': f'不支持的PKE方案: {scheme}'}), 400
            
        return jsonify({
            'status': 'success',
            'scheme': scheme,
            'ciphertext': result
        })
        
    except Exception as e:
        return jsonify({'error': f'加密失败: {str(e)}'}), 500

@app.route('/api/pke/decrypt', methods=['POST'])
def pke_decrypt():
    """PKE解密API"""
    try:
        data = request.get_json()
        scheme = data.get('scheme', '').upper()
        ciphertext = data.get('ciphertext')
        private_key = data.get('private_key')

        if not ciphertext or not private_key:
            return jsonify({'error': '密文和私钥不能为空'}), 400
        
        if scheme == 'ECC':
            # --- 健壮性修复：预处理密文 ---
            if isinstance(ciphertext, str):
                if len(ciphertext) % 2 != 0:
                    ciphertext = '0' + ciphertext
                ciphertext_bytes = bytes.fromhex(ciphertext)
            else:
                ciphertext_bytes = ciphertext
            result_bytes = ecc_scheme.decrypt(private_key, ciphertext_bytes)
            result = result_bytes.decode('utf-8')

        elif scheme == 'ELGAMAL':
            # --- 健壮性修复：预处理密文 ---
            if isinstance(ciphertext, str):
                if len(ciphertext) % 2 != 0:
                    ciphertext = '0' + ciphertext
                ciphertext_bytes = bytes.fromhex(ciphertext)
            else:
                ciphertext_bytes = ciphertext

            elgamal_private_key = elgamal_scheme.ElGamalKey(
                p=int(private_key['p']),
                g=int(private_key['g']),
                y=int(private_key['y']),
                x=int(private_key['x'])
            )
            result_bytes = elgamal_scheme.decrypt(elgamal_private_key, ciphertext_bytes)
            result = result_bytes.decode('utf-8')

        elif scheme == 'SM2':
            # --- 健壮性修复：预处理密文 ---
            if isinstance(ciphertext, str):
                if len(ciphertext) % 2 != 0:
                    ciphertext = '0' + ciphertext
                ciphertext_bytes = bytes.fromhex(ciphertext)
            else:
                ciphertext_bytes = ciphertext
            
            result_bytes = sm2_scheme.decrypt(private_key, ciphertext_bytes)
            result = result_bytes.decode('utf-8')

        else:
            return jsonify({'error': f'不支持的PKE方案: {scheme}'}), 400
            
        return jsonify({
            'status': 'success',
            'scheme': scheme,
            'plaintext': result
        })
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': f'解密失败: {str(e)}'}), 500

def get_ibe_instance(scheme_name):
    """获取IBE方案实例"""
    try:
        # 根据方案名创建相应的实例
        if scheme_name.lower() == 'boneh_franklin':
            from src.ibe.boneh_franklin_scheme_simple import SimpleBonehFranklinIBE
            return SimpleBonehFranklinIBE()
        elif scheme_name.lower() == 'boneh_boyen':
            from src.ibe.boneh_boyen_scheme import BonehBoyenIBE
            return BonehBoyenIBE()
        elif scheme_name.lower() == 'sakai_kasahara':
            from src.ibe.sakai_kasahara_scheme import SakaiKasaharaIBE
            return SakaiKasaharaIBE()
        else:
            raise ValueError(f"不支持的IBE方案: {scheme_name}")
    except Exception as e:
        print(f"[ERROR] 获取IBE方案失败: {e}")
        raise

@app.route('/api/ibe/setup', methods=['POST'])
def ibe_setup():
    """IBE系统设置API"""
    try:
        data = request.get_json()
        scheme = data.get('scheme', '').lower()
        
        print(f"[DEBUG] IBE Setup请求 - scheme: {scheme}")
        
        ibe = get_ibe_instance(scheme)
        setup_result = ibe.setup()
        
        # 保存系统状态
        ibe_systems[scheme] = {
            'ibe_instance': ibe,
            'setup_result': setup_result
        }
        
        return jsonify({
            'status': 'success',
            'scheme': scheme,
            'public_params': setup_result['public_params']
        })
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': f'IBE系统设置失败: {str(e)}'}), 500

@app.route('/api/ibe/extract', methods=['POST'])
def ibe_extract():
    """IBE密钥提取API"""
    try:
        data = request.get_json()
        scheme = data.get('scheme', '').lower()
        identity = data.get('identity', '')
        
        if not identity:
            return jsonify({'error': '身份信息不能为空'}), 400
            
        if scheme not in ibe_systems:
            return jsonify({'error': f'IBE系统未初始化，请先调用setup接口'}), 400
            
        ibe = ibe_systems[scheme]['ibe_instance']
        private_key = ibe.extract(identity)
        
        return jsonify({
            'status': 'success',
            'scheme': scheme,
            'identity': identity,
            'private_key': private_key
        })
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': f'密钥提取失败: {str(e)}'}), 500

@app.route('/api/ibe/encrypt', methods=['POST'])
def ibe_encrypt():
    """IBE加密API"""
    try:
        data = request.get_json()
        scheme = data.get('scheme', '').lower()
        identity = data.get('identity', '')
        message = data.get('message', '')
        
        if not identity or not message:
            return jsonify({'error': '身份信息和消息不能为空'}), 400
            
        if scheme not in ibe_systems:
            return jsonify({'error': f'IBE系统未初始化，请先调用setup接口'}), 400
            
        ibe = ibe_systems[scheme]['ibe_instance']
        ciphertext = ibe.encrypt(identity, message)
        
        return jsonify({
            'status': 'success',
            'scheme': scheme,
            'identity': identity,
            'ciphertext': ciphertext
        })
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': f'加密失败: {str(e)}'}), 500

@app.route('/api/ibe/decrypt', methods=['POST'])
def ibe_decrypt():
    """IBE解密API"""
    try:
        data = request.get_json()
        scheme = data.get('scheme', '').lower()
        private_key_data = data.get('private_key')
        ciphertext_data = data.get('ciphertext')
        
        print(f"[DEBUG] IBE解密请求 - scheme: {scheme}")
        print(f"[DEBUG] private_key_data类型: {type(private_key_data)}")
        print(f"[DEBUG] ciphertext_data类型: {type(ciphertext_data)}")
        
        if scheme not in ibe_systems:
            return jsonify({'error': f'IBE系统未初始化，请先调用setup接口'}), 400
        
        # 转换私钥数据格式：将hex字符串转换回bytes
        processed_private_key = {}
        for key, value in private_key_data.items():
            if key == 'private_key' and isinstance(value, str):
                # 私钥从hex字符串转换为bytes
                processed_private_key[key] = bytes.fromhex(value)
                print(f"[DEBUG] 转换私钥: {key} 从hex字符串转为bytes")
            else:
                processed_private_key[key] = value
        
        # 转换密文数据格式：将hex字符串转换回bytes
        processed_ciphertext = {}
        for key, value in ciphertext_data.items():
            if isinstance(value, str) and key in ['encrypted_session_key', 'kek_nonce', 'kek_tag', 
                                                  'ciphertext', 'msg_nonce', 'msg_tag', 'r', 
                                                  'sk_randomizer', 'auth_tag']:
                # 这些字段从hex字符串转换为bytes
                try:
                    processed_ciphertext[key] = bytes.fromhex(value)
                    print(f"[DEBUG] 转换密文字段: {key} 从hex字符串转为bytes")
                except ValueError:
                    print(f"[DEBUG] 字段 {key} 不是有效的hex字符串，保持原值")
                    processed_ciphertext[key] = value
            else:
                processed_ciphertext[key] = value
        
        print(f"[DEBUG] 处理后的私钥类型: {type(processed_private_key.get('private_key', 'N/A'))}")
        print(f"[DEBUG] 处理后的nonce类型: {type(processed_ciphertext.get('kek_nonce', 'N/A'))}")
        
        # 调用IBE解密
        ibe = ibe_systems[scheme]['ibe_instance']
        plaintext = ibe.decrypt(processed_private_key, processed_ciphertext)
        
        # 如果返回的是bytes，转换为字符串
        if isinstance(plaintext, bytes):
            plaintext = plaintext.decode('utf-8')
            
        return jsonify({
            'status': 'success',
            'scheme': scheme,
            'plaintext': plaintext
        })
        
    except Exception as e:
        print(f"[DEBUG] IBE解密异常: {e}")
        traceback.print_exc()
        return jsonify({'error': f'解密失败: {str(e)}'}), 500


# === PKE应用演示API ===

@app.route('/api/pke/dataset/download', methods=['POST'])
def pke_dataset_download():
    """下载并缓存MinsaPay数据集"""
    try:
        force_download = request.json.get('force_download', False) if request.json else False
        
        if dataset_manager.download_dataset() or not force_download:
            return jsonify({
                'status': 'success',
                'message': '数据集下载成功'
            })
        else:
            return jsonify({
                'status': 'error',
                'message': '数据集下载失败'
            }), 500
            
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': f'下载数据集失败: {str(e)}'}), 500

@app.route('/api/pke/dataset/preview')
def pke_dataset_preview():
    """获取数据集预览"""
    try:
        size = request.args.get('size', 'medium')
        limit = int(request.args.get('limit', 10))
        
        preview_data = dataset_manager.get_preview_data(size, limit)
        
        if 'error' in preview_data:
            return jsonify({'status': 'error', 'message': preview_data['error']}), 500
        
        # --- 终极修复：在jsonify之前强制转换数据 ---
        # 这一步将所有特殊类型（如Timestamp）转换为JSON兼容的字符串
        json_compatible_string = json.dumps(preview_data, default=CustomJSONProvider.default)
        compatible_data = json.loads(json_compatible_string)
        
        return jsonify({
            'status': 'success',
            'data': compatible_data
        })
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': f'获取数据预览失败: {str(e)}'}), 500

@app.route('/api/pke/encrypt_transactions', methods=['POST'])
def pke_encrypt_transactions():
    """批量加密交易数据"""
    try:
        data = request.json or {}
        size = data.get('size', 'medium')
        fields_to_encrypt = data.get('fields', ['amount', 'balance', 'user', 'booth'])
        
        # 获取数据集
        df = dataset_manager.get_dataset(size)
        if df is None:
            return jsonify({'status': 'error', 'message': '无法加载数据集'}), 500
        
        # 使用SM2算法进行加密
        # 生成密钥对
        private_key_hex, public_key_hex = sm2_scheme.generate_keys()
        
        encrypted_data = []
        performance_stats = {
            'total_records': len(df),
            'encrypted_fields': fields_to_encrypt,
            'encryption_times': [],
            'original_size': 0,
            'encrypted_size': 0
        }
        
        import time
        
        for idx, row in df.iterrows():
            encrypted_row = row.to_dict()
            row_start_time = time.time()
            
            # 加密指定字段
            for field in fields_to_encrypt:
                if field in encrypted_row:
                    original_value = str(encrypted_row[field])
                    performance_stats['original_size'] += len(original_value.encode('utf-8'))
                    
                    # 使用SM2加密
                    encrypted_value = sm2_scheme.encrypt(public_key_hex, original_value.encode('utf-8'))
                    encrypted_row[field] = encrypted_value.hex()
                    performance_stats['encrypted_size'] += len(encrypted_value)
            
            row_end_time = time.time()
            performance_stats['encryption_times'].append((row_end_time - row_start_time) * 1000)  # 毫秒
            
            # 添加加密标记
            encrypted_row['_encrypted'] = True
            encrypted_row['_encrypted_fields'] = fields_to_encrypt
            
            encrypted_data.append(encrypted_row)
        
        # 计算性能统计
        performance_stats['total_time'] = sum(performance_stats['encryption_times'])
        performance_stats['avg_time_per_record'] = performance_stats['total_time'] / len(df)
        performance_stats['size_expansion_ratio'] = performance_stats['encrypted_size'] / performance_stats['original_size']
        
        return jsonify({
            'status': 'success',
            'data': {
                'encrypted_data': encrypted_data[:10],  # 只返回前10条用于预览
                'performance_stats': performance_stats,
                'public_key': public_key_hex,
                'private_key': private_key_hex  # 注意：实际应用中不应返回私钥
            }
        })
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': f'批量加密失败: {str(e)}'}), 500

@app.route('/api/pke/decrypt_transactions', methods=['POST'])
def pke_decrypt_transactions():
    """批量解密交易数据验证"""
    try:
        data = request.json or {}
        encrypted_data = data.get('encrypted_data')
        private_key_hex = data.get('private_key')
        
        if not encrypted_data or not private_key_hex:
            return jsonify({'status': 'error', 'message': '缺少必需的参数'}), 400
        
        decrypted_data = []
        performance_stats = {
            'total_records': len(encrypted_data),
            'decryption_times': [],
            'verification_success': 0
        }
        
        import time
        
        for encrypted_row in encrypted_data:
            decrypted_row = encrypted_row.copy()
            row_start_time = time.time()
            
            if encrypted_row.get('_encrypted'):
                encrypted_fields = encrypted_row.get('_encrypted_fields', [])
                
                try:
                    # 解密指定字段
                    for field in encrypted_fields:
                        if field in encrypted_row and field != '_encrypted' and field != '_encrypted_fields':
                            encrypted_value = bytes.fromhex(encrypted_row[field])
                            decrypted_value = sm2_scheme.decrypt(private_key_hex, encrypted_value)
                            decrypted_row[field] = decrypted_value.decode('utf-8')
                    
                    # 移除加密标记
                    decrypted_row.pop('_encrypted', None)
                    decrypted_row.pop('_encrypted_fields', None)
                    
                    performance_stats['verification_success'] += 1
                    
                except Exception as decrypt_error:
                    decrypted_row['_decryption_error'] = str(decrypt_error)
            
            row_end_time = time.time()
            performance_stats['decryption_times'].append((row_end_time - row_start_time) * 1000)  # 毫秒
            
            decrypted_data.append(decrypted_row)
        
        # 计算性能统计
        performance_stats['total_time'] = sum(performance_stats['decryption_times'])
        performance_stats['avg_time_per_record'] = performance_stats['total_time'] / len(encrypted_data)
        performance_stats['success_rate'] = performance_stats['verification_success'] / len(encrypted_data)
        
        return jsonify({
            'status': 'success',
            'data': {
                'decrypted_data': decrypted_data,
                'performance_stats': performance_stats
            }
        })
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': f'批量解密失败: {str(e)}'}), 500

@app.route('/api/pke/performance_stats')
def pke_performance_stats():
    """获取PKE应用演示的性能统计"""
    try:
        size = request.args.get('size', 'medium')
        
        stats = dataset_manager.get_dataset_stats(size)
        
        return jsonify({
            'status': 'success',
            'data': {
                'dataset_stats': stats,
                'optimal_scheme': 'SM2',
                'scheme_performance': {
                    'SM2': {
                        'key_generation': 0.05,  # 毫秒
                        'encryption_speed': 0.94,  # 毫秒/记录
                        'decryption_speed': 0.06,  # 毫秒/记录
                        'security_level': 'High',
                        'recommendation': '最优选择'
                    }
                }
            }
        })
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': f'获取性能统计失败: {str(e)}'}), 500

@app.route('/api/pke/export_results', methods=['POST'])
def pke_export_results():
    """导出加密结果"""
    try:
        data = request.json or {}
        encrypted_data = data.get('encrypted_data')
        format_type = data.get('format', 'csv')
        
        if not encrypted_data:
            return jsonify({'status': 'error', 'message': '没有数据可导出'}), 400
        
        if format_type == 'csv':
            import pandas as pd
            import io
            
            df = pd.DataFrame(encrypted_data)
            output = io.StringIO()
            df.to_csv(output, index=False)
            csv_content = output.getvalue()
            
            return jsonify({
                'status': 'success',
                'data': {
                    'content': csv_content,
                    'filename': f'encrypted_transactions_{pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")}.csv',
                    'format': 'csv'
                }
            })
        else:
            return jsonify({'status': 'error', 'message': '不支持的导出格式'}), 400
            
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': f'导出结果失败: {str(e)}'}), 500


@app.errorhandler(404)
def not_found(error):
    """404错误处理"""
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """500错误处理"""
    return render_template('500.html'), 500

# 静态文件路由
@app.route('/static/<path:filename>')
def static_files(filename):
    """静态文件服务"""
    return send_from_directory('static', filename)

if __name__ == '__main__':
    print("🚀 启动密码学工具Web应用...")
    print("📱 访问地址: http://localhost:5000")
    print("🔧 开发模式: 启用")
    
    # 开发模式运行
    app.run(debug=True, host='0.0.0.0', port=5000) 