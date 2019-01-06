# -*- mode: python -*-

block_cipher = None


a = Analysis(['radioline_serialtest\\main.py'],
             pathex=['C:\\Users\\Asenta\\PycharmProjects\\radioline_serialtest'],
             binaries=[],
             datas=[('radioline_serialtest/UI/MainWindow.ui', 'UI'), ('radioline_serialtest/MainWindow_rc.py', '.')],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='radioline_serialtest_v0.0.1_x86',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=False )
