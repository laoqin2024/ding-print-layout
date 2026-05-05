// 设计器调试脚本
// 在浏览器控制台（F12 -> Console）中粘贴并运行此脚本

console.log('=== 设计器调试信息 ===');

// 1. 检查是否有选中的控件
if (typeof state !== 'undefined' && state.selected && state.selected.size > 0) {
    const selectedIdx = Array.from(state.selected)[0];
    const item = state.items[selectedIdx];
    
    console.log('\n✅ 已选中控件');
    console.log('控件索引:', selectedIdx);
    console.log('控件类型:', item.renderer);
    console.log('控件宽度:', item.w);
    console.log('控件高度:', item.h);
    console.log('字号:', item.font_size);
    console.log('text_wrap:', item.text_wrap);
    console.log('完整配置:', item);
    
    // 2. 检查 DOM 元素的样式
    const domElement = document.querySelector(`[data-idx="${selectedIdx}"]`);
    if (domElement) {
        console.log('\n✅ 找到 DOM 元素');
        const styles = window.getComputedStyle(domElement);
        console.log('实际宽度:', styles.width);
        console.log('实际高度:', styles.height);
        console.log('white-space:', styles.whiteSpace);
        console.log('word-break:', styles.wordBreak);
        console.log('overflow:', styles.overflow);
        console.log('box-sizing:', styles.boxSizing);
        console.log('max-width:', styles.maxWidth);
    } else {
        console.log('\n❌ 未找到 DOM 元素');
    }
    
    // 3. 测试手动启用换行
    console.log('\n--- 测试命令 ---');
    console.log('手动启用换行：');
    console.log(`state.items[${selectedIdx}].text_wrap = true; renderItems();`);
    console.log('\n手动禁用换行：');
    console.log(`state.items[${selectedIdx}].text_wrap = false; renderItems();`);
    
} else {
    console.log('\n❌ 没有选中任何控件');
    console.log('请先在画布上点击选中一个控件');
}

// 4. 检查 propTextWrap 元素
if (typeof propTextWrap !== 'undefined' && propTextWrap) {
    console.log('\n✅ propTextWrap 元素存在');
    console.log('是否勾选:', propTextWrap.checked);
} else {
    console.log('\n❌ propTextWrap 元素不存在');
    console.log('可能是 JS 文件没有正确加载');
}

// 5. 检查 CSS 样式
const testDiv = document.createElement('div');
testDiv.className = 'designer-item';
document.body.appendChild(testDiv);
const testStyles = window.getComputedStyle(testDiv);
console.log('\n--- designer-item 基础样式 ---');
console.log('box-sizing:', testStyles.boxSizing);
console.log('max-width:', testStyles.maxWidth);
console.log('word-wrap:', testStyles.wordWrap);
document.body.removeChild(testDiv);

console.log('\n=== 调试信息结束 ===');
