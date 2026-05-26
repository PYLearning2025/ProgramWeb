# 部署到 Azure App Service

本文件說明如何將 ProgramWeb（Django 5.2 + PostgreSQL）部署到 **Azure App Service (Linux, Python 3.12)**。
日常開發在 `develop` 分支；push 至 `develop` 會觸發 GitHub Actions 自動部署到 App Service `programwebdevelop`。

---

## 1. 架構與流程概觀

```
本機 / GitHub (develop 分支)
        │  git push origin develop
        ▼
GitHub Actions (.github/workflows/develop_programwebdevelop.yml)
        │  build → upload artifact → azure/webapps-deploy
        ▼
Azure App Service「programwebdevelop」(Linux, Python 3.12)
        │  Oryx 建置 → 安裝 requirements.txt → 啟動命令
        ▼
PostgreSQL（Azure Database for PostgreSQL 或外部）
```

- **App 名稱**：`programwebdevelop`
- **網域**：`https://programwebdevelop.azurewebsites.net`
- **CI**：目前 workflow **未**執行測試、`collectstatic`、`migrate`（見 §5、§6）

---

## 2. 部署前置：必須先補的程式碼調整

> 這些是「能在 Azure 正常啟動並安全運作」的前提，建議在部署前合併。

### 2-1. `requirements.txt` 補上 WSGI 伺服器與靜態檔處理

Azure Linux App Service 以 **gunicorn** 啟動 WSGI；正式環境靜態檔建議用 **whitenoise**。

```diff
  django==5.2.3
  psycopg2==2.9.10
  pillow==11.2.1
  python-dotenv==1.0.1
+ gunicorn==23.0.0
+ whitenoise==6.7.0
  langchain==0.3.27
  ...
```

### 2-2. `settings.py` 改為由環境變數讀取（取代硬編碼）

目前 `DEBUG`、`ALLOWED_HOSTS`、`CSRF_TRUSTED_ORIGINS` 為硬編碼，且 `DATABASES` 缺 `PORT`。建議：

```python
# 修改：DEBUG 由環境變數控制，預設 False（安全預設）
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# 修改：由環境變數讀取，逗號分隔
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
CSRF_TRUSTED_ORIGINS = os.getenv("CSRF_TRUSTED_ORIGINS", "").split(",")

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DATABASE_NAME"),
        "USER": os.getenv("DATABASE_USER"),
        "PASSWORD": os.getenv("DATABASE_PASSWORD"),
        "HOST": os.getenv("DATABASE_HOST"),
        "PORT": os.getenv("DATABASE_PORT", "5432"),  # 新增
    }
}
```

`MIDDLEWARE` 加入 whitenoise（緊接在 `SecurityMiddleware` 之後），並啟用壓縮儲存：

```python
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # 新增
    ...
]

# 新增：whitenoise 靜態檔壓縮與快取
STORAGES = {
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
}
```

> 詳細的本機 / 雲端差異請見 `LOCAL_DEVELOPMENT.md`。

---

## 3. 在 Azure 建立資源（首次部署）

可用 Azure Portal 或 CLI。以下為 CLI 範例（變數請自行替換）。

```bash
# 登入
az login

# 變數
RG=programweb-rg
PLAN=programweb-plan
APP=programwebdevelop
LOCATION=eastasia

# 資源群組 + Linux App Service 方案
az group create --name $RG --location $LOCATION
az appservice plan create --name $PLAN --resource-group $RG --is-linux --sku B1

# 建立 Python 3.12 Web App
az webapp create --resource-group $RG --plan $PLAN --name $APP \
  --runtime "PYTHON:3.12"
```

PostgreSQL 可使用 Azure Database for PostgreSQL（Flexible Server）：

```bash
az postgres flexible-server create \
  --resource-group $RG --name programweb-db \
  --location $LOCATION --tier Burstable --sku-name Standard_B1ms \
  --admin-user pgadmin --admin-password '請填入強密碼' \
  --version 16 --public-access 0.0.0.0
# 取得連線資訊後填入 §4 的環境變數；HOST 形如 programweb-db.postgres.database.azure.com
```

---

## 4. 設定環境變數（Application settings）

**不要上傳 `.env`**。將 `.env.example` 列出的每個變數設到 App Service：

