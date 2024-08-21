# ADAS Functional Safety Simulation Tool

## プロジェクト概要
このプロジェクトは、先進運転支援システム（ADAS）の機能安全性を評価するためのシミュレーションツールです。Automotive Safety Integrity Level (ASIL)を様々なシチュエーションで判定し、ADASの安全性を包括的に分析します。

## 主な機能
- 多様なシナリオ（意図しない加速、減速、操舵）のシミュレーション
- ASILの計算と評価
- 結果の可視化と分析
- ユーザーフレンドリーなGUIインターフェース

## 最近の更新
- data_generator.pyの改善：エラーハンドリングの強化、パフォーマンスの最適化
- utils/functions.pyの修正：データ生成機能の信頼性向上

## 使用方法

### データ生成
data_generator.pyを使用してシミュレーション用のデータを生成できます。

1. 仮想環境をアクティベートします：
   ```
   myenv\Scripts\activate  # Windowsの場合
   ```

2. プロジェクトのルートディレクトリに移動します。

3. 以下のコマンドを実行します：
   ```
   python src/data_generation/data_generator.py
   ```

4. 生成されたデータは `data/output/accel_in.csv` に保存されます。

注意: データ生成パラメータをカスタマイズする場合は、data_generator.py内のuser_input辞書を編集してください。

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
   myenv\Scripts\activate  # Windowsの場合
   ```

3. 必要なパッケージをインストールします：
   ```
   pip install -r requirements.txt
   ```

## 開発
- `src/` ディレクトリには、各機能モジュールが含まれています。
- `tests/` ディレクトリには、対応するテストファイルがあります。
- 新しい機能を追加する場合は、適切なモジュールに実装し、対応するテストを作成してください。

## 今後の計画
- シミュレーションエンジンの実装
- ASIL計算モジュールの開発
- GUIの拡張と改善
- 包括的なテストスイートの作成

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