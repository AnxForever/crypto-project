import requests
import pandas as pd
import os
import json
import hashlib
from typing import Dict, List, Tuple, Optional
import logging
from datetime import datetime

class DatasetManager:
    """
    PKE应用演示数据集管理器
    负责下载、预处理和管理MinsaPay交易数据集
    """
    
    def __init__(self, cache_dir: str = "cache"):
        self.cache_dir = cache_dir
        self.minsapay_url = "https://raw.githubusercontent.com/minsapay/transaction-data-2019/master/transactions.csv"
        self.dataset_file = os.path.join(cache_dir, "minsapay_transactions.csv")
        self.metadata_file = os.path.join(cache_dir, "dataset_metadata.json")
        
        # 确保缓存目录存在
        os.makedirs(cache_dir, exist_ok=True)
        
        # 定义敏感字段映射
        self.sensitive_fields = {
            'amount': 'high',      # 交易金额 - 高敏感
            'balance': 'high',     # 用户余额 - 高敏感
            'user': 'medium',      # 用户ID - 中敏感
            'booth': 'medium',     # 商户ID - 中敏感
            'transaction': 'low',  # 交易号 - 低敏感
            'timestamp': 'none',   # 时间戳 - 无敏感
            'type': 'none'         # 交易类型 - 无敏感
        }
        
        # 数据集规模配置
        self.dataset_sizes = {
            'small': 100,      # 小型数据集 - 性能分析用
            'medium': 1000,    # 中型数据集 - 应用演示用
            'large': 2900      # 完整数据集 - 压力测试用
        }
        
        self.datasets = {}  # 缓存已加载的数据集
    
    def download_dataset(self, force=False) -> bool:
        """
        从GitHub下载MinsaPay交易数据集
        
        Args:
            force: 是否强制重新下载
            
        Returns:
            bool: 下载是否成功
        """
        if os.path.exists(self.dataset_file) and not force:
            print("数据集已存在，跳过下载。")
            return True
            
        try:
            print(f"正在从 {self.minsapay_url} 下载数据集...")
            
            # 下载数据
            response = requests.get(self.minsapay_url, timeout=30)
            response.raise_for_status()
            
            # 保存到本地
            with open(self.dataset_file, 'wb') as f:
                f.write(response.content)
            
            # 验证数据完整性
            if self._validate_dataset():
                # 保存元数据
                metadata = {
                    'source_url': self.minsapay_url,
                    'download_time': pd.Timestamp.now().isoformat(),
                    'file_size': len(response.content),
                    'file_hash': hashlib.md5(response.content).hexdigest()
                }
                
                with open(self.metadata_file, 'w') as f:
                    json.dump(metadata, f, indent=2)
                
                print("数据集下载并验证成功！")
                return True
            else:
                print("数据集验证失败！")
                return False
                
        except Exception as e:
            print(f"下载数据集时发生错误: {str(e)}")
            return False
    
    def _validate_dataset(self) -> bool:
        """
        验证数据集的完整性和格式正确性
        
        Returns:
            bool: 验证是否通过
        """
        try:
            # 读取数据
            df = pd.read_csv(self.dataset_file)
            
            # 检查必需的列是否存在
            required_columns = ['transaction', 'user', 'booth', 'timestamp', 'type', 'amount', 'balance']
            missing_columns = set(required_columns) - set(df.columns)
            
            if missing_columns:
                print(f"数据集缺少必需的列: {missing_columns}")
                return False
            
            # 检查数据行数
            if len(df) < 100:
                print(f"数据集行数过少: {len(df)} < 100")
                return False
            
            # 检查数据类型
            if not pd.api.types.is_numeric_dtype(df['amount']):
                print("amount列不是数值类型")
                return False
            
            if not pd.api.types.is_numeric_dtype(df['balance']):
                print("balance列不是数值类型")
                return False
            
            print(f"数据集验证通过: {len(df)} 行数据")
            return True
            
        except Exception as e:
            print(f"验证数据集时发生错误: {str(e)}")
            return False
    
    def get_dataset(self, size: str = 'medium', force_download: bool = False) -> Optional[pd.DataFrame]:
        """
        获取指定规模的数据集
        
        Args:
            size: 数据集大小 ('small', 'medium', 'large')
            force_download: 是否强制重新下载
            
        Returns:
            pandas.DataFrame: 处理后的数据集，如果失败返回None
        """
        if size in self.datasets:
            return self.datasets[size]
        
        # 检查是否需要下载数据集
        if force_download or not self._is_dataset_cached():
            if not self.download_dataset():
                return None
        
        try:
            # 读取完整数据集
            df = pd.read_csv(self.dataset_file)
            
            # 根据size参数获取相应规模的数据
            if size in self.dataset_sizes:
                max_rows = self.dataset_sizes[size]
                df = df.head(max_rows)
            
            # 数据预处理
            df = self._preprocess_data(df)
            
            self.datasets[size] = df
            return df
            
        except Exception as e:
            print(f"获取数据集时发生错误: {str(e)}")
            return None
    
    def _is_dataset_cached(self) -> bool:
        """检查数据集是否已缓存"""
        return os.path.exists(self.dataset_file) and os.path.exists(self.metadata_file)
    
    def _preprocess_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        数据预处理
        
        Args:
            df: 原始数据框
            
        Returns:
            pandas.DataFrame: 预处理后的数据框
        """
        # 创建副本避免修改原数据
        processed_df = df.copy()
        
        # 处理时间戳
        processed_df['timestamp'] = pd.to_datetime(processed_df['timestamp'])
        
        # 确保数值列为正确类型
        processed_df['amount'] = pd.to_numeric(processed_df['amount'], errors='coerce')
        processed_df['balance'] = pd.to_numeric(processed_df['balance'], errors='coerce')
        
        # 删除包含NaN的行
        processed_df = processed_df.dropna()
        
        # 重置索引
        processed_df = processed_df.reset_index(drop=True)
        
        return processed_df
    
    def get_sensitive_fields(self) -> Dict[str, str]:
        """
        获取敏感字段映射
        
        Returns:
            Dict[str, str]: 字段名到敏感级别的映射
        """
        return self.sensitive_fields.copy()
    
    def get_encryption_candidates(self, sensitivity_level: str = 'medium') -> List[str]:
        """
        获取需要加密的字段列表
        
        Args:
            sensitivity_level: 最低敏感级别 ('high', 'medium', 'low')
            
        Returns:
            List[str]: 需要加密的字段列表
        """
        sensitivity_order = ['none', 'low', 'medium', 'high']
        min_level_index = sensitivity_order.index(sensitivity_level)
        
        return [
            field for field, level in self.sensitive_fields.items()
            if sensitivity_order.index(level) >= min_level_index
        ]
    
    def get_dataset_stats(self, size: str = 'medium') -> Dict:
        """
        获取数据集统计信息
        
        Args:
            size: 数据集大小
            
        Returns:
            Dict: 统计信息
        """
        df = self.get_dataset(size)
        if df is None:
            return {}
        
        return {
            'total_records': len(df),
            'total_users': df['user'].nunique(),
            'total_booths': df['booth'].nunique(),
            'total_amount': df['amount'].sum(),
            'transaction_types': df['type'].value_counts().to_dict(),
            'date_range': {
                'start': df['timestamp'].min().isoformat(),
                'end': df['timestamp'].max().isoformat()
            },
            'sensitive_fields': self.get_encryption_candidates('medium')
        }
    
    def get_preview_data(self, size: str = 'medium', limit: int = 10) -> Dict:
        """
        获取数据预览
        
        Args:
            size: 数据集大小
            limit: 预览记录数量
            
        Returns:
            Dict: 包含预览数据和统计信息
        """
        df = self.get_dataset(size)
        if df is None:
            return {'error': '无法加载数据集'}
        
        # 预览数据
        preview_df = df.head(limit)
        
        # 修正：将DataFrame转换为JSON兼容格式
        # 这是修复问题的关键点！
        preview_data_json = preview_df.to_json(orient='records', date_format='iso')
        preview_data = json.loads(preview_data_json)

        # 统计信息
        stats = {
            'total_records': len(df),
            'total_users': df['user'].nunique(),
            'total_booths': df['booth'].nunique(),
            'total_amount': df['amount'].sum(),
            'transaction_types': df['type'].value_counts().to_dict()
        }
        
        # 字段信息
        column_info = {
            'time': {'type': 'datetime', 'sensitive_level': 'low'},
            'user': {'type': 'string', 'sensitive_level': 'medium'},
            'booth': {'type': 'string', 'sensitive_level': 'medium'},
            'type': {'type': 'category', 'sensitive_level': 'none'},
            'amount': {'type': 'float', 'sensitive_level': 'high'},
            'balance': {'type': 'float', 'sensitive_level': 'high'}
        }
        
        return {
            'preview_data': preview_data,
            'stats': stats,
            'column_info': column_info
        } 