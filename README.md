### 前提条件
以下のソフトウェアがマシンにインストールされていることを確認してください：

Git

Python 

Streamlit


### インストール手順
1.リポジトリをクローンする:
``` cmd
git clone https://github.com/yusu8901/rirekisho
```

2.rirekishoへ移動：
```cmd
cd rirekisho
```


3.仮想環境を作成する:
``` cmd
python -m venv .venv
``` 

4.仮想環境をアクティベートする:

 ``` cmd
# Windows command prompt
.venv\Scripts\activate.bat

# Windows PowerShell(windowsユーザーはPowerShellの使用を推奨)
.venv\Scripts\Activate.ps1

# macOS and Linux
source .venv/bin/activate
```

5.必要な依存関係をインストールする:
``` cmd
pip install -r requirements.txt
``` 
6.'.env.sample'ファイルを'.env'ファイルに変更後、ファイル内の"YOUR_API_KEY_HERE"を取得したOpenAI APIキーで上書きする:
``` cmd
OPENAI_API_KEY="YOUR_API_KEY_HERE"
``` 
7.Streamlitアプリケーションを実行する:
``` cmd
streamlit run rirekisho.py
``` 
streamlitでアプリを起動したい場合はstreamlit run ○○.pyを実行すること。
