# AI 资讯应用 - 项目规范

## 1. 项目概述

### 项目名称
**AI News** - 智能资讯聚合应用

### 核心定位
一款跨平台（iOS/Android/HarmonyOS）AI 资讯应用，通过大模型自动抓取、生成摘要和评价，为用户提供高质量的资讯消费体验。

### 目标用户
- 需要快速获取行业资讯的专业人士
- 对 AI 技术感兴趣的技术爱好者
- 希望节省阅读时间的知识工作者

---

## 2. 系统架构

### 整体架构
```
┌─────────────────────────────────────────────────────────────────┐
│                         移动端 (Flutter)                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │   资讯   │  │   搜索   │  │   收藏   │  │   设置   │        │
│  │   列表   │  │   功能   │  │   功能   │  │   功能   │        │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │   API 网关       │
                    │   (Nginx/CDN)    │
                    └──────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      后端服务 (Python FastAPI)                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  资讯 API    │  │  用户 API    │  │  管理 API    │          │
│  │  服务        │  │  服务        │  │  服务        │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│                              │                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  LLM Agent   │  │  爬虫 Agent  │  │  定时任务    │          │
│  │  (摘要/评价) │  │  (信息抓取)  │  │  调度器      │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │   MongoDB        │
                    │   (资讯/用户)    │
                    └──────────────────┘
```

---

## 3. 功能模块

### 3.1 移动端功能

#### 3.1.1 资讯列表模块
| 功能 | 描述 |
|------|------|
| 分类浏览 | 按科技、财经、教育、健康等分类展示资讯 |
| 列表展示 | 卡片式列表，显示标题、摘要预览、来源、发布时间 |
| 下拉刷新 | 下拉刷新获取最新资讯 |
| 加载更多 | 上滑加载更多历史资讯 |
| 搜索功能 | 关键词搜索资讯 |

#### 3.1.2 资讯详情模块
| 功能 | 描述 |
|------|------|
| 摘要展示 | AI 生成的资讯摘要（100-200字） |
| 评价展示 | AI 对资讯的分析评价（50-100字） |
| 来源跳转 | 点击来源链接跳转到原始资讯页面 |
| 收藏功能 | 收藏当前资讯 |
| 分享功能 | 分享资讯给好友 |

#### 3.1.3 个人中心模块
| 功能 | 描述 |
|------|------|
| 收藏列表 | 查看已收藏的资讯 |
| 阅读历史 | 浏览历史记录 |
| 设置选项 | 主题切换、通知设置、清除缓存 |

### 3.2 后端功能

#### 3.2.1 爬虫 Agent
| 功能 | 描述 |
|------|------|
| 定时抓取 | 每小时自动从预设来源抓取新资讯 |
| 多源支持 | 支持 RSS、API、网页爬取多种方式 |
| 去重处理 | 基于标题/内容哈希去重 |
| 增量更新 | 仅抓取新增内容 |

#### 3.2.2 LLM 处理 Agent
| 功能 | 描述 |
|------|------|
| 摘要生成 | 将长文内容压缩为100-200字摘要 |
| 评价生成 | 生成50-100字的分析评价 |
| 标签提取 | 自动提取资讯关键词/标签 |
| 分类判断 | 判断资讯所属分类 |

#### 3.2.3 API 服务
| 接口 | 方法 | 描述 |
|------|------|------|
| `/api/v1/news` | GET | 获取资讯列表（支持分页、分类筛选） |
| `/api/v1/news/{id}` | GET | 获取资讯详情 |
| `/api/v1/news/search` | GET | 搜索资讯 |
| `/api/v1/categories` | GET | 获取分类列表 |
| `/api/v1/users/favorites` | GET/POST/DELETE | 收藏管理 |
| `/api/v1/admin/refresh` | POST | 手动触发资讯刷新 |

---

## 4. 数据模型

### 4.1 News 资讯表
```json
{
  "_id": "ObjectId",
  "title": "string",           // 标题
  "summary": "string",         // AI生成的摘要
  "evaluation": "string",       // AI生成的评价
  "content": "string",         // 原始内容（可选存储）
  "source_name": "string",     // 来源名称
  "source_url": "string",      // 原始链接
  "category": "string",        // 分类
  "tags": ["string"],          // 标签
  "published_at": "datetime",  // 发布时间
  "created_at": "datetime",    // 创建时间
  "updated_at": "datetime",    // 更新时间
  "view_count": "int",         // 浏览次数
  "is_active": "bool"          // 是否显示
}
```

