================================================================================
🐛 Bug 修复报告 - 附件底图预览问题
================================================================================

修复时间: 2026-05-04 16:20
问题: 预览 PDF 时没有加载附件底图

================================================================================
🔍 问题分析
================================================================================

问题 1: 附件底图配置默认被启用
---------------------------------------------------------------
原因: data/print_layouts.json 中保存的配置 enabled: true

当前配置:
```json
{
  "enabled": true,
  "field_id": "DDAttachment_1PKSP5YV9WRGG",
  "attachment_index": 0,
  "page_index": 0,
  "apply_mode": "preview_and_print"
}
```

解决方案: 
- 如果不想默认启用，需要在设计器中取消勾选并保存
- 或者手动修改 data/print_layouts.json 中的 enabled: false

问题 2: 预览 PDF 时没有加载附件底图 ⚠️ 关键问题
---------------------------------------------------------------
原因: previewPdf 函数没有传递 attachment_background_config

后端逻辑:
```python
# designer.py line 1356-1370
if cover_source_mode == "attachment":
    if attachment_bg_enabled and attachment_bg_field_id:
        should_apply = (
            attachment_bg_apply_mode in ("preview_and_print", "preview_only", "both") or
            not attachment_bg_apply_mode
        )
        if should_apply:
            source_pdf_bytes = ding.download_specific_attachment_pdf(...)
```

前端问题（修复前）:
```javascript
// static/js/designer_edit.js line 1424-1435
const payload = {
  process_code: processCode,
  base_pdf: basePdf,
  // ... 其他参数 ...
  items: state.items,
  // ❌ 缺少 attachment_background_config
};
```

结果: 后端收不到 attachment_background_config，导致：
- attachment_bg_enabled = False
- attachment_bg_field_id = ""
- 不会下载附件 PDF

================================================================================
✅ 修复方案
================================================================================

修复: static/js/designer_edit.js - previewPdf 函数
---------------------------------------------------------------

修复前:
```javascript
const payload = {
  process_code: processCode,
  base_pdf: basePdf,
  use_template: !!state.useTemplate,
  orientation: state.orient || "l",
  cover_source_mode: state.coverSourceMode || "base",
  cover_mode: state.coverMode || "strict",
  cover_offset_x: Number(state.coverOffsetX || 0),
  cover_offset_y: Number(state.coverOffsetY || 0),
  instance_id: (instanceIdEl?.value || "").trim(),
  items: state.items,
  // ❌ 缺少 attachment_background_config
};
```

修复后:
```javascript
const payload = {
  process_code: processCode,
  base_pdf: basePdf,
  use_template: !!state.useTemplate,
  orientation: state.orient || "l",
  cover_source_mode: state.coverSourceMode || "base",
  cover_mode: state.coverMode || "strict",
  cover_offset_x: Number(state.coverOffsetX || 0),
  cover_offset_y: Number(state.coverOffsetY || 0),
  instance_id: (instanceIdEl?.value || "").trim(),
  items: state.items,
  // ✅ 新增：传递附件底图配置
  attachment_background_config: {
    enabled: state.attachmentBg.enabled,
    field_id: state.attachmentBg.fieldId,
    attachment_index: state.attachmentBg.attachmentIndex,
    page_index: state.attachmentBg.pageIndex,
    apply_mode: state.attachmentBg.applyMode,
  },
};
```

================================================================================
🔄 完整的调用链（修复后）
================================================================================

1. 前端发送请求
   ```javascript
   fetch("/designer/api/preview", {
     method: "POST",
     body: JSON.stringify({
       cover_source_mode: "attachment",
       attachment_background_config: {
         enabled: true,
         field_id: "DDAttachment_1PKSP5YV9WRGG",
         attachment_index: 0,
         page_index: 0,
         apply_mode: "preview_and_print"
       }
     })
   })
   ```

2. 后端接收参数
   ```python
   attachment_bg_config = payload.get("attachment_background_config") or {}
   attachment_bg_enabled = attachment_bg_config.get("enabled", False)  # ✅ True
   attachment_bg_field_id = str(attachment_bg_config.get("field_id") or "").strip()  # ✅ "DDAttachment_1PKSP5YV9WRGG"
   ```

3. 后端判断逻辑
   ```python
   if cover_source_mode == "attachment":  # ✅ True
       if attachment_bg_enabled and attachment_bg_field_id:  # ✅ True
           should_apply = (
               attachment_bg_apply_mode in ("preview_and_print", "preview_only", "both")  # ✅ True
           )
           if should_apply:  # ✅ True
               source_pdf_bytes = ding.download_specific_attachment_pdf(...)  # ✅ 下载附件
   ```

4. 后端使用附件
   ```python
   if source_pdf_bytes:  # ✅ True
       src_doc = fitz.open(stream=source_pdf_bytes, filetype="pdf")  # ✅ 使用附件作为底图
   ```

================================================================================
🧪 测试步骤
================================================================================

1. 刷新浏览器页面（清除缓存）
   - 按 Cmd+Shift+R (Mac) 或 Ctrl+Shift+R (Windows)

2. 在设计器中操作
   - 勾选"启用附件底图"
   - 选择附件字段
   - 点击"预览 PDF"

3. 预期结果
   - ✅ 附件底图应该显示在预览中
   - ✅ 浏览器控制台无错误
   - ✅ 后端日志显示下载附件成功

4. 调试日志
   - 打开浏览器控制台（F12）
   - 查看 Network 标签
   - 找到 /designer/api/preview 请求
   - 查看 Request Payload 是否包含 attachment_background_config

================================================================================
⚠️ 关于"默认启用"的问题
================================================================================

如果不想附件底图默认启用，有两种方法：

方法 1: 在设计器中修改并保存
---------------------------------------------------------------
1. 打开设计器
2. 取消勾选"启用附件底图"
3. 点击"保存布局"
4. 配置文件会更新为 enabled: false

方法 2: 手动修改配置文件
---------------------------------------------------------------
编辑 data/print_layouts.json:
```json
{
  "PROC-941085FC-98E5-4D84-8144-B81A054C17CB": {
    "attachment_background_config": {
      "enabled": false,  // ← 改为 false
      "field_id": "DDAttachment_1PKSP5YV9WRGG",
      "attachment_index": 0,
      "page_index": 0,
      "apply_mode": "preview_and_print"
    }
  }
}
```

================================================================================
✅ 修复总结
================================================================================

修复的文件:
- ✅ static/js/designer_edit.js - previewPdf 函数

修复的问题:
- ✅ 预览 PDF 时传递 attachment_background_config
- ✅ 后端能正确接收附件底图配置
- ✅ 附件底图能在预览中显示

未修复（不是 bug）:
- ⚠️ 附件底图默认启用 - 这是配置文件中保存的状态，不是 bug

下一步:
1. 刷新浏览器页面
2. 测试预览功能
3. 如果不想默认启用，取消勾选并保存

================================================================================
