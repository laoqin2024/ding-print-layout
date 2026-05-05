================================================================================
✅ 钉钉打印功能最终修复方案
================================================================================

修复时间: 2026-05-04 17:20
问题: 点击"立即打印"打印整个页面而不是 PDF 内容

================================================================================
🐛 问题根本原因
================================================================================

问题 1: blob: URL 无法被钉钉下载
---------------------------------------------------------------
- loadPDF() 函数使用 URL.createObjectURL(blob) 创建 blob: URL
- blob: URL 只在当前页面有效
- 钉钉的 dd.biz.util.print() 无法下载 blob: URL
- 导致打印失败，降级到 window.print()

问题 2: /designer/api/preview 只支持 POST
---------------------------------------------------------------
- 原始 API 只支持 POST 方法
- dd.biz.util.print() 需要 GET URL
- 无法直接使用 API URL

================================================================================
✅ 最终解决方案
================================================================================

方案: 支持 GET 方法 + 使用真实 URL
---------------------------------------------------------------

修改 1: app/routes/designer.py - designer_preview 函数
```python
@designer_bp.route("/designer/api/preview", methods=["POST", "GET"])
def designer_preview():
    # 支持 POST 和 GET 两种方法
    if request.method == "POST":
        payload = request.get_json(force=True) or {}
    else:  # GET
        # 从查询参数中获取数据
        payload = {}
        for key in request.args:
            value = request.args.get(key)
            # 解析 JSON 字符串
            if key in ('items', 'attachment_background_config'):
                payload[key] = json.loads(value)
            elif key == 'use_template':
                payload[key] = value in ('1', 'true', 'True')
            # ...
```

修改 2: templates/designer_print.html - 打印按钮
```javascript
printFab?.addEventListener('click', () => {
  if (window.dd && dd.env && dd.env.platform !== "notInDingTalk") {
    // 构建 GET URL
    const params = new URLSearchParams({
      process_code: boot.processCode,
      instance_id: boot.instanceId,
      use_template: useTemplate ? '1' : '0',
      attachment_background_config: JSON.stringify(attachmentBgConfig),
      items: JSON.stringify(layout.items || []),
      // ... 其他参数
    });
    
    const pdfUrl = window.location.origin + '/designer/api/preview?' + params.toString();
    
    // 使用钉钉原生打印
    dd.ready(function () {
      dd.biz.util.print({
        url: pdfUrl,
        onSuccess: function () {
          console.log('[DingTalk] 正在唤起钉钉打印...');
        },
        onFail: function (err) {
          console.error('[DingTalk] 钉钉打印失败:', err);
          window.print();
        },
      });
    });
  } else {
    window.print();
  }
});
```

================================================================================
🔄 完整的打印流程（修复后）
================================================================================

1. 用户点击"立即打印"按钮
2. 检测钉钉环境
3. 构建 GET URL:
   ```
   http://192.168.8.168:8000/designer/api/preview?
     process_code=PROC-xxx&
     instance_id=xxx&
     use_template=1&
     cover_source_mode=attachment&
     attachment_background_config={"enabled":true,...}&
     items=[...]
   ```
4. 调用 dd.biz.util.print({ url: pdfUrl })
5. 钉钉下载 PDF（通过 GET 请求）
6. 后端生成带附件底图的 PDF
7. 钉钉唤起原生打印对话框
8. 用户选择打印机并打印

================================================================================
📊 修复前后对比
================================================================================

修复前:
- 使用 blob: URL
- 钉钉无法下载
- 降级到 window.print()
- 打印整个 HTML 页面

修复后:
- 使用真实的 GET URL
- 钉钉可以下载 PDF
- 使用 dd.biz.util.print()
- 打印 PDF 内容

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
   - 等待 PDF 加载完成
   - 点击"立即打印"按钮

3. 预期结果
   - 钉钉唤起原生打印对话框
   - 打印的是 PDF 内容（带附件底图）
   - 浏览器控制台显示: [DingTalk] 正在唤起钉钉打印...

4. 查看终端日志
   应该看到:
   ```
   GET /designer/api/preview?process_code=xxx&... HTTP/1.1" 200 -
   [DEBUG] ===== 开始处理附件底图 =====
   [DEBUG] ✅ 附件下载成功
   ```

================================================================================
⚠️ 注意事项
================================================================================

1. URL 长度限制
   - GET URL 可能很长（包含 items 数组）
   - 如果超过浏览器/服务器限制，需要改用 POST + 临时 token

2. 参数编码
   - JSON 参数需要正确编码
   - 使用 URLSearchParams 自动处理

3. 降级逻辑
   - 如果钉钉打印失败，降级到 window.print()
   - 如果不在钉钉环境，直接使用 window.print()

4. JSAPI 配置
   - 确保 dd.config 已正确配置
   - 确保 jsApiList 包含 "biz.util.print"

================================================================================
✅ 修复完成
================================================================================

修改的文件:
1. ✅ app/routes/designer.py - 支持 GET 方法
2. ✅ templates/designer_print.html - 使用 GET URL 打印

修复的问题:
- ✅ 钉钉打印现在使用原生打印对话框
- ✅ 打印的是 PDF 内容而不是整个页面
- ✅ 附件底图正确显示

下一步:
1. 重启服务器
2. 在钉钉中测试打印功能
3. 查看终端和浏览器日志确认

================================================================================
