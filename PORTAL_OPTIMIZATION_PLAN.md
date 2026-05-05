================================================================================
🎯 打印门户优化方案 - 卡片式模板展示
================================================================================

## 📋 当前问题

### 现有逻辑
1. 用户登录打印门户
2. 后端加载所有已配置的模板（print_layouts.json）
3. **遍历每个模板，调用钉钉 API 拉取审批实例**
4. 返回所有审批实例的列表
5. 前端展示列表

### 问题
- ❌ 加载慢：需要调用多次钉钉 API
- ❌ 不必要：用户可能只需要查看某一个模板的审批
- ❌ 体验差：等待时间长，没有渐进式加载

---

## ✅ 优化方案

### 新逻辑（两步加载）

#### 第一步：展示模板卡片
1. 用户登录打印门户
2. 后端只返回已配置的模板列表（不拉取审批实例）
3. 前端展示模板卡片（类似管理后台的卡片布局）
4. 每个卡片显示：
   - 模板名称
   - 模板图标
   - 流程 code
   - "查看审批"按钮

#### 第二步：查看审批列表
1. 用户点击某个模板卡片
2. 前端调用新的 API：`/api/get_template_instances?p_code=xxx`
3. 后端只拉取该模板的审批实例
4. 前端展示该模板的审批列表（保持现有的列表样式）

---

## 🎨 UI 设计

### 首页（模板卡片）

```
┌─────────────────────────────────────┐
│  打印门户                            │
│  已配置 3 个打印模板                 │
└─────────────────────────────────────┘

┌──────────────┐  ┌──────────────┐
│ 📄 设计图纸   │  │ 📋 变更通知   │
│ 变更通知单    │  │ 单            │
│              │  │              │
│ [查看审批]    │  │ [查看审批]    │
└──────────────┘  └──────────────┘

┌──────────────┐
│ 📝 设计文件   │
│ 更改通知单    │
│              │
│ [查看审批]    │
└──────────────┘
```

### 审批列表页（点击卡片后）

```
┌─────────────────────────────────────┐
│  ← 返回模板列表                      │
│  设计图纸变更通知单                  │
└─────────────────────────────────────┘

[搜索框] [排序] [状态筛选]

┌─────────────────────────────────────┐
│ 审批编号: 202605050001               │
│ 标题: XXX项目设计变更                │
│ 状态: 已通过                         │
│ [预览PDF] [下载PDF]                  │
└─────────────────────────────────────┘
```

---

## 🔧 技术实现

### 后端修改

#### 1. 新增 API：获取模板列表
```python
@portal_bp.route("/api/get_templates")
def get_templates():
    """只返回已配置的模板列表，不拉取审批实例"""
    auth_code = request.args.get("code") or ""
    
    try:
        ding = _ding()
        userid = ding.get_userid_by_auth_code(auth_code)
    except DingTalkError:
        return jsonify({"errcode": 1, "errmsg": "身份校验失败"})
    
    cfg = _cfg()
    user_info = _load_user_info(userid, cfg)
    
    # Load designer layouts
    designer_layouts = {}
    try:
        layouts_path = cfg.base_dir / "data" / "print_layouts.json"
        if layouts_path.exists():
            data = json.loads(layouts_path.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                designer_layouts = data
    except Exception:
        pass
    
    # Build template list
    templates = []
    for p_code, layout in designer_layouts.items():
        # Check permission
        if not _check_process_permission(user_info, p_code, layout):
            continue
        
        templates.append({
            "p_code": p_code,
            "name": layout.get("name", p_code),
            "orientation": layout.get("orientation", "p"),
            "icon": "📄"  # 可以根据类型设置不同图标
        })
    
    return jsonify({
        "errcode": 0,
        "templates": templates,
        "user_info": {
            "userid": userid,
            "name": (user_info or {}).get("name", "")
        }
    })
```

#### 2. 新增 API：获取指定模板的审批实例
```python
@portal_bp.route("/api/get_template_instances")
def get_template_instances():
    """获取指定模板的审批实例"""
    auth_code = request.args.get("code") or ""
    p_code = request.args.get("p_code") or ""
    
    if not p_code:
        return jsonify({"errcode": 1, "errmsg": "缺少模板代码"})
    
    try:
        ding = _ding()
        userid = ding.get_userid_by_auth_code(auth_code)
    except DingTalkError:
        return jsonify({"errcode": 1, "errmsg": "身份校验失败"})
    
    cfg = _cfg()
    
    # Load template info
    designer_layouts = {}
    try:
        layouts_path = cfg.base_dir / "data" / "print_layouts.json"
        if layouts_path.exists():
            data = json.loads(layouts_path.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                designer_layouts = data
    except Exception:
        pass
    
    layout = designer_layouts.get(p_code)
    if not layout:
        return jsonify({"errcode": 1, "errmsg": "模板不存在"})
    
    template_name = layout.get("name", p_code)
    
    # Get instances for this template
    my_list = []
    try:
        ins_ids = ding.list_process_instance_ids(p_code, userid)
    except DingTalkError as e:
        return jsonify({"errcode": 1, "errmsg": f"获取审批列表失败: {str(e)}"})
    
    for ins_id in ins_ids:
        try:
            instance = ding.get_process_instance(ins_id)
        except DingTalkError:
            continue
        
        my_list.append({
            "id": ins_id,
            "approval_no": str(instance.get("business_id") or ins_id),
            "title": instance.get("title"),
            "create_time": instance.get("create_time"),
            "status": instance.get("status"),
            "result": instance.get("result"),
            "template_name": template_name,
            "p_code": p_code,
        })
    
    return jsonify({
        "errcode": 0,
        "list": my_list,
        "template_name": template_name,
        "p_code": p_code
    })
```

