# Cat Food Backend

[![codecov](https://codecov.io/gh/TJCatFood/backend/branch/main/graph/badge.svg?token=C1YPF6SH0G)](https://codecov.io/gh/TJCatFood/backend/)

![Django CI/CD Workflow](https://github.com/TJCatFood/backend/workflows/Django%20CI/CD%20Workflow/badge.svg)

## 目录结构

```
.
|─catfood                # Django Project
|   ├─manage.py          # CLI 工具
|   ├─catfood            # Django App，web 入口
|   |    ├─__init__.py   # 标识这是一个 python 包
|   |    ├─asgi.py       # ASGI 兼容支持
|   |    ├─settings.py   # 全局 配置文件，目前为 Debug 模式
|   |    ├─urls.py       # 全局 路由
|   |    ├─views.py      # 本模块 views
|   |    └wsgi.py        # WSGI 兼容
|   |
|   ├─module0
|   ├─module1
|   ├─module2
|   └─module3            # 其他功能模块，和 /catfood/catfood 平级目录,配置作用于本功能模块
|                                                  
├─requirements           # python 依赖目录
|    ├─dev.txt           # 开发环境依赖
|    └─prod.txt          # 生产环境部署依赖
├─Dockerfile.web.dev     # 开发环境 Dockerfile
├─docker-compose.yml     # 开发环境 docker compose 配置
└README.md               # 说明
```

## 如何开始

请先仔细阅读 [**如何获取和提交源码**](https://github.com/TJCatFood/README)

### 配置 Docker 和 Docker Compose

- [如何在 Linux 安装 Docker (TUNA/docker-ce)](https://mirrors.tuna.tsinghua.edu.cn/help/docker-ce/)

- [如何安装 Docker Compose](https://docs.docker.com/compose/install/)

- [清华大学学生网络与开源软件协会 (TUNA) 镜像站](https://mirrors.tuna.tsinghua.edu.cn/)

- [网易 Docker Hub 镜像](https://hub-mirror.c.163.com/)

- [Docker 文档](https://docs.docker.com/)


### 使用 Docker 环境开发

**注意！**
- **不要滥用 sudo**
- 在本地开发分支中执行以下操作
- 所有对于 `catfood` 下文件的修改都与本地目录同步
- DB 的数据会持久化存储在 `.persistence` 下，删除请使用

    ```
    # sudo rm -rf .persistence #
    ```
#### 启动 Web 服务器

进入代码根目录，运行

```
USER_ID=`id -u` GROUP_ID=`id -g` docker-compose up
```

不要关闭终端，使用代码编辑器修改代码

在 `http://127.0.0.1:8000` 可以访问 Web API，本地文件保存时会自动刷新服务器

#### 在 Docker 中运行指令

找到 web 的容器

```
docker ps
```

打开交互 Shell

```
docker exec -it <container name or id> /bin/bash 
```

#### 关闭 Web 服务器

```
docker-compose down
```

了解其他配置可以阅读 `Dockerfile.web.dev` 和 `docker-compose.yml`

### VSCode 使用建议

#### VSCode Docker

[Docker](https://marketplace.visualstudio.com/items?itemName=ms-azuretools.vscode-docker)

##### 打开 Docker 的 Shell

![VSCode Docker](./image/vscode-docker.png)

#### VSCode Remote

[Remote - Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)

##### Remote Dev in Docker

点击左下角 `><` 图标，选择 Attach to Running Container

![VSCode Remote Container](./image/vscode-remote-container.png)
