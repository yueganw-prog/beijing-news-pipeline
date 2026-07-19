import sys, os, json
import pwd, grp, resource
resource.RLIM_INFINITY = 9223372036854775807
os.environ["AIRFLOW_HOME"] = r"C:\Users\admin\Desktop\beijing-news-pipeline\.local\airflow"

from airflow.providers.amazon.aws.hooks.base_aws import AwsBaseHook
try:
    hook = AwsBaseHook(aws_conn_id="news_minio", client_type="s3")
    print("Hook created")
    print(f"Extra: {hook.extra_dejson}")
    
    # Check how get_client works
    client = hook.get_client()
    buckets = client.list_buckets()
    names = [b["Name"] for b in buckets["Buckets"]]
    print(f"Buckets: {names}")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
