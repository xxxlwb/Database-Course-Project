# NKG 设计系统配色方案 · MiniMax 风格

最终落地后的完整设计 token、字体、间距、阴影、渐变方案。可直接复制到下一个项目。

灵感来源：
- 主色板：MiniMax 官网产品卡（M2-her / Music 2.6 / Audio / Agent / 海螺视频）
- 暗色 Chrome：minimax.io 站点导航 #232A33
- 亮色画布 + 暗色侧边栏：参考 OpenAI / Vercel 控制台

---

## 1. 核心 Token

```css
:root {
  /* ============ 画布 + 表面 (浅) ============ */
  --canvas: #FFFFFF;
  --surface: #F7F8FA;
  --surface-2: #F2F3F5;
  --surface-sunken: #E5E6EB;

  /* ============ Chrome (暗色侧边栏/header) ============ */
  --chrome: #232A33;          /* 侧边栏底 (从 #181E25 提一档,更柔) */
  --chrome-2: #2D3540;        /* hover/elevated */
  --chrome-3: #3A4452;        /* 内边/分割 */
  --chrome-border: #1A2028;   /* 比 chrome 还深一档,作为外边 */

  /* ============ 文字 (在浅底上) ============ */
  --ink: #181E25;             /* 主文字,几乎是黑 */
  --ink-2: #2D3540;           /* 次主 */
  --ink-3: #4E5969;           /* 描述文字 */
  --ink-4: #86909C;           /* 弱文字 / placeholder */
  --ink-5: #C9CDD2;           /* 边界感文字 */

  /* ============ 文字 (在暗底上) ============ */
  --ink-on-dark: #FFFFFF;
  --ink-on-dark-2: #C9CDD2;
  --ink-on-dark-3: #86909C;

  /* ============ 品牌色 ============ */
  /* 紫 (主 CTA / 链接 / focus / 选中) */
  --purple: #8C7DEF;          /* 软紫,匹配 MiniMax Music 卡 */
  --purple-hover: #7367E5;
  --purple-light: #CAC9FF;
  --purple-soft: #E8E5FF;
  --purple-deep: #5A4ACF;

  /* 红 (品牌标 / danger / 删除) */
  --red: #DC4D44;             /* 暖珊瑚红 (从 #D01316 软化) */
  --red-hover: #C73E36;
  --red-soft: #FCE8E6;
  --red-deep: #8B2620;

  /* 金 (warning / 强调) */
  --gold: #E8A93D;
  --gold-light: #FFD388;
  --gold-soft: #FFF3DC;

  /* MiniMax 拓展色 (用于多卡片差异化) */
  --blue: #4A6FA5;            /* MiniMax Agent 卡深蓝 */
  --blue-light: #7FB1DA;
  --blue-soft: #DCE9F4;
  --pink: #E54998;            /* 海螺视频卡主粉 */
  --pink-light: #F6BAD2;
  --pink-soft: #F9D8E5;

  /* ============ 状态色 (Element Plus 兼容) ============ */
  --success: #00B42A;
  --success-soft: #E8F8EC;
  --warning: #FF7D00;
  --warning-soft: #FFF3E8;
  --danger: var(--red);
  --danger-soft: var(--red-soft);
  --info: #165DFF;
  --info-soft: #E8F3FF;

  /* ============ 边界 ============ */
  --border: #E5E6EB;          /* 默认 */
  --border-strong: #C9CDD2;   /* hover / focus */
  --border-faint: #F2F3F5;    /* 内嵌分割 */

  /* ============ 圆角 (几何感, 不要 pill) ============ */
  --r-sm: 4px;                /* tag / 小 chip */
  --r: 6px;                   /* 按钮 / input */
  --r-md: 8px;                /* 大按钮 / 输入区 */
  --r-lg: 10px;               /* card / dialog */
  --r-xl: 14px;               /* 大 dialog */

  /* ============ 间距 (4px base) ============ */
  --s-1: 4px;
  --s-2: 8px;
  --s-3: 12px;
  --s-4: 16px;
  --s-5: 24px;
  --s-6: 32px;
  --s-7: 48px;
  --s-8: 64px;

  /* ============ 阴影 (极淡, 主要靠 1px 边框做深度) ============ */
  --shadow-sm: 0 1px 2px rgba(24, 30, 37, 0.04);
  --shadow:    0 4px 12px rgba(24, 30, 37, 0.06);
  --shadow-lg: 0 12px 32px rgba(24, 30, 37, 0.10);

  /* focus glow (主紫) */
  --shadow-glow: 0 0 0 4px rgba(140, 125, 239, 0.14);
  --shadow-glow-red:  0 0 0 4px rgba(220, 77, 68, 0.10);
  --shadow-glow-blue: 0 0 0 4px rgba(22, 93, 255, 0.10);

  /* ============ 过渡 ============ */
  --t-fast: 120ms ease;
  --t:      180ms cubic-bezier(0.4, 0, 0.2, 1);
  --t-slow: 280ms cubic-bezier(0.4, 0, 0.2, 1);

  /* ============ 字体 ============ */
  --font:      'Manrope', -apple-system, 'PingFang SC', 'Microsoft YaHei', sans-serif;
  --font-mono: 'JetBrains Mono', 'SF Mono', Menlo, monospace;
}
```