Portal 路徑：**App Service → 設定 → 環境變數 → 應用程式設定**。
或用 CLI 一次設定：

```bash
az webapp config appsettings set --resource-group $RG --name $APP --settings \
  DJANGO_SECRET_KEY='隨機密鑰' \
  DEBUG='False' \
  ALLOWED_HOSTS='programwebdevelop.azurewebsites.net' \
  CSRF_TRUSTED_ORIGINS='https://programwebdevelop.azurewebsites.net' \
  DATABASE_NAME='programweb' \
  DATABASE_USER='pgadmin' \
  DATABASE_PASSWORD='資料庫密碼' \
  DATABASE_HOST='programweb-db.postgres.database.azure.com' \
  DATABASE_PORT='5432' \
  GEMINI_API_KEY='Gemini金鑰' \
  OPENAI_API_KEY='OpenAI金鑰' \
  SCM_DO_BUILD_DURING_DEPLOYMENT='1'
```

> `SCM_DO_BUILD_DURING_DEPLOYMENT=1` 讓 Oryx 在部署時安裝 `requirements.txt`。

---

## 5. 設定啟動命令（Startup Command）

Django 專案的 WSGI 進入點為 `ProgramWeb/wsgi.py`（`WSGI_APPLICATION = "ProgramWeb.wsgi.application"`）。

Portal 路徑：**App Service → 設定 → 一般設定 → 啟動命令**，填入：

```bash
gunicorn --bind=0.0.0.0 --timeout 600 ProgramWeb.wsgi
```

或 CLI：

```bash
az webapp config set --resource-group $RG --name $APP \
  --startup-file "gunicorn --bind=0.0.0.0 --timeout 600 ProgramWeb.wsgi"
```

---

## 6. 資料庫遷移與靜態檔

CI workflow 目前未自動執行，需處理：

- **`collectstatic`**：Oryx 偵測到 Django 時預設會跑 `collectstatic`。若要關閉可設 `DISABLE_COLLECTSTATIC=true`。本專案 `STATIC_ROOT = staticfiles/` 已設定，搭配 §2-1 的 whitenoise 即可。
- **`migrate`**：建議在首次部署與每次有 migration 時，於 App Service 主控台手動執行，或加入 startup 腳本。

透過 **App Service → 開發工具 → SSH** 連入後執行：

```bash
cd /home/site/wwwroot
python manage.py migrate
python manage.py createsuperuser   # 首次建立管理員
python manage.py compilemessages   # 若有 i18n 字串更新
```

---

## 7. 觸發部署

```bash
git checkout develop
git push origin develop      # 自動觸發 GitHub Actions
```

也可在 GitHub 的 **Actions** 頁面手動 `workflow_dispatch` 執行。

部署金鑰由 repository secret `AZUREAPPSERVICE_PUBLISHPROFILE_FD017640982B4226A27543F35CB1C7EE` 提供（App Service 的發佈設定檔）。更換 App 時需在 **GitHub → Settings → Secrets and variables → Actions** 更新此 secret。

---

## 8. 驗證與疑難排解

```bash
# 即時查看應用程式日誌
az webapp log tail --resource-group $RG --name $APP
```

| 症狀 | 可能原因 | 處理 |
|------|----------|------|
| `Bad Request (400)` | `ALLOWED_HOSTS` 未含 Azure 網域 | 補上 `programwebdevelop.azurewebsites.net` |
| CSRF 驗證失敗 | `CSRF_TRUSTED_ORIGINS` 缺 https 網域 | 設為 `https://...azurewebsites.net` |
| 502 / 應用無法啟動 | 缺 gunicorn 或啟動命令錯誤 | 確認 §2-1、§5 |
| CSS/JS 404 | 未跑 collectstatic / 無 whitenoise | 確認 §2-1、§6 |
| DB 連線失敗 | 連線字串或防火牆 | 確認 §4 變數、PostgreSQL 允許 Azure 服務存取 |

---

## 相關檔案

- `.env.example` — 環境變數範本
- `LOCAL_DEVELOPMENT.md` — 本機開發設定與需調整的檔案
- `.github/workflows/develop_programwebdevelop.yml` — CI/CD 設定
