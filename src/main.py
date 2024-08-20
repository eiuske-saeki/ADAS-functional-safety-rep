import sys
from PyQt5.QtWidgets import QApplication

from src.gui.gui import MainWindow
from src.data_generation.data_generator import DataGenerator
from src.simulation.simulation_engine import SimulationEngine
from src.asil_calculation.asil_calculator import ASILCalculator
from src.visualization.result_visualizer import ResultVisualizer

class ADASSimulationApp:
    def __init__(self):
        self.data_generator = DataGenerator()
        self.simulation_engine = SimulationEngine()
        self.asil_calculator = ASILCalculator()
        self.result_visualizer = ResultVisualizer()

    def run_simulation(self, parameters):
        # シミュレーションの実行フロー
        data = self.data_generator.generate(parameters)
        simulation_results = self.simulation_engine.run(data)
        asil_results = self.asil_calculator.calculate(simulation_results)
        visualization = self.result_visualizer.visualize(asil_results)
        return visualization

def main():
    app = QApplication(sys.argv)
    simulation_app = ADASSimulationApp()
    main_window = MainWindow(simulation_app)
    main_window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()