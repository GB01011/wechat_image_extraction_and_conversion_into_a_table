import yaml
import time
from pathlib import Path
from src.logger import logger
from src.config_validator import ConfigValidator
from src.wechat_listener import LocalFileListener
from src.llm_vision_parser import LLMParser
from src.image_processor import ImageProcessor
from src.data_validator import DataValidator
from src.excel_engine import ExcelGenerator
from src.table_structure_detector import TableStructureDetector


def load_config():
    """加载配置文件"""
    config_path = Path("config/settings.yaml")
    if not config_path.exists():
        logger.error(f"配置文件不存在: {config_path.absolute()}")
        raise FileNotFoundError(f"请创建配置文件: {config_path}")
    
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        logger.info("✓ 配置文件加载成功")
        return config
    except yaml.YAMLError as e:
        logger.error(f"配置文件格式错误: {e}")
        raise
    except Exception as e:
        logger.error(f"加载配置文件失败: {e}")
        raise


def create_listener(config):
    """
    根据配置创建合适的监听器
    
    Args:
        config: 配置字典
    
    Returns:
        监听器实例（LocalFileListener）
    """
    # 获取监听模式，默认为 local（推荐）
    listen_mode = config.get('wechat', {}).get('mode', 'local').lower()
    
    if listen_mode == 'local':
        # 推荐方案：本地文件监听
        listen_dir = config.get('wechat', {}).get('listen_dir', 'data/temp_images')
        logger.info(f"\n【监听模式】本地文件模式（推荐）")
        logger.info(f"【监听目录】{listen_dir}")
        logger.info(f"【说明】请将要处理的图片放到此目录")
        listener = LocalFileListener(watch_dir=listen_dir)
    else:
        logger.error(f"❌ 不支持的监听模式: {listen_mode}")
        logger.error("支持模式: local（本地文件）")
        raise ValueError(f"不支持的监听模式: {listen_mode}")
    
    return listener