#### 3. 保留旧 API（向后兼容）
```python
@portal_bp.route("/api/get_my_list")
def get_my_list():
    """保留旧接口，向后兼容"""
    # 可以添加一个参数来切换新旧逻辑
    use_new_logic = request.args.get("new", "0") == "1"
    
    if use_new_logic:
        # 重定向到新接口
        return get_templates()
    else:
        # 保持原有逻辑
        # ... 原有代码 ...
```

---

### 前端修改

#### 1. 新增模板卡片页面
```html
<!-- templates/portal_templates.html -->
<div id="templates-view" class="grid grid-cols-1 md:grid-cols-2 gap-5">
  <!-- 模板卡片将通过 JS 动态生成 -->
</div>
```

#### 2. 修改 portal.js

```javascript
// 状态管理
const state = {
  view: 'templates', // 'templates' | 'instances'
  currentTemplate: null,
  templates: [],
  instances: []
};

// 初始化：加载模板列表
async function init() {
  try {
    const code = getAuthCode();
    const res = await fetch(`/api/get_templates?code=${code}`);
    const data = await res.json();
    
    if (data.errcode === 0) {
      state.templates = data.templates;
      renderTemplates();
    } else {
      showError(data.errmsg);
    }
  } catch (err) {
    showError('加载模板失败');
  }
}

// 渲染模板卡片
function renderTemplates() {
  const container = document.getElementById('templates-view');
  container.innerHTML = state.templates.map(tpl => `
    <div class="glass rounded-2xl p-5 shadow-md hover:shadow-xl transition-all duration-300 hover:scale-[1.02] cursor-pointer"
         onclick="loadTemplateInstances('${tpl.p_code}')">
      <div class="flex items-start gap-4">
        <div class="w-12 h-12 rounded-xl bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center text-2xl">
          ${tpl.icon}
        </div>
        <div class="flex-1">
          <h3 class="font-black text-slate-800 dark:text-slate-200 text-base mb-1">
            ${tpl.name}
          </h3>
          <p class="text-xs text-slate-600 dark:text-slate-400 font-mono">
            ${tpl.p_code}
          </p>
        </div>
        <div class="text-blue-600 dark:text-blue-400">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
          </svg>
        </div>
      </div>
    </div>
  `).join('');
}

// 加载指定模板的审批实例
async function loadTemplateInstances(pCode) {
  state.view = 'instances';
  state.currentTemplate = pCode;
  
  showLoading();
  
  try {
    const code = getAuthCode();
    const res = await fetch(`/api/get_template_instances?code=${code}&p_code=${pCode}`);
    const data = await res.json();
    
    if (data.errcode === 0) {
      state.instances = data.list;
      renderInstances();
    } else {
      showError(data.errmsg);
    }
  } catch (err) {
    showError('加载审批列表失败');
  }
}

// 返回模板列表
function backToTemplates() {
  state.view = 'templates';
  state.currentTemplate = null;
  renderTemplates();
}
```

---

## 📊 性能对比

### 优化前
- 首屏加载时间: **5-10秒**（取决于模板数量和审批数量）
- API 调用次数: **N+1**（N 个模板 + 1 次认证）
- 用户等待: **长时间白屏**

### 优化后
- 首屏加载时间: **0.5-1秒**（只加载模板列表）
- API 调用次数: **1+M**（1 次模板列表 + M 次用户点击）
- 用户等待: **渐进式加载，体验更好**

---

## 🎯 实施步骤

1. ✅ 后端：新增 `/api/get_templates` 接口
2. ✅ 后端：新增 `/api/get_template_instances` 接口
3. ✅ 前端：创建模板卡片视图
4. ✅ 前端：修改路由逻辑（模板列表 ↔ 审批列表）
5. ✅ 前端：添加返回按钮
6. ✅ 测试：验证新旧逻辑都能正常工作
7. ✅ 部署：灰度发布，逐步切换到新逻辑

---

## 🔄 向后兼容

- 保留旧的 `/api/get_my_list` 接口
- 通过参数控制使用新旧逻辑
- 前端可以通过配置切换

---

## 📝 后续优化

1. **缓存优化**: 缓存模板列表，减少重复加载
2. **预加载**: 鼠标悬停时预加载审批列表
3. **统计信息**: 在模板卡片上显示审批数量
4. **搜索功能**: 在模板列表中搜索
5. **收藏功能**: 收藏常用模板

================================================================================
