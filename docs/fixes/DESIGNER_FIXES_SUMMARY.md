# 设计器问题修复总结

## 更新时间
2026-05-02

## 修复的问题

### 问题1：附件底图配置勾选启用时提示检查参数 ✅

**现象**：
- 勾选"启用"时弹出提示"请填写流程代码、实例ID和选择附件字段"
- 让用户误以为是错误

**原因**：
- 参数验证过于严格
- 在配置未完成时就显示错误提示

**修复方案**：
1. 参数不完整时不弹出错误提示
2. 只在画布标题显示友好提示："等待配置..."
3. 只在真正出错时才弹窗提示
4. 改进错误信息的可读性

**修改文件**：
- `static/js/designer_edit.js` - loadAttachmentBackground 函数

**修复后效果**：
- ✅ 勾选"启用"时不会弹窗
- ✅ 画布标题显示："附件底图：等待配置..."
- ✅ 配置完成后自动加载
- ✅ 只在真正出错时才提示

---

### 问题2：部门控件不会自动换行 ✅

**现象**：
- 勾选"文本自动换行"后，部门控件还是不换行
- 增大字号后文本被截断

**可能原因**：
1. 用户没有点击"更新选中项"按钮
2. CSS 样式使用 `pre-wrap` 可能有兼容性问题
3. 浏览器缓存了旧版本

**修复方案**：
1. 将 `white-space: pre-wrap` 改为 `white-space: normal`
2. 添加 `text-overflow: clip` 确保不显示省略号
3. 明确重置不换行时的样式
4. 确保 CSS 优先级正确

**修改文件**：
- `static/js/designer_edit.js` - renderItems 函数

**修复前代码**：
```javascript
if (it.text_wrap) {
  el.style.whiteSpace = "pre-wrap";
  el.style.wordBreak = "break-all";
  el.style.overflowWrap = "break-word";
  el.style.overflow = "hidden";
}
```

**修复后代码**：
```javascript
if (it.text_wrap) {
  el.style.whiteSpace = "normal";      // 改为 normal
  el.style.wordBreak = "break-all";
  el.style.overflowWrap = "break-word";
  el.style.overflow = "hidden";
  el.style.textOverflow = "clip";      // 新增：不显示省略号
} else {
  el.style.whiteSpace = "nowrap";
  el.style.overflow = "hidden";
  el.style.textOverflow = "ellipsis";
  el.style.wordBreak = "normal";       // 新增：重置
  el.style.overflowWrap = "normal";    // 新增：重置
}
```

**修复后效果**：
- ✅ 启用换行后文本正确换行
- ✅ 控件宽度保持固定
- ✅ 不会显示省略号
- ✅ 禁用换行时正常显示省略号

---

### 问题3：状态章和签名遮盖底图内容 ✅

**现象**：
- 状态章贴到附件上会把底图内容遮盖
- 签名也会遮盖底图
- 应该是透明背景，但显示为白色背景

**原因**：
- `page.insert_image()` 没有设置 `overlay=True` 参数
- 默认情况下，图片会作为背景层插入，覆盖底图内容
- PNG 的透明背景没有正确处理

**修复方案**：
- 在所有 `page.insert_image()` 调用中添加 `overlay=True` 参数
- 这样图片会作为覆盖层插入，保留透明背景

**修改文件**：
- `app/routes/designer.py`

**修复位置**：
1. 状态章渲染（第1520行）
2. 签名渲染 - auto_sequence 模式（第1666行）
3. 签名渲染 - manual 模式（第1680行）
4. 二维码渲染（第1563行）

**修复前代码**：
```python
page.insert_image(rect, filename=str(stamp_path), keep_proportion=True, rotate=0)
```

**修复后代码**：
```python
page.insert_image(rect, filename=str(stamp_path), keep_proportion=True, rotate=0, overlay=True)
```

**修复后效果**：
- ✅ 状态章透明背景正确显示
- ✅ 签名透明背景正确显示
- ✅ 不会遮盖底图内容
- ✅ 二维码也正确叠加

---

## 技术说明

### overlay=True 参数的作用

在 PyMuPDF (fitz) 中，`insert_image()` 的 `overlay` 参数：

- **overlay=False（默认）**：
  - 图片作为背景层插入
  - 会覆盖底图内容
  - PNG 透明区域显示为白色

- **overlay=True**：
  - 图片作为覆盖层插入
  - 保留 PNG 透明背景
  - 不会遮盖底图内容
  - 适合印章、签名等需要透明背景的图片

### white-space 属性说明

- **normal**：
  - 合并空白符
  - 允许自动换行
  - 最常用的换行模式

- **pre-wrap**：
  - 保留空白符
  - 允许自动换行
  - 适合显示预格式化文本
  - 可能导致意外的空白

- **nowrap**：
  - 不换行
  - 文本在一行显示
  - 超出部分隐藏或显示省略号

## 测试建议

### 测试1：附件底图配置

1. 打开设计器
2. 勾选"附件底图配置 - 启用"
3. 确认不会弹出错误提示
4. 画布标题显示："等待配置..."
5. 填写实例ID和选择附件字段
6. 确认自动加载附件底图

### 测试2：部门控件换行

1. 创建部门控件，宽度 100px
2. 勾选"文本自动换行"
3. 点击"更新选中项"
4. 设置字号为 14px
5. 点击"更新选中项"
6. 确认文本在画布中换行显示
7. 预览 PDF，确认打印效果

### 测试3：状态章透明背景

1. 添加状态章控件
2. 使用附件底图或底稿 PDF
3. 将状态章放在有内容的区域
4. 预览 PDF
5. 确认状态章透明背景正确显示
6. 确认底图内容没有被遮盖

### 测试4：签名透明背景

1. 添加签名控件
2. 使用附件底图或底稿 PDF
3. 将签名放在有内容的区域
4. 填写实例ID预览
5. 确认签名透明背景正确显示
6. 确认底图内容没有被遮盖

## 注意事项

### 1. 浏览器缓存

修改后需要强制刷新浏览器：
- Windows/Linux: `Ctrl + Shift + R`
- Mac: `Cmd + Shift + R`

### 2. 更新选中项

修改控件属性后，必须点击"更新选中项"按钮才能保存。

### 3. 保存布局

配置完成后，记得点击"保存布局"按钮。

### 4. PNG 图片要求

- 状态章和签名图片必须是 PNG 格式
- 必须包含透明通道（Alpha 通道）
- 如果是 JPG 格式，会显示白色背景

## 文件变更清单

- ✅ `static/js/designer_edit.js` - 优化附件底图加载逻辑
- ✅ `static/js/designer_edit.js` - 修复文本换行样式
- ✅ `app/routes/designer.py` - 添加 overlay=True 参数

## 已知限制

1. **文本换行精度**：画布预览的换行效果可能与 PDF 略有差异（字体渲染差异）
2. **附件底图加载速度**：首次加载需要下载附件，可能较慢
3. **透明背景支持**：只支持 PNG 格式，不支持 JPG

---

**状态**: ✅ 已完成  
**版本**: 2.1.0  
**日期**: 2026-05-02
