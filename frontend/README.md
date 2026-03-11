# 汤姆·里德尔的日记 - Tom Riddle's Diary

一个基于 React + TypeScript + Vite 构建的交互式魔法日记应用，灵感来自《哈利·波特与密室》中的汤姆·里德尔日记。

## 特性

- 🎨 精美的 3D 翻页效果
- ✨ 魔法般的墨水渗透动画
- 💬 与汤姆·里德尔的互动对话
- 📱 响应式设计，支持移动端和桌面端
- ⚡ 使用 Vite 构建，开发体验极佳

## 技术栈

- **React 18** - UI 框架
- **TypeScript** - 类型安全
- **Vite** - 构建工具
- **Tailwind CSS** - 样式框架
- **CSS3** - 3D 动画效果

## 快速开始

### 安装依赖

```bash
npm install
```

### 开发模式

```bash
npm run dev
```

应用将在 `http://localhost:3000` 启动。

### 构建生产版本

```bash
npm run build
```

### 预览生产版本

```bash
npm run preview
```

## 项目结构

```
frontend/
├── src/
│   ├── components/          # React 组件
│   │   ├── TomRiddleDiary.tsx
│   │   └── MetalCorner.tsx
│   ├── styles/              # 样式文件
│   │   └── diary.css
│   ├── types/               # TypeScript 类型定义
│   │   └── index.ts
│   ├── App.tsx              # 根组件
│   ├── main.tsx             # 应用入口
│   └── index.css            # 全局样式
├── index.html               # HTML 模板
├── vite.config.ts           # Vite 配置
├── tsconfig.json            # TypeScript 配置
├── tailwind.config.js       # Tailwind 配置
└── package.json             # 项目依赖
```

## 使用说明

1. 点击日记封面上的 "T. M. Riddle" 打开日记
2. 在打开的页面上输入文字与汤姆·里德尔对话
3. 按 Enter 键发送消息
4. 点击右上角的 "合上日记" 关闭日记

## 互动关键词

尝试输入以下关键词与汤姆对话：
- 你好 / hello
- 谁 / who
- 密室 / chamber / secret
- 伏地魔 / voldemort
- 哈利·波特 / harry potter
- 魔法 / magic
- 邓布利多 / dumbledore
- 魂器 / horcrux

## 开发

### 代码规范

项目使用 ESLint 进行代码检查：

```bash
npm run lint
```

### 类型检查

TypeScript 配置为严格模式，确保类型安全。

## License

MIT
