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

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# 导入算法模块
from src.pke import ecc_scheme, elgamal_scheme, sm2_scheme
from src.ibe import get_scheme as get_ibe_scheme, list_schemes as list_ibe_schemes

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
        for size in encrypt_data['data_size'].unique():
            size_data = encrypt_data[encrypt_data['data_size'] == size]
            encryption_performance[f'{size}B'] = {
                'schemes': size_data['scheme'].tolist(),
                'times': (size_data['time'] * 1000).tolist(),  # 转换为毫秒
                'sizes': size_data['ciphertext_size'].tolist()
            }
        
        # 解密性能数据
        decrypt_data = df[df['operation'] == 'decrypt']
        decryption_performance = {}
        for size in decrypt_data['data_size'].unique():
            size_data = decrypt_data[decrypt_data['data_size'] == size]
            decryption_performance[f'{size}B'] = {
                'schemes': size_data['scheme'].tolist(),
                'times': (size_data['time'] * 1000).tolist()  # 转换为毫秒
            }
        
        # 综合性能评分
        performance_scores = []
        for scheme in schemes:
            scheme_data = df[df['scheme'] == scheme]
            key_gen_time = scheme_data[scheme_data['operation'] == 'key_gen']['time'].values[0]
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