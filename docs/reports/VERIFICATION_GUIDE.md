# 问题修复验证指南

## 诊断结果

✅ 代码已正确修改：
- `designer_edit.js` - 部门控件换行代码已更新
- `designer.py` - 状态章和签名的 overlay=True 已添加
- PNG 文件 - 包含透明通道（RGBA）

## 问题原因

代码已经修改正确，但可能由于以下原因未生效：

### 1. Python 服务器未重启
- Python 代码修改后必须重启服务器才能生效
- `overlay=True` 的修改在 `app/routes/designer.py` 中

### 2. 浏览器缓存
- JavaScript 代码可能被浏览器缓存
- 需要强制刷新才能加载新版本

### 3. 配置未保存
- 勾选"文本自动换行"后必须点击"更新选中项"
- 必须点击"保存布局"才能持久化

## 立即执行的操作步骤

### 步骤1：重启 Flask 服务器 ⚠️ 最重要！

找到运行 Flask 的终端，按 `Ctrl+C` 停止，然后重新启动：

```bash
cd /root/dingtalk-h5-app
# 停止当前服务器（Ctrl+C）
# 重新启动
python app.py
# 或
flask run
```

**如果使用 systemd 或其他服务管理器：**
```bash
sudo systemctl restart your-service-name
```

### 步骤2：清除浏览器缓存并强制刷新

1. 打开设计器页面
2. 按 `Ctrl + Shift + R`（Windows/Linux）或 `Cmd + Shift + R`（Mac）
3. 或者按 `F12` 打开开发者工具，右键点击刷新按钮，选择"清空缓存并硬性重新加载"

### 步骤3：验证状态章透明背景

1. 打开设计器
2. 确保有底稿 PDF 或附件底图
3. 添加状态章控件
4. 将状态章放在有内容的区域上
5. 点击"预览 PDF"
6. 查看 PDF 中状态章是否透明

**预期效果：**
- ✅ 状态章背景透明
- ✅ 可以看到底图内容
- ✅ 只有印章图案，没有白色背景

### 步骤4：验证部门控件换行

1. 打开设计器
2. 选中部门控件（点击画布上的部门控件）
3. 在右侧属性面板中：
   - 设置宽度：100
   - 设置高度：50
   - 设置字号：14
   - ✅ 勾选"文本自动换行（text_wrap）"
4. **点击"更新选中项"按钮** ⚠️ 必须！
5. 观察画布中的部门控件是否换行
6. 点击"保存布局"
7. 点击"预览 PDF"查看打印效果

**预期效果：**
- ✅ 画布中文本换行显示
- ✅ 控件宽度保持 100px
- ✅ PDF 中文本也换行显示

## 调试方法

### 方法1：在浏览器控制台检查

1. 按 `F12` 打开开发者工具
2. 切换到 Console 标签
3. 输入以下代码：

```javascript
// 检查选中的控件配置
const idx = Array.from(state.selected)[0];
const item = state.items[idx];
console.log('控件类型:', item.renderer);
console.log('text_wrap:', item.text_wrap);
console.log('宽度:', item.w);
console.log('高度:', item.h);
console.log('字号:', item.font_size);

// 检查 DOM 元素样式
const el = document.querySelector(`[data-idx="${idx}"]`);
const styles = window.getComputedStyle(el);
console.log('white-space:', styles.whiteSpace);
console.log('word-break:', styles.wordBreak);
console.log('overflow:', styles.overflow);
```

**预期输出：**
```
控件类型: dept
text_wrap: true
宽度: 100
高度: 50
字号: 14
white-space: normal
word-break: break-all
overflow: hidden
```

### 方法2：手动设置换行

如果界面设置不生效，可以在控制台手动设置：

```javascript
// 1. 选中控件
const idx = Array.from(state.selected)[0];

// 2. 启用换行
state.items[idx].text_wrap = true;

// 3. 刷新显示
renderItems();

// 4. 保存（需要点击界面上的"保存布局"按钮）
```

### 方法3：检查服务器日志

查看 Flask 服务器的输出，确认：
1. 服务器已重启
2. 没有 Python 错误
3. PDF 预览请求成功

## 常见问题

### Q1: 状态章还是有白色背景？

**可能原因：**
- 服务器没有重启
- PNG 文件本身不是透明背景

**解决方法：**
1. 确认服务器已重启
2. 检查 PNG 文件：
   ```bash
   file /root/dingtalk-h5-app/static/stamps/client/agree.png
   ```
   应该显示 "RGBA"（包含透明通道）

3. 如果 PNG 文件没有透明通道，需要重新制作：
   - 使用 Photoshop、GIMP 等工具
   - 删除白色背景
   - 保存为 PNG 格式（保留透明通道）

### Q2: 部门控件还是不换行？

**可能原因：**
- 没有点击"更新选中项"
- 浏览器缓存
- text_wrap 配置没有保存

**解决方法：**
1. 强制刷新浏览器（Ctrl+Shift+R）
2. 选中控件
3. 勾选"文本自动换行"
4. **点击"更新选中项"** ⚠️
5. 在控制台检查 `state.items[idx].text_wrap` 是否为 `true`
6. 点击"保存布局"
7. 刷新页面重新加载

### Q3: 画布中换行了，但 PDF 中没有？

**可能原因：**
- 后端代码没有处理 text_wrap 参数

**解决方法：**
1. 确认服务器已重启
2. 检查后端代码：
   ```bash
   grep -n "text_wrap" /root/dingtalk-h5-app/app/routes/designer.py
   ```
   应该能找到相关代码

## 验证清单

在报告问题之前，请确认以下所有步骤：

- [ ] 已重启 Flask 服务器
- [ ] 已强制刷新浏览器（Ctrl+Shift+R）
- [ ] 已选中部门控件（边框变粉色）
- [ ] 已勾选"文本自动换行"
- [ ] 已点击"更新选中项"按钮
- [ ] 已点击"保存布局"按钮
- [ ] 已在控制台检查 text_wrap 为 true
- [ ] 已在控制台检查 white-space 为 normal
- [ ] 已预览 PDF 查看效果

## 如果还是不生效

请提供以下信息：

1. **浏览器控制台输出**
   - 运行上面的调试代码
   - 截图或复制输出

2. **服务器日志**
   - Flask 服务器的输出
   - 是否有错误信息

3. **配置截图**
   - 选中控件后的属性面板
   - 特别是"文本自动换行"复选框的状态

4. **PDF 截图**
   - 预览 PDF 的效果
   - 标注问题区域

---

**重要提醒：Python 代码修改后必须重启服务器！**
