(function () {
  const boot = window.DESIGNER_BOOT || {};
  const stage = document.getElementById("designer-stage");
  const canvas = document.getElementById("designer-canvas");
  const canvasScrollWrap = document.getElementById("canvas-scroll-wrap");
  const bg = document.getElementById("designer-bg");
  const marginGuide = document.getElementById("margin-guide");
  const grid = document.getElementById("designer-grid");
  const guideH = document.getElementById("guide-h");
  const guideV = document.getElementById("guide-v");
  const marquee = document.getElementById("marquee");
  const fieldList = document.getElementById("field-list");
  const systemFieldList = document.getElementById("system-field-list");
  const toggleSystemFieldsBtn = document.getElementById("toggle-system-fields");
  const toggleFormFieldsBtn = document.getElementById("toggle-form-fields");
  const toggleSystemIcon = document.getElementById("toggle-system-icon");
  const toggleFormIcon = document.getElementById("toggle-form-icon");
  const nodeList = document.getElementById("node-list");
  const saveNodeNamesBtn = document.getElementById("save-node-names-btn");
  const processCodeEl = document.getElementById("process-code");
  const processGroupEl = document.getElementById("process-group");
  const processPickEl = document.getElementById("process-pick");
  const processListMeta = document.getElementById("process-list-meta");
  const refreshProcessesBtn = document.getElementById("refresh-processes-btn");
  const layoutNameEl = document.getElementById("layout-name");
  const useTemplateEl = document.getElementById("use-template");
  const basePdfEl = document.getElementById("base-pdf");
  const paperOrientEl = document.getElementById("paper-orient");
  const instanceIdEl = document.getElementById("instance-id");
  const lockCurrentInstanceEl = document.getElementById("lock-current-instance");
  const coverSourceModeEl = document.getElementById("cover-source-mode");
  const coverModeEl = document.getElementById("cover-mode");
  const coverOffsetXEl = document.getElementById("cover-offset-x");
  const coverOffsetYEl = document.getElementById("cover-offset-y");
  const fieldSearchEl = document.getElementById("field-search");
  const qrStatusBadge = document.getElementById("qr-status-badge");
  const loadSchemaBtn = document.getElementById("load-schema-btn");
  const addTextBtn = document.getElementById("add-text-btn");
  const previewBtn = document.getElementById("preview-btn");
  const saveBtn = document.getElementById("save-btn");
  const undoBtn = document.getElementById("undo-btn");
  const redoBtn = document.getElementById("redo-btn");
  const zoomOutBtn = document.getElementById("zoom-out");
  const zoomInBtn = document.getElementById("zoom-in");
  const zoomResetBtn = document.getElementById("zoom-reset");
  const zoomLabel = document.getElementById("zoom-label");
  const canvasTitle = document.getElementById("canvas-title");
  const gridSizeEl = document.getElementById("grid-size");
  const snapToggle = document.getElementById("snap-toggle");
  const propX = document.getElementById("prop-x");
  const propY = document.getElementById("prop-y");
  const propW = document.getElementById("prop-w");
  const propH = document.getElementById("prop-h");
  const propLabel = document.getElementById("prop-label");
  const propBindField = document.getElementById("prop-bind-field");
  const propFieldId = document.getElementById("prop-field-id");
  const propFieldName = document.getElementById("prop-field-name");
  const propFieldType = document.getElementById("prop-field-type");
  const propFontFamily = document.getElementById("prop-font-family");
  const propFontSize = document.getElementById("prop-font-size");
  const propFontColor = document.getElementById("prop-font-color");
  const propFontWeight = document.getElementById("prop-font-weight");
  const propTextAlign = document.getElementById("prop-text-align");
  const propVerticalAlign = document.getElementById("prop-vertical-align");
  const propFontStyle = document.getElementById("prop-font-style");
  const propEmptyPolicy = document.getElementById("prop-empty-policy");
  const propLineHeight = document.getElementById("prop-line-height");
  const propLetterSpacing = document.getElementById("prop-letter-spacing");
  const propOverflowMarker = document.getElementById("prop-overflow-marker");
  const propTextWrap = document.getElementById("prop-text-wrap");
  const propLineDirection = document.getElementById("prop-line-direction");
  const propLineStyle = document.getElementById("prop-line-style");
  const propStrokeWidth = document.getElementById("prop-stroke-width");
  const propRectRadius = document.getElementById("prop-rect-radius");
  const propStrokeColor = document.getElementById("prop-stroke-color");
  const propImageUrl = document.getElementById("prop-image-url");
  const propImageFit = document.getElementById("prop-image-fit");
  const propImageUpload = document.getElementById("prop-image-upload");
  const propStampStatus = document.getElementById("prop-stamp-status");
  const propStampPack = document.getElementById("prop-stamp-pack");
  const propStampFetchUrl = document.getElementById("prop-stamp-fetch-url");
  const fetchStampBtn = document.getElementById("fetch-stamp-btn");
  const stampConfig = document.getElementById("stamp-config");
  const imageConfig = document.getElementById("image-config");
  const qrcodeConfig = document.getElementById("qrcode-config");
  const slotConfig = document.getElementById("slot-config");
  const propSigFillMode = document.getElementById("prop-sig-fill-mode");
  const propSlotIndex = document.getElementById("prop-slot-index");
  const propLocalUserName = document.getElementById("prop-local-user-name");
  const propDeptSource = document.getElementById("prop-dept-source");
  const propQrSource = document.getElementById("prop-qr-source");
  const propQrValue = document.getElementById("prop-qr-value");
  const propRenderer = document.getElementById("prop-renderer");
  const updatePropBtn = document.getElementById("update-prop-btn");
  const deleteItemBtn = document.getElementById("delete-item-btn");
  const selHint = document.getElementById("sel-hint");
  const propHelp = document.getElementById("prop-help");
  const attachmentBgEnabled = document.getElementById("attachment-bg-enabled");
  const attachmentBgFields = document.getElementById("attachment-bg-fields");
  const attachmentBgField = document.getElementById("attachment-bg-field");
  const attachmentBgIndex = document.getElementById("attachment-bg-index");
  const attachmentBgPage = document.getElementById("attachment-bg-page");
  const attachmentBgApplyMode = document.getElementById("attachment-bg-apply-mode");

  const state = {
    items: Array.isArray((boot.layout || {}).items) ? (boot.layout || {}).items.slice() : [],
    selected: new Set(),
    dragging: null,
    resizing: null,
    marquee: null,
    zoom: 1,
    gridSize: 10,
    snap: true,
    guides: { x: null, y: null },
    history: [],
    future: [],
    historyArmed: false,
    fields: [],
    systemFields: [],
    collapsed: { system: false, form: false },
    nodeNameMap: {},
    orient: (boot.layout || {}).orientation === "p" ? "p" : "l",
    orientLockedByUser: !!((boot.layout || {}).orientation),
    coverSourceMode: String((boot.layout || {}).cover_source_mode || "base"),
    coverMode: String((boot.layout || {}).cover_mode || "strict"),
    coverOffsetX: Number((boot.layout || {}).cover_offset_x || 0),
    coverOffsetY: Number((boot.layout || {}).cover_offset_y || 0),
    useTemplate: (boot.layout || {}).use_template !== false,
    processGroups: [],
    clipboard: null,
    attachmentBg: {
      enabled: !!((boot.layout || {}).attachment_background_config || {}).enabled,
      fieldId: String(((boot.layout || {}).attachment_background_config || {}).field_id || ""),
      attachmentIndex: Number(((boot.layout || {}).attachment_background_config || {}).attachment_index || 0),
      pageIndex: Number(((boot.layout || {}).attachment_background_config || {}).page_index || 0),
      applyMode: String(((boot.layout || {}).attachment_background_config || {}).apply_mode || "print_only"),
    },
  };

  const LOCK_INSTANCE_KEY = "designer_edit_lock_instance";
  try {
    if (lockCurrentInstanceEl && sessionStorage.getItem(LOCK_INSTANCE_KEY) === "1") {
      lockCurrentInstanceEl.checked = true;
    }
  } catch (e) {
    // ignore
  }
  lockCurrentInstanceEl?.addEventListener("change", () => {
    try {
      sessionStorage.setItem(LOCK_INSTANCE_KEY, lockCurrentInstanceEl.checked ? "1" : "0");
    } catch (err) {
      // ignore
    }
  });

  function fillProcessPickForGroup(gname) {
    if (!processPickEl) return;
    processPickEl.innerHTML = '<option value="">-- 再选具体流程 --</option>';
    const g = state.processGroups.find((x) => String(x.name || "") === String(gname || ""));
    if (!g || !Array.isArray(g.processes)) return;
    g.processes.forEach((p) => {
      const opt = document.createElement("option");
      opt.value = String(p.process_code || "");
      opt.textContent = `${p.name || p.process_code} · ${p.process_code}`;
      processPickEl.appendChild(opt);
    });
  }

  function syncPickersFromProcessCode() {
    const want = String(processCodeEl?.value || "").trim();
    if (!want || !state.processGroups.length) return;
    for (let i = 0; i < state.processGroups.length; i += 1) {
      const g = state.processGroups[i];
      const hit = (g.processes || []).find((p) => String(p.process_code || "").trim() === want);
      if (hit) {
        if (processGroupEl) processGroupEl.value = String(g.name || "");
        fillProcessPickForGroup(g.name);
        if (processPickEl) processPickEl.value = want;
        return;
      }
    }
  }

  async function loadProcessGroups() {
    if (processListMeta) processListMeta.textContent = "正在从钉钉拉取流程列表…";
    try {
      const res = await fetch("/designer/api/processes_grouped?scope=corp");
      const data = await res.json();
      if (!data.ok) {
        if (processListMeta) processListMeta.textContent = data.msg || "加载失败";
        state.processGroups = [];
        return;
      }
      state.processGroups = Array.isArray(data.groups) ? data.groups : [];
      if (processGroupEl) {
        processGroupEl.innerHTML = '<option value="">-- 先选流程分组 --</option>';
        state.processGroups.forEach((g) => {
          const opt = document.createElement("option");
          opt.value = String(g.name || "");
          const n = (g.processes || []).length;
          opt.textContent = `${g.name || "未命名"}（${n}）`;
          processGroupEl.appendChild(opt);
        });
      }
      if (processPickEl) processPickEl.innerHTML = '<option value="">-- 再选具体流程 --</option>';
      let meta = `共 ${Number(data.total || 0)} 个流程（范围：${data.scope === "user" ? "当前用户" : "企业全部"}）`;
      if (data.group_hint) {
        meta += ` · ${data.group_hint}`;
      }
      if (data.capped) {
        meta += "；已达分页上限，若仍不全可联系调大 max_pages";
      }
      if (processListMeta) processListMeta.textContent = meta;
      syncPickersFromProcessCode();
    } catch (e) {
      if (processListMeta) processListMeta.textContent = "网络异常，无法加载流程列表";
      state.processGroups = [];
    }
  }

  // ========================================================================
  // 控件参数配置映射
  // ========================================================================
  
  // 定义每个控件类型支持的参数
  const CONTROL_PARAMS = {
    text: {
      basic: ['x', 'y', 'w', 'h', 'label'],
      binding: ['field_id', 'field_name', 'field_type'],
      font: ['font_family', 'font_size', 'font_color', 'font_weight', 'font_style'],
      layout: ['text_align', 'vertical_align', 'line_height', 'letter_spacing'],
      behavior: ['empty_policy', 'overflow_marker', 'text_wrap']
    },
    date: {
      basic: ['x', 'y', 'w', 'h', 'label'],
      binding: ['field_id', 'field_name', 'field_type'],
      font: ['font_family', 'font_size', 'font_color', 'font_weight', 'font_style'],
      layout: ['text_align', 'vertical_align', 'line_height'],
      behavior: ['empty_policy']
    },
    label: {
      basic: ['x', 'y', 'w', 'h', 'label'],
      font: ['font_family', 'font_size', 'font_color', 'font_weight', 'font_style'],
      layout: ['text_align', 'vertical_align', 'line_height', 'letter_spacing']
    },
    signature: {
      basic: ['x', 'y', 'w', 'h'],
      binding: ['field_id', 'field_name', 'field_type'],
      signature: ['sig_fill_mode', 'slot_index', 'local_user_name']
    },
    dept: {
      basic: ['x', 'y', 'w', 'h'],
      font: ['font_family', 'font_size', 'font_color', 'font_weight', 'font_style'],
      layout: ['text_align', 'vertical_align', 'line_height'],
      dept: ['dept_source', 'slot_index']
    },
    qrcode: {
      basic: ['x', 'y', 'w', 'h'],
      qrcode: ['qr_source', 'qr_value']
    },
    status_stamp: {
      basic: ['x', 'y', 'w', 'h'],
      stamp: ['stamp_status', 'stamp_pack', 'stamp_fetch_url']
    },
    image: {
      basic: ['x', 'y', 'w', 'h'],
      image: ['image_url', 'image_fit', 'image_upload']
    },
    rect: {
      basic: ['x', 'y', 'w', 'h'],
      shape: ['stroke_width', 'stroke_color', 'rect_radius']
    },
    line: {
      basic: ['x', 'y', 'w', 'h'],
      line: ['line_direction', 'line_style', 'stroke_width', 'stroke_color']
    },
    flow_result: {
      basic: ['x', 'y', 'w', 'h'],
      font: ['font_family', 'font_size', 'font_weight', 'font_style'],
      layout: ['text_align', 'vertical_align', 'line_height', 'letter_spacing'],
      behavior: ['overflow_marker', 'text_wrap']
    }
  };

  // 参数到 DOM 元素 ID 的映射
  const PARAM_TO_ELEMENT = {
    x: 'prop-x',
    y: 'prop-y',
    w: 'prop-w',
    h: 'prop-h',
    label: 'prop-label',
    field_id: 'prop-field-id',
    field_name: 'prop-field-name',
    field_type: 'prop-field-type',
    font_family: 'prop-font-family',
    font_size: 'prop-font-size',
    font_color: 'prop-font-color',
    font_weight: 'prop-font-weight',
    font_style: 'prop-font-style',
    text_align: 'prop-text-align',
    vertical_align: 'prop-vertical-align',
    line_height: 'prop-line-height',
    letter_spacing: 'prop-letter-spacing',
    empty_policy: 'prop-empty-policy',
    overflow_marker: 'prop-overflow-marker',
    text_wrap: 'prop-text-wrap',
    stroke_width: 'prop-stroke-width',
    stroke_color: 'prop-stroke-color',
    rect_radius: 'prop-rect-radius',
    line_direction: 'prop-line-direction',
    line_style: 'prop-line-style',
    image_url: 'prop-image-url',
    image_fit: 'prop-image-fit',
    image_upload: 'prop-image-upload',
    stamp_status: 'prop-stamp-status',
    stamp_pack: 'prop-stamp-pack',
    stamp_fetch_url: 'prop-stamp-fetch-url',
    sig_fill_mode: 'prop-sig-fill-mode',
    slot_index: 'prop-slot-index',
    local_user_name: 'prop-local-user-name',
    dept_source: 'prop-dept-source',
    qr_source: 'prop-qr-source',
    qr_value: 'prop-qr-value'
  };

  // 获取控件支持的所有参数
  function getSupportedParams(renderer) {
    const config = CONTROL_PARAMS[renderer] || CONTROL_PARAMS.text;
    const params = new Set();
    Object.values(config).forEach(group => {
      group.forEach(param => params.add(param));
    });
    return params;
  }

  // 获取多个控件的公共参数
  function getCommonParams(renderers) {
    if (renderers.length === 0) return new Set();
    if (renderers.length === 1) return getSupportedParams(renderers[0]);
    
    // 不同类型控件：只有基础参数是公共的
    const uniqueRenderers = [...new Set(renderers)];
    if (uniqueRenderers.length > 1) {
      return new Set(['x', 'y', 'w', 'h']);
    }
    
    // 同类型控件：所有参数都是公共的
    return getSupportedParams(renderers[0]);
  }

  // ========================================================================
  // 参数帮助文本
  // ========================================================================
  
  const PARAM_HELP_BY_RENDERER = {
    text: [
      "位置尺寸：X/Y/W/H 控制文本框位置与范围。",
      "字段绑定：field_id / field_name / field_type 指定取值来源；不绑定则使用 label 文本。",
      "文字样式：font_family / font_size / font_color / font_weight / font_style / text_align。",
      "排版：line_height 行高、letter_spacing 字间距、overflow_marker 溢出省略号。",
      "空值策略：empty_policy 可设为 show_placeholder / hide / dim。",
    ],
    date: [
      "date 本质是文本渲染，优先显示绑定字段值。",
      "可使用文本同款样式参数（字号、颜色、对齐、行高等）。",
      "建议绑定日期字段并设置合适宽度避免截断。",
    ],
    label: [
      "label 用于静态说明文字，默认显示 label 参数。",
      "可绑定字段实现动态标签（如系统字段）。",
      "支持全部文本样式参数。",
    ],
    signature: [
      "签名框用于渲染手写签名图，推荐绑定具体 SignatureField 组件ID。",
      "field_id 指向钉钉签名组件ID；绑定后优先按组件ID精准取签名，不再按完成时间错配。",
      "若签名组件值只有图片URL，可填写 local_user_name 作为该组件对应的本地人员。",
      "sig_fill_mode=auto_sequence 会先按 field_id 自动填充；未绑定 field_id 时才按 slot_index 顺序兜底。",
      "X/Y/W/H 控制签名图放置区域；图片按比例适配。",
    ],
    dept: [
      "部门控件建议绑定与对应签名框相同的 SignatureField 组件ID。",
      "渲染时会通过该签名组件识别人员；如果组件值只有图片URL，则使用 local_user_name 绑定本地人员。",
      "field_id 优先；未绑定时才用 slot_index 跟随第几个签名槽位。",
      "部门来源固定为 local_user_by_signature，不再在线查询钉钉部门。",
    ],
    rect: [
      "边框用于画矩形结构，不参与字段取值。",
      "stroke_width 控制边框粗细；stroke_color 控制边框颜色。",
      "rect_radius 控制圆角半径（0 为直角）。",
    ],
    line: [
      "线条用于分隔布局，不参与字段取值。",
      "line_direction 控制横线/竖线。",
      "line_style 控制实线/虚线，stroke_width 控制线宽，stroke_color 控制颜色。",
    ],
    image: [
      "图片控件用于放置 logo/印章等静态图像。",
      "image_url 支持 http(s) 或 data:image（本地上传后自动填充）。",
      "image_fit=contain 保持完整，cover 会铺满区域并可能裁切。",
    ],
    status_stamp: [
      "状态章控件用于显示“已通过/已拒绝”等印章图。",
      "stamp_status=auto 时按流程结果自动选择状态章。",
      "可通过“拉取并保存本地状态章”把钉钉图标URL保存为本地资源。",
    ],
    flow_result: [
      "流程结果控件自动根据 sys.status / sys.result 生成状态文字。",
      "显示值：审批通过 / 审批拒绝 / 已撤销 / 等待{当前审批人}处理。",
      "字体颜色自动跟随状态：通过=绿色、等待=橙色（其余状态自动配色）。",
    ],
    qrcode: [
      "二维码控件用于生成可扫码内容（URL或文本）。",
      "qr_source=field 时使用绑定字段值；qr_source=custom 时使用 qr_value。",
      "推荐绑定 sys.preferred_qr_url（优先 aflow/qr 稳定链接）。",
      "建议给控件较大尺寸（如 60x60 以上）保证扫码成功率。",
    ],
  };

  function renderPropHelp(renderer) {
    if (!propHelp) return;
    const key = String(renderer || "text").toLowerCase();
    const lines = PARAM_HELP_BY_RENDERER[key] || PARAM_HELP_BY_RENDERER.text;
    propHelp.innerHTML = lines.map((x) => `<div>· ${x}</div>`).join("");
  }

  /**
   * 根据控件类型显示/隐藏参数
   */
  function updateParamVisibility(renderer) {
    const supportedParams = getSupportedParams(renderer);
    
    console.log('[updateParamVisibility] renderer:', renderer);
    console.log('[updateParamVisibility] supportedParams:', Array.from(supportedParams));
    
    // 遍历所有参数元素，显示/隐藏对应的行
    Object.entries(PARAM_TO_ELEMENT).forEach(([param, elementId]) => {
      const element = document.getElementById(elementId);
      if (!element) {
        console.warn('[updateParamVisibility] 元素不存在:', elementId);
        return;
      }
      
      // 找到参数所在的行（父元素或祖父元素）
      let row = element.closest('.glass');
      if (!row) {
        console.warn('[updateParamVisibility] 找不到父容器:', elementId);
        return;
      }
      
      // 显示或隐藏
      if (supportedParams.has(param)) {
        row.classList.remove('hidden');
        console.log('[updateParamVisibility] 显示:', param, elementId);
      } else {
        row.classList.add('hidden');
        console.log('[updateParamVisibility] 隐藏:', param, elementId);
      }
    });
    
    // 特殊配置区域的显示/隐藏
    if (stampConfig) stampConfig.classList.toggle('hidden', renderer !== 'status_stamp');
    if (imageConfig) imageConfig.classList.toggle('hidden', renderer !== 'image');
    if (qrcodeConfig) qrcodeConfig.classList.toggle('hidden', renderer !== 'qrcode');
    if (slotConfig) slotConfig.classList.toggle('hidden', !(renderer === 'signature' || renderer === 'dept'));
    
    console.log('[updateParamVisibility] 完成');
  }

  function cloneItems(items) {
    return JSON.parse(JSON.stringify(items || []));
  }

  function armHistory() {
    state.historyArmed = true;
  }

  function pushHistory(reason) {
    if (!state.historyArmed) return;
    state.historyArmed = false;
    state.history.push(cloneItems(state.items));
    if (state.history.length > 100) state.history.shift();
    state.future = [];
    // eslint-disable-next-line no-unused-vars
    const _ = reason;
    refreshUndoRedoUI();
  }

  function undo() {
    if (!state.history.length) return;
    state.future.push(cloneItems(state.items));
    state.items = state.history.pop();
    state.selected.clear();
    renderItems();
    refreshUndoRedoUI();
  }

  function redo() {
    if (!state.future.length) return;
    state.history.push(cloneItems(state.items));
    state.items = state.future.pop();
    state.selected.clear();
    renderItems();
    refreshUndoRedoUI();
  }

  function refreshUndoRedoUI() {
    if (undoBtn) undoBtn.disabled = state.history.length === 0;
    if (redoBtn) redoBtn.disabled = state.future.length === 0;
  }

  function itemStyle(it) {
    return `left:${it.x}px;top:${it.y}px;width:${it.w}px;height:${it.h}px;`;
  }

  function applyZoom() {
    if (!stage) return;
    stage.style.transform = `scale(${state.zoom})`;
    if (zoomLabel) zoomLabel.textContent = `${Math.round(state.zoom * 100)}%`;
  }

  function applyCanvasSize() {
    const orient = state.orient || "l";
    const w = orient === "p" ? 595 : 842;
    const h = orient === "p" ? 842 : 595;
    if (canvasTitle) {
      canvasTitle.textContent = orient === "p" ? "画布（A4 纵向）" : "画布（A4 横向）";
    }
    if (stage) {
      stage.style.width = `${w}px`;
      stage.style.height = `${h}px`;
    }
    if (canvas) {
      canvas.style.width = `${w}px`;
      canvas.style.height = `${h}px`;
    }
    updateMarginGuide();
  }

  function updateMarginGuide() {
    if (!marginGuide || !canvas) return;
    // Custom print-safe margins (cm -> pt at 72dpi):
    // left/right: 1.2cm, bottom: 2cm, top: keep 2.54cm.
    const cm2pt = 72 / 2.54;
    const insetLeft = 1.2 * cm2pt;
    const insetRight = 1.2 * cm2pt;
    const insetBottom = 2.0 * cm2pt;
    const insetTop = 2.54 * cm2pt;
    const w = Number(canvas.style.width.replace("px", "") || (state.orient === "p" ? 595 : 842));
    const h = Number(canvas.style.height.replace("px", "") || (state.orient === "p" ? 842 : 595));
    marginGuide.style.left = `${insetLeft}px`;
    marginGuide.style.top = `${insetTop}px`;
    marginGuide.style.width = `${Math.max(0, w - insetLeft - insetRight)}px`;
    marginGuide.style.height = `${Math.max(0, h - insetTop - insetBottom)}px`;
    marginGuide.classList.toggle("hidden", !!state.useTemplate);
  }

  function centerCanvasInViewport() {
    if (!canvasScrollWrap) return;
    const maxLeft = Math.max(0, canvasScrollWrap.scrollWidth - canvasScrollWrap.clientWidth);
    const maxTop = Math.max(0, canvasScrollWrap.scrollHeight - canvasScrollWrap.clientHeight);
    canvasScrollWrap.scrollLeft = Math.round(maxLeft / 2);
    canvasScrollWrap.scrollTop = Math.round(maxTop / 2);
  }

  async function autoDetectOrientation() {
    if (state.orientLockedByUser) return;
    const basePdf = (basePdfEl?.value || "").trim();
    if (!basePdf) return;
    try {
      const res = await fetch(`/designer/api/pdf_meta?base_pdf=${encodeURIComponent(basePdf)}`);
      const data = await res.json();
      if (!data.ok) return;
      const orient = String((((data || {}).first_page || {}).orient) || "").toLowerCase();
      if (orient !== "l" && orient !== "p") return;
      state.orient = orient;
      if (paperOrientEl) paperOrientEl.value = orient;
      applyCanvasSize();
      refreshBgPreview();
    } catch (err) {
      // keep current orientation when detection fails
    }
  }

  function applyGrid() {
    const sz = Number(state.gridSize || 10);
    if (grid) grid.style.backgroundSize = `${sz}px ${sz}px`;
  }

  function currentOrient() {
    return String(paperOrientEl?.value || state.orient || "l") === "p" ? "p" : "l";
  }

  function syncCoverUiState() {
    if (coverSourceModeEl) coverSourceModeEl.value = state.coverSourceMode || "base";
    if (coverModeEl) coverModeEl.value = state.coverMode || "strict";
    if (coverOffsetXEl) coverOffsetXEl.value = Number(state.coverOffsetX || 0);
    if (coverOffsetYEl) coverOffsetYEl.value = Number(state.coverOffsetY || 0);
    const enableOffset = (state.coverMode || "strict") === "fit_offset";
    if (coverOffsetXEl) coverOffsetXEl.disabled = !enableOffset;
    if (coverOffsetYEl) coverOffsetYEl.disabled = !enableOffset;
    if (useTemplateEl) useTemplateEl.checked = !!state.useTemplate;
    const disableTemplateRelated = !state.useTemplate;
    if (basePdfEl) basePdfEl.disabled = disableTemplateRelated;
    if (coverSourceModeEl) coverSourceModeEl.disabled = disableTemplateRelated;
    if (coverModeEl) coverModeEl.disabled = disableTemplateRelated;
    if (coverOffsetXEl) coverOffsetXEl.disabled = disableTemplateRelated || !enableOffset;
    if (coverOffsetYEl) coverOffsetYEl.disabled = disableTemplateRelated || !enableOffset;
    updateMarginGuide();
  }

  // Centralized binding rules per renderer (easy extension for future controls).
  const BINDING_RULES = {
    text: { bindable: true, allowFieldTypes: [] },
    date: { bindable: true, allowFieldTypes: [] },
    label: { bindable: true, allowFieldTypes: [] },
    signature: { bindable: true, allowFieldTypes: ["SignatureField"] },
    dept: { bindable: true, allowFieldTypes: ["SignatureField"] },
    rect: { bindable: false, allowFieldTypes: [] },
    line: { bindable: false, allowFieldTypes: [] },
    image: { bindable: false, allowFieldTypes: [] },
    status_stamp: { bindable: false, allowFieldTypes: [] },
    flow_result: { bindable: false, allowFieldTypes: [] },
    qrcode: { bindable: true, allowFieldTypes: [] },
  };

  function bindingRule(renderer) {
    const key = String(renderer || "").toLowerCase();
    return BINDING_RULES[key] || { bindable: true, allowFieldTypes: [] };
  }

  function isFieldAllowedForRenderer(renderer, fieldType) {
    const rule = bindingRule(renderer);
    if (!rule.bindable) return false;
    const allowed = Array.isArray(rule.allowFieldTypes) ? rule.allowFieldTypes : [];
    if (!allowed.length) return true;
    return allowed.includes(String(fieldType || ""));
  }

  function sanitizeBindingByRenderer(it) {
    if (!it) return;
    if (!isFieldAllowedForRenderer(it.renderer || "text", it.field_type || "")) {
      it.field_id = "";
      it.field_name = "";
      it.field_type = "";
    }
  }

  function clientToCanvas(clientX, clientY) {
    const rect = canvas.getBoundingClientRect();
    const x = (clientX - rect.left) / state.zoom;
    const y = (clientY - rect.top) / state.zoom;
    return { x, y };
  }

  function snap(n) {
    if (!state.snap) return n;
    const g = Number(state.gridSize || 10);
    return Math.round(n / g) * g;
  }

  function rectOf(it) {
    return { x: Number(it.x || 0), y: Number(it.y || 0), w: Number(it.w || 0), h: Number(it.h || 0) };
  }

  const FIXED_STATUS_STAMP_ID = "__fixed_status_stamp_portrait";

  function ensureFixedStatusStamp() {
    const isPortrait = (state.orient || "l") === "p";
    const idx = state.items.findIndex((it) => String(it.id || "") === FIXED_STATUS_STAMP_ID);
    if (!isPortrait) {
      if (idx >= 0) state.items.splice(idx, 1);
      return;
    }
    const fixed = {
      id: FIXED_STATUS_STAMP_ID,
      locked: true,
      renderer: "status_stamp",
      label: "状态章",
      page: 0,
      x: 450,
      y: 80,
      w: 70,
      h: 70,
      stamp_status: "auto",
      stamp_pack: "client",
    };
    if (idx >= 0) {
      state.items[idx] = { ...state.items[idx], ...fixed };
    } else {
      state.items.push(fixed);
    }
  }

  function intersects(a, b) {
    return !(a.x + a.w < b.x || b.x + b.w < a.x || a.y + a.h < b.y || b.y + b.h < a.y);
  }

  function updateGuidesFor(idx, nx, ny) {
    const tol = 4;
    const it = state.items[idx];
    const w = Number(it.w || 0);
    const h = Number(it.h || 0);
    const edges = { left: nx, right: nx + w, top: ny, bottom: ny + h, cx: nx + w / 2, cy: ny + h / 2 };
    let gx = null;
    let gy = null;
    for (let j = 0; j < state.items.length; j++) {
      if (j === idx) continue;
      const r = rectOf(state.items[j]);
      const e = { left: r.x, right: r.x + r.w, top: r.y, bottom: r.y + r.h, cx: r.x + r.w / 2, cy: r.y + r.h / 2 };
      for (const key of ["left", "right", "cx"]) {
        if (Math.abs(edges[key] - e[key]) <= tol) gx = e[key] - (key === "right" ? w : key === "cx" ? w / 2 : 0);
      }
      for (const key of ["top", "bottom", "cy"]) {
        if (Math.abs(edges[key] - e[key]) <= tol) gy = e[key] - (key === "bottom" ? h : key === "cy" ? h / 2 : 0);
      }
    }
    state.guides.x = gx;
    state.guides.y = gy;
    if (guideV) {
      if (gx === null) guideV.classList.add("hidden");
      else {
        guideV.classList.remove("hidden");
        guideV.style.left = `${(gx + (w / 2))}px`;
      }
    }
    if (guideH) {
      if (gy === null) guideH.classList.add("hidden");
      else {
        guideH.classList.remove("hidden");
        guideH.style.top = `${(gy + (h / 2))}px`;
      }
    }
  }

  function renderItems() {
    canvas.querySelectorAll(".designer-item").forEach((x) => x.remove());
    state.items.forEach((it, idx) => {
      const el = document.createElement("div");
      const active = state.selected.has(idx);
      el.className = "designer-item" + (active ? (state.selected.size === 1 ? " active" : " multi") : "");
      const r = (it.renderer || "text").toLowerCase();
      if (r) el.classList.add(r);
      el.style = itemStyle(it);
      if (it.font_color) el.style.color = String(it.font_color);
      if (it.font_size) el.style.fontSize = `${Number(it.font_size)}px`;
      if (it.font_weight) el.style.fontWeight = String(it.font_weight);
      if (it.font_style) el.style.fontStyle = String(it.font_style);
      if (it.line_height) el.style.lineHeight = String(it.line_height);
      if (it.letter_spacing || it.letter_spacing === 0) el.style.letterSpacing = `${Number(it.letter_spacing)}px`;
      if (it.text_align) el.style.textAlign = String(it.text_align);
      if (r === "line") {
        const dir = String(it.line_direction || "horizontal");
        const lineStyle = String(it.line_style || "solid");
        el.dataset.lineOrient = dir === "vertical" ? "vertical" : "horizontal";
        el.style.setProperty("--line-thickness", `${Math.max(0.2, Number(it.stroke_width || 1))}px`);
        el.style.setProperty("--line-color", String(it.stroke_color || "#111827"));
        el.style.setProperty("--line-style", lineStyle === "dashed" ? "dashed" : "solid");
      }
      if (r === "image") {
        if (it.image_url) {
          el.style.backgroundImage = `url("${String(it.image_url).replace(/"/g, "&quot;")}")`;
          el.style.backgroundRepeat = "no-repeat";
          el.style.backgroundPosition = "center";
          el.style.backgroundSize = String(it.image_fit || "contain") === "cover" ? "cover" : "contain";
          el.style.backgroundColor = "rgba(255,255,255,0.25)";
        } else {
          el.style.backgroundColor = "rgba(14,165,233,0.08)";
        }
      }
      if (r === "status_stamp") {
        el.style.backgroundColor = "rgba(16,185,129,0.08)";
        el.style.borderColor = "rgba(16,185,129,.55)";
      }
      if (r === "dept") {
        el.style.backgroundColor = "rgba(59,130,246,0.08)";
        el.style.borderColor = "rgba(59,130,246,.55)";
      }
      if (r === "flow_result") {
        el.style.backgroundColor = "rgba(255,255,255,0.6)";
        el.style.borderColor = "rgba(249,115,22,.55)";
      }
      if (r === "qrcode") {
        el.textContent = "";
      }
      if (r === "rect") {
        el.style.borderStyle = "solid";
        el.style.borderWidth = `${Math.max(0.2, Number(it.stroke_width || 0.8))}px`;
        el.style.borderColor = String(it.stroke_color || "#334155");
        el.style.borderRadius = `${Math.max(0, Number(it.rect_radius || 0))}px`;
      }
      if (it.font_family === "china-s") {
        el.style.fontFamily = '"Songti SC","SimSun","Noto Serif CJK SC",serif';
      } else if (it.font_family === "helv") {
        el.style.fontFamily = "Arial, Helvetica, sans-serif";
      }
      if (r === "flow_result") {
        el.textContent = "流程结果（自动）";
      } else if (r === "dept") {
        const deptText = it.field_name ? `部门：${it.field_name}` : `部门槽位 #${Math.max(1, Number(it.slot_index || 1))}`;
        // Support text wrapping in preview
        if (it.text_wrap) {
          el.style.whiteSpace = "normal";     // 允许换行
          el.style.wordBreak = "break-all";   // 任意位置断行
          el.style.overflowWrap = "break-word"; // 单词内换行
          el.style.overflow = "hidden";       // 隐藏溢出
          el.style.textOverflow = "clip";     // 不显示省略号
        } else {
          el.style.whiteSpace = "nowrap";
          el.style.overflow = "hidden";
          el.style.textOverflow = "ellipsis";
          el.style.wordBreak = "normal";
          el.style.overflowWrap = "normal";
        }
        el.textContent = deptText;
      } else if (r === "signature" && String(it.sig_fill_mode || "manual") === "auto_sequence") {
        el.textContent = it.field_name ? `签名：${it.field_name}` : `签名槽位 #${Math.max(1, Number(it.slot_index || 1))}`;
      } else {
        // Support text wrapping for all text-based renderers
        if (it.text_wrap && (r === "text" || r === "label")) {
          el.style.whiteSpace = "normal";
          el.style.wordBreak = "break-all";
          el.style.overflowWrap = "break-word";
          el.style.overflow = "hidden";
          el.style.textOverflow = "clip";
        } else if (r === "text" || r === "label") {
          el.style.whiteSpace = "nowrap";
          el.style.overflow = "hidden";
          el.style.textOverflow = "ellipsis";
          el.style.wordBreak = "normal";
          el.style.overflowWrap = "normal";
        }
        el.textContent = it.label || it.field_name || it.field_id || "item";
      }
      if (it.locked) {
        el.style.outline = "1px dashed rgba(16,185,129,.8)";
        el.style.cursor = "not-allowed";
        el.title = "固定状态章（不可移动/删除）";
      }
      el.dataset.idx = String(idx);
      el.addEventListener("mousedown", (e) => beginDrag(e, idx));
      el.addEventListener("click", (e) => onItemClick(e, idx));
      if (active && state.selected.size === 1) {
        const hSe = document.createElement("span");
        hSe.className = "designer-resize-handle se";
        hSe.addEventListener("mousedown", (e) => beginResize(e, idx, "se"));
        el.appendChild(hSe);

        const hS = document.createElement("span");
        hS.className = "designer-resize-handle s";
        hS.addEventListener("mousedown", (e) => beginResize(e, idx, "s"));
        el.appendChild(hS);
      }
      canvas.appendChild(el);
    });
  }

  function syncProp() {
    // Batch edit mode: multiple items selected
    if (state.selected.size > 1) {
      const selectedItems = Array.from(state.selected).map(idx => state.items[idx]).filter(Boolean);
      const renderers = [...new Set(selectedItems.map(it => it.renderer || "text"))];
      
      if (renderers.length === 1) {
        // Same type: show batch edit mode
        const renderer = renderers[0];
        const firstItem = selectedItems[0];
        
        // Show batch edit hint
        if (selHint) selHint.textContent = `批量编辑模式（已选 ${state.selected.size} 个 ${renderer} 控件）`;
        
        // Update parameter visibility for this renderer type
        updateParamVisibility(renderer);
        
        // Populate with first item's values as reference
        if (propFontFamily) propFontFamily.value = firstItem.font_family || "helv";
        if (propFontSize) propFontSize.value = Number(firstItem.font_size || 10);
        if (propFontColor) propFontColor.value = firstItem.font_color || "#1e3a8a";
        if (propFontWeight) propFontWeight.value = firstItem.font_weight || "bold";
        if (propTextAlign) propTextAlign.value = firstItem.text_align || "left";
        if (propVerticalAlign) propVerticalAlign.value = firstItem.vertical_align || "top";
        if (propFontStyle) propFontStyle.value = firstItem.font_style || "normal";
        if (propLineHeight) propLineHeight.value = Number(firstItem.line_height || 1.2);
        if (propLetterSpacing) propLetterSpacing.value = Number(firstItem.letter_spacing || 0);
        if (propStrokeWidth) propStrokeWidth.value = Number(firstItem.stroke_width || 0.8);
        if (propStrokeColor) propStrokeColor.value = firstItem.stroke_color || "#334155";
        if (propRectRadius) propRectRadius.value = Number(firstItem.rect_radius || 0);
        if (propImageFit) propImageFit.value = firstItem.image_fit || "contain";
        if (propSigFillMode) propSigFillMode.value = firstItem.sig_fill_mode || "manual";
        if (propSlotIndex) propSlotIndex.value = Math.max(1, Number(firstItem.slot_index || 1));
        
        // Show average position/size as reference
        const avgX = Math.round(selectedItems.reduce((sum, it) => sum + it.x, 0) / selectedItems.length);
        const avgY = Math.round(selectedItems.reduce((sum, it) => sum + it.y, 0) / selectedItems.length);
        const avgW = Math.round(selectedItems.reduce((sum, it) => sum + it.w, 0) / selectedItems.length);
        const avgH = Math.round(selectedItems.reduce((sum, it) => sum + it.h, 0) / selectedItems.length);
        
        propX.value = avgX;
        propY.value = avgY;
        propW.value = avgW;
        propH.value = avgH;
        
        propRenderer.value = renderer;
        
        // Disable unique fields in batch mode
        if (propLabel) propLabel.disabled = true;
        if (propFieldId) propFieldId.disabled = true;
        if (propFieldName) propFieldName.disabled = true;
        if (propBindField) propBindField.disabled = true;
        
        renderPropHelp(renderer);
      } else {
        // Different types: show message and only allow basic params
        if (selHint) selHint.textContent = `批量编辑模式（已选 ${state.selected.size} 个不同类型控件，只能编辑位置和尺寸）`;
        
        // Show only basic parameters (x, y, w, h)
        const basicParams = new Set(['x', 'y', 'w', 'h']);
        Object.entries(PARAM_TO_ELEMENT).forEach(([param, elementId]) => {
          const element = document.getElementById(elementId);
          if (!element) return;
          let row = element.closest('.grid');
          if (!row) {
            row = element.parentElement;
            while (row && !row.classList.contains('grid') && row.parentElement) {
              row = row.parentElement;
              if (row.classList.contains('col-span-2')) break;
            }
          }
          if (!row) return;
          
          if (basicParams.has(param)) {
            row.classList.remove('hidden');
          } else {
            row.classList.add('hidden');
          }
        });
        
        // Hide special config sections
        if (stampConfig) stampConfig.classList.add('hidden');
        if (imageConfig) imageConfig.classList.add('hidden');
        if (qrcodeConfig) qrcodeConfig.classList.add('hidden');
        if (slotConfig) slotConfig.classList.add('hidden');
        
        // Show average position/size
        const selectedItems = Array.from(state.selected).map(idx => state.items[idx]).filter(Boolean);
        const avgX = Math.round(selectedItems.reduce((sum, it) => sum + it.x, 0) / selectedItems.length);
        const avgY = Math.round(selectedItems.reduce((sum, it) => sum + it.y, 0) / selectedItems.length);
        const avgW = Math.round(selectedItems.reduce((sum, it) => sum + it.w, 0) / selectedItems.length);
        const avgH = Math.round(selectedItems.reduce((sum, it) => sum + it.h, 0) / selectedItems.length);
        
        propX.value = avgX;
        propY.value = avgY;
        propW.value = avgW;
        propH.value = avgH;
        
        // Disable all other fields
        if (propLabel) propLabel.disabled = true;
        if (propBindField) propBindField.disabled = true;
        if (propFontFamily) propFontFamily.disabled = true;
        if (propFontSize) propFontSize.disabled = true;
        if (propFontColor) propFontColor.disabled = true;
      }
      return;
    }
    
    // Single item mode (original logic)
    // Re-enable all fields
    if (propX) propX.disabled = false;
    if (propY) propY.disabled = false;
    if (propW) propW.disabled = false;
    if (propH) propH.disabled = false;
    if (propLabel) propLabel.disabled = false;
    if (propFontFamily) propFontFamily.disabled = false;
    if (propFontSize) propFontSize.disabled = false;
    if (propFontColor) propFontColor.disabled = false;
    if (propFieldId) propFieldId.disabled = false;
    if (propFieldName) propFieldName.disabled = false;
    
    if (state.selected.size !== 1) return;
    const idx = Array.from(state.selected)[0];
    const it = state.items[idx];
    if (!it) return;
    
    const renderer = it.renderer || "text";
    
    // Update parameter visibility for this renderer type
    updateParamVisibility(renderer);
    
    propX.value = it.x;
    propY.value = it.y;
    propW.value = it.w;
    propH.value = it.h;
    propLabel.value = it.label || "";
    if (propFieldId) propFieldId.value = it.field_id || "";
    if (propFieldName) propFieldName.value = it.field_name || "";
    if (propFieldType) propFieldType.value = it.field_type || "";
    refreshBindFieldOptions();
    if (propBindField) propBindField.value = it.field_id || "";
    const rule = bindingRule(renderer);
    const disabled = !rule.bindable;
    if (propBindField) propBindField.disabled = disabled;
    if (propFieldId) propFieldId.disabled = disabled;
    if (propFieldName) propFieldName.disabled = disabled;
    if (propFieldType) propFieldType.disabled = disabled;
    if (propFontFamily) propFontFamily.value = it.font_family || "helv";
    if (propFontSize) propFontSize.value = Number(it.font_size || 10);
    if (propFontColor) propFontColor.value = it.font_color || "#312e81";
    if (propFontWeight) propFontWeight.value = it.font_weight || "bold";
    if (propTextAlign) propTextAlign.value = it.text_align || "left";
    if (propVerticalAlign) propVerticalAlign.value = it.vertical_align || "top";
    if (propFontStyle) propFontStyle.value = it.font_style || "normal";
    if (propEmptyPolicy) propEmptyPolicy.value = it.empty_policy || "show_placeholder";
    if (propLineHeight) propLineHeight.value = Number(it.line_height || 1.2);
    if (propLetterSpacing) propLetterSpacing.value = Number(it.letter_spacing || 0);
    if (propOverflowMarker) propOverflowMarker.checked = it.overflow_marker !== false;
    if (propTextWrap) propTextWrap.checked = it.text_wrap === true;
    if (propLineDirection) propLineDirection.value = it.line_direction || "horizontal";
    if (propLineStyle) propLineStyle.value = it.line_style || "solid";
    if (propStrokeWidth) propStrokeWidth.value = Number(it.stroke_width || (renderer === "line" ? 1 : 0.8));
    if (propRectRadius) propRectRadius.value = Number(it.rect_radius || 0);
    if (propStrokeColor) propStrokeColor.value = it.stroke_color || "#334155";
    if (propImageUrl) propImageUrl.value = it.image_url || "";
    if (propImageFit) propImageFit.value = it.image_fit || "contain";
    if (propStampStatus) propStampStatus.value = it.stamp_status || "auto";
    if (propStampPack) propStampPack.value = it.stamp_pack || "default";
    if (propSigFillMode) propSigFillMode.value = it.sig_fill_mode || "manual";
    if (propSlotIndex) propSlotIndex.value = Math.max(1, Number(it.slot_index || 1));
    if (propLocalUserName) propLocalUserName.value = it.local_user_name || "";
    if (propDeptSource) propDeptSource.value = it.dept_source || "local_user_by_signature";
    if (propQrSource) propQrSource.value = it.qr_source || "field";
    if (propQrValue) propQrValue.value = it.qr_value || "";
    propRenderer.value = renderer;
    renderPropHelp(renderer);
    if (selHint) selHint.textContent = `已选 1 个 ${renderer} 控件`;
  }

  function clearGuides() {
    state.guides.x = null;
    state.guides.y = null;
    guideH?.classList.add("hidden");
    guideV?.classList.add("hidden");
  }

  function onItemClick(e, idx) {
    const multi = e.ctrlKey || e.metaKey || e.shiftKey;
    if (!multi) {
      state.selected.clear();
      state.selected.add(idx);
    } else {
      if (state.selected.has(idx)) state.selected.delete(idx);
      else state.selected.add(idx);
    }
    syncProp();
    renderItems();
    if (selHint) selHint.textContent = `已选 ${state.selected.size} 个`;
  }

  function beginDrag(e, idx) {
    if (state.items[idx] && state.items[idx].locked) return;
    if (e.target && e.target.classList && e.target.classList.contains("designer-resize-handle")) return;
    // select current if not in multi selection
    if (!state.selected.has(idx)) {
      if (!(e.ctrlKey || e.metaKey || e.shiftKey)) state.selected.clear();
      state.selected.add(idx);
    }
    syncProp();
    const it = state.items[idx];
    const p = clientToCanvas(e.clientX, e.clientY);
    const selectedIdxs = Array.from(state.selected);
    const origins = {};
    selectedIdxs.forEach((k) => {
      origins[k] = { x: Number(state.items[k].x || 0), y: Number(state.items[k].y || 0) };
    });
    state.dragging = {
      idx,
      startX: p.x,
      startY: p.y,
      origins,
    };
    document.addEventListener("mousemove", onDragMove);
    document.addEventListener("mouseup", endDrag);
    e.preventDefault();
    renderItems();
    if (selHint) selHint.textContent = `已选 ${state.selected.size} 个`;
  }

  function onDragMove(e) {
    if (state.resizing) return;
    if (!state.dragging) return;
    const d = state.dragging;
    const p = clientToCanvas(e.clientX, e.clientY);
    const dx = p.x - d.startX;
    const dy = p.y - d.startY;

    // guide snapping only for primary item
    const base = d.origins[d.idx] || { x: 0, y: 0 };
    let nx = snap(base.x + dx);
    let ny = snap(base.y + dy);
    updateGuidesFor(d.idx, nx, ny);
    if (state.guides.x !== null) nx = state.guides.x;
    if (state.guides.y !== null) ny = state.guides.y;

    const ddx = nx - base.x;
    const ddy = ny - base.y;
    Object.keys(d.origins).forEach((k) => {
      const i = Number(k);
      const o = d.origins[k];
      state.items[i].x = Math.max(0, Math.round(o.x + ddx));
      state.items[i].y = Math.max(0, Math.round(o.y + ddy));
    });
    syncProp();
    renderItems();
  }

  function endDrag() {
    if (state.dragging) armHistory();
    state.dragging = null;
    document.removeEventListener("mousemove", onDragMove);
    document.removeEventListener("mouseup", endDrag);
    clearGuides();
    pushHistory("drag");
  }

  function beginResize(e, idx, mode) {
    if (state.items[idx] && state.items[idx].locked) return;
    armHistory();
    state.selected.clear();
    state.selected.add(idx);
    syncProp();
    const it = state.items[idx];
    const p = clientToCanvas(e.clientX, e.clientY);
    state.resizing = {
      idx,
      mode,
      startX: p.x,
      startY: p.y,
      ow: Number(it.w || 0),
      oh: Number(it.h || 0),
    };
    document.addEventListener("mousemove", onResizeMove);
    document.addEventListener("mouseup", endResize);
    e.preventDefault();
    e.stopPropagation();
  }

  function onResizeMove(e) {
    if (!state.resizing) return;
    const r = state.resizing;
    const it = state.items[r.idx];
    const p = clientToCanvas(e.clientX, e.clientY);
    const dx = p.x - r.startX;
    const dy = p.y - r.startY;
    const minW = 20;
    const minH = 12;
    let nw = r.ow;
    let nh = r.oh;
    if (r.mode === "se") {
      nw = Math.max(minW, r.ow + dx);
      nh = Math.max(minH, r.oh + dy);
    } else if (r.mode === "s") {
      nh = Math.max(minH, r.oh + dy);
    }
    it.w = Math.round(snap(nw));
    it.h = Math.round(snap(nh));
    syncProp();
    renderItems();
  }

  function endResize() {
    if (state.resizing) pushHistory("resize");
    state.resizing = null;
    document.removeEventListener("mousemove", onResizeMove);
    document.removeEventListener("mouseup", endResize);
  }

  function beginMarquee(e) {
    if (state.resizing) return;
    // only start on blank canvas (not an item)
    if (e.target && e.target.classList && e.target.classList.contains("designer-item")) return;
    if (e.button !== 0) return;
    const p = clientToCanvas(e.clientX, e.clientY);
    state.marquee = { x0: p.x, y0: p.y, x1: p.x, y1: p.y, additive: e.shiftKey || e.ctrlKey || e.metaKey };
    if (!state.marquee.additive) state.selected.clear();
    marquee?.classList.remove("hidden");
    document.addEventListener("mousemove", onMarqueeMove);
    document.addEventListener("mouseup", endMarquee);
  }

  function onMarqueeMove(e) {
    if (!state.marquee) return;
    const p = clientToCanvas(e.clientX, e.clientY);
    state.marquee.x1 = p.x;
    state.marquee.y1 = p.y;
    const x = Math.min(state.marquee.x0, state.marquee.x1);
    const y = Math.min(state.marquee.y0, state.marquee.y1);
    const w = Math.abs(state.marquee.x1 - state.marquee.x0);
    const h = Math.abs(state.marquee.y1 - state.marquee.y0);
    if (marquee) {
      marquee.style.left = `${x}px`;
      marquee.style.top = `${y}px`;
      marquee.style.width = `${w}px`;
      marquee.style.height = `${h}px`;
    }
    const selRect = { x, y, w, h };
    state.items.forEach((it, idx) => {
      if (intersects(selRect, rectOf(it))) state.selected.add(idx);
      else if (!state.marquee.additive) state.selected.delete(idx);
    });
    renderItems();
  }

  function endMarquee() {
    state.marquee = null;
    marquee?.classList.add("hidden");
    document.removeEventListener("mousemove", onMarqueeMove);
    document.removeEventListener("mouseup", endMarquee);
    syncProp();
    if (selHint) selHint.textContent = state.selected.size ? `已选 ${state.selected.size} 个` : "未选择";
  }

  function renderFieldRows(container, rows) {
    if (!container) return;
    container.innerHTML = "";
    rows.forEach((f) => {
      const row = document.createElement("div");
      row.className = "palette-btn";
      row.draggable = true;
      row.dataset.palette = "field";
      row.dataset.fieldId = f.id;
      row.dataset.fieldName = f.name;
      row.dataset.fieldType = f.type;
      const pill = f.type === "SignatureField" ? "pill-sign" : "pill-text";
      const tag = f.id && String(f.id).startsWith("sys.") ? "SYS" : (f.type === "SignatureField" ? "SIGN" : "FIELD");
      const isPreferredQr = String(f.id || "") === "sys.preferred_qr_url";
      const displayName = isPreferredQr ? `${f.name || f.id}（推荐）` : (f.name || f.id);
      row.innerHTML = `<div>
        <div class="text-xs font-black">${displayName}</div>
        <div class="text-[10px] opacity-70">${f.type} · ${f.id}</div>
      </div>
      <span class="palette-pill ${pill}">${tag}</span>`;
      row.addEventListener("dragstart", (e) => {
        const payload = {
          kind: "field",
          field_id: f.id,
          field_name: f.name,
          field_type: f.type,
        };
        e.dataTransfer.setData("application/json", JSON.stringify(payload));
        e.dataTransfer.effectAllowed = "copy";
      });
      container.appendChild(row);
    });
  }

  function refreshBindFieldOptions() {
    if (!propBindField) return;
    const prev = String(propBindField.value || "");
    let renderer = "text";
    if (state.selected.size === 1) {
      const idx = Array.from(state.selected)[0];
      renderer = String((state.items[idx] || {}).renderer || "text");
    } else if (propRenderer) {
      renderer = String(propRenderer.value || "text");
    }
    const all = [...(state.systemFields || []), ...(state.fields || [])];
    propBindField.innerHTML = '<option value="">-- 不绑定字段（仅使用label） --</option>';
    all.forEach((f) => {
      if (!isFieldAllowedForRenderer(renderer, f.type)) return;
      const opt = document.createElement("option");
      opt.value = String(f.id || "");
      const isPreferredQr = String(f.id || "") === "sys.preferred_qr_url";
      const name = isPreferredQr ? `${f.name || f.id}（推荐）` : (f.name || f.id);
      opt.textContent = `${name} · ${f.type || "-"}`;
      propBindField.appendChild(opt);
    });
    if (prev) propBindField.value = prev;
  }

  function renderFieldList() {
    const q = (fieldSearchEl?.value || "").trim().toLowerCase();
    const listForm = (state.fields || []).filter((f) => {
      const name = String(f.name || "").toLowerCase();
      const id = String(f.id || "").toLowerCase();
      const type = String(f.type || "").toLowerCase();
      return !q || name.includes(q) || id.includes(q) || type.includes(q);
    });
    const listSys = (state.systemFields || []).filter((f) => {
      const name = String(f.name || "").toLowerCase();
      const id = String(f.id || "").toLowerCase();
      const type = String(f.type || "").toLowerCase();
      return !q || name.includes(q) || id.includes(q) || type.includes(q);
    });
    renderFieldRows(systemFieldList, listSys);
    renderFieldRows(fieldList, listForm);
    if (systemFieldList) systemFieldList.classList.toggle("hidden", !!state.collapsed.system);
    if (fieldList) fieldList.classList.toggle("hidden", !!state.collapsed.form);
    if (toggleSystemIcon) toggleSystemIcon.textContent = state.collapsed.system ? "▸" : "▾";
    if (toggleFormIcon) toggleFormIcon.textContent = state.collapsed.form ? "▸" : "▾";
    updateQrStatusBadge();
    refreshBindFieldOptions();
  }

  function updateQrStatusBadge() {
    if (!qrStatusBadge) return;
    const statusRow = (state.systemFields || []).find((f) => String(f.id || "") === "sys.preferred_qr_status");
    const text = String((statusRow && (statusRow.value || statusRow.value_preview)) || "").trim();
    if (!text) {
      qrStatusBadge.classList.add("hidden");
      qrStatusBadge.textContent = "";
      return;
    }
    qrStatusBadge.classList.remove("hidden");
    qrStatusBadge.textContent = text;
    const ok = text.includes("已绑定");
    qrStatusBadge.classList.toggle("bg-emerald-600/15", ok);
    qrStatusBadge.classList.toggle("text-emerald-700", ok);
    qrStatusBadge.classList.toggle("dark:text-emerald-300", ok);
    qrStatusBadge.classList.toggle("bg-amber-600/15", !ok);
    qrStatusBadge.classList.toggle("text-amber-700", !ok);
    qrStatusBadge.classList.toggle("dark:text-amber-300", !ok);
  }

  function renderNodeList(nodes, msg) {
    if (!nodeList) return;
    nodeList.innerHTML = "";
    const rows = Array.isArray(nodes) ? nodes : [];
    if (msg) {
      const m = document.createElement("div");
      m.className = "glass rounded-xl px-2 py-2 text-[11px] text-amber-700";
      m.textContent = msg;
      nodeList.appendChild(m);
    }
    if (!rows.length) {
      const empty = document.createElement("div");
      empty.className = "glass rounded-xl px-2 py-2 text-[11px] text-slate-500";
      empty.textContent = "暂无节点数据";
      nodeList.appendChild(empty);
      return;
    }
    rows.forEach((n) => {
      const actId = String(n.activity_id || "");
      const displayName = String(n.activity_name || state.nodeNameMap[actId] || "");
      const row = document.createElement("div");
      row.className = "glass rounded-xl px-2 py-2";
      row.innerHTML = `<div class="font-black">${actId || "(无activity_id)"} · ${n.task_status || "-"}</div>
        <div class="mt-1">
          <input data-node-name-input="${actId}" placeholder="节点中文名（可编辑）" value="${displayName.replace(/"/g, "&quot;")}" class="w-full glass rounded-lg px-2 py-1 text-[11px] outline-none" />
        </div>
        <div class="opacity-70 mt-1">task: ${n.taskid || "-"} · user: ${n.userid || "-"}</div>
        <div class="opacity-70">finish: ${n.finish_time || "-"}</div>`;
      nodeList.appendChild(row);
    });
  }

  function collectNodeNamesFromUI() {
    const map = { ...(state.nodeNameMap || {}) };
    nodeList?.querySelectorAll("[data-node-name-input]").forEach((el) => {
      const key = String(el.getAttribute("data-node-name-input") || "").trim();
      const val = String(el.value || "").trim();
      if (!key) return;
      if (val) map[key] = val;
      else delete map[key];
    });
    state.nodeNameMap = map;
    return map;
  }

  async function loadNodeNameMap(processCode) {
    if (!processCode) {
      state.nodeNameMap = {};
      return;
    }
    try {
      const res = await fetch(`/designer/api/node_names?process_code=${encodeURIComponent(processCode)}`);
      const data = await res.json();
      if (data.ok && data.node_names && typeof data.node_names === "object") {
        state.nodeNameMap = data.node_names;
      } else {
        state.nodeNameMap = {};
      }
    } catch (err) {
      state.nodeNameMap = {};
    }
  }

  async function saveNodeNameMap() {
    const processCode = (processCodeEl.value || "").trim();
    if (!processCode) {
      alert("请先输入 process_code");
      return;
    }
    const nodeNames = collectNodeNamesFromUI();
    const res = await fetch("/designer/api/node_names", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({
        process_code: processCode,
        node_names: nodeNames,
      }),
    });
    const data = await res.json();
    if (!data.ok) {
      alert(data.msg || "保存节点中文名失败");
      return;
    }
    alert("节点中文名已保存");
  }

  async function loadSchema() {
    const processCode = (processCodeEl.value || "").trim();
    if (!processCode) {
      alert("请先输入 process_code");
      return;
    }
    await loadNodeNameMap(processCode);
    const q = new URLSearchParams({ process_code: processCode });
    const inputInstanceId = (instanceIdEl?.value || "").trim();
    if (inputInstanceId) q.set("instance_id", inputInstanceId);
    const res = await fetch(`/designer/api/schema?${q.toString()}`);
    const data = await res.json();
    if (!data.ok) {
      alert(data.msg || "读取控件失败");
      renderNodeList([], "节点读取已跳过：先修复控件读取");
      return;
    }
    state.fields = Array.isArray(data.fields) ? data.fields : [];
    state.systemFields = Array.isArray(data.system_fields) ? data.system_fields : [];
    if (instanceIdEl && data.instance_id && !lockCurrentInstanceEl?.checked) {
      instanceIdEl.value = String(data.instance_id);
    }
    const resolvedInstanceId =
      (instanceIdEl?.value || "").trim() || String(data.instance_id || "");
    renderFieldList();
    refreshAttachmentFieldOptions();

    // Load node/task info for the same instance
    try {
      const nq = new URLSearchParams({
        process_code: processCode,
        instance_id: resolvedInstanceId,
      });
      const nodeRes = await fetch(`/designer/api/nodes?${nq.toString()}`);
      const nodeData = await nodeRes.json();
      if (nodeData.ok) {
        renderNodeList(nodeData.nodes || []);
      } else {
        renderNodeList([], nodeData.msg || "节点读取失败");
      }
    } catch (err) {
      renderNodeList([], "节点读取异常");
    }
  }

  async function saveLayout() {
    const processCode = (processCodeEl.value || "").trim();
    if (!processCode) {
      alert("process_code 不能为空");
      return;
    }
    state.orient = currentOrient();
    const form = new FormData();
    form.set("process_code", processCode);
    form.set("name", (layoutNameEl.value || "").trim());
    form.set("base_pdf", (basePdfEl.value || "").trim());
    form.set("use_template", state.useTemplate ? "1" : "0");
    form.set("orientation", state.orient || "l");
    form.set("cover_source_mode", state.coverSourceMode || "base");
    form.set("cover_mode", state.coverMode || "strict");
    form.set("cover_offset_x", String(Number(state.coverOffsetX || 0)));
    form.set("cover_offset_y", String(Number(state.coverOffsetY || 0)));
    form.set("items_json", JSON.stringify(state.items));
    form.set("attachment_bg_config", JSON.stringify({
      enabled: state.attachmentBg.enabled,
      field_id: state.attachmentBg.fieldId,
      attachment_index: state.attachmentBg.attachmentIndex,
      page_index: state.attachmentBg.pageIndex,
      apply_mode: state.attachmentBg.applyMode,
    }));
    const res = await fetch("/designer/save", { method: "POST", body: form });
    const data = await res.json();
    if (!data.ok) {
      alert(data.msg || "保存失败");
      return;
    }
    alert("保存成功");
  }

  function updateSelected() {
    if (state.selected.size !== 1) return;
    armHistory();
    const idx = Array.from(state.selected)[0];
    const it = state.items[idx];
    if (it && it.locked) {
      alert("该控件为固定状态章，不可修改位置或删除");
      return;
    }
    it.x = Number(propX.value || 0);
    it.y = Number(propY.value || 0);
    it.w = Number(propW.value || 50);
    it.h = Number(propH.value || 20);
    it.label = propLabel.value || "";
    it.field_id = propFieldId ? (propFieldId.value || "") : (it.field_id || "");
    it.field_name = propFieldName ? (propFieldName.value || "") : (it.field_name || "");
    it.field_type = propFieldType ? (propFieldType.value || "") : (it.field_type || "");
    it.font_family = propFontFamily ? propFontFamily.value || "helv" : "helv";
    it.font_size = propFontSize ? Number(propFontSize.value || 10) : 10;
    it.font_color = propFontColor ? propFontColor.value || "#312e81" : "#312e81";
    it.font_weight = propFontWeight ? propFontWeight.value || "normal" : "normal";
    it.text_align = propTextAlign ? propTextAlign.value || "left" : "left";
    it.font_style = propFontStyle ? propFontStyle.value || "normal" : "normal";
    it.empty_policy = propEmptyPolicy ? propEmptyPolicy.value || "show_placeholder" : "show_placeholder";
    it.line_height = propLineHeight ? Number(propLineHeight.value || 1.2) : 1.2;
    it.letter_spacing = propLetterSpacing ? Number(propLetterSpacing.value || 0) : 0;
    it.overflow_marker = propOverflowMarker ? !!propOverflowMarker.checked : true;
    it.text_wrap = propTextWrap ? !!propTextWrap.checked : false;
    it.line_direction = propLineDirection ? (propLineDirection.value || "horizontal") : "horizontal";
    it.line_style = propLineStyle ? (propLineStyle.value || "solid") : "solid";
    it.stroke_width = propStrokeWidth ? Number(propStrokeWidth.value || 1) : 1;
    it.rect_radius = propRectRadius ? Number(propRectRadius.value || 0) : 0;
    it.stroke_color = propStrokeColor ? (propStrokeColor.value || "#334155") : "#334155";
    it.image_url = propImageUrl ? (propImageUrl.value || "") : (it.image_url || "");
    it.image_fit = propImageFit ? (propImageFit.value || "contain") : "contain";
    it.stamp_status = propStampStatus ? (propStampStatus.value || "auto") : "auto";
    it.stamp_pack = propStampPack ? (propStampPack.value || "default") : "default";
    it.sig_fill_mode = propSigFillMode ? (propSigFillMode.value || "manual") : (it.sig_fill_mode || "manual");
    it.slot_index = Math.max(1, Number(propSlotIndex ? (propSlotIndex.value || 1) : (it.slot_index || 1)));
    it.local_user_name = propLocalUserName ? (propLocalUserName.value || "") : (it.local_user_name || "");
    it.dept_source = propDeptSource ? (propDeptSource.value || "local_user_by_signature") : (it.dept_source || "local_user_by_signature");
    it.qr_source = propQrSource ? (propQrSource.value || "field") : "field";
    it.qr_value = propQrValue ? (propQrValue.value || "") : "";
    it.renderer = propRenderer.value || "text";
    sanitizeBindingByRenderer(it);
    renderItems();
    syncProp();
    pushHistory("update");
  }

  function removeSelected() {
    if (!state.selected.size) return;
    armHistory();
    const idxs = Array.from(state.selected).sort((a, b) => b - a);
    idxs.forEach((idx) => {
      const it = state.items[idx];
      if (it && it.locked) return;
      state.items.splice(idx, 1);
    });
    state.selected.clear();
    renderItems();
    pushHistory("delete");
  }

  function refreshBgPreview() {
    if (!state.useTemplate) {
      bg.classList.add("hidden");
      return;
    }
    
    // 如果是附件底图模式，画布无法预览，显示提示
    if (state.coverSourceMode === "attachment") {
      bg.classList.add("hidden");
      // 可以在这里添加一个提示信息
      if (canvasTitle) {
        const orient = state.orient === "p" ? "纵向" : "横向";
        canvasTitle.textContent = `画布（A4 ${orient}）- 附件底图模式：请点击"预览 PDF"查看实际效果`;
      }
      return;
    }
    
    const pdf = (basePdfEl.value || "").trim();
    if (!pdf) {
      bg.classList.add("hidden");
      return;
    }
    
    // 恢复正常标题
    if (canvasTitle) {
      const orient = state.orient === "p" ? "纵向" : "横向";
      canvasTitle.textContent = `画布（A4 ${orient}）`;
    }
    
    state.orient = currentOrient();
    bg.src = `/admin/pdf_render/${encodeURIComponent(pdf)}?page=0&orient=${encodeURIComponent(state.orient || "l")}&t=${Date.now()}`;
    bg.classList.remove("hidden");
  }

  async function loadAttachmentBackground() {
    const processCode = (processCodeEl.value || "").trim();
    const instanceId = (instanceIdEl?.value || "").trim();
    const fieldId = state.attachmentBg.fieldId || "";
    const attachmentIndex = state.attachmentBg.attachmentIndex || 0;
    const pageIndex = state.attachmentBg.pageIndex || 0;
    
    if (!processCode || !instanceId || !fieldId) {
      // 参数不完整时，不显示错误，只是隐藏背景图
      bg.classList.add("hidden");
      if (canvasTitle) {
        const orient = state.orient === "p" ? "纵向" : "横向";
        canvasTitle.textContent = `画布（A4 ${orient}）- 附件底图：等待配置...`;
      }
      return;
    }
    
    if (canvasTitle) {
      canvasTitle.textContent = `画布 - 正在加载附件底图...`;
    }
    
    try {
      // 调用后端 API 获取附件底图
      const url = `/designer/api/render_attachment_bg?process_code=${encodeURIComponent(processCode)}&instance_id=${encodeURIComponent(instanceId)}&field_id=${encodeURIComponent(fieldId)}&attachment_index=${attachmentIndex}&page_index=${pageIndex}&orient=${encodeURIComponent(state.orient || "l")}&t=${Date.now()}`;
      
      const response = await fetch(url);
      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(errorText || `HTTP ${response.status}`);
      }
      
      // 将响应转换为 blob URL
      const blob = await response.blob();
      const blobUrl = URL.createObjectURL(blob);
      
      // 显示在画布背景
      bg.src = blobUrl;
      bg.classList.remove("hidden");
      
      if (canvasTitle) {
        const orient = state.orient === "p" ? "纵向" : "横向";
        canvasTitle.textContent = `画布（A4 ${orient}）- 附件底图已加载`;
      }
    } catch (error) {
      console.error('加载附件底图失败:', error);
      bg.classList.add("hidden");
      if (canvasTitle) {
        canvasTitle.textContent = `画布 - 附件底图加载失败：${error.message}`;
      }
      // 只在真正出错时才弹窗提示
      if (error.message && !error.message.includes('not found')) {
        alert(`加载附件底图失败：${error.message}\n\n请确认：\n1. 实例ID正确\n2. 附件字段包含PDF文件\n3. 附件索引和页码正确`);
      }
    }
  }

  async function previewPdf() {
    const processCode = (processCodeEl.value || "").trim();
    const basePdf = (basePdfEl.value || "").trim();
    
    // 检查是否启用附件底图
    const usingAttachmentBg = state.attachmentBg.enabled && state.coverSourceMode === "attachment";
    
    // 验证必填参数
    if (!processCode) {
      alert("请先填写 process_code");
      return;
    }
    
    // 如果使用模板但不是附件底图，需要 base_pdf
    if (state.useTemplate && !usingAttachmentBg && !basePdf) {
      alert("请先选择底稿 PDF");
      return;
    }
    
    // Always honor current UI selection at preview time.
    state.orient = currentOrient();
    
    // 如果启用了附件底图，强制 use_template = true
    const useTemplate = state.useTemplate || usingAttachmentBg;
    
    const payload = {
      process_code: processCode,
      base_pdf: basePdf || "",  // 使用附件底图时可以为空
      use_template: useTemplate,
      orientation: state.orient || "l",
      cover_source_mode: state.coverSourceMode || "base",
      cover_mode: state.coverMode || "strict",
      cover_offset_x: Number(state.coverOffsetX || 0),
      cover_offset_y: Number(state.coverOffsetY || 0),
      instance_id: (instanceIdEl?.value || "").trim(),
      items: state.items,
      // 传递附件底图配置
      attachment_background_config: {
        enabled: state.attachmentBg.enabled,
        field_id: state.attachmentBg.fieldId,
        attachment_index: state.attachmentBg.attachmentIndex,
        page_index: state.attachmentBg.pageIndex,
        apply_mode: state.attachmentBg.applyMode,
      },
    };
    const res = await fetch("/designer/api/preview", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!res.ok) {
      const txt = await res.text();
      alert(txt || "预览失败");
      return;
    }
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    window.open(url, "_blank");
  }

  processGroupEl?.addEventListener("change", () => {
    const g = String(processGroupEl.value || "");
    fillProcessPickForGroup(g);
    if (processPickEl) processPickEl.value = "";
  });
  processPickEl?.addEventListener("change", () => {
    const v = String(processPickEl.value || "").trim();
    if (v && processCodeEl) processCodeEl.value = v;
  });
  processCodeEl?.addEventListener("change", () => {
    syncPickersFromProcessCode();
  });
  refreshProcessesBtn?.addEventListener("click", loadProcessGroups);

  loadSchemaBtn?.addEventListener("click", loadSchema);
  saveBtn?.addEventListener("click", saveLayout);
  saveNodeNamesBtn?.addEventListener("click", saveNodeNameMap);
  addTextBtn?.addEventListener("click", () => {
    armHistory();
    state.items.push({
      field_id: "",
      field_name: "",
      field_type: "TextField",
      renderer: "text",
      label: "文本",
      page: 0,
      x: 20,
      y: 20,
      w: 90,
      h: 24,
      font_family: "helv",
      font_size: 10,
      font_color: "#312e81",
      font_weight: "bold",
      text_align: "left",
      font_style: "normal",
      empty_policy: "show_placeholder",
      line_height: 1.2,
      letter_spacing: 0,
      overflow_marker: true,
    });
    state.selected.clear();
    state.selected.add(state.items.length - 1);
    syncProp();
    renderItems();
    pushHistory("add-text");
  });
  // updatePropBtn event listener is defined later (line ~2117) with batch edit support
  deleteItemBtn?.addEventListener("click", removeSelected);
  basePdfEl?.addEventListener("change", async () => {
    // Changing base PDF re-enables auto orientation detection.
    state.orientLockedByUser = false;
    await autoDetectOrientation();
    refreshBgPreview();
  });
  useTemplateEl?.addEventListener("change", () => {
    state.useTemplate = !!useTemplateEl.checked;
    syncCoverUiState();
    refreshBgPreview();
  });
  coverSourceModeEl?.addEventListener("change", () => {
    state.coverSourceMode = String(coverSourceModeEl.value || "base");
    syncCoverUiState();
    refreshBgPreview();
  });
  coverModeEl?.addEventListener("change", () => {
    state.coverMode = String(coverModeEl.value || "strict");
    syncCoverUiState();
  });
  coverOffsetXEl?.addEventListener("input", () => {
    state.coverOffsetX = Number(coverOffsetXEl.value || 0);
  });
  coverOffsetYEl?.addEventListener("input", () => {
    state.coverOffsetY = Number(coverOffsetYEl.value || 0);
  });
  paperOrientEl && (paperOrientEl.value = state.orient);
  state.orient = currentOrient();
  paperOrientEl?.addEventListener("change", () => {
    state.orientLockedByUser = true;
    state.orient = String(paperOrientEl.value || "l") === "p" ? "p" : "l";
    ensureFixedStatusStamp();
    applyCanvasSize();
    refreshBgPreview();
    centerCanvasInViewport();
  });
  previewBtn?.addEventListener("click", previewPdf);

  canvas?.addEventListener("mousedown", beginMarquee);
  canvas?.addEventListener("dragover", (e) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = "copy";
  });
  canvas?.addEventListener("drop", (e) => {
    e.preventDefault();
    let raw = "";
    try {
      raw = e.dataTransfer.getData("application/json") || "";
    } catch {
      raw = "";
    }
    if (!raw) return;
    let payload;
    try {
      payload = JSON.parse(raw);
    } catch {
      return;
    }
    const p = clientToCanvas(e.clientX, e.clientY);
    const x = Math.max(0, snap(p.x));
    const y = Math.max(0, snap(p.y));
    armHistory();
    const kind = String(payload.kind || payload.palette || "").toLowerCase();
    const base = {
      page: 0,
      x,
      y,
      w: 100,
      h: 24,
      renderer: "text",
      label: "item",
    };
    if (kind === "label") {
      state.items.push({ ...base, renderer: "label", label: "标签", w: 90, h: 22, font_family: "helv", font_size: 10, font_color: "#065f46", font_weight: "bold", text_align: "left", font_style: "normal", empty_policy: "show_placeholder", line_height: 1.2, letter_spacing: 0, overflow_marker: true });
    } else if (kind === "text") {
      state.items.push({ ...base, renderer: "text", label: "文本框", w: 120, h: 24, font_family: "helv", font_size: 10, font_color: "#1e3a8a", font_weight: "bold", text_align: "left", font_style: "normal", empty_policy: "show_placeholder", line_height: 1.2, letter_spacing: 0, overflow_marker: true });
    } else if (kind === "rect") {
      state.items.push({ ...base, renderer: "rect", label: "边框", w: 120, h: 40, stroke_width: 0.8, rect_radius: 0, stroke_color: "#334155" });
    } else if (kind === "line") {
      state.items.push({ ...base, renderer: "line", label: "线条", w: 160, h: 10, line_direction: "horizontal", line_style: "solid", stroke_width: 1, rect_radius: 0, stroke_color: "#111827" });
    } else if (kind === "signature") {
      state.items.push({ ...base, renderer: "signature", label: "签名框", w: 120, h: 35, sig_fill_mode: "auto_sequence", slot_index: 1 });
    } else if (kind === "dept") {
      state.items.push({
        ...base,
        renderer: "dept",
        label: "部门",
        w: 120,
        h: 22,
        slot_index: 1,
        dept_source: "local_user_by_signature",
        font_family: "china-s",
        font_size: 10,
        font_color: "#334155",
        font_weight: "bold",
        text_align: "left",
        font_style: "normal",
        empty_policy: "show_placeholder",
        line_height: 1.2,
        letter_spacing: 0,
        overflow_marker: true,
        text_wrap: false,
      });
    } else if (kind === "image") {
      state.items.push({ ...base, renderer: "image", label: "图片", w: 120, h: 60, image_url: "", image_fit: "contain" });
    } else if (kind === "status_stamp") {
      state.items.push({ ...base, renderer: "status_stamp", label: "状态章", w: 70, h: 70, stamp_status: "auto", stamp_pack: "default" });
    } else if (kind === "flow_result") {
      state.items.push({
        ...base,
        renderer: "flow_result",
        label: "流程结果",
        w: 180,
        h: 24,
        font_family: "helv",
        font_size: 11,
        font_color: "#FF933C",
        font_weight: "bold",
        text_align: "left",
        font_style: "normal",
        empty_policy: "show_placeholder",
        line_height: 1.2,
        letter_spacing: 0,
        overflow_marker: true,
      });
    } else if (kind === "qrcode") {
      state.items.push({
        ...base,
        renderer: "qrcode",
        label: "二维码",
        w: 70,
        h: 70,
        qr_source: "field",
        qr_value: "",
        field_id: "sys.preferred_qr_url",
        field_name: "二维码优先链接（推荐）",
        field_type: "SystemField",
      });
    } else if (kind === "field") {
      const ft = String(payload.field_type || "");
      state.items.push({
        ...base,
        field_id: payload.field_id || "",
        field_name: payload.field_name || "",
        field_type: ft,
        renderer: ft === "SignatureField" ? "signature" : "text",
        sig_fill_mode: ft === "SignatureField" ? "auto_sequence" : undefined,
        label: payload.field_name || payload.field_id || "字段",
        w: ft === "SignatureField" ? 120 : 140,
        h: ft === "SignatureField" ? 35 : 24,
        font_family: "helv",
        font_size: 10,
        font_color: "#1e3a8a",
        font_weight: "bold",
        text_align: "left",
        font_style: "normal",
        empty_policy: "show_placeholder",
        line_height: 1.2,
        letter_spacing: 0,
        overflow_marker: true,
      });
    } else {
      return;
    }
    state.selected.clear();
    state.selected.add(state.items.length - 1);
    renderItems();
    syncProp();
    pushHistory("drop");
    if (selHint) selHint.textContent = "已选 1 个";
  });

  document.querySelectorAll("[data-palette]").forEach((el) => {
    el.addEventListener("dragstart", (e) => {
      const kind = String(el.dataset.palette || "").trim();
      if (!kind) return;
      e.dataTransfer.setData("application/json", JSON.stringify({ kind }));
      e.dataTransfer.effectAllowed = "copy";
    });
  });

  fieldSearchEl?.addEventListener("input", renderFieldList);
  propBindField?.addEventListener("change", () => {
    if (state.selected.size !== 1) return;
    const idx = Array.from(state.selected)[0];
    const it = state.items[idx];
    const selectedId = String(propBindField.value || "");
    if (!selectedId) {
      if (propFieldId) propFieldId.value = "";
      if (propFieldName) propFieldName.value = "";
      if (propFieldType) propFieldType.value = "";
      it.field_id = "";
      it.field_name = "";
      it.field_type = "";
      return;
    }
    const all = [...(state.systemFields || []), ...(state.fields || [])];
    const f = all.find((x) => String(x.id || "") === selectedId);
    if (!f) return;
    if (!isFieldAllowedForRenderer(it.renderer || "text", f.type || "")) {
      alert("当前控件类型不支持绑定该字段类型");
      if (propBindField) propBindField.value = "";
      return;
    }
    if (propFieldId) propFieldId.value = String(f.id || "");
    if (propFieldName) propFieldName.value = String(f.name || "");
    if (propFieldType) propFieldType.value = String(f.type || "");
    it.field_id = String(f.id || "");
    it.field_name = String(f.name || "");
    it.field_type = String(f.type || "");
    if (String(f.type || "") === "SignatureField" && String(it.renderer || "") === "signature") {
      it.sig_fill_mode = "auto_sequence";
      if (propSigFillMode) propSigFillMode.value = "auto_sequence";
    }
  });
  propRenderer?.addEventListener("change", () => {
    refreshBindFieldOptions();
    renderPropHelp(propRenderer.value || "text");
    const r = propRenderer.value || "text";
    if (stampConfig) stampConfig.classList.toggle("hidden", r !== "status_stamp");
    if (imageConfig) imageConfig.classList.toggle("hidden", r !== "image");
    if (qrcodeConfig) qrcodeConfig.classList.toggle("hidden", r !== "qrcode");
    if (slotConfig) slotConfig.classList.toggle("hidden", !(r === "signature" || r === "dept"));
    if (propSigFillMode) propSigFillMode.disabled = r !== "signature";
    if (propDeptSource) propDeptSource.disabled = r !== "dept";
  });
  propImageUpload?.addEventListener("change", () => {
    if (state.selected.size !== 1) return;
    const file = propImageUpload.files && propImageUpload.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = () => {
      const idx = Array.from(state.selected)[0];
      const it = state.items[idx];
      if (!it) return;
      it.image_url = String(reader.result || "");
      if (propImageUrl) propImageUrl.value = it.image_url;
      renderItems();
      syncProp();
    };
    reader.readAsDataURL(file);
  });
  fetchStampBtn?.addEventListener("click", async () => {
    const url = String(propStampFetchUrl?.value || "").trim();
    const key = String(propStampStatus?.value || "agree").trim().toLowerCase();
    const pack = String(propStampPack?.value || "default").trim().toLowerCase();
    if (!url) {
      alert("请先输入状态章URL");
      return;
    }
    const res = await fetch("/designer/api/stamp/fetch", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ url, key, pack }),
    });
    const data = await res.json();
    if (!data.ok) {
      alert(data.msg || "状态章拉取失败");
      return;
    }
    alert(`状态章已保存：${data.path || ""}`);
  });
  toggleSystemFieldsBtn?.addEventListener("click", () => {
    state.collapsed.system = !state.collapsed.system;
    renderFieldList();
  });
  toggleFormFieldsBtn?.addEventListener("click", () => {
    state.collapsed.form = !state.collapsed.form;
    renderFieldList();
  });

  undoBtn?.addEventListener("click", undo);
  redoBtn?.addEventListener("click", redo);
  zoomOutBtn?.addEventListener("click", () => {
    state.zoom = Math.max(0.4, Math.round((state.zoom - 0.1) * 10) / 10);
    applyZoom();
  });
  zoomInBtn?.addEventListener("click", () => {
    state.zoom = Math.min(2.5, Math.round((state.zoom + 0.1) * 10) / 10);
    applyZoom();
  });
  zoomResetBtn?.addEventListener("click", () => {
    state.zoom = 1;
    applyZoom();
  });
  gridSizeEl?.addEventListener("change", () => {
    state.gridSize = Number(gridSizeEl.value || 10);
    applyGrid();
  });
  snapToggle?.addEventListener("change", () => {
    state.snap = !!snapToggle.checked;
  });

  // Canvas-first wheel behavior:
  // - wheel over canvas scroll area only (prevent page scroll chaining)
  // - Ctrl/Cmd + wheel to zoom canvas
  canvasScrollWrap?.addEventListener("wheel", (e) => {
    if (e.ctrlKey || e.metaKey) {
      e.preventDefault();
      const delta = e.deltaY > 0 ? -0.1 : 0.1;
      state.zoom = Math.min(2.5, Math.max(0.4, Math.round((state.zoom + delta) * 10) / 10));
      applyZoom();
      return;
    }
    // lock wheel scrolling inside canvas container
    e.preventDefault();
    canvasScrollWrap.scrollTop += e.deltaY;
    if (e.shiftKey) canvasScrollWrap.scrollLeft += e.deltaY;
    else canvasScrollWrap.scrollLeft += e.deltaX;
  }, { passive: false });

  document.addEventListener("keydown", (e) => {
    // Copy: Ctrl+C / Cmd+C
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "c") {
      if (document.activeElement && ["INPUT", "TEXTAREA", "SELECT"].includes(document.activeElement.tagName)) return;
      if (state.selected.size === 0) return;
      e.preventDefault();
      const selectedItems = Array.from(state.selected).map(idx => state.items[idx]).filter(Boolean);
      state.clipboard = JSON.parse(JSON.stringify(selectedItems));
      console.log(`Copied ${state.clipboard.length} item(s)`);
    }
    // Paste: Ctrl+V / Cmd+V
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "v") {
      if (document.activeElement && ["INPUT", "TEXTAREA", "SELECT"].includes(document.activeElement.tagName)) return;
      if (!state.clipboard || state.clipboard.length === 0) return;
      e.preventDefault();
      armHistory();
      state.selected.clear();
      state.clipboard.forEach(item => {
        const newItem = JSON.parse(JSON.stringify(item));
        // Generate new ID (timestamp + random)
        newItem.id = `item_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        // Offset position to avoid overlap
        newItem.x = (newItem.x || 0) + 10;
        newItem.y = (newItem.y || 0) + 10;
        state.items.push(newItem);
        state.selected.add(state.items.length - 1);
      });
      renderItems();
      syncProp();
      pushHistory("paste");
      if (selHint) selHint.textContent = `已选 ${state.selected.size} 个`;
      console.log(`Pasted ${state.clipboard.length} item(s)`);
    }
    // Duplicate: Ctrl+D / Cmd+D
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "d") {
      if (document.activeElement && ["INPUT", "TEXTAREA", "SELECT"].includes(document.activeElement.tagName)) return;
      if (state.selected.size === 0) return;
      e.preventDefault();
      armHistory();
      const selectedItems = Array.from(state.selected).map(idx => state.items[idx]).filter(Boolean);
      state.selected.clear();
      selectedItems.forEach(item => {
        const newItem = JSON.parse(JSON.stringify(item));
        newItem.id = `item_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        newItem.x = (newItem.x || 0) + 10;
        newItem.y = (newItem.y || 0) + 10;
        state.items.push(newItem);
        state.selected.add(state.items.length - 1);
      });
      renderItems();
      syncProp();
      pushHistory("duplicate");
      if (selHint) selHint.textContent = `已选 ${state.selected.size} 个`;
      console.log(`Duplicated ${selectedItems.length} item(s)`);
    }
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "z") {
      e.preventDefault();
      undo();
    }
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "y") {
      e.preventDefault();
      redo();
    }
    if (e.key === "Delete" || e.key === "Backspace") {
      if (document.activeElement && ["INPUT", "TEXTAREA", "SELECT"].includes(document.activeElement.tagName)) return;
      removeSelected();
    }
    if (e.key === "Escape") {
      state.selected.clear();
      renderItems();
      clearGuides();
      if (selHint) selHint.textContent = "未选择";
    }
  });

  // Update properties button
  updatePropBtn?.addEventListener("click", () => {
    if (state.selected.size === 0) return;
    
    armHistory();
    
    // Batch mode: update all selected items
    if (state.selected.size > 1) {
      const selectedItems = Array.from(state.selected).map(idx => state.items[idx]).filter(Boolean);
      const renderers = [...new Set(selectedItems.map(it => it.renderer || "text"))];
      
      // Get common parameters
      const commonParams = getCommonParams(renderers);
      
      // Apply common properties to all selected items
      selectedItems.forEach(it => {
        // Basic parameters (always common)
        if (commonParams.has('x')) it.x = Number(propX.value || 0);
        if (commonParams.has('y')) it.y = Number(propY.value || 0);
        if (commonParams.has('w')) it.w = Number(propW.value || 100);
        if (commonParams.has('h')) it.h = Number(propH.value || 24);
        
        // Font parameters
        if (commonParams.has('font_family') && propFontFamily && !propFontFamily.disabled) {
          it.font_family = propFontFamily.value;
        }
        if (commonParams.has('font_size') && propFontSize && !propFontSize.disabled) {
          it.font_size = Number(propFontSize.value || 10);
        }
        if (commonParams.has('font_color') && propFontColor && !propFontColor.disabled) {
          it.font_color = propFontColor.value;
        }
        if (commonParams.has('font_weight') && propFontWeight && !propFontWeight.disabled) {
          it.font_weight = propFontWeight.value;
        }
        if (commonParams.has('font_style') && propFontStyle && !propFontStyle.disabled) {
          it.font_style = propFontStyle.value;
        }
        
        // Layout parameters
        if (commonParams.has('text_align') && propTextAlign && !propTextAlign.disabled) {
          it.text_align = propTextAlign.value;
        }
        if (commonParams.has('vertical_align') && propVerticalAlign && !propVerticalAlign.disabled) {
          it.vertical_align = propVerticalAlign.value;
        }
        if (commonParams.has('line_height') && propLineHeight && !propLineHeight.disabled) {
          it.line_height = Number(propLineHeight.value || 1.2);
        }
        if (commonParams.has('letter_spacing') && propLetterSpacing && !propLetterSpacing.disabled) {
          it.letter_spacing = Number(propLetterSpacing.value || 0);
        }
        
        // Shape parameters
        if (commonParams.has('stroke_width') && propStrokeWidth && !propStrokeWidth.disabled) {
          it.stroke_width = Number(propStrokeWidth.value || 0.8);
        }
        if (commonParams.has('stroke_color') && propStrokeColor && !propStrokeColor.disabled) {
          it.stroke_color = propStrokeColor.value;
        }
        if (commonParams.has('rect_radius') && propRectRadius && !propRectRadius.disabled) {
          it.rect_radius = Number(propRectRadius.value || 0);
        }
        
        // Line parameters
        if (commonParams.has('line_direction') && propLineDirection && !propLineDirection.disabled) {
          it.line_direction = propLineDirection.value;
        }
        if (commonParams.has('line_style') && propLineStyle && !propLineStyle.disabled) {
          it.line_style = propLineStyle.value;
        }
        
        // Image parameters
        if (commonParams.has('image_fit') && propImageFit && !propImageFit.disabled) {
          it.image_fit = propImageFit.value;
        }
        
        // Signature parameters
        if (commonParams.has('sig_fill_mode') && propSigFillMode && !propSigFillMode.disabled) {
          it.sig_fill_mode = propSigFillMode.value;
        }
        if (commonParams.has('slot_index') && propSlotIndex && !propSlotIndex.disabled) {
          it.slot_index = Math.max(1, Number(propSlotIndex.value || 1));
        }
        
        // Stamp parameters
        if (commonParams.has('stamp_status') && propStampStatus && !propStampStatus.disabled) {
          it.stamp_status = propStampStatus.value;
        }
        if (commonParams.has('stamp_pack') && propStampPack && !propStampPack.disabled) {
          it.stamp_pack = propStampPack.value;
        }
        
        // Behavior parameters
        if (commonParams.has('empty_policy') && propEmptyPolicy && !propEmptyPolicy.disabled) {
          it.empty_policy = propEmptyPolicy.value;
        }
        if (commonParams.has('overflow_marker') && propOverflowMarker && !propOverflowMarker.disabled) {
          it.overflow_marker = propOverflowMarker.checked;
        }
        if (commonParams.has('text_wrap') && propTextWrap && !propTextWrap.disabled) {
          it.text_wrap = propTextWrap.checked;
        }
      });
      
      renderItems();
      pushHistory("batch_update");
      
      const paramCount = commonParams.size;
      const paramTypes = renderers.length === 1 ? '所有参数' : '公共参数（位置和尺寸）';
      alert(`已批量更新 ${selectedItems.length} 个控件的${paramTypes}（${paramCount} 个参数）`);
      return;
    }
    
    // Single item mode
    const idx = Array.from(state.selected)[0];
    const it = state.items[idx];
    if (!it) return;
    
    it.x = Number(propX.value || 0);
    it.y = Number(propY.value || 0);
    it.w = Number(propW.value || 100);
    it.h = Number(propH.value || 24);
    it.label = propLabel.value || "";
    it.renderer = propRenderer.value || "text";
    
    if (propFontFamily) it.font_family = propFontFamily.value;
    if (propFontSize) it.font_size = Number(propFontSize.value || 10);
    if (propFontColor) it.font_color = propFontColor.value;
    if (propFontWeight) it.font_weight = propFontWeight.value;
    if (propTextAlign) it.text_align = propTextAlign.value;
    if (propVerticalAlign) it.vertical_align = propVerticalAlign.value;
    if (propFontStyle) it.font_style = propFontStyle.value;
    if (propEmptyPolicy) it.empty_policy = propEmptyPolicy.value;
    if (propLineHeight) it.line_height = Number(propLineHeight.value || 1.2);
    if (propLetterSpacing) it.letter_spacing = Number(propLetterSpacing.value || 0);
    if (propOverflowMarker) it.overflow_marker = propOverflowMarker.checked;
    if (propLineDirection) it.line_direction = propLineDirection.value;
    if (propLineStyle) it.line_style = propLineStyle.value;
    if (propStrokeWidth) it.stroke_width = Number(propStrokeWidth.value || 0.8);
    if (propRectRadius) it.rect_radius = Number(propRectRadius.value || 0);
    if (propStrokeColor) it.stroke_color = propStrokeColor.value;
    if (propImageUrl) it.image_url = propImageUrl.value;
    if (propImageFit) it.image_fit = propImageFit.value;
    if (propStampStatus) it.stamp_status = propStampStatus.value;
    if (propStampPack) it.stamp_pack = propStampPack.value;
    if (propSigFillMode) it.sig_fill_mode = propSigFillMode.value;
    if (propSlotIndex) it.slot_index = Math.max(1, Number(propSlotIndex.value || 1));
    if (propDeptSource) it.dept_source = propDeptSource.value;
    if (propQrSource) it.qr_source = propQrSource.value;
    if (propQrValue) it.qr_value = propQrValue.value;
    
    renderItems();
    pushHistory("update");
  });

  // Delete button
  deleteItemBtn?.addEventListener("click", () => {
    removeSelected();
  });

  // Attachment background config
  attachmentBgEnabled?.addEventListener("change", () => {
    state.attachmentBg.enabled = attachmentBgEnabled.checked;
    
    // 同步 cover_source_mode
    if (attachmentBgEnabled.checked) {
      state.coverSourceMode = "attachment";
      if (coverSourceModeEl) {
        coverSourceModeEl.value = "attachment";
      }
    } else {
      state.coverSourceMode = "base";
      if (coverSourceModeEl) {
        coverSourceModeEl.value = "base";
      }
    }
    
    if (attachmentBgFields) {
      attachmentBgFields.classList.toggle("hidden", !attachmentBgEnabled.checked);
    }
    
    if (attachmentBgEnabled.checked) {
      refreshAttachmentFieldOptions();
      // 自动加载附件底图到画布
      loadAttachmentBackground();
    } else {
      // 取消勾选时恢复正常底图
      refreshBgPreview();
    }
  });

  attachmentBgField?.addEventListener("change", () => {
    state.attachmentBg.fieldId = attachmentBgField.value || "";
    // 切换附件字段时重新加载
    if (attachmentBgEnabled?.checked) {
      loadAttachmentBackground();
    }
  });

  attachmentBgIndex?.addEventListener("change", () => {
    state.attachmentBg.attachmentIndex = Math.max(0, Number(attachmentBgIndex.value || 0));
    // 切换附件索引时重新加载
    if (attachmentBgEnabled?.checked) {
      loadAttachmentBackground();
    }
  });

  attachmentBgPage?.addEventListener("change", () => {
    state.attachmentBg.pageIndex = Math.max(0, Number(attachmentBgPage.value || 0));
    // 切换页码时重新加载
    if (attachmentBgEnabled?.checked) {
      loadAttachmentBackground();
    }
  });

  attachmentBgApplyMode?.addEventListener("change", () => {
    state.attachmentBg.applyMode = attachmentBgApplyMode.value || "print_only";
  });

  function refreshAttachmentFieldOptions() {
    if (!attachmentBgField) return;
    attachmentBgField.innerHTML = '<option value="">-- 选择附件字段 --</option>';
    const attachmentFields = (state.fields || []).filter(f => {
      const type = String(f.type || "").toLowerCase();
      return type.includes("attachment") || type.includes("ddattachment");
    });
    attachmentFields.forEach(f => {
      const opt = document.createElement("option");
      opt.value = String(f.id || "");
      opt.textContent = `${f.name || f.id} (${f.type})`;
      if (state.attachmentBg.fieldId === f.id) {
        opt.selected = true;
      }
      attachmentBgField.appendChild(opt);
    });
  }

  function syncAttachmentBgUI() {
      // 同步 cover_source_mode
    if (state.attachmentBg.enabled) {
      state.coverSourceMode = "attachment";
      if (coverSourceModeEl) {
      coverSourceModeEl.value = "attachment";
      }
    }
  



    if (attachmentBgEnabled) {
      attachmentBgEnabled.checked = state.attachmentBg.enabled;
    }
    if (attachmentBgFields) {
      attachmentBgFields.classList.toggle("hidden", !state.attachmentBg.enabled);
    }
    if (attachmentBgIndex) {
      attachmentBgIndex.value = state.attachmentBg.attachmentIndex;
    }
    if (attachmentBgPage) {
      attachmentBgPage.value = state.attachmentBg.pageIndex;
    }
    if (attachmentBgApplyMode) {
      attachmentBgApplyMode.value = state.attachmentBg.applyMode;
    }
    refreshAttachmentFieldOptions();
      // 同步 cover_source_mode
    if (state.attachmentBg.enabled) {
      state.coverSourceMode = "attachment";
      if (coverSourceModeEl) {
        coverSourceModeEl.value = "attachment";
      }
    }
  
    if (attachmentBgEnabled) {
      attachmentBgEnabled.checked = state.attachmentBg.enabled;
    }
  }

  // init history with initial state
  state.history.push(cloneItems(state.items));
  syncCoverUiState();
  syncAttachmentBgUI();
  if (stampConfig) stampConfig.classList.add("hidden");
  if (qrcodeConfig) qrcodeConfig.classList.add("hidden");
  renderPropHelp("text");
  
  // 初始化时显示默认控件类型（text）的参数
  updateParamVisibility("text");
  
  ensureFixedStatusStamp();
  renderItems();
  applyCanvasSize();
  centerCanvasInViewport();
  autoDetectOrientation().then(() => {
    refreshBgPreview();
    centerCanvasInViewport();
  });
  loadProcessGroups();
  applyZoom();
  applyGrid();
  refreshUndoRedoUI();
})();
