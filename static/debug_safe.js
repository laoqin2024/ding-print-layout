// ========================================
// 设计器调试脚本 - 安全版本
// ========================================
// 在设计器页面（/designer/edit）的浏览器控制台中运行

(function() {
    console.log('=== 设计器调试脚本 ===');
    console.log('');
    
    // 检查是否在设计器页面
    if (typeof state === 'undefined') {
        console.error('❌ 错误：state 未定义');
        console.log('');
        console.log('请确认：');
        console.log('1. 你在设计器页面（URL 包含 /designer/edit）');
        console.log('2. 页面已完全加载');
        console.log('3. 已强制刷新浏览器（Ctrl+Shift+R）');
        console.log('');
        console.log('当前页面:', window.location.href);
        return;
    }
    
    // 检查是否选中了控件
    if (!state.selected || state.selected.size === 0) {
        console.warn('⚠️  警告：没有选中任何控件');
        console.log('');
        console.log('请先在画布上点击选中一个控件');
        console.log('');
        return;
    }
    
    // 获取选中的控件
    const idx = Array.from(state.selected)[0];
    const item = state.items[idx];
    
    if (!item) {
        console.error('❌ 错误：控件数据不存在');
        return;
    }
    
    console.log('✅ 控件信息：');
    console.log('  类型:', item.renderer || 'text');
    console.log('  宽度:', item.w);
    console.log('  高度:', item.h);
    console.log('  字号:', item.font_size);
    console.log('  text_wrap:', item.text_wrap);
    console.log('');
    
    // 检查 DOM 元素
    const el = document.querySelector(`[data-idx="${idx}"]`);
    if (!el) {
        console.error('❌ 错误：DOM 元素不存在');
        return;
    }
    
    const styles = window.getComputedStyle(el);
    console.log('✅ DOM 样式：');
    console.log('  white-space:', styles.whiteSpace);
    console.log('  word-break:', styles.wordBreak);
    console.log('  overflow:', styles.overflow);
    console.log('  text-overflow:', styles.textOverflow);
    console.log('');
    
    // 判断是否正确配置
    if (item.text_wrap === true) {
        if (styles.whiteSpace === 'normal') {
            console.log('✅ 换行配置正确！');
        } else {
            console.warn('⚠️  text_wrap 为 true，但 white-space 不是 normal');
            console.log('   可能需要刷新页面');
        }
    } else {
        console.log('ℹ️  text_wrap 未启用（当前为 false）');
        console.log('');
        console.log('启用换行的步骤：');
        console.log('1. 勾选"文本自动换行"复选框');
        console.log('2. 点击"更新选中项"按钮');
        console.log('3. 点击"保存布局"按钮');
    }
    
    console.log('');
    console.log('=== 调试完成 ===');
})();
