"""
消息监听和采集模块

支持两种模式：
1. 【本地文件模式】 LocalFileListener - 监听本地文件夹中的图片和文本文件（推荐）
2. 【微信直连模式】 WeChatBot - 直接监听微信聊天窗口（需要wxauto库）

功能：
- 自动监听指定来源（本地文件或微信聊天窗口）
- 采集图片消息并自动保存
- 采集文字消息并检测表格结构
- 支持多个监听对象
- 包含重试机制和容错处理
"""

import os
import time
from pathlib import Path
from src.logger import logger


class LocalFileListener:
    """
    【本地文件监听器】推荐方案
    
    监听本地文件夹中的图片和文本文件，无需依赖 wxauto 库。
    支持格式：
    - 图片：.jpg, .jpeg, .png, .bmp, .gif, .webp
    - 文本：.txt, .text
    """
    
    def __init__(self, watch_dir="data/temp_images"):
        """
        初始化本地文件监听器
        
        Args:
            watch_dir: 监听的本地文件夹路径
        
        Raises:
            Exception: 如果监听目录无法创建
        """
        try:
            self.watch_dir = os.path.abspath(watch_dir)
            self.processed_files = set()  # 跟踪已处理过的文件
            
            # 创建监听目录
            if not os.path.exists(self.watch_dir):
                os.makedirs(self.watch_dir)
            
            logger.info(f"✓ 本地文件监听器初始化成功")
            logger.info(f"  监听目录: {self.watch_dir}")
            logger.info(f"  说明: 请将要处理的图片放到此目录")
            logger.info(f"  支持格式: .jpg, .jpeg, .png, .bmp, .gif, .webp, .txt")
        
        except Exception as e:
            logger.error(f"❌ 本地文件监听器初始化失败: {e}")
            raise
    
    def get_new_messages(self):
        """
        扫描本地文件夹，获取新的未处理文件
        
        Returns:
            任务列表，每个任务包含 type, source, data, timestamp 等信息
        """
        try:
            # 支持的文件扩展名
            image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp'}
            text_extensions = {'.txt', '.text'}
            
            tasks = []
            
            # 扫描目录中的所有文件
            for file_path in Path(self.watch_dir).iterdir():
                if not file_path.is_file():
                    continue
                
                # 跳过已处理的文件
                if str(file_path) in self.processed_files:
                    continue
                
                # 跳过隐藏文件和临时文件
                if file_path.name.startswith('.') or file_path.name.startswith('~'):
                    continue
                
                file_ext = file_path.suffix.lower()
                
                # 处理图片文件
                if file_ext in image_extensions:
                    try:
                        task = {
                            'type': 'image',
                            'source': 'LocalFile',  # 来源标记
                            'data': str(file_path),  # 完整路径
                            'filename': file_path.name,
                            'timestamp': time.time()
                        }
                        tasks.append(task)
                        self.processed_files.add(str(file_path))
                        logger.debug(f"发现新图片: {file_path.name}")
                    
                    except Exception as e:
                        logger.warning(f"⚠ 处理图片文件异常: {file_path.name} - {e}")
                
                # 处理文本文件
                elif file_ext in text_extensions:
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read().strip()
                        
                        if content:  # 只处理非空文件
                            task = {
                                'type': 'text',
                                'source': 'LocalFile',  # 来源标记
                                'data': content,
                                'filename': file_path.name,
                                'timestamp': time.time()
                            }
                            tasks.append(task)
                            self.processed_files.add(str(file_path))
                            logger.debug(f"发现新文本文件: {file_path.name}")
                    
                    except Exception as e:
                        logger.warning(f"⚠ 读取文本文件异常: {file_path.name} - {e}")
            
            return tasks
        
        except Exception as e:
            logger.error(f"❌ 扫描本地文件夹失败: {e}")
            return []


