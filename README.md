# 医院病房管理系统 🏥

基于 **PyQt5 + MySQL** 开发的医院病房管理系统，支持多角色登录、病房管理、患者管理、医嘱管理、费用管理等核心功能。

## 功能模块

| 模块 | 功能 |
|------|------|
| 🔐 **登录系统** | 多角色登录（管理员、医生、护士、收费员） |
| 🏠 **科室管理** | 科室信息维护 |
| 🛏️ **病房管理** | 病房信息、床位分配与管理 |
| 👤 **患者管理** | 患者信息登记、查询、修改 |
| 👨‍⚕️ **医生/护士管理** | 医护人员信息管理 |
| 📋 **住院管理** | 入院登记、出院管理、转科处理 |
| 💊 **医嘱管理** | 医嘱下达、审核、执行、停止全流程 |
| 💰 **费用管理** | 费用记录、每日床位费自动计算 |
| 📊 **统计分析** | 科室占用率等统计图表 |

## 技术栈

- **前端：** PyQt5（桌面 GUI）
- **后端：** Python 3
- **数据库：** MySQL 8.0
- **数据可视化：** matplotlib

## 快速开始

### 环境要求

- Python 3.10+
- MySQL 8.0
- pip（Python 包管理器）

### 安装步骤

1. **克隆仓库**
   ```bash
   git clone https://github.com/tao-dev06/hospital-ward-system.git
   cd hospital-ward-system
   ```

2. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

3. **配置数据库**
   修改 `db/config.py` 中的数据库连接信息：
   ```python
   DB_CONFIG = {
       "host": "localhost",
       "port": 3306,
       "user": "root",
       "password": "123456",   # 修改为你的 MySQL 密码
       "database": "hospital_ward_system",
       "charset": "utf8mb4",
       "autocommit": False
   }
   ```

4. **初始化数据库**
   ```bash
   python init_db.py
   ```

5. **启动系统**
   ```bash
   python main.py
   ```

### 默认账号

| 角色 | 用户名 | 密码 |
|------|--------|------|
| 👑 管理员 | `admin` | `admin123` |
| 👨‍⚕️ 医生 | `doctor1` | `123456` |
| 👨‍⚕️ 医生 | `doctor2` | `123456` |
| 👩‍⚕️ 护士 | `nurse1` | `123456` |
| 👩‍⚕️ 护士 | `nurse2` | `123456` |
| 💰 收费员 | `cashier1` | `123456` |

## 数据库设计

### 表结构（共 10 张表）

| 表名 | 说明 |
|------|------|
| `departments` | 科室表 |
| `wards` | 病房表 |
| `beds` | 病床表 |
| `patients` | 患者信息表 |
| `doctors` | 医生信息表 |
| `nurses` | 护士信息表 |
| `inpatient_records` | 住院记录表 |
| `medical_orders` | 医嘱表 |
| `charges` | 费用记录表 |
| `daily_bed_charges` | 每日床位费记录表 |

### 其他数据库对象

- **触发器**：自动更新病床状态、计算每日床位费等
- **存储过程**：科室占用率统计、患者费用汇总等
- **视图**：在院患者视图、病床状态视图、医嘱执行视图

## 项目结构

```
hospital-ward-system/
├── main.py               # 程序入口
├── init_db.py            # 数据库初始化脚本
├── requirements.txt      # 依赖清单
├── db/
│   ├── config.py         # 数据库配置
│   └── connection.py     # 数据库连接管理
├── models/               # 数据模型层
│   ├── patient.py
│   ├── doctor.py
│   ├── nurse.py
│   ├── ward.py
│   ├── bed.py
│   ├── inpatient.py
│   ├── medical_order.py
│   ├── charge.py
│   └── department.py
├── views/                # 界面层（PyQt5）
│   ├── login_dialog.py   # 登录窗口
│   ├── main_window.py    # 主窗口
│   ├── patient_view.py   # 患者管理
│   ├── doctor_view.py    # 医生管理
│   ├── nurse_view.py     # 护士管理
│   ├── ward_view.py      # 病房管理
│   ├── bed_view.py       # 病床管理
│   ├── order_view.py     # 医嘱管理
│   ├── charge_view.py    # 费用管理
│   └── statistics_view.py# 统计分析
├── utils/
│   └── helpers.py        # 工具函数
└── sql/                  # SQL 脚本
    ├── 01_create_tables.sql
    ├── 02_insert_sample_data.sql
    ├── 03_triggers.sql
    ├── 04_procedures.sql
    └── 05_views.sql
```

## 运行截图

> *（项目运行中，可自行截图添加）*

## 开发团队

- **陶振宇** (242210788728)
- **陈尚鹏** (242210788613)

## 许可证

本项目仅供学习交流使用。
