# conditions_bugfix

This code allows you to get the output of `github miner` and, using SrcML, process the result.
We want to extract all methods where the only part of the whole code changed in the commit is inside an **if, for or while condition**.

You have to save the txt result of `github miner` inside the **input** folder and you have to copy the **output_files** created in `github miner` inside a folder with the same name.

After installing the requiriments, you can run the code as follows:
```
python3 mining.py
```
All the results will be saved inside **result** folder.
Each record looks like the following one:
```
{"id_internal": "7044749085", "tot_processed": 8, "before": "['@', 'Override', 'public', 'void', 'onCreate', '(', 'Bundle', 'savedInstanceState', ')', '{', 'getWindow', '()', '.', 'requestFeature', '(', 'Window', '.', 'FEATURE_ACTION_BAR', ')', ';', 'super', '.', 'onCreate', '(', 'savedInstanceState', ')', ';', 'getWindow', '()', '.', 'addFlags', '(', 'WindowManager', '.', 'LayoutParams', '.', 'FLAG_KEEP_SCREEN_ON', ')', ';', 'myActivityInstance', '=', 'this', ';', 'getSupportActionBar', '()', '.', 'setTitle', '(', '\"UsbongKit\"', ')', ';', 'setContentView', '(', 'R', '.', 'layout', '.', 'main', ')', ';', 'instance', '=', 'this', ';', 'Bundle', 'extras', '= ', 'getIntent', '()', '.', 'getExtras', '()', ';', 'if ', '(', 'extras', '!=', 'null', ')', '{', 'String', 'message', '= ', 'extras', '.', 'getString', '(', '\"completed_tree\"', ')', ';', 'if ', '(', 'message', '.', 'equals', '(', '\"true\"', ')', ')', '{', 'AppRater', '.', 'showRateDialog', '(', 'this', ')', ';', '}', '}', 'reset', '()', ';', 'initMainMenuScreen', '()', ';']", "after": "['@', 'Override', 'public', 'void', 'onCreate', '(', 'Bundle', 'savedInstanceState', ')', '{', 'getWindow', '()', '.', 'requestFeature', '(', 'Window', '.', 'FEATURE_ACTION_BAR', ')', ';', 'super', '.', 'onCreate', '(', 'savedInstanceState', ')', ';', 'getWindow', '()', '.', 'addFlags', '(', 'WindowManager', '.', 'LayoutParams', '.', 'FLAG_KEEP_SCREEN_ON', ')', ';', 'myActivityInstance', '=', 'this', ';', 'getSupportActionBar', '()', '.', 'setTitle', '(', '\"UsbongKit\"', ')', ';', 'setContentView', '(', 'R', '.', 'layout', '.', 'main', ')', ';', 'instance', '=', 'this', ';', 'Bundle', 'extras', '= ', 'getIntent', '()', '.', 'getExtras', '()', ';', 'if ', '(', 'extras', '!=', 'null', ')', '{', 'String', 'message', '= ', 'extras', '.', 'getString', '(', '\"completed_tree\"', ')', ';', 'if ', '(', '(', 'message', '!=', 'null', ')', '&&', '(', 'message', '.', 'equals', '(', '\"true\"', ')', ')', ')', '{', 'AppRater', '.', 'showRateDialog', '(', 'this', ')', ';', '}', '}', 'reset', '()', ';', 'initMainMenuScreen', '()', ';']", "id_commit": "70f2422df5dc33859cd33c78863e8f9402a1c3f6", "repo": "usbong/usbong_pagtsing", "date_commit": "2018-01-01 08:33:34", "before_api": "https://github.com/usbong/usbong_pagtsing/raw/98a5d76d165ac6dbc0efc1c8aba849652b40a99d/src/usbong/android/pagtsing/UsbongMainActivity.java", "after_api": "https://github.com/usbong/usbong_pagtsing/raw/70f2422df5dc33859cd33c78863e8f9402a1c3f6/src/usbong/android/pagtsing/UsbongMainActivity.java", "URL": "https://api.github.com/repos/usbong/usbong_pagtsing/commits/70f2422df5dc33859cd33c78863e8f9402a1c3f6", "message": "+fixed: app-has-stopped-error due to a null pointer exception error when running the app as reported by team member, Zent Lim, in the app, \"Where is Heaven?\"\n--> TODO: apply: fix to all the other LIKHA and DAHON scaffolds", "file_path": "2018-01-01-8.json.gz"}
```
You can find the following fields:
1. **id_internal** of the comment (the GhArchive id),
2. the list of tokens of the method **before** and **after** the fix,
3. the **id_commit** and **repo** with information about the commit
4. **before_api** and **after_api** with the path to the raw java file (before and after the fix)
5. the **URL** to the api call done in the previous step
6. the **message** of the commit