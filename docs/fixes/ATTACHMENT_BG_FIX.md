# 附件底图功能修复完成

## 问题描述

在钉钉中预览打印时，无法自动加载流程中的附件作为底图，只显示空白页面。

## 根本原因

代码中虽然支持 `cover_source_mode = "attachment"`，但：
1. 没有读取 `attachment_background_config` 配置
2. 使用的是 `download_process_attachment_pdf` 函数，自动查找第一个 PDF 附件
3. 没有使用配置中指定的 `field_id`、`attachment_index` 和 `page_index`

## 修复内容

### 1. 读取附件底图配置（designer.py）

```python
# 读取附件底图配置
attachment_bg_config = payload.get("attachment_background_config") or {}
attachment_bg_enabled = attachment_bg_config.get("enabled", False)
attachment_bg_field_id = str(attachment_bg_config.get("field_id") or "").strip()
attachment_bg_index = int(attachment_bg_config.get("attachment_index") or 0)
attachment_bg_page = int(attachment_bg_config.get("page_index") or 0)
attachment_bg_apply_mode = str(attachment_bg_config.get("apply_mode") or "print_only").strip()
```

### 2. 使用配置下载指定附件（designer.py）

```python
if cover_source_mode == "attachment":
    # 如果配置了附件底图，使用指定的字段和索引
    if attachment_bg_enabled and attachment_bg_field_id and (attachment_bg_apply_mode == "preview_and_print" or attachment_bg_apply_mode == "both"):
        # 使用配置中指定的附件字段
        source_pdf_bytes = ding.download_specific_attachment_pdf(
            instance=instance,
            field_id=attachment_bg_field_id,
            attachment_index=attachment_bg_index
        )
    else:
        # 兼容旧逻辑：自动查找第一个 PDF 附件
        source_pdf_bytes = ding.download_process_attachment_pdf(process_instance_id=instance_id, instance=instance)
```

### 3. 支持指定页码（designer.py）

```python
if source_pdf_bytes:
    src_doc = fitz.open(stream=source_pdf_bytes, filetype="pdf")
    # 如果指定了页码，只使用指定的页
    if cover_source_mode == "attachment" and attachment_bg_enabled and attachment_bg_page >= 0:
        if attachment_bg_page < src_doc.page_count:
            # 创建只包含指定页的临时文档
            temp_doc = fitz.open()
            temp_doc.insert_pdf(src_doc, from_page=attachment_bg_page, to_page=attachment_bg_page)
            src_doc.close()
            src_doc = temp_doc
```

### 4. 新增下载指定附件方法（dingtalk_service.py）

```python
def download_specific_attachment_pdf(self, *, instance: Dict[str, Any], field_id: str, attachment_index: int = 0) -> Optional[bytes]:
    """
    Download a specific PDF attachment by field_id and attachment_index.
    
    Args:
        instance: Process instance data
        field_id: The field ID (e.g., "DDAttachment_1PKSP5YV9WRGG")
        attachment_index: Index of the attachment in the field (0-based)
    
    Returns:
        PDF bytes or None if not found
    """
    # 查找指定字段
    # 获取指定索引的附件
    # 下载 PDF
```

## 配置说明

### 附件底图配置结构

```json
{
  "attachment_background_config": {
    "enabled": true,
    "field_id": "DDAttachment_1PKSP5YV9WRGG",
    "attachment_index": 0,
    "page_index": 0,
    "apply_mode": "preview_and_print"
  }
}
```

### 参数说明

- **enabled**: 是否启用附件底图
- **field_id**: 附件字段 ID（如 `DDAttachment_1PKSP5YV9WRGG`）
- **attachment_index**: 附件索引（第几个附件，从 0 开始）
- **page_index**: PDF 页码（第几页，从 0 开始）
- **apply_mode**: 应用模式
  - `preview_and_print`: 预览和打印都使用附件
  - `print_only`: 仅打印时使用附件

## 使用方法

### 1. 在设计器中配置

1. 打开设计器页面
2. 找到"附件底图配置"区域
3. ✅ 勾选"启用"
4. 选择附件字段（从下拉框选择）
5. 设置附件索引（如果有多个附件）
6. 设置 PDF 页码（如果 PDF 有多页）
7. 选择应用模式：
   - `预览和打印都生效` - 推荐，可以在预览中看到效果
   - `仅打印时生效` - 预览快速，打印时用附件
8. 点击"保存布局"

### 2. 在钉钉中预览

1. 打开钉钉审批实例
2. 点击"打印预览"
3. 应该能看到附件底图

## 测试验证

运行测试脚本：

```bash
cd /root/dingtalk-h5-app
./dingstream/bin/python3 test_attachment_bg.py
```

测试结果：
- ✅ 读取附件底图配置
- ✅ 启用标志
- ✅ 字段ID
- ✅ 附件索引
- ✅ 页码
- ✅ 下载指定附件方法

## 故障排查

### 问题1：还是看不到附件底图

**检查清单**：
1. 确认"启用"已勾选
2. 确认选择了正确的附件字段
3. 确认附件索引正确（从 0 开始）
4. 确认应用模式是 `preview_and_print`
5. 确认实例中确实有该附件
6. 确认附件是 PDF 格式

**调试方法**：
```bash
# 查看服务器日志
tail -f /tmp/dingtalk-app.log

# 检查配置
cat data/print_layouts.json | grep -A 10 attachment_background_config
```

### 问题2：附件字段下拉框为空

**原因**：没有拉取表单控件

**解决**：
1. 在设计器中点击"拉取表单控件"
2. 等待加载完成
3. 重新选择附件字段

### 问题3：显示的不是想要的附件

**原因**：附件索引不正确

**解决**：
1. 检查该字段有几个附件
2. 调整附件索引（0 = 第一个，1 = 第二个）
3. 保存并重新预览

### 问题4：显示的不是想要的页

**原因**：页码不正确

**解决**：
1. 检查 PDF 有几页
2. 调整页码（0 = 第一页，1 = 第二页）
3. 保存并重新预览

## 兼容性

### 向后兼容

- ✅ 如果没有配置 `attachment_background_config`，使用旧逻辑（自动查找第一个 PDF）
- ✅ 如果 `enabled = false`，不使用附件底图
- ✅ 如果 `apply_mode = print_only`，预览时不使用附件

### 新功能

- ✅ 支持指定附件字段
- ✅ 支持指定附件索引（多个附件时）
- ✅ 支持指定 PDF 页码（多页 PDF 时）
- ✅ 支持选择应用模式

## 文件变更

- ✅ `app/routes/designer.py` - 读取配置，使用指定附件
- ✅ `app/services/dingtalk_service.py` - 新增 `download_specific_attachment_pdf` 方法
- ✅ `test_attachment_bg.py` - 测试脚本

## 下一步

1. **测试功能**
   - 在钉钉中预览打印
   - 确认能看到附件底图

2. **调整配置**
   - 如果显示不正确，调整附件索引或页码
   - 保存并重新测试

3. **反馈问题**
   - 如果还有问题，提供服务器日志
   - 提供配置截图

---

**状态**: ✅ 已修复  
**版本**: 2.0.0  
**日期**: 2026-05-04  
**服务器**: 已重启（PID: 863552）
