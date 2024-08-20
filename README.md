# ADAS Functional Safety Simulation Tool

## プロジェクト概要
このプロジェクトは、先進運転支援システム（ADAS）の機能安全性を評価するためのシミュレーションツールです。Automotive Safety Integrity Level (ASIL)を様々なシチュエーションで判定し、ADASの安全性を包括的に分析します。

## 主な機能
- 多様なシナリオ（意図しない加速、減速、操舵）のシミュレーション
- ASILの計算と評価
- 結果の可視化と分析
- ユーザーフレンドリーなGUIインターフェース

## プロジェクト構造
```
ADAS-functional-safety-rep/
├── data/
│   ├── input/    # 入力データファイル
│   └── output/   # シミュレーション結果出力
├── dev_log/      # 開発ログ
├── docs/         # プロジェクトドキュメント
├── src/          # ソースコード
│   ├── asil_calculation/
│   ├── data_generation/
│   ├── gui/
│   ├── models/
│   ├── simulation/
│   ├── utils/
│   ├── visualization/
│   └── main.py   # アプリケーションのエントリーポイント
├── tests/        # テストコード
├── .gitignore
├── README.md
└── requirements.txt
```

## インストール方法
1. リポジトリをクローンします：
   ```
   git clone https://github.com/eiuske-saeki/ADAS-functional-safety-rep.git
   cd ADAS-functional-safety-rep
   ```

2. 仮想環境を作成し、アクティベートします：
   ```
   python -m venv myenv
   source myenv/bin/activate  # Linuxの場合
   myenv\Scripts\activate     # Windowsの場合
   ```

3. 必要なパッケージをインストールします：
   ```
   pip install -r requirements.txt
   ```

## 使用方法
1. 仮想環境をアクティベートします（上記参照）。

2. アプリケーションを実行します：
   ```
   python src/main.py
   ```

3. GUIの指示に従って、シミュレーションパラメータを設定し、実行します。

4. 結果は `data/output/` ディレクトリに保存されます。

## 開発
- `src/` ディレクトリには、各機能モジュールが含まれています。
- `tests/` ディレクトリには、対応するテストファイルがあります。
- 新しい機能を追加する場合は、適切なモジュールに実装し、対応するテストを作成してください。

## テスト実行
```
pytest tests/
```

## ドキュメント
- API ドキュメント: `docs/api_documentation.md`
- ユーザーマニュアル: `docs/user_manual.md`

## 貢献方法
1. このリポジトリをフォークします。
2. 新しいブランチを作成します（`git checkout -b feature/AmazingFeature`）。
3. 変更をコミットします（`git commit -m 'Add some AmazingFeature'`）。
4. ブランチにプッシュします（`git push origin feature/AmazingFeature`）。
5. プルリクエストを作成します。

## ライセンス
[ここに適切なライセンス情報を記述します]

## 連絡先
[ここに連絡先情報を記述します（オプション）]
```