# Hive Mind 部署指南

## 快速开始

### 1. 环境要求

- Python 3.10+
- Node.js 18+
- Anthropic API Key（用于Claude）
- OpenAI API Key（用于GPT-4，可选）

### 2. 安装

#### 后端

```bash
cd hive-mind-platform/backend
pip install -r requirements.txt
```

#### 前端

```bash
cd hive-mind-platform/frontend
npm install
```

### 3. 配置

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，填写你的API密钥
nano .env
```

必填项：
- `ANTHROPIC_API_KEY` - Claude API密钥
- `OPENAI_API_KEY` - OpenAI API密钥（可选，用于Elon子代理）
- `SECRET_KEY` - 安全密钥（生产环境务必修改）

### 4. 启动服务

#### 方式1：本地运行

**后端：**
```bash
cd backend
python main.py
```

**前端：**
```bash
cd frontend
npm run dev
```

访问：http://localhost:5173

#### 方式2：Docker部署

```bash
# 构建镜像
docker-compose build

# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f
```

访问：http://localhost:3000

---

## 使用示例

### 1. 使用Echo（默认）

```bash
curl -X POST http://localhost:8000/api/workflow/echo \
  -H "Content-Type: application/json" \
  -d '{
    "message": "帮我优化这个项目的性能",
    "agent_type": "echo"
  }'
```

### 2. 使用Elon（技术任务）

```bash
curl -X POST http://localhost:8000/api/workflow/elon \
  -H "Content-Type: application/json" \
  -d '{
    "message": "重构用户认证模块",
    "agent_type": "elon"
  }'
```

### 3. 使用Henry（市场任务）

```bash
curl -X POST http://localhost:8000/api/workflow/henry \
  -H "Content-Type: application/json" \
  -d '{
    "message": "为重构功能写PR描述",
    "agent_type": "henry"
  }'
```

### 4. 轮询任务状态

```bash
# 获取任务列表
curl http://localhost:8000/api/tasks

# 获取单个任务状态
curl http://localhost:8000/api/tasks/task_abc123
```

### 5. WebSocket实时更新

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/main');

ws.onopen = () => {
  ws.send(JSON.stringify({
    type: 'subscribe',
    task_id: 'task_abc123'
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Task update:', data);
};
```

---

## 常见问题

### Q1: API调用失败？

检查以下几点：
- API密钥是否正确配置
- 网络连接是否正常
- API配额是否用完
- 代理设置是否正确

### Q2: 前端无法连接后端？

确保：
- 后端服务已启动（http://localhost:8000）
- 前端API URL配置正确（默认：http://localhost:8000）
- CORS设置允许前端域名

### Q3: LLM响应太慢？

优化建议：
- 使用更快的模型（如GPT-3.5）
- 减少任务复杂度
- 并行处理多个任务
- 添加缓存机制

### Q4: 如何禁用某个Agent？

在.env文件中设置：
```bash
ENABLE_ECHO=false
ENABLE_ELON=false
ENABLE_HENRY=false
```

---

## 生产部署建议

### 1. 使用反向代理

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

### 2. 使用Nginx

```bash
# 构建前端静态文件
cd frontend
npm run build

# Nginx配置
cd ../
# 使用nginx.conf模板
```

### 3. 数据库选择

- 开发/测试：内存数据库（无需配置）
- 生产：PostgreSQL
- 缓存：Redis

### 4. 安全建议

- 使用HTTPS
- 定期更新依赖
- 限制API访问频率
- 设置防火墙规则
- 定期备份数据

---

## 监控和维护

### 健康检查

```bash
curl http://localhost:8000/health
```

### 查看日志

**后端：**
```bash
tail -f backend/logs/app.log
```

**前端：**
```bash
cd frontend && npm run dev
```

### 重启服务

```bash
# 重启后端
pkill -f "python main.py"
cd backend && python main.py &

# 重启前端
pkill -f "vite"
cd frontend && npm run dev &
```

---

## 性能调优

### 后端优化

```python
# backend/main.py

# 启用缓存
app.add_middleware(CacheMiddleware, ttl=300)

# 数据库连接池
DATABASE_POOL_SIZE = 20
DATABASE_MAX_OVERFLOW = 10

# 限流
from slowapi import Limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
```

### 前端优化

```javascript
// 前端配置
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// 添加请求拦截器
axios.interceptors.request.use(config => {
  config.headers['Authorization'] = `Bearer ${token}`;
  return config;
});
```

---

## 获取帮助

- GitHub Issues: https://github.com/iiixiyan/hive-mind-platform/issues
- 文档：https://github.com/iiixiyan/hive-mind-platform/blob/main/README.md
- Email: support@hivemind.ai

---

**版本：** v0.1.1
**最后更新：** 2026-02-28
