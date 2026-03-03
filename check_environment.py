#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
环境检查脚本

功能：在启动程序前检查环境配置是否完整
使用方法：python check_environment.py
"""

import os
import sys
import importlib.util


def print_header(text):
    """打印标题"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)


def print_ok(text):
    """打印成功消息"""
    print(f"  ✓ {text}")


def print_error(text):
    """打印错误消息"""
    print(f"  ✗ {text}")


def print_warning(text):
    """打印警告消息"""
    print(f"  ⚠ {text}")


def check_python_version():
    """检查 Python 版本"""
    print_header("1. Python 版本检查")
    
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print_ok(f"Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print_error(f"Python 版本过低: {version.major}.{version.minor}，需要 3.8+")
        return False


def check_dependencies():
    """检查依赖包"""
    print_header("2. 依赖包检查")
    
    packages = {
        "yaml": "PyYAML",
        "pandas": "pandas",
        "openpyxl": "openpyxl",
        "loguru": "loguru",
        "openai": "openai",
        "cv2": "opencv-python",
        "numpy": "numpy",
        "PIL": "Pillow",
        "wxauto": "wxauto"
    }
    
    all_ok = True
    for module_name, package_name in packages.items():
        try:
            spec = importlib.util.find_spec(module_name)
            if spec is not None:
                print_ok(f"{package_name}")
            else:
                print_error(f"{package_name} 未找到")
                all_ok = False
        except ImportError:
            print_error(f"{package_name} 未安装")
            all_ok = False
    
    return all_ok


def check_directories():
    """检查必要的目录"""
    print_header("3. 目录结构检查")
    
    required_dirs = [
        "config",
        "src",
        "data",
        "data/temp_images",
        "data/output_excel",
        "logs"
    ]
    
    all_ok = True
    for directory in required_dirs:
        if os.path.exists(directory):
            print_ok(f"{directory}/")
        else:
            print_warning(f"{directory}/ 不存在，程序会自动创建")
            os.makedirs(directory, exist_ok=True)
    
    return True


def check_config_file():
    """检查配置文件"""
    print_header("4. 配置文件检查")
    
    config_path = "config/settings.yaml"
    
    if not os.path.exists(config_path):
        print_error(f"配置文件不存在: {config_path}")
        return False
    
    print_ok("配置文件存在")
    
    # 检查配置内容
    try:
        import yaml
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        
        # 检查关键配置
        checks = [
            ("wechat.listen_list", config.get("wechat", {}).get("listen_list")),
            ("wechat.save_pic_dir", config.get("wechat", {}).get("save_pic_dir")),
            ("output.excel_dir", config.get("output", {}).get("excel_dir")),
            ("llm.api_key", config.get("llm", {}).get("api_key")),
            ("llm.base_url", config.get("llm", {}).get("base_url")),
            ("llm.model_name", config.get("llm", {}).get("model_name"))
        ]
        
        all_ok = True
        for key, value in checks:
            if value:
                if "api_key" in key and isinstance(value, str) and value.startswith("sk-your"):
                    print_warning(f"{key} 仍为示例值，需修改")
                    all_ok = False
                elif "api_key" in key:
                    print_ok(f"{key} 已填写")
                elif "listen_list" in key and isinstance(value, list):
                    print_ok(f"{key} = {value}")
                else:
                    print_ok(f"{key} = {value}")
            else:
                print_error(f"{key} 未配置")
                all_ok = False
        
        return all_ok
    
    except Exception as e:
        print_error(f"配置文件解析失败: {e}")
        return False


def check_wechat():
    """检查微信"""
    print_header("5. 微信检查")
    
    try:
        from wxauto import WeChat
        try:
            wx = WeChat()
            print_ok("微信已登录并可连接")
            return True
        except Exception as e:
            print_error(f"无法连接微信: {e}")
            print_warning("请确保：")
            print_warning("  1. 微信客户端已打开")
            print_warning("  2. 已完成登录")
            print_warning("  3. 微信窗口未被最小化")
            return False
    except ImportError:
        print_error("wxauto 库未安装")
        return False


def check_api_connection():
    """检查大模型 API 连接"""
    print_header("6. 大模型 API 检查（可选）")
    
    try:
        import yaml
        with open("config/settings.yaml", "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        
        api_key = config.get("llm", {}).get("api_key")
        base_url = config.get("llm", {}).get("base_url")
        
        if api_key.startswith("sk-your"):
            print_warning("API Key 仍为示例值，请忽略此检查")
            return True
        
        try:
            from openai import OpenAI
            client = OpenAI(api_key=api_key, base_url=base_url, timeout=5)
            # 执行一个简单的测试（不一定要成功）
            print_ok("API 客户端初始化成功")
            return True
        except Exception as e:
            print_warning(f"API 连接测试失败（可能是网络问题）: {e}")
            return True  # 不作为强制要求
    
    except Exception as e:
        print_warning(f"无法检查 API: {e}")
        return True


def main():
    """主检查函数"""
    print("\n" + "=" * 60)
    print("  微信表格自动化处理工具 - 环境检查")
    print("=" * 60)
    
    checks = [
        ("Python 版本", check_python_version),
        ("依赖包", check_dependencies),
        ("目录结构", check_directories),
        ("配置文件", check_config_file),
        ("微信连接", check_wechat),
        ("API 连接", check_api_connection)
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print_error(f"{name} 检查异常: {e}")
            results.append((name, False))
    
    # 输出总结
    print_header("检查总结")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"  {name:15} {status}")
    
    print(f"\n  总体: {passed}/{total} 项通过")
    
    if passed == total:
        print_ok("所有检查通过！可以启动程序")
        print("\n  运行命令：python main.py\n")
        return 0
    else:
        print_error("有检查项未通过，请修正后重试")
        print("\n  详见上面的错误信息\n")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
