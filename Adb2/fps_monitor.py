#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Android应用帧率监控工具
使用ADB命令抓取指定应用的帧率数据并绘制图表
"""

import subprocess
import time
import re
import argparse
import sys
import os
from datetime import datetime
from typing import List, Tuple
from configparser import ConfigParser
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np

def load_config(config_path: str = 'config.ini') -> ConfigParser:
    """
    加载配置文件
    
    Args:
        config_path: 配置文件路径
        
    Returns:
        ConfigParser对象
    """
    config = ConfigParser()
    
    # 设置默认值
    config['adb'] = {
        'adb_path': 'adb',
        'command_timeout': '5'
    }
    config['monitor'] = {
        'default_duration': '60',
        'default_interval': '1.0',
        'primary_method': 'gfxinfo',
        'fallback_method': 'surfaceflinger'
    }
    config['chart'] = {
        'figure_width': '12',
        'figure_height': '8',
        'dpi': '300',
        'fps_60_color': 'green',
        'fps_30_color': 'orange',
        'font_family': 'Microsoft YaHei'
    }
    config['filter'] = {
        'min_frame_time': '1',
        'max_frame_time': '100',
        'filter_zero_fps': 'true'
    }
    
    # 如果配置文件存在，则读取并覆盖默认值
    if os.path.exists(config_path):
        config.read(config_path, encoding='utf-8')
    
    return config


# 加载配置
CONFIG = load_config()

# 设置中文字体支持
font_family = CONFIG.get('chart', 'font_family', fallback='Microsoft YaHei')
plt.rcParams['font.sans-serif'] = [font_family, 'SimHei', 'Microsoft YaHei']  # Windows中文字体
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题


class FPSMonitor:
    """Android应用帧率监控类"""
    
    def __init__(self, package_name: str, duration: int = 60, interval: float = 1.0, config: ConfigParser = None):
        """
        初始化帧率监控器
        
        Args:
            package_name: Android应用包名
            duration: 监控持续时间（秒）
            interval: 采样间隔（秒）
            config: 配置对象
        """
        self.config = config if config else CONFIG
        self.package_name = package_name
        self.duration = duration
        self.interval = interval
        self.fps_data = []
        self.time_data = []
        self.start_time = None
        
        # 从配置文件读取设置
        adb_path_raw = self.config.get('adb', 'adb_path', fallback='adb')
        # 去除引号（如果有）
        self.adb_path = adb_path_raw.strip('"').strip("'")
        self.adb_timeout = self.config.getint('adb', 'command_timeout', fallback=5)
        self.min_frame_time = self.config.getfloat('filter', 'min_frame_time', fallback=1.0)
        self.max_frame_time = self.config.getfloat('filter', 'max_frame_time', fallback=100.0)
        self.filter_zero_fps = self.config.getboolean('filter', 'filter_zero_fps', fallback=True)
        
    def check_adb_connection(self) -> bool:
        """检查ADB连接状态"""
        print(self.adb_path)
        try:
            result = subprocess.run(
                [self.adb_path, 'devices'],
                capture_output=True,
                text=True,
                timeout=self.adb_timeout
            )
            
            lines = result.stdout.strip().split('\n')
            if len(lines) < 2:
                print("❌ 未找到已连接的设备")
                return False
            
            devices = [line for line in lines[1:] if line.strip() and 'device' in line]
            if not devices:
                print("❌ 未找到已连接的设备")
                return False
                
            print(f"✓ 找到 {len(devices)} 个设备")
            print(f"✓ 使用 ADB 路径: {self.adb_path}")
            return True
            
        except FileNotFoundError:
            print(f"❌ 未找到adb命令: {self.adb_path}")
            print("   请检查配置文件中的 adb_path 设置，或确保 ADB 已添加到 PATH")
            return False
        except Exception as e:
            print(f"❌ 检查ADB连接时出错: {e}")
            return False
    
    def get_fps_from_dumpsys(self) -> float:
        """
        从dumpsys gfxinfo获取帧率数据
        
        Returns:
            当前帧率，如果获取失败返回0
        """
        print("get_fps_from_dumpsys");
        try:
            # 先清除之前的统计数据
            subprocess.run(
                [self.adb_path, 'shell', 'dumpsys', 'gfxinfo', self.package_name, 'reset'],
                capture_output=True,
                timeout=2
            )
            
            # 等待一小段时间让应用生成新的帧数据
            time.sleep(0.5)
            
            # 使用dumpsys gfxinfo获取帧率信息
            result = subprocess.run(
                [self.adb_path, 'shell', 'dumpsys', 'gfxinfo', self.package_name, 'framestats'],
                capture_output=True,
                text=True,
                timeout=self.adb_timeout
            )
            
            if result.returncode != 0:
                return 0
            
            # 解析帧时间数据
            lines = result.stdout.split('\n')
            frame_times = []
            
            # 寻找帧数据部分
            in_frame_data = False
            for line in lines:
                if '---PROFILEDATA---' in line:
                    in_frame_data = True
                    continue
                    
                if in_frame_data:
                    if line.strip() == '':
                        break
                    
                    # 跳过头部说明
                    if line.startswith('Flags,IntendedVsync'):
                        continue
                        
                    # 解析帧数据
                    parts = line.strip().split(',')
                    if len(parts) >= 3:
                        try:
                            # 第二列是IntendedVsync，第三列是实际帧完成时间
                            vsync_time = int(parts[1])
                            frame_time = int(parts[2])
                            if vsync_time > 0 and frame_time > 0:
                                # 计算帧耗时（纳秒转毫秒）
                                frame_duration = (frame_time - vsync_time) / 1000000.0
                                frame_times.append(frame_duration)
                        except (ValueError, IndexError):
                            continue
            
            # 计算平均FPS
            if frame_times:
                # 使用配置文件中的过滤范围
                valid_times = [t for t in frame_times if self.min_frame_time < t < self.max_frame_time]
                if valid_times:
                    avg_frame_time = np.mean(valid_times)
                    fps = 1000.0 / avg_frame_time
                    return round(fps, 2)
            
            return 0
            
        except Exception as e:
            print(f"获取FPS数据时出错: {e}")
            return 0
    
    def get_fps_surfaceflinger(self) -> float:
        """
        使用SurfaceFlinger方式获取FPS
        这是一个备用方法
        
        Returns:
            当前帧率
        """
        print("get_fps_surfaceflinger");

        try:
            # 清除之前的数据
            subprocess.run(
                [self.adb_path, 'shell', 'dumpsys', 'SurfaceFlinger', '--latency-clear'],
                capture_output=True,
                timeout=3
            )
            
            time.sleep(self.interval)
            
            # 获取帧数据
            result = subprocess.run(
                [self.adb_path, 'shell', 'dumpsys', 'SurfaceFlinger', '--latency', self.package_name],
                capture_output=True,
                text=True,
                timeout=self.adb_timeout
            )
            
            lines = result.stdout.strip().split('\n')
            if len(lines) < 2:
                return 0
            
            # 第一行是刷新周期（纳秒）
            refresh_period = float(lines[0])
            if refresh_period == 0:
                return 0
            
            # 统计有效帧数
            frame_count = 0
            for line in lines[1:]:
                parts = line.strip().split()
                if len(parts) == 3:
                    try:
                        if int(parts[0]) > 0:
                            frame_count += 1
                    except ValueError:
                        continue
            
            if frame_count > 0:
                # 计算FPS
                fps = (frame_count / self.interval)
                return round(fps, 2)
            
            return 0
            
        except Exception as e:
            print(f"使用SurfaceFlinger获取FPS时出错: {e}")
            return 0
    
    def get_fps_simple(self) -> float:
        """
        使用简单方法获取FPS（解析gfxinfo的总帧数）
        
        Returns:
            当前帧率
        """
        print("get_fps_simple");        
        try:
            # 第一次采样
            result1 = subprocess.run(
                [self.adb_path, 'shell', 'dumpsys', 'gfxinfo', self.package_name],
                capture_output=True,
                text=True,
                timeout=self.adb_timeout
            )
            
            # 提取第一次的总帧数
            total_frames_1 = 0
            for line in result1.stdout.split('\n'):
                if 'Total frames rendered:' in line:
                    parts = line.split(':')
                    if len(parts) >= 2:
                        total_frames_1 = int(parts[1].strip())
                        break
            
            # 等待采样间隔
            time.sleep(1.0)
            
            # 第二次采样
            result2 = subprocess.run(
                [self.adb_path, 'shell', 'dumpsys', 'gfxinfo', self.package_name],
                capture_output=True,
                text=True,
                timeout=self.adb_timeout
            )
            
            # 提取第二次的总帧数
            total_frames_2 = 0
            for line in result2.stdout.split('\n'):
                if 'Total frames rendered:' in line:
                    parts = line.split(':')
                    if len(parts) >= 2:
                        total_frames_2 = int(parts[1].strip())
                        break
            
            # 计算FPS
            if total_frames_2 > total_frames_1:
                fps = (total_frames_2 - total_frames_1) / 1.0
                return round(fps, 2)
            
            return 0
            
        except Exception as e:
            return 0
    
    def collect_data(self):
        """持续采集帧率数据"""
        print(f"\n开始监控应用: {self.package_name}")
        print(f"监控时长: {self.duration}秒")
        print(f"采样间隔: {self.interval}秒")
        print("=" * 50)
        
        self.start_time = time.time()
        iteration = 0
        
        while time.time() - self.start_time < self.duration:
            iteration += 1
            current_time = time.time() - self.start_time
            
            # 获取FPS数据（尝试三种方法）
            fps = self.get_fps_from_dumpsys()
            method_used = "gfxinfo"
            
            # 如果主方法失败，尝试备用方法
            if fps == 0:
                fps = self.get_fps_simple()
                method_used = "simple"
            
            if fps == 0:
                fps = self.get_fps_surfaceflinger()
                method_used = "surfaceflinger"
            
            # 根据配置决定是否过滤0值
            if not self.filter_zero_fps or fps > 0:
                self.fps_data.append(fps)
                self.time_data.append(current_time)
            
            # 显示进度（第一次显示使用的方法）
            progress = (current_time / self.duration) * 100
            if iteration == 1 and fps > 0:
                print(f"✓ 使用 {method_used} 方法采集数据")
            print(f"[{iteration:3d}] 时间: {current_time:6.1f}s | FPS: {fps:6.2f} | 进度: {progress:5.1f}%")
            
            # 等待下一次采样
            time.sleep(self.interval)
        
        print("=" * 50)
        print(f"✓ 数据采集完成，共采集 {len(self.fps_data)} 个数据点")
    
    def plot_fps_data(self, save_path: str = None):
        """
        绘制FPS数据图表
        
        Args:
            save_path: 图表保存路径，如果为None则显示图表
        """
        if not self.fps_data:
            print("❌ 没有数据可以绘制")
            return
        
        # 从配置读取图表设置
        fig_width = self.config.getfloat('chart', 'figure_width', fallback=12)
        fig_height = self.config.getfloat('chart', 'figure_height', fallback=8)
        dpi = self.config.getint('chart', 'dpi', fallback=300)
        fps_60_color = self.config.get('chart', 'fps_60_color', fallback='green')
        fps_30_color = self.config.get('chart', 'fps_30_color', fallback='orange')
        
        # 创建图表
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(fig_width, fig_height))
        
        # 图表1: FPS时间序列
        ax1.plot(self.time_data, self.fps_data, 'b-', linewidth=1.5, label='FPS')
        ax1.axhline(y=60, color=fps_60_color, linestyle='--', linewidth=1, alpha=0.7, label='60 FPS')
        ax1.axhline(y=30, color=fps_30_color, linestyle='--', linewidth=1, alpha=0.7, label='30 FPS')
        ax1.fill_between(self.time_data, self.fps_data, alpha=0.3)
        
        ax1.set_xlabel('时间 (秒)', fontsize=12)
        ax1.set_ylabel('帧率 (FPS)', fontsize=12)
        ax1.set_title(f'应用帧率监控 - {self.package_name}', fontsize=14, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        ax1.legend()
        
        # 统计信息
        fps_array = np.array(self.fps_data)
        valid_fps = fps_array[fps_array > 0]
        
        if len(valid_fps) > 0:
            avg_fps = np.mean(valid_fps)
            max_fps = np.max(valid_fps)
            min_fps = np.min(valid_fps)
            std_fps = np.std(valid_fps)
            
            stats_text = f'平均: {avg_fps:.2f} | 最大: {max_fps:.2f} | 最小: {min_fps:.2f} | 标准差: {std_fps:.2f}'
            ax1.text(0.02, 0.98, stats_text, transform=ax1.transAxes,
                    fontsize=10, verticalalignment='top',
                    bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        # 图表2: FPS分布直方图
        if len(valid_fps) > 0:
            ax2.hist(valid_fps, bins=30, color='skyblue', edgecolor='black', alpha=0.7)
            ax2.axvline(x=60, color=fps_60_color, linestyle='--', linewidth=2, label='60 FPS')
            ax2.axvline(x=30, color=fps_30_color, linestyle='--', linewidth=2, label='30 FPS')
            ax2.set_xlabel('帧率 (FPS)', fontsize=12)
            ax2.set_ylabel('频次', fontsize=12)
            ax2.set_title('帧率分布', fontsize=12, fontweight='bold')
            ax2.grid(True, alpha=0.3, axis='y')
            ax2.legend()
        
        plt.tight_layout()
        
        # 保存或显示图表
        if save_path:
            plt.savefig(save_path, dpi=dpi, bbox_inches='tight')
            print(f"✓ 图表已保存到: {save_path}")
        else:
            plt.show()
    
    def save_data_to_csv(self, csv_path: str = None):
        """
        保存数据到CSV文件
        
        Args:
            csv_path: CSV文件保存路径
        """
        if not self.fps_data:
            print("❌ 没有数据可以保存")
            return
        
        if csv_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            csv_path = f"fps_data_{timestamp}.csv"
        
        try:
            with open(csv_path, 'w', encoding='utf-8') as f:
                f.write("Time(s),FPS\n")
                for t, fps in zip(self.time_data, self.fps_data):
                    f.write(f"{t:.2f},{fps:.2f}\n")
            
            print(f"✓ 数据已保存到: {csv_path}")
        except Exception as e:
            print(f"❌ 保存数据时出错: {e}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='Android应用帧率监控工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python fps_monitor.py com.example.app -d 60 -i 1.0
  python fps_monitor.py com.tencent.mm -d 120 -i 0.5 -o fps_chart.png
  python fps_monitor.py com.android.chrome -d 30 --csv fps_data.csv
  python fps_monitor.py com.example.app --config custom_config.ini

配置文件:
  可以在 config.ini 中配置 ADB 路径和其他参数
  使用 --config 参数可以指定自定义配置文件
        """
    )
    
    parser.add_argument('package', nargs='?', default=None,
                       help='Android应用包名（可选，未指定则从配置文件读取）')
    parser.add_argument('-d', '--duration', type=int, default=None,
                       help='监控持续时间（秒），默认从配置文件读取或60秒')
    parser.add_argument('-i', '--interval', type=float, default=None,
                       help='采样间隔（秒），默认从配置文件读取或1.0秒')
    parser.add_argument('-o', '--output', type=str, default=None,
                       help='图表输出文件路径（png/jpg/pdf），不指定则显示图表')
    parser.add_argument('--csv', type=str, default=None,
                       help='导出CSV数据文件路径')
    parser.add_argument('--config', type=str, default='config.ini',
                       help='配置文件路径，默认为 config.ini')
    parser.add_argument('-p', '--package-name', dest='package_flag', default=None,
                       help='应用包名（备选方式，与位置参数二选一）')
    
    args = parser.parse_args()
    
    # 加载配置
    config = load_config(args.config)
    
    # 确定包名（优先级：命令行位置参数 > --package-name > 配置文件）
    package_name = args.package or args.package_flag
    if not package_name:
        package_name = config.get('monitor', 'default_package', fallback='').strip()
    
    if not package_name:
        print("❌ 错误：未指定应用包名")
        print("   请通过以下方式之一指定包名：")
        print("   1. 命令行参数：python fps_monitor.py com.example.app")
        print("   2. 配置文件：在 config.ini 的 [monitor] 节中设置 default_package")
        print("   3. --package-name 参数：python fps_monitor.py --package-name com.example.app")
        sys.exit(1)
    
    # 从配置文件获取默认值（如果命令行参数未指定）
    duration = args.duration if args.duration is not None else config.getint('monitor', 'default_duration', fallback=60)
    interval = args.interval if args.interval is not None else config.getfloat('monitor', 'default_interval', fallback=1.0)
    
    # 创建监控器
    monitor = FPSMonitor(package_name, duration, interval, config)
    
    # 检查ADB连接
    if not monitor.check_adb_connection():
        sys.exit(1)
    
    try:
        # 采集数据
        monitor.collect_data()
        
        # 保存CSV数据
        if args.csv:
            monitor.save_data_to_csv(args.csv)
        
        # 绘制图表
        monitor.plot_fps_data(args.output)
        
    except KeyboardInterrupt:
        print("\n\n⚠ 用户中断，正在保存已采集的数据...")
        if monitor.fps_data:
            monitor.plot_fps_data(args.output)
            if args.csv:
                monitor.save_data_to_csv(args.csv)
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()

