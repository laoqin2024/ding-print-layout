================================================================================
✅ 独立的横向和纵向对齐功能已添加
================================================================================

修复时间: 2026-05-04 18:20
问题: 需要独立控制横向和纵向的对齐方式

================================================================================
✅ 解决方案
================================================================================

修改内容:
1. _draw_text_with_spacing 函数添加 vertical_align 参数
2. 所有调用位置添加 vertical_align 参数读取
3. 从配置中读取 vertical_align 字段

支持的对齐方式:
- 横向对齐 (text_align): left, center, right
- 纵向对齐 (vertical_align): top, middle, bottom

默认值:
- 横向: left
- 纵向: middle

================================================================================
📊 对齐组合示例
================================================================================

1. 左上角对齐
   ```json
   {
     "text_align": "left",
     "vertical_align": "top"
   }
   ```
   ```
   ┌─────────────────┐
   │ 文本            │
   │                 │
   │                 │
   └─────────────────┘
   ```

2. 居中对齐（横向+纵向）
   ```json
   {
     "text_align": "center",
     "vertical_align": "middle"
   }
   ```
   ```
   ┌─────────────────┐
   │                 │
   │      文本       │
   │                 │
   └─────────────────┘
   ```

3. 右下角对齐
   ```json
   {
     "text_align": "right",
     "vertical_align": "bottom"
   }
   ```
   ```
   ┌─────────────────┐
   │                 │
   │                 │
   │            文本 │
   └─────────────────┘
   ```

4. 横向居中 + 纵向顶部
   ```json
   {
     "text_align": "center",
     "vertical_align": "top"
   }
   ```
   ```
   ┌─────────────────┐
   │      文本       │
   │                 │
   │                 │
   └─────────────────┘
   ```

5. 横向左对齐 + 纵向居中
   ```json
   {
     "text_align": "left",
     "vertical_align": "middle"
   }
   ```
   ```
   ┌─────────────────┐
   │                 │
   │ 文本            │
   │                 │
   └─────────────────┘
   ```

================================================================================
🔧 配置示例
================================================================================

在 data/print_layouts.json 中:

```json
{
  "items": [
    {
      "renderer": "label",
      "label": "钉钉流程编号：",
      "x": 30,
      "y": 40,
      "w": 230,
      "h": 20,
      "text_align": "left",        // 横向左对齐
      "vertical_align": "middle",  // 纵向居中
      "font_size": 10,
      "font_family": "china-s"
    },
    {
      "renderer": "text",
      "field_id": "sys.approval_no",
      "x": 120,
      "y": 40,
      "w": 140,
      "h": 20,
      "text_align": "center",      // 横向居中
      "vertical_align": "top",     // 纵向顶部
      "font_size": 10
    }
  ]
}
```

================================================================================
🎨 前端设计器集成（建议）
================================================================================

在设计器中添加纵向对齐选项:

1. 添加 UI 控件
   ```html
   <div class="form-group">
     <label>纵向对齐</label>
     <select id="vertical-align">
       <option value="top">顶部</option>
       <option value="middle" selected>居中</option>
       <option value="bottom">底部</option>
     </select>
   </div>
   ```

2. 保存到配置
   ```javascript
   const item = {
     // ... 其他属性 ...
     text_align: textAlignSelect.value,      // left, center, right
     vertical_align: verticalAlignSelect.value, // top, middle, bottom
   };
   ```

3. 同步到 state
   ```javascript
   state.items[index].vertical_align = value;
   ```

================================================================================
🧪 测试步骤
================================================================================

1. 重启服务器
   ```bash
   cd "/Volumes/MyDisk/App programs/dingtalk-h5-app"
   pkill -f "python.*run.py"
   python run.py
   ```

2. 手动修改配置测试
   ```bash
   # 编辑 data/print_layouts.json
   # 找到标签控件，添加 vertical_align 字段
   {
     "renderer": "label",
     "label": "测试文本",
     "text_align": "center",
     "vertical_align": "top"  // 添加这一行
   }
   ```

3. 在设计器中预览
   - 打开设计器
   - 点击"预览 PDF"
   - 确认文本按照配置对齐

4. 测试所有组合
   - left + top
   - left + middle
   - left + bottom
   - center + top
   - center + middle
   - center + bottom
   - right + top
   - right + middle
   - right + bottom

================================================================================
📝 代码实现细节
================================================================================

1. 函数签名
   ```python
   def _draw_text_with_spacing(
       *,
       # ... 其他参数 ...
       vertical_align: str = "middle",  # 新增
   ):
   ```

2. 纵向偏移计算
   ```python
   total_text_height = len(lines) * line_step
   if vertical_align == "top":
       vertical_offset = 0
   elif vertical_align == "bottom":
       vertical_offset = max(0, rect.height - total_text_height)
   else:  # middle
       vertical_offset = max(0, (rect.height - total_text_height) / 2.0)
   
   y = rect.y0 + fontsize + vertical_offset + i * line_step
   ```

3. 配置读取
   ```python
   vertical_align_map = {"top": "top", "middle": "middle", "bottom": "bottom"}
   vertical_align = vertical_align_map.get(
       str(it.get("vertical_align") or "middle").lower(), 
       "middle"
   )
   ```

================================================================================
✅ 修复完成
================================================================================

修改的文件:
- app/routes/designer.py

新增功能:
- ✅ 独立的横向对齐控制 (text_align)
- ✅ 独立的纵向对齐控制 (vertical_align)
- ✅ 9 种对齐组合 (3x3)

下一步:
1. 重启服务器
2. 手动修改配置测试
3. 在设计器中添加 UI 控件（可选）

================================================================================
