# 停止进程和端口的命令指导

## 📋 项目端口

| 服务 | 端口 | 进程 | 说明 |
|------|------|------|------|
| Flask 后端 | 5000 | python | 主应用服务器 |
| Vite 前端开发 | 5173 | node | 前端开发服务器 |
| 其他应用 | 需要查询 | - | 根据需要查找 |

---

## 🔍 查找进程

### 1. 查看在特定端口上运行的进程

```bash
# 查看 5000 端口（Flask）
lsof -i :5000

# 查看 5173 端口（Vite）
lsof -i :5173

# 查看特定端口（替换 PORT_NUMBER）
lsof -i :PORT_NUMBER
```

### 2. 查找特定程序的所有进程

```bash
# 查找所有 Python 进程
ps aux | grep python

# 查找所有 Node.js 进程
ps aux | grep node

# 查找所有 Flask 服务器进程
ps aux | grep "python.*run.py"

# 查找 Vite 服务器进程
ps aux | grep "vite"
```

### 3. 查看进程详细信息

```bash
# 显示完整命令行（不截断）
ps -ef | grep python

# 查看进程树
pstree -p | grep python
```

---

## 🛑 停止进程

### 方法 1：按进程 ID (PID) 停止

```bash
# 正常终止进程（允许清理资源）
kill <PID>

# 例如：停止 PID 为 12345 的进程
kill 12345

# 强制杀死进程（立即结束，可能丢失数据）
kill -9 <PID>

# 例如：强制杀死 PID 为 12345 的进程
kill -9 12345
```

### 方法 2：按端口停止

```bash
# macOS/Linux - 停止在 5000 端口上的进程
lsof -i :5000 | grep LISTEN | awk '{print $2}' | xargs kill -9

# 或直接使用：
fuser -k 5000/tcp

# 停止在 5173 端口上的进程
lsof -i :5173 | grep LISTEN | awk '{print $2}' | xargs kill -9

# 或直接使用：
fuser -k 5173/tcp
```

### 方法 3：按进程名称停止

```bash
# 停止所有 Python 进程
killall python3

# 停止所有 Node.js 进程
killall node

# 使用 pkill（更精确）- 停止包含 "run.py" 的进程
pkill -f "python.*run.py"

# 停止包含 "vite" 的进程
pkill -f vite

# 强制停止
pkill -9 -f "python.*run.py"
pkill -9 -f vite
```

---

## ⚡ 快速命令

### 停止本项目的所有服务

```bash
# 停止 Flask 后端（5000 端口）
lsof -i :5000 | grep LISTEN | awk '{print $2}' | xargs kill -9

# 停止 Vite 前端（5173 端口）
lsof -i :5173 | grep LISTEN | awk '{print $2}' | xargs kill -9

# 或使用一条命令停止两个端口
lsof -i :5000,:5173 | grep LISTEN | awk '{print $2}' | xargs kill -9
```

### 使用已有的脚本停止服务

```bash
# 项目中已有重启脚本（会自动停止 Flask 服务）
bash restart_server.sh
```

---

## 🔧 创建便利脚本

### kill_flask.sh - 停止 Flask 服务

```bash
#!/bin/bash
echo "停止 Flask 服务器（端口 5000）..."
lsof -i :5000 | grep LISTEN | awk '{print $2}' | xargs kill -9 2>/dev/null && echo "✅ Flask 已停止" || echo "❌ 未找到 Flask 进程"
```

### kill_vite.sh - 停止 Vite 服务

```bash
#!/bin/bash
echo "停止 Vite 前端服务（端口 5173）..."
lsof -i :5173 | grep LISTEN | awk '{print $2}' | xargs kill -9 2>/dev/null && echo "✅ Vite 已停止" || echo "❌ 未找到 Vite 进程"
```

### kill_all.sh - 停止所有服务

```bash
#!/bin/bash
echo "停止所有服务..."
echo "停止 Flask（5000）..."
lsof -i :5000 | grep LISTEN | awk '{print $2}' | xargs kill -9 2>/dev/null && echo "✅ Flask 已停止" || echo "⚠️ Flask 进程未找到"

echo "停止 Vite（5173）..."
lsof -i :5173 | grep LISTEN | awk '{print $2}' | xargs kill -9 2>/dev/null && echo "✅ Vite 已停止" || echo "⚠️ Vite 进程未找到"

sleep 1
echo "所有服务已停止"
```

### 使用脚本

```bash
# 赋予执行权限
chmod +x kill_flask.sh
chmod +x kill_vite.sh
chmod +x kill_all.sh

# 执行脚本
./kill_flask.sh
./kill_vite.sh
./kill_all.sh
```

---

## ⚠️ 常见问题

### Q: 怎么查看进程树？
```bash
ps -ef | head -20  # 查看进程列表前 20 行
ps aux --sort=-%cpu  # 按 CPU 使用率排序
ps aux --sort=-%mem  # 按内存使用率排序
```

### Q: 如何获取特定端口的 PID？
```bash
# macOS
lsof -i :5000 | awk 'NR==2 {print $2}'

# Linux
ss -tlnp | grep :5000
```

### Q: 如何检查端口是否被占用？
```bash
# 检查 5000 端口
lsof -i :5000

# 如果输出为空，则端口未被占用
```

### Q: 强制杀死进程后应该做什么？
```bash
# 1. 等待 1-2 秒
sleep 2

# 2. 验证进程是否真的停止
lsof -i :5000

# 3. 重新启动服务
python run.py
```

---

## 📌 最佳实践

1. **先用温和的方式停止** (`kill <PID>`) 再用强制方式 (`kill -9`)
2. **总是验证进程是否真的停止** 后再启动新进程
3. **为频繁使用的命令创建别名** 提高效率
4. **记录 PID** 便于后续管理

---

## 🎯 快速参考卡片

```bash
# 查看所有开放的端口
lsof -i -P | grep LISTEN

# 停止特定端口
kill -9 $(lsof -t -i :5000)

# 查看进程及其子进程
ps -ef | grep -E "python|node"

# 清理僵尸进程
ps aux | grep Z  # 查看僵尸进程
```

---

## 🔗 相关资源

- `restart_server.sh` - 项目提供的服务重启脚本
- `app.py` - Flask 应用入口
- `frontend/` - Vite 前端项目

