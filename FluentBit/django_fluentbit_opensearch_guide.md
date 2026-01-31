# Django → Fluent Bit → OpenSearch → Dashboard Setup Guide (Zero to Hero) - Markdown Version

This guide provides a complete end-to-end setup for sending Django logs to OpenSearch using Fluent Bit, with dashboard visualization. Includes installation, configuration, testing, and troubleshooting.

---

## 1. Prerequisites

### 1.1 System Requirements
- **OS**: Windows 10/11 or Linux (Ubuntu 20.04+)
- **Python**: 3.10+ (with virtualenv)
- **Django**: 4.x+
- **OpenSearch**: 3.x+
- **Fluent Bit**: 2.x+
- **pip packages**:
  ```bash
  pip install python-json-logger
  ```

### 1.2 OpenSearch Setup
- Download & install OpenSearch: [Official OpenSearch Downloads](https://opensearch.org/downloads.html)
- Install OpenSearch Dashboards
- Ensure ports:
  - OpenSearch: 9200
  - Dashboards: 5601

### 1.3 Fluent Bit Setup
- Download Fluent Bit:
  - [Windows](https://fluentbit.io/download/) / [Linux](https://fluentbit.io/download/)
- Ensure `fluent-bit.exe` (Windows) or `fluent-bit` (Linux) is available in PATH.

---

## 2. Django Logging Setup

### 2.1 Directory Structure
```
DevOpsVaultX_App/
├── logs/
├── payments/
├── products/
├── manage.py
├── settings.py
```

### 2.2 Logging Configuration (settings.py)
```python
# =========================
# Logger
# =========================
import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Ensure the logs directory exists, otherwise Django will throw an error
LOG_DIR = BASE_DIR / "logs"
if not LOG_DIR.exists():
    LOG_DIR.mkdir(parents=True, exist_ok=True)

# Production-ready JSON Logging Configuration for DevOpsVaultX
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,

    "formatters": {
        "json": {
            # Structured logging for OpenSearch compatibility
            "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "format": "%(asctime)s %(levelname)s %(name)s %(message)s %(ip)s",
        },
        "verbose": {
            "format": "[{asctime}] {levelname} {name} {message}",
            "style": "{",
        },
    },

    "handlers": {
        "file_info": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            # Convert Path object to string using str() to avoid errors
            "filename": str(BASE_DIR / "logs" / "devopsvaultx_json.log"),
            "maxBytes": 10 * 1024 * 1024,  # 10 MB
            "backupCount": 5,
            "formatter": "json",
        },
        "file_error": {
            "level": "ERROR",
            "class": "logging.handlers.RotatingFileHandler",
            # Separate file for critical errors to speed up troubleshooting
            "filename": str(BASE_DIR / "logs" / "errors_json.log"),
            "maxBytes": 5 * 1024 * 1024,   # 5 MB
            "backupCount": 5,
            "formatter": "json",
        },
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },

    "loggers": {
        "django": {
            "handlers": ["file_info", "file_error", "console"],
            "level": "INFO",
            "propagate": True,
        },
        "products": {
            "handlers": ["file_info", "file_error", "console"], # console जोडल्यामुळे terminal वर पण दिसेल
            "level": "INFO",
            "propagate": False,
        },
        "payments": {
            "handlers": ["file_info", "file_error", "console"],
            "level": "INFO",
            "propagate": False,
        },
        "db_monitor": {
            "handlers": ["file_info", "file_error", "console"],
            "level": "INFO",
            "propagate": False,
        },
        "pages": {
            "handlers": ["file_info", "file_error", "console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}
```

### 2.3 Test Logging
```python
import logging
logger = logging.getLogger('payments')
logger.info('Payment process started', extra={'ip': '127.0.0.1'})
```
- Check `logs/devopsvaultx_json.log` for output.

---

## 3. Fluent Bit Setup

### 3.1 Fluent Bit Configuration (`fluent-bit.conf`)
```ini
[SERVICE]
    Flush        5
    Log_Level    info
    Daemon       off
    Parsers_File parsers.conf

[INPUT]
    Name           tail
    Path           D:\Sachin\Projects\DevOpsVaultX_App\logs\*.log
    Tag            DevOpsVaultX_App.logs
    Read_from_Head true
    Parser         json_parser

[OUTPUT]
    Name            opensearch
    Match           *
    Host            192.168.1.50
    Port            9200
    HTTP_User       admin
    HTTP_Passwd     admin
    Index           devopsvaultx_app
    Logstash_Format On
    Logstash_Prefix devopsvaultx
    Suppress_Type_Name On
    tls             On
    tls.verify      Off

[PARSER]
    Name        json_parser
    Format      json
```

### 3.2 Run Fluent Bit
- **Windows**
```powershell
fluent-bit.exe -c fluent-bit.conf
```
- **Linux**
```bash
fluent-bit -c fluent-bit.conf
```

### 3.3 Fluent Bit Windows Service
```powershell
# Install service
fluent-bit.exe -i tail -c fluent-bit.conf -o opensearch
# Start service
Start-Service -Name FluentBit
# Stop service
Stop-Service -Name FluentBit -Force
```

### 3.4 Troubleshooting
| Issue | Cause | Fix |
|-------|-------|-----|
| Logs not appearing in OpenSearch | Incorrect path / parser mismatch | Check `Path` and `Parser` in conf, ensure JSON format matches logs |
| TLS connection failed | Invalid cert / TLS enabled | Set `tls.verify Off` for testing |
| Fluent Bit cannot start | Port already in use | Change port or kill conflicting process |

---

## 4. OpenSearch Setup

### 4.1 Verify Index
```bash
curl -u admin:admin -X GET "https://192.168.1.50:9200/_cat/indices?v&pretty" --insecure
```

### 4.2 Create Index Template (Optional)
```json
PUT _index_template/devopsvaultx_template
{
  "index_patterns": ["devopsvaultx*"],
  "template": {
    "settings": {"number_of_shards": 1},
    "mappings": {"properties": {"asctime": {"type": "date"}, "levelname": {"type": "keyword"}}}
  }
}
```

### 4.3 OpenSearch Dashboards
- Access: `https://192.168.1.50:5601`
- Create index pattern: `devopsvaultx*`
- Visualize logs using `Discover` tab

---

## 5. Testing Pipeline

1. Run Django dev server and generate logs.
2. Check `logs/devopsvaultx_json.log` for entries.
3. Start Fluent Bit.
4. Verify logs appear in OpenSearch index:
```bash
curl -u admin:admin -X GET "https://192.168.1.50:9200/devopsvaultx_app/_search?pretty" --insecure
```
5. Open Dashboards → `Discover` → select `devopsvaultx*` → see logs.

---

## 6. Common Issues & Fixes

- **Fluent Bit stops immediately**: Check conf syntax, paths, and parser.
- **Logs missing fields**: Ensure `JsonFormatter` matches keys used in logs.
- **OpenSearch auth error**: Check `HTTP_User` & `HTTP_Passwd` in output.
- **Windows service cannot stop/start**: Use `Get-Service -Name FluentBit` to verify status.

---

## 7. Best Practices

- Rotate logs to avoid disk full
- Use JSON structured logs for easier search/filter
- Enable TLS in production
- Monitor Fluent Bit logs for errors

---

## 8. References
- [Fluent Bit Docs](https://docs.fluentbit.io/)
- [OpenSearch Docs](https://opensearch.org/docs/)
- [Python JSON Logger](https://github.com/madzak/python-json-logger)

