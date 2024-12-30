import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *
from PySpice.Spice.NgSpice.Shared import NgSpiceShared

class StaircaseLightingSimulation:
    def __init__(self):
        self.circuit = Circuit('Staircase Lighting System')
        self.ngspice = NgSpiceShared.new_instance()
        self.setup_circuit()
        print(self.circuit)
    def setup_circuit(self):
        # Nguồn điện AC
        self.circuit.SinusoidalVoltageSource('input', 'input', self.circuit.gnd, 
                                             amplitude=311@u_V, 
                                             frequency=50@u_Hz)
        
        # Mạch chỉnh lưu
        self.circuit.Diode('D1', 'input', 'rect_out1', model='1N4007')
        self.circuit.Diode('D2', 'rect_out1', 'rect_out2', model='1N4007')
        
        # Tụ lọc
        self.circuit.C('filter', 'rect_out2', self.circuit.gnd, 2200@u_uF)
        
        # Mô phỏng cảm biến và điều khiển LED
        for i in range(3):
            # Điện trở kích hoạt cảm biến
            self.circuit.R(f'R_PIR{i+1}', 'rect_out2', f'pir_node{i+1}', 10@u_kΩ)
            
            # Transistor điều khiển LED
            self.circuit.model(f'Q{i+1}', 'NPN', IS=1.8e-14, VAF=100)
            self.circuit.Q(f'Q_LED{i+1}', f'led_node{i+1}', f'pir_node{i+1}', 
                           self.circuit.gnd, model=f'Q{i+1}')
            
            # LED với điện trở giới hạn dòng
            self.circuit.R(f'R_LED{i+1}', 'rect_out2', f'led_node{i+1}', 100@u_Ω)
            self.circuit.Diode(f'LED{i+1}', f'led_node{i+1}', self.circuit.gnd, 
                               model='LED')

        # Thêm mô hình diode và LED
        self.circuit.model('1N4007', 'D', IS=1e-14, RS=0.01)
        self.circuit.model('LED', 'D', IS=1e-14, N=1.7, RS=0.1, BV=5)

    def run_simulation(self, duration=0.1):
        # Tạo netlist
        simulator = self.circuit.simulator(temperature=25, nominal_temperature=25)
        analysis = simulator.transient(step_time=1@u_ms, end_time=duration@u_s)
        
        return analysis

def plot_simulation_results(analysis):
    # Thiết lập đồ thị
    fig, axs = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle('Mô Phỏng Hệ Thống Đèn Cầu Thang', fontsize=16)

    # Nguồn vào
    axs[0, 0].plot(analysis['input'], label='Nguồn AC')
    axs[0, 0].set_title('Nguồn Điện Vào')
    axs[0, 0].set_xlabel('Thời Gian')
    axs[0, 0].set_ylabel('Điện Áp (V)')
    axs[0, 0].legend()

    # Tín hiệu chỉnh lưu
    axs[0, 1].plot(analysis['rect_out2'], label='Tín Hiệu Sau Chỉnh Lưu')
    axs[0, 1].set_title('Tín Hiệu Sau Chỉnh Lưu')
    axs[0, 1].set_xlabel('Thời Gian')
    axs[0, 1].set_ylabel('Điện Áp (V)')
    axs[0, 1].legend()

    # Trạng thái LED các tầng
    for i in range(3):
        axs[1, 0].plot(analysis[f'led_node{i+1}'], label=f'Tầng {i+1}')
    axs[1, 0].set_title('Trạng Thái LED Các Tầng')
    axs[1, 0].set_xlabel('Thời Gian')
    axs[1, 0].set_ylabel('Điện Áp (V)')
    axs[1, 0].legend()

    # Trạng thái cảm biến các tầng
    for i in range(3):
        axs[1, 1].plot(analysis[f'pir_node{i+1}'], label=f'Tầng {i+1}')
    axs[1, 1].set_title('Trạng Thái Cảm Biến')
    axs[1, 1].set_xlabel('Thời Gian')
    axs[1, 1].set_ylabel('Điện Áp (V)')
    axs[1, 1].legend()

    plt.tight_layout()
    plt.show()

def main():
    # Khởi tạo và chạy mô phỏng
    sim = StaircaseLightingSimulation()
    analysis = sim.run_simulation(duration=0.1)  # 100ms mô phỏng
    
    # Hiển thị kết quả
    plot_simulation_results(analysis)

if __name__ == '__main__':
    main()