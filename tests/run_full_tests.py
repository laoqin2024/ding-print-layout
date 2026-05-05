#!/usr/bin/env python3
"""
钉钉 H5 应用完整自动化测试套件
"""

import sys
import os
import json
import subprocess
from pathlib import Path
from typing import Tuple

# 添加项目路径（使用脚本所在目录）
SCRIPT_DIR = Path(__file__).parent.absolute()
sys.path.insert(0, str(SCRIPT_DIR))

class TestSuite:
    def __init__(self):
        self.base_dir = SCRIPT_DIR
        self.results = []
        self.passed = 0
        self.failed = 0
        
    def log_result(self, test_name: str, success: bool, message: str):
        """记录测试结果"""
        self.results.append({'name': test_name, 'success': success, 'message': message})
        if success:
            self.passed += 1
        else:
            self.failed += 1
    
    def test_server_running(self) -> Tuple[bool, str]:
        """测试服务器是否运行"""
        try:
            result = subprocess.run(["ps", "aux"], capture_output=True, text=True, timeout=5)
            lines = [l for l in result.stdout.split('\n') if 'python' in l and 'run.py' in l and 'grep' not in l]
            if lines:
                pid = lines[0].split()[1]
                return True, f"服务器运行中 (PID: {pid})"
            return False, "服务器未运行"
        except Exception as e:
            return False, f"检查失败: {e}"
    
    def test_process_configs(self) -> Tuple[bool, str]:
        """测试流程配置"""
        config_file = self.base_dir / "data/process_configs.json"
        if not config_file.exists():
            return False, "配置文件不存在"
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                configs = json.load(f)
            if not configs:
                return False, "配置为空"
            issues = []
            for code, config in configs.items():
                if not config.get('name'):
                    issues.append(f"{code}: 缺少 name")
                if not config.get('base_pdf'):
                    issues.append(f"{code}: 缺少 base_pdf")
            if issues:
                return False, f"配置问题: {'; '.join(issues)}"
            return True, f"✅ {len(configs)} 个流程配置正常"
        except Exception as e:
            return False, f"检查失败: {e}"
    
    def test_pdf_templates(self) -> Tuple[bool, str]:
        """测试 PDF 模板"""
        template_dir = self.base_dir / "templates/pdf_templates"
        if not template_dir.exists():
            return False, "模板目录不存在"
        pdfs = list(template_dir.glob("*.pdf"))
        if not pdfs:
            return False, "没有找到 PDF 模板"
        total_size = sum(p.stat().st_size for p in pdfs)
        avg_size = total_size / len(pdfs)
        return True, f"✅ {len(pdfs)} 个 PDF 模板，平均大小: {avg_size/1024:.1f} KB"
    
    def test_overlay_parameter(self) -> Tuple[bool, str]:
        """测试 overlay 参数"""
        designer_py = self.base_dir / "app/routes/designer.py"
        if not designer_py.exists():
            return False, "designer.py 不存在"
        content = designer_py.read_text()
        overlay_count = content.count("overlay=True")
        has_stamp = "stamp_path" in content and "overlay=True" in content
        has_signature = "sig_fill_mode" in content and "overlay=True" in content
        if overlay_count >= 3 and has_stamp and has_signature:
            return True, f"✅ overlay=True 已添加（{overlay_count} 处）"
        return False, f"overlay=True 不完整（仅 {overlay_count} 处）"
    
    def test_text_wrap_frontend(self) -> Tuple[bool, str]:
        """测试前端文本换行代码"""
        js_file = self.base_dir / "static/js/designer_edit.js"
        if not js_file.exists():
            return False, "designer_edit.js 不存在"
        content = js_file.read_text()
        checks = [('propTextWrap', '元素引用'), ('text_wrap', '属性名'), ('whiteSpace', '样式设置'), ('r === "dept"', '部门控件')]
        missing = [desc for pattern, desc in checks if pattern not in content]
        if missing:
            return False, f"缺少: {', '.join(missing)}"
        return True, "✅ 文本换行代码完整"
    
    def test_text_wrap_backend(self) -> Tuple[bool, str]:
        """测试后端文本换行代码"""
        designer_py = self.base_dir / "app/routes/designer.py"
        if not designer_py.exists():
            return False, "designer.py 不存在"
        content = designer_py.read_text()
        if 'def _draw_text_with_spacing' not in content:
            return False, "_draw_text_with_spacing 函数不存在"
        if 'text_wrap' not in content:
            return False, "text_wrap 参数未添加"
        wrap_calls = content.count('text_wrap=')
        if wrap_calls >= 3:
            return True, f"✅ text_wrap 参数已添加（{wrap_calls} 处调用）"
        return False, f"text_wrap 调用不完整（仅 {wrap_calls} 处）"
    
    def test_stamp_files(self) -> Tuple[bool, str]:
        """测试状态章文件"""
        stamps_dir = self.base_dir / "static/stamps"
        if not stamps_dir.exists():
            return False, "stamps 目录不存在"
        pngs = list(stamps_dir.rglob("*.png"))
        if not pngs:
            return False, "没有找到状态章 PNG 文件"
        issues = []
        for png in pngs:
            size = png.stat().st_size
            if size < 100:
                issues.append(f"{png.name}: 文件太小")
            elif size > 1024 * 1024:
                issues.append(f"{png.name}: 文件太大")
        if issues:
            return False, f"文件问题: {'; '.join(issues)}"
        return True, f"✅ {len(pngs)} 个状态章文件正常"
    
    def test_attachment_bg_api(self) -> Tuple[bool, str]:
        """测试附件底图 API"""
        designer_py = self.base_dir / "app/routes/designer.py"
        if not designer_py.exists():
            return False, "designer.py 不存在"
        content = designer_py.read_text()
        if 'render_attachment_bg' not in content:
            return False, "render_attachment_bg API 不存在"
        checks = ['process_code', 'instance_id', 'field_id', 'attachment_index', 'page_index']
        missing = [c for c in checks if c not in content]
        if missing:
            return False, f"缺少参数: {', '.join(missing)}"
        return True, "✅ 附件底图 API 完整"
    
    def test_loadAttachmentBackground(self) -> Tuple[bool, str]:
        """测试前端附件底图加载函数"""
        js_file = self.base_dir / "static/js/designer_edit.js"
        if not js_file.exists():
            return False, "designer_edit.js 不存在"
        content = js_file.read_text()
        if 'loadAttachmentBackground' not in content:
            return False, "loadAttachmentBackground 函数不存在"
        if 'render_attachment_bg' not in content:
            return False, "未调用 render_attachment_bg API"
        return True, "✅ 附件底图加载函数完整"
    
    def run_all_tests(self):
        """运行所有测试"""
        print("=" * 80)
        print("钉钉 H5 应用完整自动化测试套件")
        print("=" * 80)
        print()
        
        test_groups = [
            ("基础设施", [("服务器运行状态", self.test_server_running)]),
            ("配置文件", [("流程配置", self.test_process_configs)]),
            ("PDF 模板", [("PDF 模板文件", self.test_pdf_templates)]),
            ("代码质量", [
                ("overlay 参数", self.test_overlay_parameter),
                ("前端文本换行", self.test_text_wrap_frontend),
                ("后端文本换行", self.test_text_wrap_backend),
            ]),
            ("资源文件", [("状态章 PNG 文件", self.test_stamp_files)]),
            ("功能完整性", [
                ("附件底图 API", self.test_attachment_bg_api),
                ("附件底图前端", self.test_loadAttachmentBackground),
            ]),
        ]
        
        for group_name, tests in test_groups:
            print(f"\n{'='*80}")
            print(f"测试组: {group_name}")
            print(f"{'='*80}\n")
            
            for test_name, test_func in tests:
                print(f"测试: {test_name}")
                print("-" * 80)
                try:
                    success, message = test_func()
                    if success:
                        print(f"✅ 通过")
                    else:
                        print(f"❌ 失败")
                    print(f"   {message}")
                    self.log_result(test_name, success, message)
                except Exception as e:
                    print(f"❌ 异常: {e}")
                    self.log_result(test_name, False, f"异常: {e}")
                print()
        
        print("=" * 80)
        print("测试总结")
        print("=" * 80)
        print()
        print(f"总计: {self.passed + self.failed} 个测试")
        print(f"✅ 通过: {self.passed}")
        print(f"❌ 失败: {self.failed}")
        print(f"成功率: {self.passed / (self.passed + self.failed) * 100:.1f}%")
        print()
        
        if self.failed == 0:
            print("🎉 所有测试通过！")
            return True
        else:
            print("⚠️  有测试失败")
            print("\n失败的测试:")
            for result in self.results:
                if not result['success']:
                    print(f"  - {result['name']}: {result['message']}")
            return False

if __name__ == "__main__":
    suite = TestSuite()
    success = suite.run_all_tests()
    sys.exit(0 if success else 1)
