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
│   │   └── asil_calculator.py
│   ├── visualization/
│   ├── gui/
│   │   └── gui.py
│   ├── utils/
│   │   └── functions.py
│   ├── scripts/
│   │   └── run_simulation.py
│   └── main.py
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
   git clone https://github.com/eiuske-saeki/ADAS-functional-safety-rep.git
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

# ADAS機能安全シミュレーションツール 操作マニュアル

## 目次
1. はじめに
   - 本ツールの概要
   - システム要件
2. 基本操作
   - ツールの起動方法
   - 画面構成
3. 各タブの操作方法
   - Overview
   - Data Generation
   - Simulation
   - ASIL Calculation
   - Visualization
4. トラブルシューティング
5. 付録

## 1. はじめに

### 本ツールの概要
本ツールは、ADAS（先進運転支援システム）の機能安全性を評価するためのシミュレーションツールです。車両の挙動シミュレーションを行い、その結果に基づいてASIL（Automotive Safety Integrity Level）の判定を行うことができます。

### システム要件
- Python 3.x
- 必要なライブラリ（requirements.txtに記載）
- 最小画面解像度：1024×768

## 2. 基本操作

### ツールの起動方法
1. コマンドプロンプトまたはターミナルを開きます
2. プロジェクトのルートディレクトリに移動
3. 以下のコマンドを実行：
   ```bash
   python src/main.py
   ```

### 画面構成
ツールは以下の5つのタブで構成されています：
- Overview：全体の状況確認
- Data Generation：シミュレーションデータの生成
- Simulation：シミュレーションの実行
- ASIL Calculation：ASIL値の計算
- Visualization：結果の可視化

## 3. 各タブの操作方法

### Overviewタブ
![Overview Tab]

#### 主な機能
- Current Status：現在の処理状況の確認
- Quick Actions：よく使う機能へのショートカット
- Latest Results：最新の処理結果の表示



#### 操作手順
1. ステータス表示を確認
2. 必要に応じてQuick Actionsボタンをクリック
3. Latest Resultsで結果を確認

### Data Generationタブ

**入力：パラメータ設定**

**出力：data/input/accel_in.csv**

#### パラメータ設定
1. Vehicle Weights
   - 「Add Weight」ボタンで重量入力フィールドを追加
   - 複数の重量を設定可能
   - 不要な入力フィールドは「×」ボタンで削除

2. Range Parameters
   - Velocity Range：速度範囲（km/h）
   - Time Range：時間範囲（sec）
   - Acceleration Range：加速度範囲（G）
   
   各パラメータに対して：
   - Start値：開始値
   - End値：終了値
   - Step値：刻み幅

3. Evasive Parameters
   - No evasion：回避行動なし（デフォルト：0）
   - C0：第1回避行動（デフォルト：0.4）
   - C1：第2回避行動（デフォルト：0.8）
   - C2：第3回避行動（デフォルト：1.0）

4. Reaction Time
   - ドライバーの反応時間（sec）

#### データ生成手順
1. 各パラメータを設定
2. 「Generate Data」ボタンをクリック
3. 生成結果を確認（Results欄）
4. データは自動的に`data/input/accel_in.csv`に保存

### Simulationタブ

**入力：data/input/accel_in.csv**

**出力：data/output/simulation_results.csv**

#### パラメータ設定
- Time step：シミュレーションの時間刻み（sec）
- Max simulation time：最大シミュレーション時間（sec）
- Acceleration jerk：加速度変化率（G）
- Deceleration jerk：減速度変化率（G）

#### シミュレーション実行手順
1. 各パラメータを設定
2. 「Select Input & Run Simulation」ボタンをクリック
3. 入力ファイル（CSVファイル）を選択
4. プログレスバーで進捗を確認
5. 結果を確認（Results欄）
6. シミュレーション結果は`data/output/simulation_results.csv`に保存

### ASIL Calculationタブ

**入力：data/output/simulation_results.csv**

**出力：data/output/[入力ファイル名]_with_asil.csv**

#### ASIL計算手順
1. 「Run ASIL Calculation」ボタンをクリック
2. シミュレーション結果のCSVファイルを選択
3. プログレスバーで進捗を確認
4. 結果を確認（Results欄）
5. ASIL計算結果は入力ファイル名に「_with_asil」を付加して保存

### Visualizationタブ

**入力：data/output/[入力ファイル名]_with_asil.csv**

**出力：data/output/asil_maps/**

#### ASIL Map生成手順
1. 「Load CSV File」ボタンをクリック
2. ASIL計算結果のCSVファイルを選択
3. X軸とY軸のパラメータを選択
4. Color mapを選択
5. 「Generate ASIL Map」ボタンをクリック
6. 生成結果を確認（Results欄）
7. ASILマップは`data/output/asil_maps/`に保存

## 4. トラブルシューティング

### 一般的な問題と解決方法

#### データ生成時のエラー
- エラーメッセージ：「Please add at least one weight value」
  - 解決方法：少なくとも1つの重量値を追加してください

#### シミュレーション実行時のエラー
- CSV読み込みエラー
  - 解決方法：CSVファイルが開いていないことを確認
  - 解決方法：文字コードがUTF-8であることを確認

#### ASIL計算時のエラー
- データ不足エラー
  - 解決方法：必要なすべての列がCSVファイルに存在することを確認

#### 可視化時のエラー
- パラメータ未選択エラー
  - 解決方法：X軸、Y軸の両方のパラメータを選択

### エラーメッセージの解釈
エラーメッセージは以下の2箇所に表示されます：
1. 各タブのResults欄
2. エラーポップアップウィンドウ

## 5. 付録

### パラメータの推奨値
- Time step：0.1（sec）
- Max simulation time：10.0（sec）
- Acceleration jerk：1.0（G）
- Deceleration jerk：2.5（G）

### データフォーマット
入力CSVファイルは以下の列を含む必要があります：
- No：通し番号
- 先行車質量[kg]：先行車の重量
- 先行車速度[km/h]：先行車の速度
- 後続車質量[kg]：後続車の重量
- 後続車速度[km/h]：後続車の速度
- 車間時間[sec]：車間時間
- 回避行動パラメータ[回避無し/C0/C1/C2]：各回避行動の値

### 注意事項
- シミュレーション実行中はGUIが一時的に応答しなくなることがありますが、正常な動作です
- 大規模なデータセットを処理する場合は、十分なメモリを確保してください
- データ処理中にツールを終了すると、データが破損する可能性があります

<!-- 
### データ生成
カスタムシミュレーションデータを直接生成するには：
```
python src/data_generation/data_generator.py
```
生成されたデータは `data/input/accel_in.csv` に保存されます。
-->

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
- 現在、`data/output/` フォルダが事前に存在していないとエラーが発生する場合があります。エラーが発生した場合は、このフォルダが存在することを確認してください。
=>解決しました。自動でoutputフォルダが生成されるようになりました。
- ツールで使用する `data/output/` フォルダや `data/input/` フォルダをユーザーが開いていると、ツールが正常に動作しない場合があります。シミュレーション実行前にこれらのフォルダを閉じていることを確認してください。
- 長時間の使用やデータ処理後に動作が遅くなる場合は、メモリの解放が適切に行われていない可能性があります（現在調査中）。このような症状が見られた場合は、ツールを再起動してみてください。
- GUIの起動に問題がある場合は、必要なライブラリ（特にtkinter）が正しくインストールされているか確認してください。

## ライセンス
[ここに適切なライセンス情報を記述します]

## 連絡先
[ここに連絡先情報を記述します（オプション）]

## 謝辞
[必要に応じて、貢献者や使用したライブラリなどへの謝辞を記述します]