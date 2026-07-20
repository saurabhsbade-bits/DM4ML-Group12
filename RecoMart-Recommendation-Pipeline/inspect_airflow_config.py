from pathlib import Path
p = Path(r'C:\Users\saura\DM4ML-Group12\.venv\Lib\site-packages\airflow\configuration.py')
text = p.read_text(encoding='utf-8')
for needle in ['def get_airflow_home', 'AIRFLOW_HOME', 'def _get_config_file_from_env', 'def _get_env_var_name', 'def _get_config_from_env']:
    idx = text.find(needle)
    print('needle', needle, 'idx', idx)
    if idx != -1:
        print(text[idx:idx+6000])
        print('---')
