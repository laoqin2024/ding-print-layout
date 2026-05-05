================================================================================
✅ 附件下载问题调试 - 已添加详细日志
================================================================================

完成时间: 2026-05-04
问题: "加载附件底图失败: No download URL"

================================================================================
🔧 已完成的修复
================================================================================

### 1. 空白模板位置修复 ✅

**错误位置**: data/templates/
**正确位置**: templates/pdf_templates/

**已创建文件**:
- templates/pdf_templates/blank_landscape.pdf (518 字节)
- templates/pdf_templates/blank_portrait.pdf (518 字节)

**后端逻辑**:
```python
# 根据方向自动选择空白模板
if using_attachment_bg and not base_pdf:
    if orientation == "p":
        base_pdf = "blank_portrait.pdf"  # 纵向
    else:
        base_pdf = "blank_landscape.pdf"  # 横向
```

### 2. 附件下载调试日志 ✅

**修改文件**: app/services/dingtalk_service.py
**函数**: download_specific_attachment_pdf

**新增日志**:
1. ✅ 函数开始 - 显示 field_id 和 attachment_index
2. ✅ 找到字段 - 显示字段 ID
3. ✅ 字段原始值 - 显示前 200 个字符
4. ✅ 解析结果 - 显示附件数量
5. ✅ 附件项详情 - 显示完整的附件对象
6. ✅ fileId 信息 - 显示 fileType, fileName, fileId
7. ✅ 下载过程 - 显示 URL 和响应状态
8. ✅ 异常信息 - 显示完整的错误堆栈

================================================================================
🧪 测试步骤
================================================================================

### 1. 重启服务器
```bash
cd "/Volumes/MyDisk/App programs/dingtalk-h5-app"
pkill -f "python.*run.py"
python run.py
```

### 2. 刷新浏览器
```
按 Ctrl+Shift+R 强制刷新
```

### 3. 测试附件底图功能
1. 启用附件底图
2. 选择附件字段 (DDAttachment_1PKSP5YV9WRGG)
3. 点击"预览 PDF"

### 4. 查看终端日志

应该看到类似这样的日志：

```
[DEBUG] download_specific_attachment_pdf 开始
[DEBUG] field_id: DDAttachment_1PKSP5YV9WRGG
[DEBUG] attachment_index: 0
[DEBUG] 找到字段: DDAttachment_1PKSP5YV9WRGG
[DEBUG] 字段原始值: [{"fileId":"xxx","fileName":"test.pdf","fileType":"pdf",...
[DEBUG] 解析成功，附件数量: 1
[DEBUG] 附件项: {'fileId': 'xxx', 'fileName': 'test.pdf', ...}
[DEBUG] fileType: pdf
[DEBUG] fileName: test.pdf
[DEBUG] fileId: xxx
[DEBUG] process_instance_id: kskSi1YsSLCUu-2pf5GLhQ08981777468307
[DEBUG] 调用 get_process_attachment_url
[DEBUG] 下载 URL: https://...
[DEBUG] 下载响应状态: 200, 大小: 12345 bytes
[DEBUG] ✅ PDF 下载成功
```

### 5. 如果出错，日志会显示具体原因

可能的错误场景：

**场景 1: 字段未找到**
```
[DEBUG] ❌ 未找到匹配的附件
```
→ 检查 field_id 是否正确

**场景 2: 字段值格式不对**
```
[DEBUG] 字段值格式不对，不是 JSON 数组
```
→ 检查附件字段的数据格式

**场景 3: fileId 为空**
```
[DEBUG] fileId 为空
```
→ 附件对象中没有 fileId 字段

**场景 4: 下载失败**
```
[DEBUG] ❌ 下载失败: workflow attachment download-url missing url
```
→ 钉钉 API 返回的响应中没有 downloadUri

**场景 5: 不是 PDF**
```
[DEBUG] ❌ 不是有效的 PDF
```
→ 下载的文件不是 PDF 格式

================================================================================
📊 可能的问题原因
================================================================================

### 原因 1: 附件字段数据格式变化

**之前的格式** (使用 fileId):
```json
[
  {
    "fileId": "xxx",
    "fileName": "test.pdf",
    "fileType": "pdf"
  }
]
```

**可能的新格式** (使用 URL):
```json
[
  {
    "url": "https://...",
    "fileName": "test.pdf",
    "fileType": "pdf"
  }
]
```

**解决方案**: 如果是这种情况，需要修改代码同时支持两种格式

### 原因 2: 钉钉 API 变化

钉钉可能更新了附件下载 API：
- 旧 API: `/v1.0/workflow/processInstances/spaces/files/urls/download`
- 新 API: 可能有新的接口

**解决方案**: 查看钉钉最新文档，更新 API 调用

### 原因 3: 权限问题

可能缺少附件下载权限：
- 需要在钉钉开放平台配置权限
- 需要申请 `workflow.processInstance.file.download` 权限

**解决方案**: 检查钉钉应用权限配置

### 原因 4: process_instance_id 格式问题

可能 instance 对象的字段名变化了：
- 之前: `process_instance_id`
- 现在: `processInstanceId` 或其他

**解决方案**: 日志会显示 process_instance_id 的值，检查是否为空

================================================================================
🔍 下一步调试
================================================================================

### 步骤 1: 收集日志信息

重启服务器并测试，把终端中的所有 [DEBUG] 日志发给我，包括：
- field_id 的值
- 字段原始值
- 附件项的完整内容
- fileId 的值
- 错误信息

### 步骤 2: 检查附件字段格式

如果日志显示 fileId 为空，可能需要：
1. 检查附件对象的实际字段名
2. 可能是 `file_id` 而不是 `fileId`
3. 可能是 `spaceId` + `fileId` 的组合

### 步骤 3: 检查钉钉 API 响应

如果 get_process_attachment_url 失败，可能需要：
1. 检查 API 返回的完整响应
2. 查看是否有新的字段名
3. 可能需要更新 API 版本

### 步骤 4: 兼容旧格式

如果确认是格式变化，可以修改代码同时支持：
```python
# 尝试多种可能的字段名
file_id = (
    str(item.get("fileId") or "").strip() or
    str(item.get("file_id") or "").strip() or
    str(item.get("id") or "").strip()
)
```

================================================================================
📝 总结
================================================================================

已完成:
1. ✅ 修复空白模板位置 (templates/pdf_templates/)
2. ✅ 添加详细调试日志
3. ✅ 保持使用 fileId (不是 URL)

待确认:
1. ⏳ 附件字段的实际数据格式
2. ⏳ fileId 是否正确获取
3. ⏳ 钉钉 API 是否有变化

下一步:
1. 重启服务器
2. 测试并查看日志
3. 把日志发给我分析

================================================================================
