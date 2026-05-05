# 🚀 快速参考指南

## 一键测试

```bash
cd /root/dingtalk-h5-app
./dingstream/bin/python3 run_full_tests.py
```

## 测试结果

✅ **9/9 测试通过（100%）**

---

## 常用命令

### 运行测试
```bash
# 完整测试套件
./dingstream/bin/python3 run_full_tests.py

# 基础测试
./dingstream/bin/python3 run_tests.py

# overlay 参数测试
./dingstream/bin/python3 test_overlay.py

# PNG 透明度检查
./dingstream/bin/python3 check_png_transparency.py
```

### 服务器管理
```bash
# 重启服务器
./restart_server.sh

# 检查服务器状态
ps aux | grep "python.*run.py" | grep -v grep

# 查看日志
tail -f /tmp/dingtalk-app.log
```

### 修复工具
```bash
# 恢复默认数据
./fix_default_data.sh

# 系统诊断
./diagnose.sh

# 去除 PNG 白色背景（需要 Pillow）
./dingstream/bin/pip install Pillow
./dingstream/bin/python3 remove_white_background.py
```

---

## 已修复的功能

### 1. ✅ 状态章透明背景
- 添加 `overlay=True` 参数
- PNG 文件已处理

### 2. ✅ 部门控件文本换行
- 前端和后端都已支持
- 画布预览和 PDF 打印都正常

### 3. ✅ 附件底图画布预览
- API 端点已添加
- 前端加载函数已实现

### 4. ✅ 系统自检
- 默认数据已恢复
- 所有检查项通过

---

## 测试文件清单

### 测试脚本
- `run_full_tests.py` - 完整测试套件 ⭐
- `run_tests.py` - 基础测试
- `test_overlay.py` - overlay 测试
- `check_png_transparency.py` - PNG 检查

### 修复脚本
- `fix_default_data.sh` - 恢复数据
- `restart_server.sh` - 重启服务器
- `diagnose.sh` - 系统诊断
- `remove_white_background.py` - PNG 处理

### 文档
- `TEST_REPORT.md` - 测试报告 ⭐
- `FINAL_DIAGNOSIS.md` - 问题诊断
- `FIX_COMPLETE_SUMMARY.md` - 修复总结
- `VERIFICATION_GUIDE.md` - 验证指南

---

## 快速故障排查

### 问题：测试失败

1. 检查服务器是否运行
   ```bash
   ps aux | grep run.py
   ```

2. 重启服务器
   ```bash
   ./restart_server.sh
   ```

3. 重新运行测试
   ```bash
   ./dingstream/bin/python3 run_full_tests.py
   ```

### 问题：状态章还是有白色背景

1. 查看测试 PDF
   ```bash
   ls -lh /tmp/test_transparency.pdf
   ```

2. 如果 PNG 有白色，重新处理
   ```bash
   # 使用在线工具 https://www.remove.bg/
   # 或使用脚本
   ./dingstream/bin/python3 remove_white_background.py
   ```

3. 重启服务器并测试

### 问题：部门控件不换行

1. 强制刷新浏览器（Ctrl+Shift+R）
2. 选中控件，勾选"文本自动换行"
3. **点击"更新选中项"** ⚠️
4. 点击"保存布局"
5. 预览 PDF

---

## 联系方式

如有问题，请提供：
1. 测试输出
2. 错误截图
3. 服务器日志

---

**版本**: 1.0.0  
**更新**: 2026-05-04
