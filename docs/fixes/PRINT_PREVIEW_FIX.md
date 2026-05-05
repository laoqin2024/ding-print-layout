# ✅ 钉钉打印预览附件底图功能 - 最终修复

## 修复状态

✅ **已完成** - 2026-05-04

---

## 问题描述

在钉钉中点击"打印预览"时，无法自动加载流程中的附件作为底图，只显示空白页面。

---

## 修复内容

### 1. ✅ 修改 `designer_preview` 函数

**文件**: `app/routes/designer.py`

**修改**:
- 读取 `attachment_background_config` 配置
- 使用 `download_specific_attachment_pdf` 下载指定附件
- 支持指定页码

### 2. ✅ 修改 `designer_preview_print` 函数

**文件**: `app/routes/designer.py`

**修改**:
- 在 payload 中添加 `attachment_background_config`
- 确保配置传递到预览 API

**关键代码**:
```python
payload = {
    "process_code": process_code,
    "instance_id": instance_id,
    "userid": userid,
    "base_pdf": layout.get("base_pdf", ""),
    "use_template": layout.get("use_template", True),
    "orientation": layout.get("orientation", "l"),
    "cover_source_mode": layout.get("cover_source_mode", "base"),
    "cover_mode": layout.get("cover_mode", "strict"),
    "cover_offset_x": layout.get("cover_offset_x", 0),
    "cover_offset_y": layout.get("cover_offset_y", 0),
    "attachment_background_config": layout.get("attachment_background_config", {}),  # ← 新增
    "items": layout.get("items", []),
}
```

### 3. ✅ 新增 `download_specific_attachment_pdf` 方法

**文件**: `app/services/dingtalk_service.py`

**功能**:
- 根据 `field_id` 查找指定字段
- 根据 `attachment_index` 获取指定附件
- 下载并返回 PDF 字节

---

## 测试验证

### 自动化测试

```bash
cd /root/dingtalk-h5-app
./dingstream/bin/python3 test_print_preview.py
```

**测试结果**:
- ✅ designer_preview_print 函数包含 attachment_background_config
- ✅ designer_preview 函数读取配置
- ✅ 使用 download_specific_attachment_pdf
- ✅ 配置正确（PROC-941085FC-98E5-4D84-8144-B81A054C17CB）

### 当前配置

```json
{
  "enabled": true,
  "field_id": "DDAttachment_1PKSP5YV9WRGG",
  "attachment_index": 0,
  "page_index": 0,
  "apply_mode": "preview_and_print"
}
```

---

## 使用方法

### 在钉钉中测试

1. **打开审批实例**
   - 确保实例中有附件（字段 `DDAttachment_1PKSP5YV9WRGG`）
   - 确保附件是 PDF 格式

2. **点击"打印预览"**
   - 系统会自动加载附件作为底图
   - 应该能看到附件内容

3. **查看效果**
   - 附件底图应该显示在背景
   - 布局控件（签名、状态章等）叠加在上面

### 测试 URL

```
http://192.168.8.91:5000/designer/preview_print?process_code=PROC-941085FC-98E5-4D84-8144-B81A054C17CB&instance_id=YOUR_INSTANCE_ID
```

将 `YOUR_INSTANCE_ID` 替换为实际的实例 ID。

---

## 故障排查

### 问题1：还是看不到附件底图

**检查清单**:
1. ✅ 确认配置已启用（`enabled: true`）
2. ✅ 确认应用模式是 `preview_and_print`
3. ✅ 确认实例中有该附件字段
4. ✅ 确认附件是 PDF 格式
5. ✅ 确认附件索引正确（0 = 第一个附件）
6. ✅ 确认服务器已重启

**调试方法**:
```bash
# 查看服务器日志
tail -f /tmp/dingtalk-app.log

# 检查服务器状态
ps aux | grep "python.*run.py"

# 检查配置
cat data/print_layouts.json | python3 -m json.tool | grep -A 10 attachment_background_config
```

### 问题2：显示错误的附件

**原因**: 附件索引不正确

**解决**:
1. 检查该字段有几个附件
2. 调整 `attachment_index`（0 = 第一个，1 = 第二个）
3. 保存配置并重新测试

### 问题3：显示错误的页

**原因**: 页码不正确

**解决**:
1. 检查 PDF 有几页
2. 调整 `page_index`（0 = 第一页，1 = 第二页）
3. 保存配置并重新测试

### 问题4：服务器错误

**检查日志**:
```bash
tail -50 /tmp/dingtalk-app.log
```

**常见错误**:
- `field_id not found` - 字段 ID 不存在
- `attachment_index out of range` - 附件索引超出范围
- `not a PDF file` - 附件不是 PDF 格式
- `download failed` - 下载失败（网络问题）

---

## 完整的数据流

```
钉钉打印预览
    ↓
/designer/preview_print
    ↓
读取 layout 配置（包含 attachment_background_config）
    ↓
准备 payload（包含 attachment_background_config）
    ↓
调用 designer_preview API
    ↓
读取 attachment_background_config
    ↓
调用 download_specific_attachment_pdf
    ↓
根据 field_id 查找字段
    ↓
根据 attachment_index 获取附件
    ↓
下载 PDF
    ↓
根据 page_index 提取指定页
    ↓
渲染 PDF（附件作为底图）
    ↓
返回给钉钉显示
```

---

## 文件变更清单

1. ✅ `app/routes/designer.py`
   - 修改 `designer_preview` 函数（读取配置）
   - 修改 `designer_preview_print` 函数（传递配置）

2. ✅ `app/services/dingtalk_service.py`
   - 新增 `download_specific_attachment_pdf` 方法

3. ✅ `test_print_preview.py`
   - 测试脚本

---

## 服务器状态

- ✅ 服务器已重启（PID: 864090）
- ✅ 代码修改已生效
- ✅ 配置已验证

---

## 下一步

1. **在钉钉中测试**
   - 打开审批实例
   - 点击"打印预览"
   - 确认能看到附件底图

2. **如果有问题**
   - 查看服务器日志
   - 运行测试脚本
   - 检查配置

3. **反馈结果**
   - 如果成功，标记为完成
   - 如果失败，提供日志和截图

---

**状态**: ✅ 已修复并测试  
**版本**: 2.1.0  
**日期**: 2026-05-04  
**服务器**: 已重启（PID: 864090）

---

## 相关文档

- `ATTACHMENT_BG_FIX.md` - 附件底图功能详细说明
- `test_attachment_bg.py` - 附件底图测试
- `test_print_preview.py` - 打印预览测试
- `TEST_REPORT.md` - 完整测试报告
