前提条件
以下のソフトウェアがマシンにインストールされていることを確認してください：

Git
Python 3.7以上
Streamlit
インストール手順
リポジトリをクローンする:

git clone https://github.com/yusu8901/rirekisho
仮想環境を作成する:

python -m venv .venv
仮想環境をアクティベートする:

# Windows command prompt
.venv\Scripts\activate.bat

# Windows PowerShell(windowsユーザーはPowerShellの使用を推奨)
.venv\Scripts\Activate.ps1

# macOS and Linux
source .venv/bin/activate
必要な依存関係をインストールする:

pip install -r requirements.txt
.env.sampleファイルを.envファイルに変更後、ファイル内の"YOUR_API_KEY_HERE"を取得したOpenAI APIキーで上書きする:

OPENAI_API_KEY="YOUR_API_KEY_HERE"
Streamlitアプリケーションを実行する:

streamlit run rirekisho.py
streamlitでアプリを起動したい場合はstreamlit run ○○.pyを実行すること。
