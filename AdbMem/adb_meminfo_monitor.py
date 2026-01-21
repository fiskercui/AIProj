#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ADB Memory Info Monitor
监控指定Android进程的内存信息，每秒执行一次并输出到文件
"""

import subprocess
import time
import os
import re
import json
from datetime import datetime

# 配置文件路径
CONFIG_FILE = "adb_meminfo_config.json"

# 默认配置值
DEFAULT_CONFIG = {
    "adb_path": "adb.exe",
    "target_process_keyword": "com.android.webview:sandboxed_process0",
    "monitor_interval_seconds": 1
}

# 全局配置变量
ADB_PATH = None
TARGET_PROCESS_KEYWORD = None
MONITOR_INTERVAL = None

# 输出文件名
OUTPUT_FILE = f"meminfo_output_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"


def load_config():
    """
    从配置文件加载配置
    
    Returns:
        配置字典
    """
    global ADB_PATH, TARGET_PROCESS_KEYWORD, MONITOR_INTERVAL
    
    config = DEFAULT_CONFIG.copy()
    
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                user_config = json.load(f)
                config.update(user_config)
            print(f"已从配置文件加载: {CONFIG_FILE}")
        except Exception as e:
            print(f"警告: 读取配置文件失败，使用默认配置: {e}")
    else:
        print(f"警告: 未找到配置文件 '{CONFIG_FILE}'，使用默认配置")
        print(f"您可以创建 {CONFIG_FILE} 来自定义配置")
    
    ADB_PATH = config["adb_path"]
    TARGET_PROCESS_KEYWORD = config["target_process_keyword"]
    MONITOR_INTERVAL = config["monitor_interval_seconds"]
    
    return config


def run_adb_command(command):
    """
    执行ADB命令并返回输出
    
    Args:
        command: 完整的命令字符串
        
    Returns:
        命令输出的字符串，如果失败返回None
    """
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding='gbk',  # Windows中文环境使用gbk编码
            errors='ignore',  # 忽略无法解码的字符
            shell=True
        )
        
        if result.returncode == 0:
            return result.stdout
        else:
            print(f"命令执行失败: {command}")
            if result.stderr:
                print(f"错误信息: {result.stderr}")
            return None
    except Exception as e:
        print(f"执行命令时出错: {e}")
        return None


def find_target_process():
    """
    查找包含目标关键字的进程
    
    Returns:
        完整的进程名，如果未找到返回None
    """
    print(f"正在查找包含 '{TARGET_PROCESS_KEYWORD}' 的进程...")
    
    # 执行 ps -A 命令获取所有进程
    command = f'"{ADB_PATH}" shell ps -A'
    output = run_adb_command(command)
    
    if output is None:
        return None
    
    # 解析输出，查找目标进程
    for line in output.split('\n'):
        if TARGET_PROCESS_KEYWORD in line:
            # 进程名通常在最后一列
            parts = line.split()
            if len(parts) > 0:
                process_name = parts[-1]
                print(f"找到目标进程: {process_name}")
                return process_name
    
    print(f"未找到包含 '{TARGET_PROCESS_KEYWORD}' 的进程")
    return None


def get_meminfo(process_name):
    """
    获取指定进程的内存信息
    
    Args:
        process_name: 进程名
        
    Returns:
        dumpsys meminfo的输出
    """
    command = f'"{ADB_PATH}" shell dumpsys meminfo {process_name}'
    return run_adb_command(command)


def format_meminfo_to_markdown(meminfo_text):
    """
    将dumpsys meminfo的输出格式化为Markdown
    
    Args:
        meminfo_text: dumpsys meminfo的原始输出
        
    Returns:
        格式化后的Markdown文本
    """
    if not meminfo_text:
        return "**错误**: 无法获取内存信息\n"
    
    markdown_output = []
    lines = meminfo_text.strip().split('\n')
    
    i = 0
    while i < len(lines):
        line = lines[i].rstrip()
        
        # 空行
        if not line.strip():
            markdown_output.append("")
            i += 1
            continue
        
        # 检测两行表头的情况 (Pss / Total 这种分两行的)
        # 第一行: Pss  Private  Private  SwapPss  Rss  Heap  Heap  Heap
        # 第二行:      Total    Dirty    Clean    Dirty Total Size  Alloc Free
        if i + 1 < len(lines):
            next_line = lines[i + 1].rstrip()
            
            # 如果当前行包含Pss, Private等关键字，且下一行包含Total, Dirty等
            if (re.search(r'\b(Pss|Private|Shared|SwapPss|Rss|Heap)\b', line) and
                re.search(r'\b(Total|Dirty|Clean|Size|Alloc|Free)\b', next_line)):
                
                # 检查是否为表头（主要是不包含太多数字）
                num_count = sum(1 for part in line.split() if part.replace(',', '').isdigit())
                
                if num_count < 3:  # 是表头
                    # 合并两行表头
                    parts1 = line.split()
                    parts2 = next_line.split()
                    
                    # 组合表头
                    headers = []
                    j1, j2 = 0, 0
                    
                    while j1 < len(parts1) or j2 < len(parts2):
                        if j1 < len(parts1):
                            # 检查parts2是否有对应的子项
                            if j2 < len(parts2) and parts2[j2] not in ['Pss', 'Private', 'Shared', 'SwapPss', 'Rss', 'Heap']:
                                headers.append(f"{parts1[j1]} {parts2[j2]}")
                                j2 += 1
                            else:
                                headers.append(parts1[j1])
                            j1 += 1
                        elif j2 < len(parts2):
                            headers.append(parts2[j2])
                            j2 += 1
                    
                    # 输出Markdown表格头
                    markdown_output.append("\n| " + " | ".join(headers) + " |")
                    markdown_output.append("| " + " | ".join(["---"] * len(headers)) + " |")
                    
                    # 跳过第二行，开始读取数据
                    i += 2
                    
                    # 读取表格数据行
                    while i < len(lines):
                        data_line = lines[i].rstrip()
                        
                        if not data_line.strip():
                            break
                        
                        # 检查是否是数据行（包含数字或者以已知标签开头）
                        data_parts = data_line.split()
                        if len(data_parts) > 0:
                            # 检查是否是新的节
                            if data_line.strip().isupper() or ':' in data_line:
                                break
                            
                            # 处理多词标签（如"Native Heap"）
                            # 查找第一个数字的位置
                            first_num_idx = -1
                            for idx, part in enumerate(data_parts):
                                if part.replace(',', '').isdigit():
                                    first_num_idx = idx
                                    break
                            
                            if first_num_idx > 0:
                                # 标签是第一个数字之前的所有词
                                label = ' '.join(data_parts[:first_num_idx])
                                values = data_parts[first_num_idx:]
                                
                                # 确保数据列数与表头匹配
                                row_data = [label] + values
                                markdown_output.append("| " + " | ".join(row_data) + " |")
                                i += 1
                            else:
                                # 没有找到数字，可能是节标题
                                break
                        else:
                            break
                    
                    continue
        
        # 检测节标题（通常以特定关键字开头或全大写）
        if line.strip().isupper() or line.startswith('App Summary') or line.startswith('Objects'):
            markdown_output.append(f"\n### {line}")
            i += 1
            continue
        
        # 包含冒号的行（键值对）
        if ':' in line and not re.search(r'^\s+', line):
            key_value = line.split(':', 1)
            if len(key_value) == 2:
                key = key_value[0].strip()
                value = key_value[1].strip()
                markdown_output.append(f"**{key}**: {value}")
            else:
                markdown_output.append(line)
            i += 1
            continue
        
        # 普通文本行
        markdown_output.append(line)
        i += 1
    
    return '\n'.join(markdown_output)


def main():
    """
    主函数：循环监控进程内存信息
    """
    print("=" * 60)
    print("ADB 内存信息监控工具")
    print("=" * 60)
    
    # 加载配置
    load_config()
    
    print(f"ADB路径: {ADB_PATH}")
    print(f"目标进程关键字: {TARGET_PROCESS_KEYWORD}")
    print(f"监控间隔: {MONITOR_INTERVAL}秒")
    print(f"输出文件: {OUTPUT_FILE}")
    print("=" * 60)
    
    # 检查ADB是否可用
    if not os.path.exists(ADB_PATH):
        print(f"错误: 未找到ADB可执行文件 '{ADB_PATH}'")
        print("请确保adb.exe在当前目录下")
        return
    
    # 查找目标进程
    process_name = find_target_process()
    
    if process_name is None:
        print("无法找到目标进程，程序退出")
        return
    
    print(f"\n开始监控进程: {process_name}")
    print(f"每{MONITOR_INTERVAL}秒获取一次内存信息...")
    print(f"输出将保存到: {OUTPUT_FILE}")
    print("按 Ctrl+C 停止监控\n")
    
    # 打开输出文件
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        # 写入Markdown文件头信息
        f.write(f"# ADB Memory Info Monitor\n\n")
        f.write(f"**Target Process**: `{process_name}`\n\n")
        f.write(f"**Start Time**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("---\n\n")
        f.flush()
        
        execution_count = 0
        
        try:
            while True:
                execution_count += 1
                current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                print(f"[{current_time}] 第 {execution_count} 次执行...")
                
                # 获取内存信息
                meminfo = get_meminfo(process_name)
                
                if meminfo:
                    # 格式化为Markdown并写入
                    markdown_content = format_meminfo_to_markdown(meminfo)
                    
                    f.write(f"\n## Execution #{execution_count}\n\n")
                    f.write(f"**Time**: {current_time}\n\n")
                    f.write(markdown_content)
                    f.write("\n\n---\n\n")
                    f.flush()  # 立即刷新到文件
                    
                    # 提取并显示关键信息（PSS总量）
                    for line in meminfo.split('\n'):
                        if 'TOTAL' in line and 'PSS' in line:
                            print(f"    {line.strip()}")
                            break
                else:
                    print(f"    获取内存信息失败")
                    f.write(f"\n[{current_time}] 获取内存信息失败\n")
                    f.flush()
                
                # 等待指定时间间隔
                time.sleep(MONITOR_INTERVAL)
                
        except KeyboardInterrupt:
            print("\n\n监控已停止")
            f.write(f"\n\n---\n\n")
            f.write(f"## Summary\n\n")
            f.write(f"**Monitoring Stopped**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**Total Executions**: {execution_count}\n")
    
    print(f"\n结果已保存到: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