def main():
    logger.info("=" * 60)
    logger.info("微信表格自动化处理工具启动")
    logger.info("=" * 60)
    
    # 1. 加载和验证配置
    try:
        config = load_config()
        ConfigValidator.validate(config)
    except Exception as e:
        logger.error(f"❌ 配置验证失败: {e}")
        return
    
    # 2. 初始化监听器（根据配置选择本地或微信模式）
    try:
        listener = create_listener(config)
    except Exception as e:
        logger.error(f"❌ 监听器初始化失败: {e}")
        return
    
    # 3. 初始化其他模块
    try:
        logger.info("正在初始化其他模块...")
        
        parser = LLMParser(
            api_key=config['llm']['api_key'],
            base_url=config['llm']['base_url'],
            model_name=config['llm']['model_name'],
            request_timeout=config['llm'].get('request_timeout', 30),
            max_retries=config['llm'].get('max_retries', 3)
        )
        logger.info("✓ 大模型解析模块初始化完成")
        
        image_processor = ImageProcessor(
            enable_preprocessing=config['image'].get('enable_preprocessing', True),
            save_processed=config['image'].get('save_processed_images', False)
        )
        logger.info("✓ 图片处理模块初始化完成")
        
        excel_gen = ExcelGenerator(output_dir=config['output']['excel_dir'])
        logger.info("✓ Excel 生成模块初始化完成")
        
        logger.info("-" * 60)
        logger.info("系统初始化成功！开始监听消息...")
        logger.info(f"输出目录: {config['output']['excel_dir']}")
        logger.info("-" * 60)
    
    except Exception as e:
        logger.error(f"❌ 模块初始化失败: {e}")
        return
    
    # 4. 主循环
    error_count = 0
    max_consecutive_errors = 5
    message_count = 0
    
    # 如果是本地模式，给出提示
    if config.get('wechat', {}).get('mode', 'local').lower() == 'local':
        logger.info("\n💡 本地文件模式提示：")
        logger.info(f"   请将要处理的图片文件放到: {config['wechat']['listen_dir']}")
        logger.info("   支持的图片格式: .jpg, .jpeg, .png, .bmp, .gif, .webp")
        logger.info("   支持的文本格式: .txt")
        logger.info("")
    
    while True:
        try:
            # 获取新消息
            tasks = listener.get_new_messages()
            
            if not tasks:
                time.sleep(2)  # 没有消息时短暂休眠
                continue
            
            logger.info(f"\n📬 收到 {len(tasks)} 条待处理消息")
            
            for idx, task in enumerate(tasks, 1):
                try:
                    logger.info(f"【{idx}/{len(tasks)}】处理来自【{task['source']}】的{task['type']}信息...")
                    
                    parsed_data = None
                    
                    # 根据消息类型处理
                    if task["type"] == "image":
                        try:
                            # 图片预处理
                            processed_image = image_processor.preprocess_image(
                                task["data"],
                                output_dir=config['wechat']['listen_dir'] + "/processed"
                            )
                            parsed_data = parser.parse_content(image_path=processed_image)
                        except Exception as e:
                            logger.error(f"图片处理失败: {e}")
                    
                    elif task["type"] == "text":
                        try:
                            parsed_data = parser.parse_content(text_content=task["data"])
                        except Exception as e:
                            logger.error(f"文字处理失败: {e}")
                    
                    # 【新增】检测表格结构，识别动态列名
                    if parsed_data is None:
                        logger.warning("⚠ 解析失败（LLM 返回 None），跳过该消息")
                    elif not parsed_data.get('has_table', False):
                        logger.warning("⚠ 未识别到有效的表格内容")
                    else:
                        # 检测表格结构
                        structure_result = TableStructureDetector.detect_structure(parsed_data)
                        
                        if structure_result is None:
                            logger.warning("⚠ 表格结构检测失败，跳过该消息")
                        elif not structure_result.get('has_table', False):
                            logger.warning("⚠ 表格检测器确认无有效表格")
                        else:
                            # 规范化数据格式，确保所有数据都是字典格式
                            try:
                                normalized_data = TableStructureDetector.normalize_data(structure_result)
                                
                                # 数据验证和清洗（传入动态列名）
                                cleaned_data = DataValidator.validate_and_clean(
                                    normalized_data,
                                    enable_dedup=config['data'].get('enable_deduplication', True),
                                    columns=structure_result['columns'] if structure_result['columns'] else None
                                )
                                
                                if cleaned_data:
                                    logger.info(f"✓ 解析成功 - 提取 {len(cleaned_data)} 条有效记录")
                                    logger.info(f"✓ 识别列名: {structure_result['columns']}")
                                    
                                    # 【关键修改】传入动态列名给 Excel 生成器
                                    excel_path = excel_gen.generate(
                                        cleaned_data,
                                        source_name=task["source"],
                                        columns=structure_result['columns'] if structure_result['columns'] else None
                                    )
                                    
                                    if excel_path:
                                        logger.info(f"✓ Excel 已保存: {excel_path}")
                                        message_count += 1
                                        error_count = 0  # 重置错误计数
                                    else:
                                        logger.warning("⚠ Excel 生成失败")
                                else:
                                    logger.warning("⚠ 数据清洗后无有效记录")
                            except Exception as e:
                                logger.error(f"❌ 数据处理失败: {e}")
                                import traceback
                                logger.error(traceback.format_exc())
                
                except Exception as e:
                    logger.error(f"❌ 处理消息时发生异常: {e}")
                    error_count += 1
                    continue
            
            # 成功处理后短暂休眠
            time.sleep(2)
        
        except KeyboardInterrupt:
            logger.info("\n" + "=" * 60)
            logger.info("用户手动停止程序")
            logger.info(f"本次运行共处理 {message_count} 条消息")
            logger.info("=" * 60)
            break
        
        except Exception as e:
            logger.error(f"❌ 主循环异常: {e}")
            error_count += 1
            
            if error_count >= max_consecutive_errors:
                logger.critical(f"连续错误超过 {max_consecutive_errors} 次，程序退出")
                logger.critical("建议检查日志文件以了解详细错误信息")
                break
            
            logger.warning(f"等待 5 秒后重试... (错误计数: {error_count}/{max_consecutive_errors})")
            time.sleep(5)


if __name__ == "__main__":
    main()
