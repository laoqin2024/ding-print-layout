# 设计器画布预览优化

## 更新时间
2026-05-02

## 问题说明

### 问题1：文本换行时控件被撑大
**现象**：启用文本自动换行后，增大字号会导致控件宽度被内容撑大，而不是在固定宽度内换行。

**原因**：CSS 样式不够严格，没有限制控件的最大宽度。

### 问题2：附件底图无法在画布预览
**现象**：当底图来源设置为"attachment（流程附件）"时，设计器画布中看不到底图，只能看到空白页面。

**原因**：附件底图需要从钉钉实例中动态获取，设计器画布是静态预览，无法实时获取附件内容。

## 解决方案

### 1. 修复文本换行宽度问题

#### CSS 样式优化（templates/designer_edit.html）
```css
.designer-item {
  position: absolute; 
  border: 2px solid #4f46e5; 
  background: rgba(79,70,229,.08);
  color: #312e81; 
  font-size: 10px; 
  font-weight: 700; 
  padding: 2px 4px; 
  cursor: move; 
  user-select: none;
  min-width: 36px; 
  min-height: 18px; 
  overflow: hidden;
  box-sizing: border-box;  /* 新增：包含边框和内边距 */
  max-width: 100%;         /* 新增：限制最大宽度 */
  word-wrap: break-word;   /* 新增：强制换行 */
}
```

#### JavaScript 样式设置（static/js/designer_edit.js）
```javascript
if (it.text_wrap) {
  el.style.whiteSpace = "pre-wrap";      // 保留换行，允许自动换行
  el.style.wordBreak = "break-all";      // 任意位置断行
  el.style.overflowWrap = "break-word";  // 单词内换行
  el.style.overflow = "hidden";          // 隐藏溢出内容
}
```

### 2. 附件底图预览提示

#### 添加智能提示（static/js/designer_edit.js）
```javascript
function refreshBgPreview() {
  if (!state.useTemplate) {
    bg.classList.add("hidden");
    return;
  }
  
  // 如果是附件底图模式，画布无法预览，显示提示
  if (state.coverSourceMode === "attachment") {
    bg.classList.add("hidden");
    if (canvasTitle) {
      const orient = state.orient === "p" ? "纵向" : "横向";
      canvasTitle.textContent = `画布（A4 ${orient}）- 附件底图模式：请点击"预览 PDF"查看实际效果`;
    }
    return;
  }
  
  // ... 正常的底稿 PDF 预览逻辑
}
```

#### 添加事件监听
```javascript
coverSourceModeEl?.addEventListener("change", () => {
  state.coverSourceMode = String(coverSourceModeEl.value || "base");
  syncCoverUiState();
  refreshBgPreview();  // 新增：切换底图来源时刷新预览
});
```

## 使用说明

### 文本换行功能

**正确使用方式：**
1. 拖拽部门控件到画布
2. 设置控件宽度（如 120px）
3. 勾选"文本自动换行"
4. 增大字号（如 12px、14px）
5. 文本会在固定宽度内自动换行，不会撑大控件

**效果：**
- ✅ 控件宽度保持固定
- ✅ 文本在控件内自动换行
- ✅ 超出高度的内容被隐藏
- ✅ 画布预览和 PDF 打印效果一致

### 附件底图功能

**使用流程：**

1. **选择底图来源**
   - `base`（底稿）：使用预设的 PDF 模板，画布可预览
   - `attachment`（流程附件）：使用钉钉实例的附件，画布无法预览

2. **附件底图模式**
   - 画布标题会显示提示：`画布（A4 横向）- 附件底图模式：请点击"预览 PDF"查看实际效果`
   - 画布中只显示控件，不显示底图
   - 点击"预览 PDF"按钮，会生成包含附件底图的完整 PDF

3. **配置附件底图**
   - 勾选"启用"附件底图配置
   - 选择附件字段（如"附件"、"图纸"等）
   - 设置附件索引（第几个附件，从 0 开始）
   - 设置 PDF 页码（附件 PDF 的第几页，从 0 开始）
   - 选择应用模式：
     - `仅打印时生效`（推荐）：设计器预览快速，钉钉打印用真实附件
     - `预览和打印都生效`：预览也用附件（较慢但真实）

## 技术限制说明

### 为什么附件底图无法在画布预览？

1. **动态数据依赖**
   - 附件底图来自钉钉审批实例
   - 每个实例的附件不同
   - 需要实时从钉钉 API 获取

2. **性能考虑**
   - 设计器画布是静态预览，追求快速响应
   - 实时获取附件会导致每次操作都需要等待网络请求
   - 影响设计体验

3. **解决方案**
   - 画布预览：只显示控件布局，不显示附件底图
   - PDF 预览：点击"预览 PDF"按钮，生成包含真实附件的完整 PDF
   - 这样既保证了设计效率，又能看到最终效果

## 最佳实践

### 使用附件底图时的工作流程

1. **初始设计阶段**
   - 底图来源选择 `base`（底稿）
   - 使用一个示例 PDF 作为参考底图
   - 在画布上布局控件
   - 快速调整位置和样式

2. **精确定位阶段**
   - 保持 `base` 模式
   - 使用实际的 PDF 模板
   - 精确调整控件位置
   - 确保对齐正确

3. **切换到附件模式**
   - 布局完成后，切换底图来源为 `attachment`
   - 配置附件字段和索引
   - 点击"预览 PDF"查看实际效果
   - 如需调整，可以临时切回 `base` 模式

4. **最终测试**
   - 使用真实的钉钉实例 ID 预览
   - 确认附件底图正确显示
   - 确认控件位置准确
   - 保存布局配置

### 文本换行的最佳实践

1. **控件尺寸**
   - 宽度：根据内容长度设置，建议 100-150px
   - 高度：启用换行后，建议 40-60px（容纳 2-3 行）

2. **字体设置**
   - 字号：10-12px 适合大多数场景
   - 行高：1.2-1.5 确保行间距合适
   - 字体：中文建议使用"宋体(内置)"

3. **测试**
   - 输入最长的可能文本测试
   - 确保不会溢出控件
   - 预览 PDF 确认打印效果

## 文件变更清单

- ✅ `templates/designer_edit.html` - 优化 CSS 样式
- ✅ `static/js/designer_edit.js` - 修复换行逻辑，添加附件底图提示

## 已知限制

1. **附件底图画布预览**：无法在设计器画布中预览附件底图（技术限制）
2. **换行精度**：画布预览的换行效果可能与 PDF 略有差异（字体渲染差异）
3. **性能**：启用附件底图的 PDF 预览会比较慢（需要下载附件）

---

**状态**: ✅ 已完成  
**版本**: 1.1.0  
**日期**: 2026-05-02
