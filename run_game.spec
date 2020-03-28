# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

import platform

if platform.system() == 'Darwin':
	icon_path = 'data/icon.icns'
else:
	icon_path = 'data/icon.ico'

a = Analysis(['run_game.pyw'],
             pathex=['C:\\Users\\Starbuck\\Desktop\\pyweek29'],
             binaries=[],
             datas=[('data/*', 'data'), 
		    ('data/lora/*', 'data/lora'), 
                    ('data/ui_images/*', 'data/ui_images'), 
                    ('data/advisors/*', 'data/advisors'),
                    ('data/sound_files/*', 'data/sound_files'), 
                    ('data/queen_animation/*', 'data/queen_animation'),
	            ('data/towns/*', 'data/towns')],
             hiddenimports=['pkg_resources.py2_warn'],
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
          name='QueenOfTheHill',
          icon=icon_path,
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=True ) #change later to false
