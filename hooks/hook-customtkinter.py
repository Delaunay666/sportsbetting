
# Hook para customtkinter
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

datas = collect_data_files('customtkinter')
hiddenimports = collect_submodules('customtkinter')
