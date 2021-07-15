# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

added_files = [
            ('data', 'data'),
            ('output', 'output'),
            (HOMEPATH + '\\PyQt5\\Qt\\bin\*', 'PyQt5\\Qt\\bin'),
            (HOMEPATH + '\\cloudscraper\\', 'cloudscraper'),
            (HOMEPATH + '\\helheim\\', 'helheim'),
            (HOMEPATH + '\\polling.py', 'polling')
            ]

a = Analysis(['launcher.py'],
             pathex=['C:\\Users\\Adam\\PycharmProjects\\Rhynio-Request-Bot'],
             binaries=[],
             datas=added_files,
             hiddenimports=['cloudscraper.interpreters.native'],
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
          name='rhynio-raffle',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False,
          icon='icon.ico')
