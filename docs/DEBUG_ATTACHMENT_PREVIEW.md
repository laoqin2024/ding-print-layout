================================================================================
🔍 调试指南 - 附件底图预览问题
================================================================================

问题: 预览 PDF 时没有显示附件底图
状态: 已添加调试日志

================================================================================
✅ 已完成的修改
================================================================================

1. static/js/designer_edit.js
   - ✅ previewPdf 函数已添加 attachment_background_config 参数

2. app/routes/designer.py
   - ✅ 已添加详细的调试日志

================================================================================
🔍 调试步骤
================================================================================

步骤 1: 重启服务器
---------------------------------------------------------------
```bash
cd "/Volumes/MyDisk/App programs/dingtalk-h5-app"
pkill -f "python.*run.py"
python run.py
```

步骤 2: 在设计器中测试
---------------------------------------------------------------
1. 打开设计器页面
2. 确保勾选"启用附件底图"
3. 选择附件字段
4. 点击"预览 PDF"按钮

步骤 3: 查看终端日志
---------------------------------------------------------------
应该看到类似这样的输出：

```
[DEBUG] cover_source_mode == 'attachment'
[DEBUG] attachment_bg_enabled: True
[DEBUG] attachment_bg_field_id: DDAttachment_1PKSP5YV9WRGG
[DEBUG] attachment_bg_apply_mode: preview_and_print
[DEBUG] should_apply: True
[DEBUG] 尝试下载附件: field_id=DDAttachment_1PKSP5YV9WRGG, index=0
[DEBUG] ✅ 附件下载成功，大小: 123456 bytes
[DEBUG] 使用附件 PDF 作为底图
```

步骤 4: 查看浏览器 Network
---------------------------------------------------------------
1. 打开浏览器开发者工具（F12）
2. 切换到 Network 标签
3. 点击"预览 PDF"
4. 查看 `/designer/api/preview` 请求
5. 确认 Request Payload 包含 attachment_background_config

================================================================================
🐛 可能的问题和解决方案
================================================================================

问题 1: 看到 "❌ 附件下载失败或为空"
---------------------------------------------------------------
原因: 
- instance_id 不正确
- field_id 不正确
- 附件不存在或不是 PDF

解决方案:
1. 检查 instance_id 是否正确
2. 检查 field_id 是否匹配实际的附件字段
3. 在钉钉审批中确认附件存在且是 PDF 格式

问题 2: 没有看到任何 [DEBUG] 日志
---------------------------------------------------------------
原因:
- cover_source_mode 不是 "attachment"
- 前端没有传递 attachment_background_config

解决方案:
1. 检查浏览器 Network 中的 Request Payload
2. 确认 cover_source_mode: "attachment"
3. 确认 attachment_background_config 存在

问题 3: 看到 "尝试兜底逻辑：自动查找第一个 PDF 附件"
---------------------------------------------------------------
原因:
- attachment_bg_enabled 为 False
- attachment_bg_field_id 为空
- should_apply 为 False

解决方案:
1. 检查前端是否正确传递了配置
2. 检查 apply_mode 是否正确（应该是 "preview_and_print"）

问题 4: 附件下载成功但预览还是没有显示
---------------------------------------------------------------
原因:
- PDF 渲染问题
- 页面索引问题

解决方案:
1. 检查日志中的 "使用附件 PDF 作为底图"
2. 检查 page_index 是否在有效范围内
3. 尝试使用 page_index: 0

================================================================================
📊 完整的数据流
================================================================================

1. 前端发送请求
   ```javascript
   {
     cover_source_mode: "attachment",
     attachment_background_config: {
       enabled: true,
       field_id: "DDAttachment_1PKSP5YV9WRGG",
       attachment_index: 0,
       page_index: 0,
       apply_mode: "preview_and_print"
     }
   }
   ```

2. 后端接收参数
   ```python
   attachment_bg_config = payload.get("attachment_background_config") or {}
   attachment_bg_enabled = True
   attachment_bg_field_id = "DDAttachment_1PKSP5YV9WRGG"
   ```

3. 后端判断逻辑
   ```python
   if cover_source_mode == "attachment":  # ✅
       if attachment_bg_enabled and attachment_bg_field_id:  # ✅
           should_apply = (
               attachment_bg_apply_mode in ("preview_and_print", ...)  # ✅
           )
           if should_apply:  # ✅
               source_pdf_bytes = ding.download_specific_attachment_pdf(...)
   ```

4. 后端下载附件
   ```python
   # dingtalk_service.py
   def download_specific_attachment_pdf(self, *, instance, field_id, attachment_index):
       # 查找字段
       # 解析附件 JSON
       # 获取 fileId
       # 调用 get_process_attachment_url
       # 下载 PDF
       return pdf_bytes
   ```

5. 后端使用附件
   ```python
   if source_pdf_bytes:
       src_doc = fitz.open(stream=source_pdf_bytes, filetype="pdf")
       # 渲染到预览 PDF
   ```

================================================================================
✅ 下一步
================================================================================

1. 重启服务器
2. 测试预览功能
3. 查看终端日志
4. 根据日志输出判断问题所在

如果看到 "✅ 附件下载成功" 但预览还是没有显示附件底图，
请截图终端日志并告诉我，我会进一步排查。

================================================================================