字体加载（`<head>` 里）：
```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Manrope:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
```

---

## 2. 关键渐变片段 (拿来即用)

### 2.1 暖珊瑚 Hero 大区 (M2-her 风格)
```css
background:
  radial-gradient(ellipse 90% 80% at 25% 22%, #FFA083 0%, transparent 60%),
  radial-gradient(ellipse 70% 70% at 78% 80%, #E5544A 0%, transparent 55%),
  linear-gradient(155deg, #FF7060 0%, #EE5147 55%, #D63E36 100%);
```
配套：标题白色 + `text-shadow: 0 2px 12px rgba(120,30,25,0.25)`，强调字用 `#FFE4A8` + 下划线 `#FFD27D`。

### 2.2 品牌方块 (M 标 38×38 双层渐变)
```css
background:
  radial-gradient(circle at 25% 22%, rgba(255,200,180,0.55), transparent 55%),
  linear-gradient(135deg, #F26354 0%, #DC4D44 48%, #B8362E 100%);
box-shadow: inset 0 -1px 0 rgba(0,0,0,0.10);
/* hover: + 0 8px 22px rgba(220,77,68,0.45) */
```

### 2.3 4 张统计卡的粉彩艺术区底
```css
.t-red    { background: linear-gradient(135deg, #FCEDE9 0%, #F8DAD3 100%); }
.t-purple { background: linear-gradient(135deg, #F1EEFC 0%, #E2DCF8 100%); }
.t-blue   { background: linear-gradient(135deg, #E8F0F8 0%, #CFDFF0 100%); }
.t-pink   { background: linear-gradient(135deg, #FAE3EC 0%, #F5C9DC 100%); }
```

每张卡内的 SVG 装饰色（同色系 3-4 档明度）：
| 卡 | 浅 → 中 → 深 |
|---|---|
| 主题空间 (red) | `#FBE0DA` → `#F4B4AB` → `#E58075` → `#DC4D44` |
| 文档 (purple) | `#E8E5FF` → `#D9D2F8` → `#B4A8F0` → `#8C7DEF` |
| 实体 (blue) | `#DCE9F4` → `#A6C8E5` → `#7FB1DA` → `#4A6FA5` |
| 关系 (pink) | `#F8C5D9` → `#EE5BAB` → `#C8367F` |

---

## 3. 排版规则

| 元素 | font-size | font-weight | letter-spacing | font-family |
|---|---|---|---|---|
| h1 (page title) | 28px | 700 | -0.02em | 主 |
| h2 (section title) | 20px | 600 | -0.01em | 主 |
| h3 | 16px | 600 | -0.01em | 主 |
| 大数字 (stat) | 32-44px | 700 | -0.025em | 主 + `font-feature-settings: 'tnum'` |
| Body | 14-15px | 400 | normal | 主 |
| 按钮 / nav | 13-14px | 500 | 0.005em | 主 |
| Eyebrow / label | 11-12px | 600 | 0.04-0.18em UPPERCASE | 主 或 mono |
| 代码 / SQL / meta | 11-13px | 400-500 | 0.04em | mono |

中文衬线感：所有标题加 `letter-spacing: -0.01em ~ -0.025em` 收紧 → 现代感强。

---

## 4. 微交互 (统一规则)

```css
.btn-or-card {
  transition: transform var(--t), box-shadow var(--t),
              background var(--t), border-color var(--t), color var(--t);
}
.btn-or-card:hover {
  transform: translateY(-1px);          /* 卡片用 -3px */
  box-shadow: var(--shadow-sm);         /* 卡片用 var(--shadow) */
  border-color: var(--border-strong);
}
.btn-or-card:active { transform: translateY(0); }

/* focus ring (无障碍) */
.btn-or-card:focus-visible { box-shadow: var(--shadow-glow); }
```

**禁忌**：
- ❌ scale 1.05 弹跳 (太"AI slop")
- ❌ rotate
- ❌ 大幅度颜色翻转
- ✅ 只做 1-3px translateY + 阴影 + 颜色微调

---

## 5. 状态胶囊 (status pill)

```css
.status-pill {
  display: inline-flex; align-items: center;
  font-size: 11px; font-weight: 600;
  padding: 2px 8px; border-radius: var(--r-sm);
  letter-spacing: 0.04em; text-transform: uppercase;
}
.status-pill.s-pending  { color: var(--ink-3);   background: var(--surface-2); }
.status-pill.s-running  { color: var(--warning); background: var(--warning-soft); }
.status-pill.s-completed{ color: var(--success); background: var(--success-soft); }
.status-pill.s-failed   { color: var(--red);     background: var(--red-soft); }
```

