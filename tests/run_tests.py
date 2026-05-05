#!/usr/bin/env python3
"""
钉钉 H5 应用自动化测试框架
"""

import sys
import os
import json
import time
from pathlib import Path
from typing import Dict, List, Tuple

# 添加项目路径（使用脚本所在目录）
SCRIPT_DIR = Path(__file__).parent.absolute()
sys.path.insert(0, str(SCRIPT_DIR))

class TestFramework:
    def __init__(self):
        self.base_dir = SCRIPT_DIR
        self.results = []
        
    def test_png_transparency(self) -> Tuple[bool, str]:
        """测试 PNG 透明度"""
        import fitz
        
        try:
            stamp_path = self.base_dir / "static/stamps/client/agree.png"
            if not stamp_path.exists():
                return False, f"文件不存在: {stamp_path}"
            
            # 创建测试 PDF
            doc = fitz.open()
            page = doc.new_page(width=300, height=300)
            
            # 绘制红色背景
            page.draw_rect(fitz.Rect(0, 0, 300, 300), color=(1, 0, 0), fill=(1, 0, 0))
            
            # 插入状态章（使用 overlay=True）
            rect = fitz.Rect(50, 50, 250, 250)
            page.insert_image(rect, filename=str(stamp_path), overlay=True)
            
            # 保存
            output = Path("/tmp/test_transparency.pdf")
            doc.save(str(output))
            doc.close()
            
            return True, f"测试 PDF 已生成: {output}\n如果能看到红色背景，说明透明度正常"
        except Exception as e:
            return False, f"测试失败: {e}"
    
    def test_overlay_parameter(self) -> Tuple[bool, str]:
        """测试 overlay 参数是否生效"""
        try:
            # 检查代码中是否有 overlay=True
            designer_py = self.base_dir / "app/routes/designer.py"
            content = designer_py.read_text()
            
            # 检查状态章
            if "stamp_path" in content and "overlay=True" in content:
                stamp_ok = True
            else:
                stamp_ok = False
            
            # 检查签名
            sig_count = content.count("overlay=True")
            
            if stamp_ok and sig_count >= 3:
                return True, f"✅ overlay=True 已添加（共 {sig_count} 处）"
            else:
                return False, f"❌ overlay=True 未正确添加"
        except Exception as e:
            return False, f"检查失败: {e}"
    
    def test_text_wrap_code(self) -> Tuple[bool, str]:
        """测试文本换行代码"""
        try:
            js_file = self.base_dir / "static/js/designer_edit.js"
            content = js_file.read_text()
            
            # 检查部门控件换行代码
            if 'r === "dept"' in content and 'whiteSpace' in content and 'normal' in content:
                return True, "✅ 部门控件换行代码已添加"
            else:
                return False, "❌ 部门控件换行代码未找到"
        except Exception as e:
            return False, f"检查失败: {e}"
    
    def test_process_configs(self) -> Tuple[bool, str]:
        """测试流程配置"""
        try:
            config_file = self.base_dir / "data/process_configs.json"
            if not config_file.exists():
                return False, "配置文件不存在"
            
            with open(config_file, 'r', encoding='utf-8') as f:
                configs = json.load(f)
            
            if not configs:
                return False, "配置为空"
            
            # 检查是否有 base_pdf
            has_base_pdf = all(c.get('base_pdf') for c in configs.values())
            
            if has_base_pdf:
                return True, f"✅ 找到 {len(configs)} 个流程配置，都有 base_pdf"
            else:
                return False, f"⚠️  有 {len(configs)} 个配置，但部分缺少 base_pdf"
        except Exception as e:
            return False, f"检查失败: {e}"
    
    def test_server_running(self) -> Tuple[bool, str]:
        """测试服务器是否运行"""
        import subprocess
        
        try:
            result = subprocess.run(
                ["ps", "aux"],
                capture_output=True,
                text=True
            )
            
            if "python" in result.stdout and "run.py" in result.stdout:
                # 提取 PID
                lines = [l for l in result.stdout.split('\n') if 'run.py' in l and 'grep' not in l]
                if lines:
                    pid = lines[0].split()[1]
                    return True, f"✅ 服务器正在运行 (PID: {pid})"
            
            return False, "❌ 服务器未运行"
        except Exception as e:
            return False, f"检查失败: {e}"
    
    def run_all_tests(self):
        """运行所有测试"""
        print("=" * 70)
        print("钉钉 H5 应用自动化测试")
        print("=" * 70)
        print()
        
        tests = [
            ("服务器状态", self.test_server_running),
            ("流程配置", self.test_process_configs),
            ("overlay 参数", self.test_overlay_parameter),
            ("文本换行代码", self.test_text_wrap_code),
            ("PNG 透明度", self.test_png_transparency),
        ]
        
        passed = 0
        failed = 0
        
        for name, test_func in tests:
            print(f"测试: {name}")
            print("-" * 70)
            
            try:
                success, message = test_func()
                
                if success:
                    print(f"✅ 通过")
                    passed += 1
                else:
                    print(f"❌ 失败")
                    failed += 1
                
                print(f"   {message}")
            except Exception as e:
                print(f"❌ 异常: {e}")
                failed += 1
            
            print()
        
        print("=" * 70)
        print(f"测试结果: {passed} 通过, {failed} 失败")
        print("=" * 70)
        print()
        
        if failed == 0:
            print("🎉 所有测试通过！")
        else:
            print("⚠️  有测试失败，请检查上面的详细信息")
        
        return failed == 0

if __name__ == "__main__":
    framework = TestFramework()
    success = framework.run_all_tests()
    sys.exit(0 if success else 1)
