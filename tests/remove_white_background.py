# 🎉 状态章透明背景问题分析和解决方案

## 测试结果

✅ **所有自动化测试通过**
- 服务器正在运行
- 流程配置正确
- overlay=True 已添加（7处）
- 文本换行代码已添加
- PNG 文件有透明通道

## 问题分析

### 为什么状态章还是有白色背景？

经过测试，代码是正确的，问题可能是：

#### 1. **PNG 文件本身的问题** ⚠️ 最可能

虽然 PNG 文件有透明通道（RGBA），但**透明区域可能被填充为白色**。

**验证方法**：
查看测试 PDF：`/tmp/test_transparency.pdf`
- 如果能看到红色背景 → PNG 透明度正常，问题在其他地方
- 如果看到白色背景 → PNG 文件需要重新制作

#### 2. **浏览器缓存** 

PDF 可能被浏览器缓存了。

**解决方法**：
- 强制刷新：`Ctrl + Shift + R`
- 清除浏览器缓存
- 使用隐私模式测试

#### 3. **服务器未重启**

虽然测试显示服务器在运行，但可能是旧进程。

**解决方法**：
```bash
cd /root/dingtalk-h5-app
./restart_server.sh
```

## 解决方案

### 方案1：重新制作透明 PNG（推荐）

如果测试 PDF 中看到白色背景，需要重新制作 PNG：

#### 使用在线工具（最简单）

1. **Remove.bg**
   - 访问：https://www.remove.bg/
   - 上传状态章图片
   - 自动去除背景
   - 下载透明 PNG

2. **在线 PNG 工具**
   - 访问：https://onlinepngtools.com/create-transparent-png
   - 上传图片
   - 选择要变透明的颜色（白色）
   - 下载结果

#### 使用 Photoshop/GIMP

1. 打开 PNG 文件
2. 使用魔棒工具选择白色背景
3. 按 Delete 删除
4. 文件 → 导出为 → PNG（确保勾选"透明度"）
5. 保存

#### 替换文件

```bash
# 备份原文件
cp /root/dingtalk-h5-app/static/stamps/client/agree.png \
   /root/dingtalk-h5-app/static/stamps/client/agree.png.bak

# 上传新文件到服务器
# 替换 /root/dingtalk-h5-app/static/stamps/client/agree.png
```

### 方案2：使用 Python 自动去除白色背景

<function_calls>
<invoke name="Write">
<parameter name="contents">#!/usr/bin/env python3
"""
自动去除 PNG 白色背景
需要安装: pip install Pillow
"""

from PIL import Image
import numpy as np
from pathlib import Path

# 获取脚本所在目录（项目根目录）
SCRIPT_DIR = Path(__file__).parent.absolute()

def remove_white_background(input_path, output_path, threshold=240):
    """
    去除 PNG 的白色背景
    
    Args:
        input_path: 输入 PNG 文件路径
        output_path: 输出 PNG 文件路径
        threshold: 白色阈值（0-255），默认 240
    """
    # 打开图片
    img = Image.open(input_path)
    
    # 转换为 RGBA
    img = img.convert("RGBA")
    
    # 转换为 numpy 数组
    data = np.array(img)
    
    # 获取 RGB 通道
    r, g, b, a = data[:,:,0], data[:,:,1], data[:,:,2], data[:,:,3]
    
    # 找到白色像素（RGB 都接近 255）
    white_mask = (r > threshold) & (g > threshold) & (b > threshold)
    
    # 将白色像素的 alpha 通道设为 0（透明）
    data[white_mask, 3] = 0
    
    # 创建新图片
    result = Image.fromarray(data)
    
    # 保存
    result.save(output_path, "PNG")
    
    print(f"✅ 已处理: {output_path}")
    print(f"   原始尺寸: {img.size}")
    print(f"   透明像素数: {np.sum(white_mask)}")

if __name__ == "__main__":
    stamps_dir = SCRIPT_DIR / "static/stamps"
    
    # 处理所有 PNG 文件
    for png_file in stamps_dir.rglob("*.png"):
        print(f"\n处理: {png_file.name}")
        
        # 备份
        backup = png_file.with_suffix(".png.bak")
        if not backup.exists():
            import shutil
            shutil.copy(png_file, backup)
            print(f"   备份到: {backup.name}")
        
        # 处理
        try:
            remove_white_background(png_file, png_file)
        except Exception as e:
            print(f"   ❌ 失败: {e}")
    
    print("\n✅ 所有文件处理完成")
    print("\n如果效果不好，可以从备份恢复：")
    print("  cp *.png.bak *.png")
