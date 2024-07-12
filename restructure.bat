@echo off

REM 新しいディレクトリの作成
mkdir src\data_generation src\asil_calculation src\visualization data\input data\output docs

REM 既存ファイルの移動
move src\simulation\make_sim_data.py src\data_generation\data_generator.py
move src\simulation\make_asil_map.py src\asil_calculation\asil_calculator.py

REM 新しいファイルの作成
type nul > src\simulation\simulation_engine.py
type nul > src\visualization\result_visualizer.py
type nul > src\data_generation\__init__.py
type nul > src\asil_calculation\__init__.py
type nul > src\visualization\__init__.py
type nul > docs\user_manual.md
type nul > docs\api_documentation.md
type nul > setup.py

REM テストファイルの作成
type nul > tests\test_data_generator.py
type nul > tests\test_simulation_engine.py
type nul > tests\test_asil_calculator.py
type nul > tests\test_result_visualizer.py
type nul > tests\test_vehicle_model.py

echo プロジェクト構造の変更が完了しました。