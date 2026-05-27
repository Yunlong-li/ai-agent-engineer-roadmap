# GitHub Pages 部署指南

这个目录已经可以作为一个独立 GitHub 仓库使用。推到 GitHub 后，可以用 GitHub Pages 自动部署成一个手机可访问的网站。

## 1. 本地预览

```powershell
npm install
npm run docs:dev
```

打开终端输出的本地地址，通常是：

```text
http://localhost:5173
```

构建检查：

```powershell
npm run docs:build
npm run docs:preview
```

## 2. 创建 GitHub 仓库

建议仓库名：

```text
ai-agent-engineer-roadmap
```

如果这个目录本身还不是 Git 仓库，可以在 `ai-agent-engineer-roadmap` 目录里执行：

```powershell
git init
git add .
git commit -m "init vitepress roadmap site"
git branch -M main
git remote add origin https://github.com/<你的用户名>/ai-agent-engineer-roadmap.git
git push -u origin main
```

## 3. 开启 GitHub Pages

进入 GitHub 仓库：

```text
Settings -> Pages -> Build and deployment -> Source -> GitHub Actions
```

之后每次推送到 `main` 分支，`.github/workflows/deploy.yml` 都会自动构建并部署。

默认访问地址通常是：

```text
https://<你的用户名>.github.io/ai-agent-engineer-roadmap/
```

## 4. base 路径说明

如果部署到普通项目页：

```text
https://<你的用户名>.github.io/ai-agent-engineer-roadmap/
```

当前配置会自动使用：

```text
/ai-agent-engineer-roadmap/
```

如果你部署到用户主页仓库：

```text
https://<你的用户名>.github.io/
```

仓库名通常是：

```text
<你的用户名>.github.io
```

当前配置会自动使用：

```text
/
```

如果你绑定了自定义域名，并且站点部署在根路径，可以在 GitHub 仓库的 `Settings -> Secrets and variables -> Actions -> Variables` 增加：

```text
VITEPRESS_BASE=/
```

## 5. 常见问题

### 页面样式或链接错乱

大概率是 `base` 路径不对。普通项目页需要 `/<仓库名>/`，自定义域名根路径需要 `/`。

### GitHub Actions 没有运行

检查：

- 仓库默认分支是否是 `main`。
- `.github/workflows/deploy.yml` 是否在仓库根目录。
- Pages 的 Source 是否选择了 GitHub Actions。

### Mermaid 图没有显示

本项目已经在 VitePress 主题中集成了 `mermaid` 渲染。如果线上不显示，先检查构建日志里依赖是否安装成功。