class WeChatBot:
    """
    【微信直连监听器】
    
    直接连接微信客户端监听聊天窗口，支持监听多个聊天窗口。
    【注意】需要安装 wxauto 库（可选）
    """
    
    def __init__(self, listen_list, save_pic_dir):
        """
        初始化微信机器人
        
        Args:
            listen_list: 监听列表（好友名/群名）
            save_pic_dir: 图片保存目录
        
        Raises:
            Exception: 初始化失败时抛出异常
        """
        try:
            # 延迟导入 wxauto
            try:
                from wxauto import WeChat
            except ImportError:
                logger.error("❌ wxauto 库未安装")
                logger.error("请执行: pip install wxauto")
                logger.error("或使用本地文件监听模式（推荐）")
                raise ImportError("wxauto 库未找到")
            
            logger.info("正在连接微信...")
            self.wx = WeChat()
            logger.info("✓ 微信连接成功")
            
            self.listen_list = listen_list
            self.save_pic_dir = os.path.abspath(save_pic_dir)
            
            # 确保图片目录存在
            if not os.path.exists(self.save_pic_dir):
                os.makedirs(self.save_pic_dir)
                logger.info(f"✓ 创建图片保存目录: {self.save_pic_dir}")
            
            # 添加监听对象，支持重试
            for name in self.listen_list:
                self._add_listen_with_retry(name, max_retries=3)
            
            logger.info(f"✓ 微信机器人初始化完成，监听对象数: {len(self.listen_list)}")
        
        except Exception as e:
            logger.error(f"❌ 微信初始化失败: {e}")
            logger.error("请确保：")
            logger.error("  1. 微信已登录（已经打开微信客户端)")
            logger.error("  2. 监听对象是正确的微信好友名或群名")
            logger.error("  3. 微信窗口未被最小化")
            raise
    
    def _add_listen_with_retry(self, name, max_retries=3):
        """
        添加监听对象，支持重试机制
        
        Args:
            name: 聊天窗口名称（好友名或群名）
            max_retries: 最大重试次数
        
        Returns:
            成功返回 True，失败返回 False
        """
        for attempt in range(max_retries):
            try:
                self.wx.AddListenChat(who=name, savepic=True)
                logger.info(f"✓ 成功添加监听: 【{name}】")
                return True
            
            except Exception as e:
                logger.warning(f"⚠ 添加监听失败【{name}】（第{attempt+1}次尝试）: {e}")
                
                if attempt < max_retries - 1:
                    time.sleep(2)
                else:
                    logger.error(f"❌ 无法监听【{name}】，已重试{max_retries}次")
                    logger.warning(f"建议检查好友/群名是否正确拼写")
                    return False
    
    def get_new_messages(self):
        """
        获取新消息并分类处理
        
        处理流程：
        1. 从微信消息队列获取新消息
        2. 分类为图片消息或文字消息
        3. 图片自动保存
        4. 文字信息被过滤（仅保留结构化数据）
        
        Returns:
            任务列表，每个任务包含 type, source, data, timestamp 等信息
        
        Raises:
            Exception: 消息获取失败时返回空列表
        """
        try:
            msgs = self.wx.GetListenMessage()
        except Exception as e:
            logger.error(f"❌ 获取消息失败: {e}")
            return []
        
        if not msgs:
            return []
        
        tasks = []
        total_msgs = sum(len(messages) for messages in msgs.values())
        logger.debug(f"获取到 {total_msgs} 条消息，共来自 {len(msgs)} 个聊天窗口")
        
        for chat_room, messages in msgs.items():
            for msg in messages:
                try:
                    sender = msg.sender if hasattr(msg, 'sender') else "Unknown"
                    msg_type = msg.type if hasattr(msg, 'type') else None
                    content = msg.content if hasattr(msg, 'content') else None
                    
                    # 排除系统消息和自己的消息
                    if msg_type == 'sys' or msg_type is None:
                        logger.debug(f"跳过系统消息")
                        continue
                    
                    if sender == 'Self' or sender == 'self':
                        logger.debug(f"跳过自己发送的消息")
                        continue
                    
                    # 根据消息类型处理
                    if msg_type == 'pic':
                        self._handle_image_message(chat_room, sender, content, tasks)
                    
                    elif msg_type == 'friendmsg' or msg_type == 'txt' or msg_type == 'text':
                        self._handle_text_message(chat_room, sender, content, tasks)
                    
                    else:
                        logger.debug(f"忽略消息类型: {msg_type}")
                
                except Exception as e:
                    logger.warning(f"⚠ 处理消息异常: {e}")
                    continue
        
        logger.debug(f"本轮共提取 {len(tasks)} 条待处理消息")
        return tasks
    
    def _handle_image_message(self, chat_room, sender, content, tasks):
        """
        处理图片消息
        
        流程：
        1. 拿到图片路径（wxauto自动保存）
        2. 验证文件存在
        3. 添加到待处理队列
        
        Args:
            chat_room: 聊天窗口
            sender: 发送者
            content: 内容（图片路径）
            tasks: 待处理任务列表（修改此列表）
        """
        logger.info(f"📷 收到来自【{chat_room} - {sender}】的图片消息")
        
        # 微信自动保存图片，等待一下确保文件已写入
        time.sleep(1)
        
        if isinstance(content, str) and os.path.exists(content):
            file_size_kb = os.path.getsize(content) / 1024
            logger.info(f"✓ 图片文件有效 ({file_size_kb:.1f} KB): {content}")
            
            tasks.append({
                "type": "image",
                "source": f"{chat_room}-{sender}",
                "data": content,
                "timestamp": time.time(),
                "chat_room": chat_room,
                "sender": sender
            })
        else:
            logger.warning(f"❌ 图片路径无效或文件不存在: {content}")
    
    def _handle_text_message(self, chat_room, sender, content, tasks):
        """
        处理文字消息
        
        过滤规则：
        - 必须包含换行符（表明可能是表格）
        - 或包含表格相关关键词（品名、规格、价格等）
        
        Args:
            chat_room: 聊天窗口
            sender: 发送者
            content: 文字内容
            tasks: 待处理任务列表（修改此列表）
        """
        if not isinstance(content, str):
            return
        
        # 检测是否为结构化数据
        # 条件1：包含换行符（多行）
        # 条件2：包含表格相关关键词
        keyword_list = [
            # 产品相关
            "品名", "品牌", "商品", "产品", "物品",
            # 规格相关
            "规格", "型号", "尺寸", "大小", "尺码",
            # 价格相关
            "价格", "金额", "费用", "成本", "单价",
            # 其他
            "数量", "生产", "仓库", "库房", "产地", "材质"
        ]
        
        contains_keyword = any(keyword in content for keyword in keyword_list)
        contains_newline = "\n" in content
        
        if contains_newline or contains_keyword:
            logger.info(f"📝 收到来自【{chat_room} - {sender}】的结构化文字({len(content)}字)")
            
            tasks.append({
                "type": "text",
                "source": f"{chat_room}-{sender}",
                "data": content,
                "timestamp": time.time(),
                "chat_room": chat_room,
                "sender": sender
            })
        else:
            logger.debug(f"⊘ 文字消息不符合表格特征，跳过: {content[:50]}...")

