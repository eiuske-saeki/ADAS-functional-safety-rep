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
├── src/
│   ├── data_generation/
│   │   └── data_generator.py
│   ├── simulation/
│   │   └── simulation_engine.py
│   ├── asil_calculation/
│   ├── visualization/
│   ├── gui/
│   │   └── gui.py
│   ├── utils/
│   │   └── functions.py
│   └── scripts/
│       └── run_simulation.py
├── tests/
├── data/
│   ├── input/
│   └── output/
├── docs/
├── dev_log/
├── .gitignore
├── README.md
└── requirements.txt
```

## セットアップ手順
1. リポジトリをクローンします：
   ```
   git clone https://github.com/your-username/ADAS-functional-safety-rep.git
   cd ADAS-functional-safety-rep
   ```

2. 仮想環境を作成し、アクティベートします：
   ```
   python -m venv myenv
   source myenv/bin/activate  # Unix系の場合
   myenv\Scripts\activate     # Windowsの場合
   ```

3. 必要なパッケージをインストールします：
   ```
   pip install -r requirements.txt
   ```

## 使用方法

### 環境設定
スクリプトを実行する前に、必ずプロジェクトのルートディレクトリで以下のコマンドを実行してください：

Windowsの場合:
```
set PYTHONPATH=%PYTHONPATH%;%CD%
```

Unix系の場合:
```
export PYTHONPATH=$PYTHONPATH:$(pwd)
```

### データ生成
カスタムシミュレーションデータを生成するには：
```
python src/data_generation/data_generator.py
```
生成されたデータは `data/input/accel_in.csv` に保存されます。

### シミュレーションの実行
`src/scripts/run_simulation.py` を実行してシミュレーションを開始します：
```
python src/scripts/run_simulation.py
```
`src/main.py` を実行してシミュレーションを開始します：

```
python src/main.py
```

シミュレーション結果は `data/output/simulation_results.csv` に保存されます。

注意: これらのスクリプトは、必ずプロジェクトのルートディレクトリから実行してください。

## 開発ガイドライン
- `src/` ディレクトリには、各機能モジュールが含まれています。
- `tests/` ディレクトリには、対応するテストファイルがあります。
- 新しい機能を追加する場合は、適切なモジュールに実装し、対応するテストを作成してください。
- コードの変更を行う前に、新しいブランチを作成してください。
- コミットメッセージは明確で簡潔にしてください。

## テスト実行
テストを実行するには、以下のコマンドを使用します：
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

## トラブルシューティング
- スクリプトの実行時にモジュールが見つからないエラーが発生する場合は、環境変数 `PYTHONPATH` が正しく設定されているか確認してください。
- データ生成やシミュレーション実行時にエラーが発生した場合は、`data/` ディレクトリの権限を確認してください。

## ライセンス
[ここに適切なライセンス情報を記述します]

## 連絡先
[ここに連絡先情報を記述します（オプション）]

## 謝辞
[必要に応じて、貢献者や使用したライブラリなどへの謝辞を記述します]