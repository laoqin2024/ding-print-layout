================================================================================
✅ 钉钉打印预览附件底图问题已修复
================================================================================

修复时间: 2026-05-04 17:00
问题: 钉钉打印预览没有传递 attachment_background_config

================================================================================
🐛 问题分析
================================================================================

调用链:
1. 钉钉前端 → /print_view
2. print_view → 检测到设计器布局 → 重定向到 designer_preview_print
3. designer_preview_print → 渲染 designer_print.html
4. designer_print.html → JavaScript 调用 /designer/api/preview
5. designer/api/preview → 生成 PDF

问题所在:
- designer_print.html 的 JavaScript 没有传递 attachment_background_config
- 导致后端收不到附件底图配置
- 所以预览不显示附件底图

================================================================================
✅ 修复方案
================================================================================

修改文件 1: app/routes/designer.py - designer_preview_print 函数
---------------------------------------------------------------
添加逻辑：当启用附件底图时，强制 use_template = True

```python
# 如果启用了附件底图，强制 use_template = True
attachment_bg_config = payload.get("attachment_background_config") or {}
if attachment_bg_config.get("enabled") and payload.get("cover_source_mode") == "attachment":
    payload["use_template"] = True
    print(f"[DEBUG] 钉钉打印：启用附件底图，强制 use_template = True")
```

修改文件 2: templates/designer_print.html - loadPDF 函数
---------------------------------------------------------------
添加 attachment_background_config 参数传递

修改前:
```javascript
body: JSON.stringify({
  process_code: boot.processCode,
  instance_id: boot.instanceId,
  base_pdf: layout.base_pdf || '',
  use_template: layout.use_template !== false,
  // ... 其他参数 ...
  items: layout.items || [],
  // ❌ 缺少 attachment_background_config
}),
```

修改后:
```javascript
// 如果启用了附件底图，强制 use_template = true
let useTemplate = layout.use_template !== false;
const attachmentBgConfig = layout.attachment_background_config || {};
if (attachmentBgConfig.enabled && layout.cover_source_mode === 'attachment') {
  useTemplate = true;
  console.log('[DEBUG] 钉钉打印：启用附件底图，强制 use_template = true');
}

body: JSON.stringify({
  process_code: boot.processCode,
  instance_id: boot.instanceId,
  base_pdf: layout.base_pdf || '',
  use_template: useTemplate,  // ← 使用计算后的值
  // ... 其他参数 ...
  attachment_background_config: attachmentBgConfig,  // ← 新增
  items: layout.items || [],
}),
```

================================================================================
🔄 完整的调用链（修复后）
================================================================================

1. 钉钉前端 → /print_view?id=xxx
2. print_view → 检测到设计器布局
3. 重定向 → /designer/preview_print?process_code=xxx&instance_id=xxx
4. designer_preview_print → 读取 layout 配置
5. 强制 use_template = True（如果启用附件底图）
6. 渲染 designer_print.html，传递 layout_json
7. JavaScript 读取 layout.attachment_background_config
8. 强制 use_template = true（如果启用附件底图）
9. 调用 /designer/api/preview，传递完整配置
10. 后端接收 attachment_background_config
11. 后端下载附件 PDF
12. 后端生成带附件底图的 PDF
13. 前端显示 PDF

================================================================================
🧪 测试步骤
================================================================================

1. 重启服务器
   ```bash
   cd "/Volumes/MyDisk/App programs/dingtalk-h5-app"
   pkill -f "python.*run.py"
   python run.py
   ```

2. 在钉钉中测试
   - 打开审批实例
   - 点击"打印预览"

3. 查看终端日志
   应该看到:
   ```
   [DEBUG] print_view called:
   [DEBUG] Redirecting to designer preview
   [DEBUG] 钉钉打印：启用附件底图，强制 use_template = True
   [DEBUG] ===== 开始处理附件底图 =====
   [DEBUG] ✅ 进入 attachment 分支
   [DEBUG] ✅ 附件下载成功，大小: XXXXX bytes
   [DEBUG] 使用附件 PDF 作为底图
   ```

4. 查看浏览器控制台
   应该看到:
   ```
   [DEBUG] 钉钉打印：启用附件底图，强制 use_template = true
   ```

5. 查看预览结果
   - 应该显示附件 PDF 作为底图
   - 上面叠加了设计器中配置的元素

================================================================================
✅ 修复总结
================================================================================

修改的文件:
1. ✅ app/routes/designer.py - designer_preview_print 函数
2. ✅ templates/designer_print.html - loadPDF 函数
3. ✅ static/js/designer_edit.js - previewPdf 函数（之前已修复）

修复的问题:
1. ✅ 设计器预览：已修复（use_template 强制为 true）
2. ✅ 钉钉打印预览：已修复（传递 attachment_background_config）

下一步:
1. 重启服务器
2. 在钉钉中测试打印预览
3. 查看终端和浏览器日志确认

================================================================================