### 4.2 User 用户表
```json
{
  "_id": "ObjectId",
  "openid": "string",          // 第三方OpenID
  "nickname": "string",        // 昵称
  "avatar": "string",          // 头像URL
  "favorites": ["ObjectId"],   // 收藏的资讯ID列表
  "history": [                 // 浏览历史
    {
      "news_id": "ObjectId",
      "viewed_at": "datetime"
    }
  ],
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### 4.3 Category 分类表
```json
{
  "_id": "ObjectId",
  "name": "string",            // 分类名称
  "code": "string",            // 分类代码
  "icon": "string",            // 图标
  "sort_order": "int",         // 排序
  "is_active": "bool"
}
```

### 4.4 NewsSource 资讯来源表
```json
{
  "_id": "ObjectId",
  "name": "string",            // 来源名称
  "url": "string",             // 来源URL
  "type": "string",            // rss/api/html
  "config": "object",          // 爬取配置
  "is_active": "bool",
  "last_fetch_at": "datetime"
}
```

---

## 5. 技术栈

### 5.1 前端 (Flutter)
| 组件 | 技术选型 |
|------|---------|
| 框架 | Flutter 3.x |
| 状态管理 | Riverpod / GetX |
| 网络请求 | Dio |
| 本地存储 | SharedPreferences / Hive |
| 路由 | GoRouter |
| UI组件 | Material Design 3 |

### 5.2 后端 (Python)
| 组件 | 技术选型 |
|------|---------|
| 框架 | FastAPI |
| 异步任务 | Celery + Redis |
| 数据库 | MongoDB + Motor (异步驱动) |
| LLM集成 | LangChain (支持多LLM切换) |
| 爬虫 | Playwright / RSS解析 |
| 定时任务 | APScheduler |

### 5.3 部署
| 组件 | 技术选型 |
|------|---------|
| 容器化 | Docker / Docker Compose |
| Web服务器 | Nginx |
| 反向代理 | Nginx |

---

## 6. 项目目录结构

```
ai_news_app/
├── frontend/                    # Flutter前端
│   ├── lib/
│   │   ├── main.dart
│   │   ├── app/
│   │   │   ├── app.dart
│   │   │   ├── routes.dart
│   │   │   └── theme.dart
│   │   ├── pages/
│   │   │   ├── home/
│   │   │   ├── news_detail/
│   │   │   ├── search/
│   │   │   ├── favorites/
│   │   │   └── settings/
│   │   ├── widgets/
│   │   │   ├── news_card.dart
│   │   │   ├── category_tab.dart
│   │   │   └── loading.dart
│   │   ├── services/
│   │   │   ├── api_service.dart
│   │   │   └── storage_service.dart
│   │   ├── models/
│   │   │   ├── news.dart
│   │   │   └── user.dart
│   │   └── providers/
│   │       ├── news_provider.dart
│   │       └── user_provider.dart
│   ├── pubspec.yaml
│   └── ios/android/鸿蒙相关
│
├── backend/                     # Python后端
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── models/
│   │   │   ├── news.py
│   │   │   ├── user.py
│   │   │   └── source.py
│   │   ├── schemas/
│   │   │   ├── news.py
│   │   │   └── user.py
│   │   ├── routers/
│   │   │   ├── news.py
│   │   │   ├── user.py
│   │   │   └── admin.py
│   │   ├── services/
│   │   │   ├── llm_service.py
│   │   │   └── crawler_service.py
│   │   └── agents/
│   │       ├── crawler_agent.py
│   │       └── summary_agent.py
│   ├── requirements.txt
│   └── Dockerfile
│
└── docker-compose.yml           # 部署配置
```

---

## 7. 界面设计方向

### 设计风格
- **风格**: 极简主义 + 高级感
- **关键词**: 简洁、留白、现代、专业
- **字体**: 使用系统默认字体，清晰易读

### 色彩方案
| 用途 | 颜色 |
|------|------|
| 主色 | #1A1A2E (深蓝黑) |
| 次色 | #16213E (深蓝) |
| 强调色 | #E94560 (玫红) |
| 背景色 | #FFFFFF / #F5F5F7 |
| 文字色 | #1D1D1F / #86868B |

### 布局特点
- 单栏布局为主，信息密度适中
- 大图配小文的卡片设计
- 底部导航栏4个入口
- 详情页沉浸式阅读体验

---

## 8. 开发计划

### Phase 1 - 基础架构
- [x] 项目脚手架搭建
- [x] Flutter项目初始化
- [x] FastAPI后端初始化
- [x] MongoDB数据库设计

### Phase 2 - 核心功能
- [x] 资讯列表API与界面
- [x] 资讯详情API与界面
- [x] 分类浏览功能
- [x] 搜索功能

### Phase 3 - 用户功能
- [x] 用户注册/登录（手机号/邮箱/第三方）
- [x] 收藏功能
- [x] 阅读历史
- [x] 用户设置

### Phase 4 - AI功能（LLM接口预留）
- [x] LLM服务接口设计
- [x] 爬虫Agent开发
- [x] 摘要生成接口（LLM可后续集成）
- [x] 评价生成接口（LLM可后续集成）
- [x] LangChain LLM Provider 实现
- [x] 定时任务调度器

### Phase 5 - 优化与部署
- [x] 性能优化（MongoDB索引、分页加载）
- [x] Docker部署配置
- [x] Nginx反向代理配置
- [x] 测试与bug修复

---

## 9. 已确认事项

1. **LLM选择**: 预留接口，暂不集成（可后续灵活切换 OpenAI GPT / Claude / 本地模型）
2. **用户系统**: 需要登录（邮箱注册/登录）
3. **数据规模**: 默认配置
4. **部署环境**: 云服务器（阿里云/腾讯云）

---

*文档版本: v1.1*
*创建日期: 2026-04-30*