---

## 6. 技术栈 chip 配色 (用于"Powered by ..." 标签)

每个技术栈悬停时变成自己的官方品牌色：

| 技术 | hover bg | hover border | hover text | hover dot halo |
|---|---|---|---|---|
| MySQL | `rgba(0,117,143,0.22)` | `#00758F` | `#B8E5EE` | 蓝 4px 光晕 |
| FastAPI | `rgba(0,150,136,0.22)` | `#009688` | `#9FE5DD` | 蒂芙尼绿光晕 |
| Vue 3 | `rgba(65,184,131,0.22)` | `#41B883` | `#B5E6CE` | Vue 绿光晕 |
| MiniMax | `rgba(255,210,125,0.26)` | `#FFD27D` | `white` | 金光晕 + dot scale 1.15x |
| React | `rgba(97,218,251,0.22)` | `#61DAFB` | `#B5EBF7` | 浅蓝光晕 |
| Python | `rgba(53,114,165,0.22)` | `#3572A5` | `#B5D0E5` | 深蓝光晕 |
| Go | `rgba(0,173,216,0.22)` | `#00ADD8` | `#B5E6F0` | 青光晕 |

---

## 7. Element Plus 必须 override 的 token (一锅端)

```css
:root {
  /* primary → 紫 */
  --el-color-primary: var(--purple);
  --el-color-primary-light-9: var(--purple-soft);
  --el-color-primary-dark-2: var(--purple-hover);

  /* danger → 红 */
  --el-color-danger: var(--red);
  --el-color-danger-light-9: var(--red-soft);

  /* 状态 */
  --el-color-success: var(--success);
  --el-color-warning: var(--warning);
  --el-color-info: var(--ink-3);

  /* 文字 */
  --el-text-color-primary: var(--ink);
  --el-text-color-regular: var(--ink-2);
  --el-text-color-secondary: var(--ink-3);
  --el-text-color-placeholder: var(--ink-4);

  /* 边框 */
  --el-border-color: var(--border);
  --el-border-color-light: var(--border);
  --el-border-color-extra-light: var(--border-faint);
  --el-border-color-dark: var(--border-strong);

  --el-border-radius-base: var(--r);
  --el-border-radius-small: var(--r-sm);

  /* 字体 */
  --el-font-family: var(--font);
  --el-font-size-base: 14px;
}
```

加上一组组件级 override（按钮 / table / dialog / tabs / menu 等）见 `frontend/src/styles/theme.css` 完整文件。

---

## 8. 整套色彩使用规则 (要记住这个)

| 场景 | 用色 | 理由 |
|---|---|---|
| 主 CTA 按钮 | 紫 `#8C7DEF` | 不刺眼,长时间看不累 |
| 删除/危险按钮 | 红 `#DC4D44` 描边 + hover 填充 | 语义明确 |
| 品牌标 / Logo | 红渐变 (M2-her) | 暖色更有记忆点 |
| 链接 / 视图全部 / "→ 查看" | 紫 | 与主 CTA 统一 |
| 暗色侧边栏 | `#232A33` 比纯黑柔一档 | 接 MiniMax 站点 chrome |
| 侧边栏 active 高亮 | 紫色 14% 透明底 + 紫色 3px 左竖条 | 不抢戏 |
| 输入框 focus | 紫色 1.5px 内描边 + 紫色 4px 外发光 | 一致性 |
| 选区 (::selection) | 紫色 + 白字 | 一致性 |
| Dashboard 多卡片 | 红 / 紫 / 蓝 / 粉 各一,粉彩底 + 同色系 SVG 形状 | 区分度 |
| 状态条 (Tag/Pill) | success/warning/danger/info 自己的 soft 底 + 主色字 | 信息密度高 |
| 表头 | `--surface` 浅灰底 + 12px UPPERCASE | 区分主体 |
| 分页/选中 | 紫 | 一致性 |

---

## 9. 一句话使用建议

> **暗色侧边栏稳重，浅色画布读得清，紫色当主调显高级，红色留给品牌和危险动作，浅彩底+SVG 装饰让 Dashboard 不无聊。所有过渡 180ms，悬停只抬 1-3px 不弹跳。**

---

## 10. 完整 theme.css 在哪

复用时直接抄走：`frontend/src/styles/theme.css`。

新项目接入步骤：
1. 在 `index.html` 加 Manrope + JetBrains Mono link
2. 把 `theme.css` 拷贝到 `src/styles/`
3. 在 `main.ts`/`main.tsx` 里 **必须**在 Element Plus CSS 之后 import：
   ```ts
   import 'element-plus/dist/index.css'
   import './styles/theme.css'  // 必须在 element-plus 之后,override 才生效
   ```
4. 任何组件直接用 `var(--purple)` / `var(--ink)` / `var(--r-md)` / `var(--t)` 等
