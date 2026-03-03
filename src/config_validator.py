"""
配置文件验证模块

功能：
- 验证配置文件的完整性和正确性
- 检查必需的字段
- 验证 API Key 配置
- 生成友好的错误提示
"""

from src.logger import logger


class ConfigValidator:
    """配置验证器"""
    
    @staticmethod
    def validate(config):
        """
        验证配置文件
        
        Args:
            config: 配置字典
        
        Returns:
            True 表示验证通过
        
        Raises:
            ValueError: 配置验证失败时抛出异常
        """
        try:
            logger.info("开始验证配置文件...")
            
            # 检查 config 是否为 None
            if config is None:
                raise ValueError("配置对象为空，无法进行验证")
            
            # 1. 验证 wechat 配置段
            if 'wechat' not in config or config['wechat'] is None:
                raise ValueError("❌ 缺少 wechat 配置段")
            
            wechat_config = config['wechat']
            
            # 检查监听模式
            mode = wechat_config.get('mode', 'local')
            if mode not in ['local', 'wechat']:
                raise ValueError(f"❌ 不支持的监听模式: {mode}，支持: local, wechat")
            
            # 检查本地模式配置
            if mode == 'local':
                if 'listen_dir' not in wechat_config:
                    raise ValueError("❌ 本地模式缺少 listen_dir 配置")
                listen_dir = wechat_config.get('listen_dir')
                if not listen_dir or not isinstance(listen_dir, str):
                    raise ValueError("❌ listen_dir 必须是有效的字符串路径")
                logger.info(f"✓ 本地模式配置有效: {listen_dir}")
            
            # 检查微信模式配置
            elif mode == 'wechat':
                if 'listen_list' not in wechat_config or not wechat_config['listen_list']:
                    raise ValueError("❌ 微信模式缺少 listen_list 配置")
                logger.info(f"✓ 微信模式配置有效")
            
            # 2. 验证输出配置
            if 'output' not in config or config['output'] is None:
                raise ValueError("❌ 缺少 output 配置段")
            
            if 'excel_dir' not in config['output']:
                raise ValueError("❌ output.excel_dir 不能为空")
            
            logger.info(f"✓ 输出配置有效: {config['output']['excel_dir']}")
            
            # 3. 验证 LLM 配置
            if 'llm' not in config or config['llm'] is None:
                raise ValueError("❌ 缺少 llm 配置段")
            
            llm_config = config['llm']
            
            # 检查 API Key
            api_key = llm_config.get('api_key', '').strip()
            if not api_key:
                raise ValueError("❌ llm.api_key 不能为空")
            if api_key == 'sk-your-actual-api-key-here' or api_key.startswith('sk-your'):
                raise ValueError(
                    "❌ llm.api_key 仍为示例值，请替换为真实的 API Key\n"
                    "   获取方式：\n"
                    "   1. 阿里云百炼: https://bailian.aliyun.com\n"
                    "   2. OpenAI: https://platform.openai.com\n"
                    "   3. 智谱AI: https://open.bigmodel.cn"
                )
            
            logger.info(f"✓ API Key 配置有效")
            
            # 检查 base_url
            if 'base_url' not in llm_config or not llm_config['base_url']:
                raise ValueError("❌ llm.base_url 不能为空")
            
            logger.info(f"✓ Base URL 配置有效: {llm_config['base_url']}")
            
            # 检查 model_name
            if 'model_name' not in llm_config or not llm_config['model_name']:
                raise ValueError("❌ llm.model_name 不能为空")
            
            logger.info(f"✓ 模型名称配置有效: {llm_config['model_name']}")
            
            # 4. 验证日志配置（可选）
            if 'logging' in config and config['logging']:
                logging_config = config['logging']
                log_level = logging_config.get('level', 'INFO')
                if log_level not in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
                    logger.warning(f"⚠ 日志级别非标准: {log_level}，使用默认值 INFO")
            
            # 5. 验证图片处理配置（可选）
            if 'image' not in config:
                logger.warning("⚠ 缺少 image 配置，使用默认值")
                config['image'] = {
                    'enable_preprocessing': True,
                    'save_processed_images': False
                }
            
            # 6. 验证数据处理配置（可选）
            if 'data' not in config:
                logger.warning("⚠ 缺少 data 配置，使用默认值")
                config['data'] = {
                    'enable_deduplication': True,
                    'max_empty_fields': 3
                }
            
            logger.info("✓ 配置文件验证通过！")
            return True
        
        except ValueError as e:
            logger.error(str(e))
            raise
        except Exception as e:
            logger.error(f"❌ 配置验证异常: {e}")
            raise
