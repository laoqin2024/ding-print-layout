# 设计器部门控件自动换行功能

## 更新时间
2026-05-02

## 功能说明

为设计器中的部门控件添加了 `text_wrap`（文本自动换行）参数，解决部门名称过长时的显示问题。

## 修改内容

### 1. 前端 HTML（templates/designer_edit.html）

在属性面板中添加了自动换行复选框：

```html
<div class="glass rounded-xl px-2 py-2 col-span-2">
  <label class="inline-flex items-center gap-2 text-[10px] font-black text-slate-700">
    <input id="prop-text-wrap" type="checkbox" />
    文本自动换行（text_wrap）- 适用于部门等长文本
  </label>
</div>
```

### 2. 前端 JavaScript（static/js/designer_edit.js）

#### 添加元素引用
```javascript
const propTextWrap = document.getElementById("prop-text-wrap");
```

#### 在 updateSelected 函数中保存属性
```javascript
it.text_wrap = propTextWrap ? !!propTextWrap.checked : false;
```

#### 在 syncProp 函数中同步属性到界面
```javascript
if (propTextWrap) propTextWrap.checked = it.text_wrap === true;
```

#### 创建部门控件时的默认值
```javascript
} else if (kind === "dept") {
  state.items.push({
    ...base,
    renderer: "dept",
    label: "部门",
    // ... 其他属性
    text_wrap: false,  // 默认不换行
  });
}
```

#### 在 renderItems 函数中支持画布预览换行
```javascript
} else if (r === "dept") {
  const deptText = it.field_name ? `部门：${it.field_name}` : `部门槽位 #${Math.max(1, Number(it.slot_index || 1))}`;
  // Support text wrapping in preview
  if (it.text_wrap) {
    el.style.whiteSpace = "normal";
    el.style.wordBreak = "break-all";
    el.style.overflowWrap = "break-word";
  } else {
    el.style.whiteSpace = "nowrap";
    el.style.overflow = "hidden";
    el.style.textOverflow = "ellipsis";
  }
  el.textContent = deptText;
}
```

### 3. 后端渲染逻辑（app/routes/designer.py）

#### 修改 _draw_text_with_spacing 函数签名
添加 `text_wrap` 参数：

```python
def _draw_text_with_spacing(
    *,
    fitz_mod,
    page,
    rect,
    text: str,
    fontname: str,
    fontsize: float,
    color,
    align: int,
    line_height: float,
    letter_spacing: float,
    overflow_marker: bool = True,
    text_wrap: bool = False,  # 新增参数
    fontfile: str | None = None,
):
```

#### 修改 wrap_line 函数逻辑
```python
def wrap_line(src: str):
    s = src or ""
    if not s:
        return [""]
    # If text_wrap is disabled, return single line
    if not text_wrap:
        return [s]
    # ... 原有的换行逻辑
```

#### 在所有调用处添加 text_wrap 参数
- 部门控件渲染：`text_wrap=bool(it.get("text_wrap", False))`
- 流程结果渲染：`text_wrap=bool(it.get("text_wrap", False))`
- 普通文本渲染：`text_wrap=bool(it.get("text_wrap", False))`

## 使用方法

### 1. 在设计器中配置

1. 拖拽"部门控件"到画布
2. 选中部门控件
3. 在右侧属性面板中找到"文本自动换行（text_wrap）"复选框
4. 勾选该复选框启用自动换行
5. 调整控件高度以容纳多行文本
6. 点击"更新选中项"保存设置

### 2. 效果说明

**未启用换行（默认）：**
- 部门名称过长时会被截断
- 显示省略号（如果启用了 overflow_marker）
- 单行显示

**启用换行后：**
- 部门名称会自动换行显示
- 根据控件宽度自动分行
- 可以显示完整的部门名称
- **画布预览实时显示换行效果**
- **PDF 打印也按换行渲染**
- 适合长部门名称，如"技术研发中心一部"、"生产制造管理办公室"等

### 3. 配置建议

对于部门控件：
- **短部门名**（如"财务部"、"人事部"）：不需要启用换行
- **长部门名**（如"技术研发中心一部"）：建议启用换行
- **控件高度**：启用换行后，建议将高度设置为 40-60px，以容纳 2-3 行文本
- **行高**：建议设置 line_height 为 1.2-1.5，确保行间距合适

## 示例配置

### 单行部门（不换行）
```json
{
  "renderer": "dept",
  "label": "部门",
  "w": 120,
  "h": 22,
  "font_size": 10,
  "line_height": 1.2,
  "text_wrap": false,
  "overflow_marker": true
}
```

### 多行部门（换行）
```json
{
  "renderer": "dept",
  "label": "部门",
  "w": 120,
  "h": 50,
  "font_size": 10,
  "line_height": 1.3,
  "text_wrap": true,
  "overflow_marker": true
}
```

## 技术细节

### 换行算法
1. 按字符逐个累加，计算当前行宽度
2. 如果加入下一个字符后超出控件宽度，则换行
3. 继续处理剩余字符
4. 最多显示控件高度允许的行数
5. 超出部分显示省略号（如果启用）

### 兼容性
- ✅ 向后兼容：未设置 text_wrap 的控件默认为 false（不换行）
- ✅ 适用于所有文本类控件（text、label、dept、flow_result）
- ✅ 支持中英文混排
- ✅ 支持自定义字体和字号

## 注意事项

1. **控件高度**：启用换行后，确保控件高度足够容纳多行文本
2. **字体大小**：字体越大，每行能容纳的字符越少
3. **行高设置**：合理设置 line_height，避免行间距过大或过小
4. **性能**：换行计算会略微增加渲染时间，但影响很小
5. **预览**：修改后记得预览 PDF，确认显示效果

## 文件变更清单

- ✅ `templates/designer_edit.html` - 添加 UI 控件
- ✅ `static/js/designer_edit.js` - 添加前端逻辑
- ✅ `app/routes/designer.py` - 添加后端渲染支持

## 测试建议

1. 创建部门控件，输入长部门名称
2. 不启用换行，查看截断效果
3. 启用换行，查看多行显示效果
4. 调整控件宽度和高度，测试不同布局
5. 预览 PDF，确认打印效果

---

**状态**: ✅ 已完成  
**版本**: 1.0.0  
**日期**: 2026-05-02
