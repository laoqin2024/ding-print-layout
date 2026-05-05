================================================================================
🎯 根本原因找到！附件底图预览问题已修复
================================================================================

修复时间: 2026-05-04 16:45
问题: use_template = false 导致附件底图逻辑不执行

================================================================================
🐛 根本原因
================================================================================

问题分析:
1. 前端发送的请求中 "use_template": false
2. 后端的附件底图逻辑在 if use_template: 块内
3. 因为 use_template = false，所以代码永远不会执行到附件底图逻辑
4. 导致没有任何 [DEBUG] 日志输出

代码结构:
```python
# app/routes/designer.py
src_doc = None
if use_template:  # ← 这里是 False，所以下面的代码不执行
    # Pick preview background source
    if cover_source_mode == "attachment":
        # 下载附件 PDF
        source_pdf_bytes = ding.download_specific_attachment_pdf(...)
```

================================================================================
✅ 修复方案
================================================================================

修改文件: static/js/designer_edit.js - previewPdf 函数

修复逻辑:
当启用附件底图时，强制设置 use_template = true

修复前:
```javascript
const payload = {
  use_template: !!state.useTemplate,  // ← 可能是 false
  cover_source_mode: state.coverSourceMode,
  attachment_background_config: { ... }
};
```

修复后:
```javascript
// 如果启用了附件底图，强制 use_template = true
const useTemplate = state.useTemplate || (state.attachmentBg.enabled && state.coverSourceMode === "attachment");

const payload = {
  use_template: useTemplate,  // ← 附件底图启用时自动为 true
  cover_source_mode: state.coverSourceMode,
  attachment_background_config: { ... }
};
```

================================================================================
🔄 完整的调用链（修复后）
================================================================================

1. 前端判断
   ```javascript
   state.attachmentBg.enabled = true
   state.coverSourceMode = "attachment"
   → useTemplate = true  // ← 强制设置
   ```

2. 前端发送请求
   ```json
   {
     "use_template": true,  // ← 现在是 true
     "cover_source_mode": "attachment",
     "attachment_background_config": { ... }
   }
   ```

3. 后端接收
   ```python
   use_template = True  // ← 现在是 True
   ```

4. 后端执行
   ```python
   if use_template:  // ← 条件满足，进入分支
       if cover_source_mode == "attachment":  // ← 条件满足
           source_pdf_bytes = ding.download_specific_attachment_pdf(...)  // ← 执行下载
   ```

5. 后端使用附件
   ```python
   if source_pdf_bytes:
       src_doc = fitz.open(stream=source_pdf_bytes, filetype="pdf")  // ← 使用附件作为底图
   ```

================================================================================
🧪 测试步骤
================================================================================

1. 刷新浏览器页面
   - 按 Cmd+Shift+R (Mac) 强制刷新
   - 确保加载最新的 JavaScript 代码

2. 在设计器中操作
   - 勾选"启用附件底图"
   - 选择附件字段
   - 点击"预览 PDF"

3. 查看终端日志
   应该看到:
   ```
   [DEBUG] ===== 开始处理附件底图 =====
   [DEBUG] cover_source_mode: 'attachment'
   [DEBUG] cover_source_mode == 'attachment': True
   [DEBUG] ✅ 进入 attachment 分支
   [DEBUG] attachment_bg_enabled: True
   [DEBUG] attachment_bg_field_id: DDAttachment_1PKSP5YV9WRGG
   [DEBUG] should_apply: True
   [DEBUG] 尝试下载附件: field_id=DDAttachment_1PKSP5YV9WRGG, index=0
   [DEBUG] ✅ 附件下载成功，大小: XXXXX bytes
   [DEBUG] 使用附件 PDF 作为底图
   ```

4. 查看预览结果
   - 新窗口应该显示附件 PDF 作为底图
   - 上面叠加了设计器中配置的元素

================================================================================
📊 修复前后对比
================================================================================

修复前:
- use_template: false
- 后端不执行附件底图逻辑
- 没有 [DEBUG] 日志
- 预览不显示附件底图

修复后:
- use_template: true (当启用附件底图时)
- 后端执行附件底图逻辑
- 有完整的 [DEBUG] 日志
- 预览显示附件底图

================================================================================
⚠️ 注意事项
================================================================================

1. 必须刷新浏览器页面
   - 使用 Cmd+Shift+R 强制刷新
   - 或者清除缓存后刷新

2. 确保配置正确
   - 勾选"启用附件底图"
   - 选择正确的附件字段
   - apply_mode 设置为 "preview_and_print"

3. 查看日志确认
   - 终端应该有 [DEBUG] 日志输出
   - 如果没有，说明浏览器还在使用旧代码

================================================================================
✅ 修复完成
================================================================================

修改的文件:
- static/js/designer_edit.js - previewPdf 函数

修复的问题:
- use_template = false 导致附件底图逻辑不执行

下一步:
1. 刷新浏览器页面（重要！）
2. 测试预览功能
3. 查看终端日志确认

================================================================================
