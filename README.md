# Arcade · 游戏厅

三个小游戏合并成一个项目：一个入口，统一导航，本地存档。

原来分散在三个独立仓库，现在收进一个仓库、一套目录结构、一份文档。

## 三个游戏

| 游戏 | 类型 | 运行方式 | 原仓库 |
|---|---|---|---|
| **雷霆战机** | 竖屏射击 | 浏览器 | `thunder-fighter`（已并入） |
| **俄罗斯方块** | 益智 | 浏览器 | `tetris-html`（已并入） |
| **俄罗斯方块 · 桌面版** | 益智 | 本地 Python | `tetris`（已并入） |

原三个独立仓库已删除，代码、提交与说明全部收进本仓库。在线地址统一为：

- 大厅：https://jiangsubk.github.io/game-hub/
- 雷霆战机：https://jiangsubk.github.io/game-hub/games/thunder-fighter/
- 俄罗斯方块：https://jiangsubk.github.io/game-hub/games/tetris/
- 桌面版说明：https://jiangsubk.github.io/game-hub/games/tetris-pygame/

前两个点开就玩。第三个是 Pygame 原生实现，浏览器跑不了，游戏厅里保留了一个说明页，讲清楚怎么在本地运行、以及它和网页版的差异。

## 目录结构

```
game-hub/
├── index.html                  # 游戏大厅（入口）
├── assets/
│   ├── hub.css                 # 大厅样式
│   └── hub.js                  # 最高分回填、键盘快捷入口
├── games/
│   ├── thunder-fighter/
│   │   └── index.html          # 雷霆战机（原样保留 + 注入返回按钮）
│   ├── tetris/
│   │   └── index.html          # 俄罗斯方块（+ 最高分存档）
│   └── tetris-pygame/
│       └── index.html          # 桌面版说明页
├── legacy/
│   ├── tetris.py               # Pygame 版源码（466 行）
│   └── requirements.txt
└── README.md
```

## 怎么跑

**方式一：直接打开**

双击 `index.html`。全部是静态文件，没有构建步骤。

> 注意：`file://` 协议下部分浏览器会隔离 localStorage，最高分可能不保存。想要完整效果用方式二。

**方式二：本地服务器（推荐）**

```bash
cd game-hub
python -m http.server 8123
```

然后访问 http://127.0.0.1:8123/

**桌面版俄罗斯方块**

```bash
cd legacy
pip install -r requirements.txt
python tetris.py
```

## 合并时做了什么

不是简单的三个文件堆在一起，改造点如下：

1. **统一入口** — 新增游戏大厅，三张卡片带封面、标签、个人最高分
2. **统一导航** — 两个网页游戏左上角注入「← 大厅」，随时退回
3. **统一存档** — 俄罗斯方块原来不记分，现在写入 `gamehub:tetris:best`，大厅与游戏内都能读到；雷霆战机沿用 `thunderBest`
4. **修掉原有缺陷** — 俄罗斯方块顶部信息栏的「暂存」标签在窄屏会竖排换行，已修；棋盘容器溢出已修
5. **补一份说明页** — Python 版没法在浏览器跑，做了一页档案：运行命令、操作表、特性、与网页版的逐项差异、核心源码片段
6. **一套文档** — 三个 README 合成这一份

键盘 `1` `2` `3` 可以在大厅直接进入对应游戏。

## 两版俄罗斯方块的差异

| 项目 | 网页版 | 桌面版 |
|---|---|---|
| 运行环境 | 浏览器 Canvas 2D | Python 3 + Pygame（SDL） |
| 计分规则 | NES 风格 100/300/500/800 × 等级 | 同左 |
| 下落间隔下限 | 80 ms | 100 ms |
| 触屏支持 | 有 | 无 |
| 最高分存档 | localStorage | 无 |
| 退出 | 关闭页面 | ESC |

玩法逻辑同源，网页版是桌面版的移植加强版。

## 许可

MIT。三个原始项目均为 MIT。
