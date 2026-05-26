# 本機開發設定

本文件說明在本機跑起 ProgramWeb 所需的步驟，以及**目前程式碼中需要留意 / 調整的檔案**。
正式部署請見 `DEPLOY_AZURE.md`。

---

## 1. 環境需求

- Python 3.12（與 Azure 一致）
- PostgreSQL 13+（本專案資料庫引擎為 `django.db.backends.postgresql`）
- Git

---

## 2. 快速開始

```bash
# 1. 取得程式碼
git clone <repo-url>
cd ProgramWeb

# 2. 建立並啟用虛擬環境
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

# 3. 安裝套件
pip install -r requirements.txt

# 4. 設定環境變數
cp .env.example .env              # 接著編輯 .env 填入實際值

# 5. 建立本機 PostgreSQL 資料庫（名稱需與 .env 的 DATABASE_NAME 一致）
#    psql -U postgres -c "CREATE DATABASE programweb;"

# 6. 套用 migration、建立管理員
python manage.py migrate
python manage.py createsuperuser

# 7. 啟動開發伺服器
python manage.py runserver        # http://127.0.0.1:8000/
```

---

## 3. 本機開發需要修改 / 留意的檔案

### 3-1. `.env`（必改）

由 `.env.example` 複製而來，是唯一需要每位開發者各自填寫的檔案。本機開發建議值：

```dotenv
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=http://localhost:8000,http://127.0.0.1:8000
DATABASE_HOST=localhost
DATABASE_PORT=5432
```

`GEMINI_API_KEY` 為 AI 難度分析（`ai/views.py`）所需；若暫不開發該功能可填任意佔位字串，但呼叫到分析時會失敗。

### 3-2. `ProgramWeb/settings.py`（現況提醒）

目前以下設定為**硬編碼**，與本機開發直接相關：

| 項目 | 目前值（硬編碼） | 影響 |
|------|------------------|------|
| `DEBUG` | `True`（第 30 行） | 本機可用，但正式環境須改 False |
| `ALLOWED_HOSTS` | 含 `localhost,127.0.0.1`（第 32 行） | 本機可直接跑 |
| `CSRF_TRUSTED_ORIGINS` | 僅 Azure 網域（第 33 行） | 本機 POST 表單若遇 CSRF 問題，需加入 `http://127.0.0.1:8000` |
| `DATABASES` | 無 `PORT` 設定（第 101 行起） | 若 PostgreSQL 非預設 5432，目前無法透過 env 指定 |

> ⚠️ 注意：`.env` 雖有 `ALLOWED_HOSTS`、`CSRF_TRUSTED_ORIGINS`、`DEBUG`，但 `settings.py` **尚未讀取**，目前以硬編碼為準。
> 建議依 `DEPLOY_AZURE.md` §2-2 將其改為 `os.getenv(...)`，本機與雲端即可共用同一份設定邏輯，只靠 `.env` 切換。

### 3-3. 資料庫

`settings.py` 已停用 SQLite（第 94–99 行註解掉），固定使用 PostgreSQL。本機務必先安裝並啟動 PostgreSQL、建立對應資料庫，否則 `migrate` 會失敗。

---

## 4. 常用開發指令

```bash
python manage.py runserver               # 啟動開發伺服器
python manage.py makemigrations          # 依模型變更產生 migration
python manage.py migrate                 # 套用 migration
python manage.py createsuperuser         # 建立管理員
python manage.py collectstatic           # 收集靜態檔至 staticfiles/
python manage.py test                    # 執行測試
python manage.py test questions          # 只測單一 app

# i18n：修改含 {% trans %} / gettext 字串後
python manage.py makemessages -l zh_Hant
python manage.py compilemessages
```

---

## 5. 常見問題

| 症狀 | 原因 | 處理 |
|------|------|------|
| `django.db.utils.OperationalError` | PostgreSQL 未啟動或 `.env` 連線資訊錯誤 | 確認服務啟動、`DATABASE_*` 正確 |
| 本機表單 CSRF 403 | `CSRF_TRUSTED_ORIGINS` 未含本機網域 | 暫時於 `settings.py` 加入 `http://127.0.0.1:8000` |
| `DJANGO_SECRET_KEY` 為 None | 未建立 `.env` 或未填值 | `cp .env.example .env` 並填入 |
| AI 分析報錯 | `GEMINI_API_KEY` 未設定 | 於 `.env` 填入有效金鑰 |

---

## 相關檔案

- `.env.example` — 環境變數範本
- `DEPLOY_AZURE.md` — Azure 部署指南
- `CLAUDE.md` — 專案架構說明
