import base64
import json
import time
from openai import OpenAI, APIError, APIConnectionError
from src.logger import logger

class LLMParser:
    """
    大模型视觉解析模块
    
    支持图片和文本内容的解析，调用多模态大模型进行数据提取
    """
    
    def __init__(self, api_key, base_url, model_name, request_timeout=30, max_retries=3):
        """
        初始化大模型解析器
        
        Args:
            api_key: API Key
            base_url: API 端点
            model_name: 模型名称
            request_timeout: 请求超时时间（秒）
            max_retries: 最大重试次数
        """
        try:
            self.client = OpenAI(api_key=api_key, base_url=base_url, timeout=request_timeout)
            self.model_name = model_name
            self.request_timeout = request_timeout
            self.max_retries = max_retries
            logger.info(f"✓ 大模型客户端初始化成功: {model_name}")
        except Exception as e:
            logger.error(f"❌ 大模型客户端初始化失败: {e}")
            raise
        
        self.prompt = """
        你是一个专业的表格数据提取专家。请从提供的内容（图片或文本）中精确提取数据。
        
        提取要求：
        1. 必须严格输出为以下JSON数组格式，不输出任何多余的解释文字和Markdown标记符号
        2. 每个对象代表一条产品记录，包含以下字段：
           - 品名: 产品名称（必填，不能为空）
           - 规格: 产品规格（如Φ10*1.5、M8*20等，如无则为空字符串""）
           - 材质: 产品材质（如碳钢、不锈钢等，如无则为空字符串""）
           - 产地: 产地信息（如天津、浙江等，如无则为空字符串""）
           - 仓库: 仓库位置（如库房A、库房B等，如无则为空字符串""）
           - 价格: 价格信息（如150元/支、2元/个等，保留单位，如无则为空字符串""）
        
        输出格式示例（注意：直接输出JSON，不加任何```标记）：
        [
            {"品名": "钢管", "规格": "Φ10*1.5", "材质": "碳钢", "产地": "天津", "仓库": "库房A", "价格": "150元/支"},
            {"品名": "螺栓", "规格": "M8*20", "材质": "不锈钢", "产地": "浙江", "仓库": "库房B", "价格": "2元/个"}
        ]
        
        处理规则：
        - 如果表格中某个字段为空或不存在，对应值填为空字符串""（不是null）
        - 如果表头名称与标准字段不完全一致，请根据内容语义进行映射
          例如："商品名"→"品名"，"型号"→"规格"，"来源地"→"产地"
        - 对于合并单元格或多级表头，应根据上下文推断数据所属
        - 若发现重复记录（相同的品名和规格），只保留第一条
        - 对于表格中的备注、说明等额外信息，如果分类不明确，尽量归纳到相关字段
        - 处理特殊字符（如Φ、※、●等）时保持原样，不做替换
        
        输出规则：
        - 直接输出JSON数组，不包含任何```、```json标记
        - 不输出任何言语解释或说明
        - 如果无法提取任何记录，输出空数组 []
        """
    
    def _encode_image(self, image_path):
        """编码图片文件"""
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            logger.error(f"图片编码失败: {e}")
            raise
    
    def parse_content(self, text_content=None, image_path=None):
        """
        解析内容，支持重试机制
        
        支持同时处理图片和文字，或仅其中之一
        
        Args:
            text_content: 文字内容（可选）
            image_path: 图片路径（可选）
        
        Returns:
            解析结果（JSON列表）或None
        """
        if not text_content and not image_path:
            logger.error("❌ 必须提供文字内容或图片路径之一")
            return None
        
        messages = [{"role": "system", "content": self.prompt}]
        
        # 构建用户消息
        user_content = []
        
        if text_content:
            user_content.append({
                "type": "text",
                "text": f"请精确提取以下内容中的表格数据，必须输出JSON数组格式：\n{text_content}"
            })
            logger.info(f"准备解析文字内容（{len(text_content)} 字符）...")
        
        if image_path:
            try:
                base64_image = self._encode_image(image_path)
                user_content.append({
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                })
                logger.info(f"已加载图片: {image_path}")
            except Exception as e:
                logger.error(f"❌ 无法处理图片 {image_path}: {e}")
                return None
        
        messages.append({"role": "user", "content": user_content})
        
        # 重试循环
        for attempt in range(self.max_retries):
            try:
                logger.info(f"正在调用大模型进行数据解析（第{attempt+1}/{self.max_retries}次）...")
                
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=messages,
                    timeout=self.request_timeout
                )
                
                result_str = response.choices[0].message.content.strip()
                logger.debug(f"原始响应: {result_str[:300]}...")
                
                # 清洗响应
                result_str = self._clean_response(result_str)
                
                # 验证JSON格式
                try:
                    result = json.loads(result_str)
                except json.JSONDecodeError as e:
                    logger.error(f"❌ JSON 解析失败: {e}")
                    logger.error(f"原始响应内容: {result_str[:500]}")
                    raise ValueError(f"大模型响应不是有效的JSON格式")
                
                # 验证是否为列表
                if not isinstance(result, list):
                    logger.error(f"❌ 响应类型错误，期望列表但得到 {type(result)}")
                    raise ValueError("大模型响应不是数组格式")
                
                logger.info(f"✓ 解析成功，提取到 {len(result)} 条记录")
                return result if result else []
            
            except (APIError, APIConnectionError, TimeoutError) as e:
                logger.warning(f"⚠ API 调用失败（第{attempt+1}次）: {type(e).__name__}: {e}")
                
                if attempt < self.max_retries - 1:
                    # 指数退避重试策略
                    wait_time = min(2 ** attempt, 30)
                    logger.info(f"等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"❌ 大模型解析失败，已重试 {self.max_retries} 次，放弃")
                    return None
            
            except ValueError as e:
                logger.error(f"❌ 数据验证失败: {e}")
                return None
            
            except Exception as e:
                logger.error(f"❌ 未预期的错误: {type(e).__name__}: {e}")
                return None
        
        return None
    
    @staticmethod
    def _clean_response(result_str):
        """
        清洗模型响应，移除多余的格式标记
        
        处理的情况：
        - 移除 ```json 和 ``` 标记
        - 移除多余的空白字符
        - 移除前缀和后缀的文字
        
        Args:
            result_str: 原始响应字符串
        
        Returns:
            清洗后的字符串
        """
        result_str = result_str.strip()
        
        # 移除 Markdown 代码块标记
        if result_str.startswith("```json"):
            result_str = result_str[7:]
        elif result_str.startswith("```"):
            result_str = result_str[3:]
        
        if result_str.endswith("```"):
            result_str = result_str[:-3]
        
        result_str = result_str.strip()
        
        # 查找第一个 [ 和最后一个 ]
        first_bracket = result_str.find('[')
        last_bracket = result_str.rfind(']')
        
        if first_bracket != -1 and last_bracket != -1 and first_bracket < last_bracket:
            result_str = result_str[first_bracket:last_bracket+1]
        
        return result_str.strip()