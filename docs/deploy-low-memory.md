# 小服务器部署指南 (2C2G / 4G 内存)

> 适用：1-2 vCPU、1-4 GB 内存的入门级云服务器（阿里云/腾讯云/华为云轻量应用服务器、AWS Lightsail、DigitalOcean basic droplet）

## 默认开发模式的内存账单

| 进程 | 内存占用 | 说明 |
|---|---|---|
| MySQL 8（默认配置） | 500-700 MB | innodb_buffer_pool_size=128M + 各种 buffer + performance_schema |
| Vite dev server | 400-500 MB | Node.js + esbuild + HMR watcher |
| uvicorn --reload | 200-280 MB | Python + watchfiles 监听 + SQLAlchemy 默认连接池 10+5 |
| **合计** | **~1.2 GB** | |

2GB 服务器扣掉 OS（~250MB）+ 文件缓存，**直接爆**。

## 优化后

| 进程 | 内存占用 | 节省 |
|---|---|---|
| MySQL 8（low-mem.cnf） | 150-220 MB | **-400 MB** |
| nginx 静态托管 | 10-20 MB | **-450 MB**（不再跑 vite dev） |
| uvicorn --no-reload --workers 1 | 90-140 MB | **-130 MB** |
| **合计** | **~280 MB** | **-900 MB** |

省下 800-900 MB，2GB 服务器可以舒舒服服跑还剩 1GB+ 余量。

---

## 部署步骤

### 1. MySQL 调小（最大单项收益）

```bash
sudo cp scripts/mysql-low-mem.cnf /etc/mysql/mysql.conf.d/99-low-mem.cnf
sudo systemctl restart mysql
# 验证
sudo systemctl status mysql
ps -o rss= -p $(pidof mysqld) | awk '{print $1/1024 " MB"}'
# 期望: 150-220 MB
```

### 2. 后端用生产模式起

```bash
# 编辑 .env 把连接池调小
echo "DB_POOL_SIZE=2" >> .env
echo "DB_MAX_OVERFLOW=1" >> .env

# 用新加的 backend-prod 目标(无 --reload)
make backend-prod
```

或后台跑：
```bash
nohup make backend-prod > backend.log 2>&1 &
```

更稳定的方式：用 systemd 托管（见下文）。

### 3. 前端 build 后用 nginx 服务

```bash
# build (本机或服务器都可,服务器内存够才能 build)
make frontend-build

# 装 nginx
sudo apt-get install -y nginx

# 部署 vhost
sudo cp scripts/nginx-nkg.conf /etc/nginx/sites-available/nkg
# 改 root 路径为你的实际目录
sudo nano /etc/nginx/sites-available/nkg
# 启用
sudo ln -sf /etc/nginx/sites-available/nkg /etc/nginx/sites-enabled/nkg
sudo nginx -t && sudo systemctl reload nginx
```

访问 `http://你的IP/`，nginx 把 `/api/*` 自动转给 8000 端口的 uvicorn。

> **不要再开 5173 端口** — vite dev 不再用了，5173 端口可以从安全组移除，把 80 端口加进去。

### 4. 实在不想装 nginx？降级方案

用 Python 自带 http.server（内存约 15 MB）：
```bash
make frontend-serve   # 等价 npm run build + python3 -m http.server 5173 -d frontend/dist
```

但这样 `/api` 请求不会代理，需要前端代码用绝对地址 `http://server-ip:8000/api`，并且后端 CORS 要允许你的 IP（已默认允许 `http://localhost:5173`，需要改 `backend/app/main.py` 的 `allow_origins`）。

---

## systemd 托管（推荐生产用）

防止你 ssh 断了进程被杀。两个 service 文件：

### /etc/systemd/system/nkg-backend.service

```ini
[Unit]
Description=NKG FastAPI Backend
After=network.target mysql.service
Wants=mysql.service

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/projects/Database-Course-Project/backend
EnvironmentFile=/home/ubuntu/projects/Database-Course-Project/.env
ExecStart=/home/ubuntu/.local/bin/uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 1 --no-server-header --proxy-headers
Restart=always
RestartSec=5

# 内存限制
MemoryHigh=200M
MemoryMax=300M

[Install]
WantedBy=multi-user.target
```

启用：
```bash
sudo systemctl daemon-reload
sudo systemctl enable --now nkg-backend
sudo systemctl status nkg-backend
journalctl -u nkg-backend -f   # 看日志
```

---

## 监控内存

```bash
# 总览
free -h

# 按进程排序
ps aux --sort=-rss | head -10

# 实时看 NKG 进程
watch -n 2 "ps -o pid,rss,cmd --sort=-rss -p \$(pgrep -d, -f 'uvicorn|mysqld|nginx') 2>/dev/null"
```

如果 MySQL 还吃太多：
```bash
sudo mysql -e "SHOW VARIABLES LIKE 'innodb_buffer_pool_size';"
# 当前值,可以再调小到 64M(性能会差一点)

# 看实际内存使用
sudo mysql -e "SELECT * FROM performance_schema.memory_summary_global_by_event_name ORDER BY current_alloc DESC LIMIT 5;" 2>/dev/null || \
echo "performance_schema 已关 (符合预期)"
```

---

## 极限省内存（1GB 服务器）

如果只有 1GB（比如 1C1G）：

1. MySQL `innodb_buffer_pool_size = 48M`、`max_connections = 15`
2. uvicorn 只用 `--workers 1` 不开 reload
3. SQLAlchemy `DB_POOL_SIZE=1` `DB_MAX_OVERFLOW=1`
4. **关 swap 看一眼**：`sudo swapon --show` — 如果没有，建一个 1G swap 救命：
   ```bash
   sudo fallocate -l 1G /swapfile
   sudo chmod 600 /swapfile
   sudo mkswap /swapfile
   sudo swapon /swapfile
   echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
   ```

swap 比 OOM kill 体验好得多，虽然慢，但服务不会挂。

---

## 总结回顾

| 操作 | 内存收益 | 时间成本 |
|---|---|---|
| MySQL 配 low-mem.cnf | -400 MB | 1 min |
| 前端 build + nginx | -450 MB | 10 min（含装 nginx） |
| 后端 `backend-prod` 替代 `backend` | -130 MB | 30 sec |
| 连接池缩小 (DB_POOL_SIZE=2) | -20 MB | 30 sec |
| 加 1G swap (兜底) | 不省，但防 OOM | 1 min |

**最快路径**：先做前两项，省 850 MB，2C2G 立刻舒坦。
