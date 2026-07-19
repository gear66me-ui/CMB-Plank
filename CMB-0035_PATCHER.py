from pathlib import Path
print('hello from patcher')
Path('CMB-0035_GENERATED_INFRASTRUCTURE.py').write_text('print(123)\n')
