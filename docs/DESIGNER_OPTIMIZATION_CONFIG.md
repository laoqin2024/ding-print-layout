================================================================================
设计器优化 - 控件参数配置
================================================================================

## 控件参数配置映射

```javascript
// 控件参数配置映射
const CONTROL_PARAMS = {
  // 文本类控件
  text: {
    basic: ['x', 'y', 'w', 'h', 'label'],
    binding: ['field_id', 'field_name', 'field_type'],
    font: ['font_family', 'font_size', 'font_color', 'font_weight', 'font_style'],
    layout: ['text_align', 'vertical_align', 'line_height', 'letter_spacing'],
    behavior: ['empty_policy', 'overflow_marker', 'text_wrap']
  },
  
  // 日期控件
  date: {
    basic: ['x', 'y', 'w', 'h', 'label'],
    binding: ['field_id', 'field_name', 'field_type'],
    font: ['font_family', 'font_size', 'font_color', 'font_weight', 'font_style'],
    layout: ['text_align', 'vertical_align', 'line_height'],
    behavior: ['empty_policy']
  },
  
  // 标签控件
  label: {
    basic: ['x', 'y', 'w', 'h', 'label'],
    font: ['font_family', 'font_size', 'font_color', 'font_weight', 'font_style'],
    layout: ['text_align', 'vertical_align', 'line_height', 'letter_spacing']
  },
  
  // 签名控件
  signature: {
    basic: ['x', 'y', 'w', 'h'],
    binding: ['field_id', 'field_name', 'field_type'],
    signature: ['sig_fill_mode', 'slot_index', 'local_user_name']
  },
  
  // 部门控件
  dept: {
    basic: ['x', 'y', 'w', 'h'],
    font: ['font_family', 'font_size', 'font_color', 'font_weight', 'font_style'],
    layout: ['text_align', 'vertical_align', 'line_height'],
    dept: ['dept_source', 'slot_index']
  },
  
  // 二维码控件
  qrcode: {
    basic: ['x', 'y', 'w', 'h'],
    qrcode: ['qr_source', 'qr_value']
  },
  
  // 状态章控件
  status_stamp: {
    basic: ['x', 'y', 'w', 'h'],
    stamp: ['stamp_status', 'stamp_pack', 'stamp_fetch_url']
  },
  
  // 图片控件
  image: {
    basic: ['x', 'y', 'w', 'h'],
    image: ['image_url', 'image_fit', 'image_upload']
  },
  
  // 矩形控件
  rect: {
    basic: ['x', 'y', 'w', 'h'],
    shape: ['stroke_width', 'stroke_color', 'rect_radius']
  },
  
  // 线条控件
  line: {
    basic: ['x', 'y', 'w', 'h'],
    line: ['line_direction', 'line_style', 'stroke_width', 'stroke_color']
  },
  
  // 流程结果控件
  flow_result: {
    basic: ['x', 'y', 'w', 'h'],
    font: ['font_family', 'font_size', 'font_weight', 'font_style'],
    layout: ['text_align', 'vertical_align', 'line_height', 'letter_spacing'],
    behavior: ['overflow_marker', 'text_wrap']
  }
};

// 参数到 DOM 元素 ID 的映射
const PARAM_TO_ELEMENT = {
  // 基础参数
  x: 'prop-x',
  y: 'prop-y',
  w: 'prop-w',
  h: 'prop-h',
  label: 'prop-label',
  
  // 绑定参数
  field_id: 'prop-field-id',
  field_name: 'prop-field-name',
  field_type: 'prop-field-type',
  bind_field: 'prop-bind-field',
  
  // 字体参数
  font_family: 'prop-font-family',
  font_size: 'prop-font-size',
  font_color: 'prop-font-color',
  font_weight: 'prop-font-weight',
  font_style: 'prop-font-style',
  
  // 布局参数
  text_align: 'prop-text-align',
  vertical_align: 'prop-vertical-align',
  line_height: 'prop-line-height',
  letter_spacing: 'prop-letter-spacing',
  
  // 行为参数
  empty_policy: 'prop-empty-policy',
  overflow_marker: 'prop-overflow-marker',
  text_wrap: 'prop-text-wrap',
  
  // 形状参数
  stroke_width: 'prop-stroke-width',
  stroke_color: 'prop-stroke-color',
  rect_radius: 'prop-rect-radius',
  
  // 线条参数
  line_direction: 'prop-line-direction',
  line_style: 'prop-line-style',
  
  // 图片参数
  image_url: 'prop-image-url',
  image_fit: 'prop-image-fit',
  image_upload: 'prop-image-upload',
  
  // 状态章参数
  stamp_status: 'prop-stamp-status',
  stamp_pack: 'prop-stamp-pack',
  stamp_fetch_url: 'prop-stamp-fetch-url',
  
  // 签名参数
  sig_fill_mode: 'prop-sig-fill-mode',
  slot_index: 'prop-slot-index',
  local_user_name: 'prop-local-user-name',
  
  // 部门参数
  dept_source: 'prop-dept-source',
  
  // 二维码参数
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
  if (new Set(renderers).size > 1) {
    return new Set(['x', 'y', 'w', 'h']);
  }
  
  // 同类型控件：所有参数都是公共的
  return getSupportedParams(renderers[0]);
}
```

## 参数分组说明

### basic (基础参数)
- 所有控件都支持
- x, y, w, h: 位置和尺寸
- label: 标签文本

### binding (绑定参数)
- 需要绑定表单字段的控件
- field_id, field_name, field_type

### font (字体参数)
- 文本类控件
- font_family, font_size, font_color, font_weight, font_style

### layout (布局参数)
- 文本类控件
- text_align, vertical_align, line_height, letter_spacing

### behavior (行为参数)
- 文本类控件
- empty_policy, overflow_marker, text_wrap

### shape (形状参数)
- 矩形控件
- stroke_width, stroke_color, rect_radius

### line (线条参数)
- 线条控件
- line_direction, line_style, stroke_width, stroke_color

### image (图片参数)
- 图片控件
- image_url, image_fit, image_upload

### stamp (状态章参数)
- 状态章控件
- stamp_status, stamp_pack, stamp_fetch_url

### signature (签名参数)
- 签名控件
- sig_fill_mode, slot_index, local_user_name

### dept (部门参数)
- 部门控件
- dept_source, slot_index

### qrcode (二维码参数)
- 二维码控件
- qr_source, qr_value

================================================================================
