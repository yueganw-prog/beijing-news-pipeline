"""
Airflow 直接启动脚本（Windows 兼容，绕过 daemon library）
"""
import os, sys

os.environ.setdefault("AIRFLOW_HOME", __file__)

# 确保 Unix 兼容 stub 已加载
import pwd, grp, resource

# Patch resource stubs
resource.RLIM_INFINITY = 9223372036854775807

# 从 Airflow 内部获取 Flask app
from airflow.www.app import create_app
from airflow import settings

if __name__ == "__main__":
    app = create_app()
    print(f"Airflow webserver starting on http://0.0.0.0:{sys.argv[1] if len(sys.argv) > 1 else 8080}")
    app.run(host="0.0.0.0", port=int(sys.argv[1]) if len(sys.argv) > 1 else 8080, debug=False, use_reloader=False)