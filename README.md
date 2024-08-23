# ADAS Functional Safety Simulation Tool

## プロジェクト概要
このプロジェクトは、先進運転支援システム（ADAS）の機能安全性を評価するためのシミュレーションツールです。Automotive Safety Integrity Level (ASIL)を様々なシチュエーションで判定し、ADASの安全性を包括的に分析します。

## 主な機能
- 多様なシナリオ（意図しない加速、減速、操舵）のシミュレーション
- ASILの計算と評価
- 結果の可視化と分析
- 効率的な大規模データ処理

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
│   ├── scripts/  # ユーティリティスクリプトとサンプル実行スクリプト
│   ├── simulation/
│   ├── utils/
│   └── visualization/
├── tests/        # テストコード
├── .gitignore
├── README.md
└── requirements.txt
```

## インストール方法
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

### データ生成
カスタムデータセットを生成するには：
```
python src/data_generation/data_generator.py
```
生成されたデータは `data/input/accel_in.csv` に保存されます。

### シミュレーションの実行
1. `src/scripts/run_simulation.py` を実行してシミュレーションを開始します：
   ```
   python src/scripts/run_simulation.py
   ```

2. シミュレーション結果は `data/output/simulation_results.csv` に保存されます。
3. 詳細なログは `data/output/logs/` ディレクトリに保存されます。

## 開発
- `src/` ディレクトリには、各機能モジュールが含まれています。
- `tests/` ディレクトリには、対応するテストファイルがあります。
- 新しい機能を追加する場合は、適切なモジュールに実装し、対応するテストを作成してください。

## 最近の更新
- シミュレーションエンジンの最適化：タイムステップを0.1秒に変更
- マルチプロセッシングの導入による並列処理の実現
- 回避行動の段階的評価の実装（C0で回避成功時にC1,C2をスキップ）
- データ処理の改善：バッチ処理の導入（1000行ずつデータを読み込み）
- ログ処理の改善と詳細な出力

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