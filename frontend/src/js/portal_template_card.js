// 模板卡片 HTML - 优化版本，避免文本截断
function templateCardHtml(template) {
  const iconMap = { 'p': '📄', 'l': '📋' };
  const icon = iconMap[template.orientation] || '📄';
  
  return `
    <div class="glass rounded-3xl p-6 shadow-md hover:shadow-xl transition-all duration-300 hover:scale-[1.02] cursor-pointer border border-slate-200/20 dark:border-slate-700/30"
         onclick="window.portalApp.loadInstances('${escapeHtml(template.p_code)}')">
      <div class="flex items-start gap-4">
        <div class="w-14 h-14 rounded-2xl bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center text-3xl flex-shrink-0">
          ${icon}
        </div>
        <div class="flex-1 min-w-0">
          <h3 class="font-black text-slate-800 dark:text-slate-200 text-base mb-2 leading-tight break-words">
            ${escapeHtml(template.name)}
          </h3>
          <p class="text-xs text-slate-600 dark:text-slate-400 font-mono break-all">
            ${escapeHtml(template.p_code)}
          </p>
        </div>
        <div class="text-blue-600 dark:text-blue-400 flex-shrink-0">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
          </svg>
        </div>
      </div>
    </div>
  `;
}
