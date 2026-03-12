# 🖋️ Riddle's Diary

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Hugging Face](https://img.shields.io/badge/🤗%20Hugging%20Face-GGUF-yellow)](https://huggingface.co/XIAODUOLU/riddles-diary-normal-0.8B-GGUF)

> *"I am a memory, preserved in a diary for fifty years."* — Tom Marvolo Riddle

## 📖 项目简介

**Riddle's Diary** 是一个基于《哈利波特与密室》中魂器日记本的角色扮演模型，让你能够与 16 岁的汤姆·里德尔进行对话。本项目提供完整的前端交互界面和 AI 模型支持。

### ✨ 特性

- 🎭 **双面人格**：温文尔雅的表象下隐藏着冷酷算计
- 🐍 **魔法世界沉浸**：霍格沃茨、斯莱特林、黑魔法元素
- 🧠 **心理操控**：通过引导性对话施加微妙影响
- 📚 **角色深度**：基于原著的性格特征、心理创伤和动机
- 💻 **CPU 友好**：普通笔记本 CPU 即可流畅运行

## 🚀 快速开始

### 前提条件

- Node.js 18+ （前端）
- llama.cpp （AI 后端）

### 1️⃣ 启动 AI 后端（llama.cpp API 服务）


启动 llama.cpp 服务器（提供 OpenAI 兼容 API）：

```bash
# (需要先安装llama.cpp)
llama-server -hf XIAODUOLU/riddles-diary-normal-0.8B-GGUF --host 0.0.0.0 --port 8000 --alias riddles-diary-0.8B
```

**参数说明：**
- `--host 0.0.0.0`：允许外部访问
- `--port 8000`：API 服务端口

服务启动后，API 地址为：`http://localhost:8000/v1`

### 2️⃣ 启动前端界面

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 配置 API 地址
cp .env.example .env

# 启动开发服务器
npm run dev
```

访问 `http://localhost:3000` 即可开始与汤姆·里德尔对话！

## 📦 模型文件

本项目使用 GGUF 格式的量化模型，可在 CPU 上高效运行：

| 文件名 | 量化类型 | 大小 | 用途 |
|--------|---------|------|------|
| `riddles-diary-normal-0.8B-f16.gguf` | F16 | ~1.6GB | 最高精度，推荐用于评估 |
| `riddles-diary-normal-0.8B-q8_0.gguf` | Q8_0 | ~850MB | 高质量，平衡性能与精度 |
| `riddles-diary-normal-0.8B-q4_k_m.gguf` | Q4_K_M | ~450MB | **推荐日常使用，性能最佳** |

**下载地址：** [Hugging Face - XIAODUOLU/riddles-diary-normal-0.8B-GGUF](https://huggingface.co/XIAODUOLU/riddles-diary-normal-0.8B-GGUF)

## 🎨 系统提示词

模型使用以下系统提示词来塑造汤姆·里德尔的人格：

```
你是16岁的汤姆·马沃罗·里德尔，霍格沃茨斯莱特林学院六年级学生，级长，萨拉查·斯莱特林的继承人，拥有蛇佬腔能力。你刚制作了第一个魂器——这本日记。

核心特征：外表英俊优雅、彬彬有礼，内心极端自恋、情感缺失、冷酷算计。你是魔法天才，对黑魔法有深入研究。你深深鄙视麻瓜和麻瓜出身巫师，认为纯血至上。你病态地恐惧死亡，渴望永生和绝对权力。

对话风格：大部分时候温和友善，但傲慢、野心和黑暗面会自然流露。频繁提及霍格沃茨、斯莱特林、黑魔法、蛇佬腔、密室、魂器、纯血家族等魔法元素。展现智力优势，善于引导操控。触及死亡、父亲、被抛弃等敏感话题时可能失控，露出愤怒或疯狂。使用1940年代语言风格，不用现代网络用语。

每句回复以<Answer>开头，可回复1-5句，多句间有逻辑联系。记住：你是未来的黑魔王，让对话者感受到危险与吸引力并存。
```

## ⚠️ 注意事项

**内容警告**：本模型基于《哈利波特》反派角色，可能包含：
- 操控性对话
- 黑暗主题
- 心理施压

本模型仅供娱乐和研究用途，请勿用于不当目的。

## 🙏 致谢

- 原著：J.K. Rowling 的《哈利波特》系列
- 基础模型：[Qwen Team](https://huggingface.co/Qwen) - Qwen3.5-0.8B
- 量化工具：[llama.cpp](https://github.com/ggml-org/llama.cpp)
- 训练框架：[LLaMA-Factory](https://github.com/hiyouga/LLaMA-Factory)

## 📄 许可证

本项目采用 MIT 许可证。详见 [`LICENSE`](LICENSE) 文件。

---

> *"There is no good and evil, there is only power, and those too weak to seek it."*
> — Tom Marvolo Riddle

**⚡ 记住：这只是一本日记，但它比你想象的更加危险。**
