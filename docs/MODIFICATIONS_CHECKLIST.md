================================================================================
🔄 需要确认和恢复的最新修改清单
================================================================================

根据文件修改时间，以下是最近的关键修改：

================================================================================
📅 最近修改的文件（按时间倒序）
================================================================================

1. ✅ frontend/src/js/print.js
   修改时间: 2026-05-04 15:34
   修改内容: Gemini 建议的 PDF 渲染和钉钉打印增强
   状态: 已确认存在

2. ✅ data/users.json
   修改时间: 2026-05-04 15:31
   修改内容: 用户数据更新
   状态: 数据文件，无需检查

3. ✅ static/js/designer_edit.js
   修改时间: 2026-05-04 15:22
   修改内容: 附件底图功能修复（cover_source_mode 同步）
   状态: 需要确认

4. ✅ app/routes/designer.py
   修改时间: 2026-05-04 15:22
   修改内容: 附件底图 API 修复（fileId 处理）
   状态: 需要确认

5. ✅ app/services/pdf_service.py
   修改时间: 2026-05-04 15:21
   修改内容: PDF 保存优化
   状态: 需要确认

6. ✅ data/print_layouts.json
   修改时间: 2026-05-04 14:25
   修改内容: 设计器布局配置
   状态: 需要确认

7. ✅ app/config.py
   修改时间: 2026-05-04 12:10
   修改内容: 配置文件更新
   状态: 需要确认

8. ✅ app/services/dingtalk_service.py
   修改时间: 2026-05-04 09:36
   修改内容: 钉钉服务（附件下载 API）
   状态: 需要确认

================================================================================
🔍 需要检查的关键修改
================================================================================

修改 1: app/routes/designer.py - render_attachment_bg 函数
---------------------------------------------------------------
关键代码: 使用 fileId 获取下载 URL

应该包含:
```python
# 钉钉附件格式：{"fileId": "xxx", "spaceId": "xxx", "fileName": "xxx.pdf", ...}
# 需要通过 fileId 获取下载 URL
file_id = str(attachment.get("fileId") or "").strip()

if not file_id:
    return "No fileId in attachment", 404

# 获取下载 URL
try:
    file_url = ding.get_process_attachment_url(
        process_instance_id=instance_id,
        file_id=file_id
    )
except Exception as e:
    return f"Failed to get download URL: {str(e)}", 500
```

修改 2: app/routes/designer.py - designer_preview 函数
---------------------------------------------------------------
关键代码: 改进附件底图应用模式判断

应该包含:
```python
if attachment_bg_enabled and attachment_bg_field_id:
    # 检查应用模式：preview_and_print, preview_only, print_only
    should_apply = (
        attachment_bg_apply_mode in ("preview_and_print", "preview_only", "both") or
        not attachment_bg_apply_mode  # 默认应用
    )
    if should_apply:
        # 使用配置中指定的附件字段
        source_pdf_bytes = ding.download_specific_attachment_pdf(
            instance=instance,
            field_id=attachment_bg_field_id,
            attachment_index=attachment_bg_index
        )

# 如果没有获取到附件，兜底逻辑
if not source_pdf_bytes:
    source_pdf_bytes = ding.download_process_attachment_pdf(...)
```

修改 3: static/js/designer_edit.js - syncAttachmentBgUI 函数
---------------------------------------------------------------
关键代码: 同步 cover_source_mode 状态

应该包含:
```javascript
function syncAttachmentBgUI() {
  // 同步 cover_source_mode（仅同步状态，不自动加载）
  if (state.attachmentBg.enabled) {
    state.coverSourceMode = "attachment";
    if (coverSourceModeEl) {
      coverSourceModeEl.value = "attachment";
    }
  }
  
  // ... 其他 UI 同步代码 ...
  
  // 注意：不自动加载附件底图，用户需要手动勾选开关来加载
}
```

修改 4: static/js/designer_edit.js - 开关事件监听器
---------------------------------------------------------------
关键代码: 勾选时同步 cover_source_mode

应该包含:
```javascript
attachmentBgEnabled?.addEventListener("change", () => {
  state.attachmentBg.enabled = attachmentBgEnabled.checked;
  
  // 同步 cover_source_mode
  if (attachmentBgEnabled.checked) {
    state.coverSourceMode = "attachment";
    if (coverSourceModeEl) {
      coverSourceModeEl.value = "attachment";
    }
  } else {
    state.coverSourceMode = "base";
    if (coverSourceModeEl) {
      coverSourceModeEl.value = "base";
    }
  }
  
  // ... 其他逻辑 ...
});
```

修改 5: frontend/src/js/print.js - renderPdf 函数
---------------------------------------------------------------
关键代码: 添加 cMapUrl 支持中文

应该包含:
```javascript
const loadingTask = getDocument({ 
  url: pdfUrl, 
  withCredentials: false,
  cMapUrl: 'https://cdn.jsdelivr.net/npm/pdfjs-dist@legacy/cmaps/',
  cMapPacked: true,
});
```

修改 6: frontend/src/js/print.js - doPrint 函数
---------------------------------------------------------------
关键代码: 增强钉钉打印调用

应该包含:
```javascript
async function doPrint() {
  const url = boot.pdfUrl;
  const fullUrl = url.startsWith('http') ? url : window.location.origin + url;
  
  if (window.dd && dd.env && dd.env.platform !== "notInDingTalk") {
    dd.ready(() => {
      dd.biz.util.print({
        url: fullUrl,
        onSuccess: () => console.log("正在唤起钉钉打印..."),
        onFail: (err) => {
          console.error("钉钉打印失败:", err);
          window.print();
        }
      });
    });
  } else {
    window.print();
  }
}
```

================================================================================
✅ 下一步操作
================================================================================

1. 检查每个文件是否包含上述关键修改
2. 如果缺失，从备份或文档中恢复
3. 重新编译前端代码
4. 重启服务器测试

================================================================================
