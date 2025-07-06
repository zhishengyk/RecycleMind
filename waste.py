from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QMessageBox, QLabel, QDialog, QFormLayout, QLineEdit, QDialogButtonBox,
    QTabWidget, QComboBox, QSpinBox, QDoubleSpinBox, QTextEdit, QGroupBox, QGridLayout
)
from PyQt6.QtCore import Qt
from db import get_db_conn
import numpy as np
from scipy.optimize import minimize
import json

WASTE_FIELDS = [
    "名称", "区域", "Si(%)", "Fe(%)", "Cu(%)", "Mn(%)", "Mg(%)", "Zn(%)", "Ti(%)", "Cr(%)", "Ni(%)",
    "Zr(%)", "Sr(%)", "Bi(%)", "Na(%)", "Al(%)", "重量(kg)", "单价(元/kg)"
]

ELEMENT_FIELDS = ["Si", "Fe", "Cu", "Mn", "Mg", "Zn", "Ti", "Cr", "Ni", "Zr", "Sr", "Bi", "Na", "Al"]

class ProductStandardDialog(QDialog):
    def __init__(self, parent=None, data=None):
        super().__init__(parent)
        self.setWindowTitle("产品标准")
        self.setMinimumWidth(600)
        self.edits = {}
        layout = QFormLayout(self)
        
        # 产品名称
        self.name_edit = QLineEdit(self)
        if data:
            self.name_edit.setText(data.get('name', ''))
        layout.addRow("产品名称", self.name_edit)
        
        # 添加说明标签
        info_label = QLabel("请设置各元素在最终产品中的含量范围（百分比）")
        info_label.setStyleSheet("color: gray; font-size: 10px;")
        layout.addRow(info_label)
        
        # 元素含量范围
        element_group = QGroupBox("元素含量范围")
        element_layout = QGridLayout(element_group)
        
        for i, element in enumerate(ELEMENT_FIELDS):
            row = i // 3
            col = i % 3 * 2
            
            # 最小值
            min_edit = QDoubleSpinBox()
            min_edit.setRange(0, 100)
            min_edit.setDecimals(3)
            min_edit.setSuffix(" %")
            if data and element in data.get('ranges', {}):
                min_edit.setValue(data['ranges'][element]['min'])
            
            # 最大值
            max_edit = QDoubleSpinBox()
            max_edit.setRange(0, 100)
            max_edit.setDecimals(3)
            max_edit.setSuffix(" %")
            if data and element in data.get('ranges', {}):
                max_edit.setValue(data['ranges'][element]['max'])
            
            element_layout.addWidget(QLabel(f"{element}:"), row, col)
            element_layout.addWidget(min_edit, row, col + 1)
            element_layout.addWidget(QLabel("~"), row, col + 2)
            element_layout.addWidget(max_edit, row, col + 3)
            
            self.edits[element] = {'min': min_edit, 'max': max_edit}
        
        layout.addRow(element_group)
        
        # 按钮
        btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)

    def get_data(self):
        data = {
            'name': self.name_edit.text(),
            'ranges': {}
        }
        for element, edits in self.edits.items():
            data['ranges'][element] = {
                'min': edits['min'].value(),
                'max': edits['max'].value()
            }
        return data

class WasteDialog(QDialog):
    def __init__(self, parent=None, data=None):
        super().__init__(parent)
        self.setWindowTitle("废料信息")
        self.edits = []
        layout = QFormLayout(self)
        
        # 创建字段标签和输入框的映射
        field_labels = {
            "名称": "废料名称",
            "区域": "存放区域",
            "Si(%)": "硅含量(%)",
            "Fe(%)": "铁含量(%)",
            "Cu(%)": "铜含量(%)",
            "Mn(%)": "锰含量(%)",
            "Mg(%)": "镁含量(%)",
            "Zn(%)": "锌含量(%)",
            "Ti(%)": "钛含量(%)",
            "Cr(%)": "铬含量(%)",
            "Ni(%)": "镍含量(%)",
            "Zr(%)": "锆含量(%)",
            "Sr(%)": "锶含量(%)",
            "Bi(%)": "铋含量(%)",
            "Na(%)": "钠含量(%)",
            "Al(%)": "铝含量(%)",
            "重量(kg)": "重量(kg)",
            "单价(元/kg)": "单价(元/kg)"
        }
        
        for i, field in enumerate(WASTE_FIELDS):
            edit = QLineEdit(self)
            if data:
                edit.setText(str(data[i]))
            
            # 为化学成分字段添加占位符提示
            if "%)" in field and field != "重量(kg)" and field != "单价(元/kg)":
                edit.setPlaceholderText("请输入百分比数值，如: 0.5")
            
            layout.addRow(field_labels.get(field, field), edit)
            self.edits.append(edit)
        
        btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)

    def get_data(self):
        return [edit.text() for edit in self.edits]

class OptimizationResultDialog(QDialog):
    def __init__(self, parent=None, result_data=None):
        super().__init__(parent)
        self.setWindowTitle("合成方案结果")
        self.setMinimumSize(800, 600)
        layout = QVBoxLayout(self)
        
        # 方案摘要
        summary_group = QGroupBox("方案摘要")
        summary_layout = QVBoxLayout(summary_group)
        
        if result_data:
            summary_text = f"""
            总成本: {result_data['total_cost']:.2f} 元
            总重量: {result_data['total_weight']:.2f} kg
            平均单价: {result_data['avg_price']:.2f} 元/kg
            可行性: {'可行' if result_data['feasible'] else '不可行'}
            """
            summary_label = QLabel(summary_text)
            summary_layout.addWidget(summary_label)
        
        layout.addWidget(summary_group)
        
        # 详细配比
        if result_data and 'waste_mix' in result_data:
            mix_group = QGroupBox("废料配比")
            mix_layout = QVBoxLayout(mix_group)
            
            mix_table = QTableWidget()
            mix_table.setColumnCount(4)
            mix_table.setHorizontalHeaderLabels(["废料名称", "区域", "重量(kg)", "占比(%)"])
            
            waste_mix = result_data['waste_mix']
            mix_table.setRowCount(len(waste_mix))
            for row, (name, mix_data) in enumerate(waste_mix.items()):
                if mix_data['weight'] > 0:
                    mix_table.setItem(row, 0, QTableWidgetItem(name))
                    mix_table.setItem(row, 1, QTableWidgetItem(mix_data['area']))
                    mix_table.setItem(row, 2, QTableWidgetItem(f"{mix_data['weight']:.2f}"))
                    mix_table.setItem(row, 3, QTableWidgetItem(f"{mix_data['weight']/result_data['total_weight']*100:.2f}"))
            
            mix_layout.addWidget(mix_table)
            layout.addWidget(mix_group)
        
        # 元素分析
        if result_data and 'element_analysis' in result_data:
            analysis_group = QGroupBox("元素分析")
            analysis_layout = QVBoxLayout(analysis_group)
            
            analysis_table = QTableWidget()
            analysis_table.setColumnCount(4)
            analysis_table.setHorizontalHeaderLabels(["元素", "含量(%)", "目标范围(%)", "状态"])
            
            element_analysis = result_data['element_analysis']
            analysis_table.setRowCount(len(element_analysis))
            for row, (element, data) in enumerate(element_analysis.items()):
                analysis_table.setItem(row, 0, QTableWidgetItem(element))
                analysis_table.setItem(row, 1, QTableWidgetItem(f"{data['content']:.3f}%"))
                analysis_table.setItem(row, 2, QTableWidgetItem(f"{data['target_min']:.3f}%~{data['target_max']:.3f}%"))
                status = "✓" if data['in_range'] else "✗"
                analysis_table.setItem(row, 3, QTableWidgetItem(status))
            
            analysis_layout.addWidget(analysis_table)
            layout.addWidget(analysis_group)
        
        # 关闭按钮
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

class WasteManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("废料管理系统")
        self.resize(1200, 700)
        self.waste_data = []
        self.product_standards = []
        self.init_ui()
        self.load_waste_data()
        self.load_product_standards()

    def load_waste_data(self):
        try:
            conn = get_db_conn()
            with conn.cursor() as cursor:
                cursor.execute("SELECT 名称, 区域, Si, Fe, Cu, Mn, Mg, Zn, Ti, Cr, Ni, Zr, Sr, Bi, Na, Al, 重量, 单价 FROM wastes")
                self.waste_data = [list(map(str, row)) for row in cursor.fetchall()]
            self.refresh_waste_table()
        except Exception as e:
            QMessageBox.critical(self, "数据库错误", str(e))
        finally:
            if 'conn' in locals():
                conn.close()

    def load_product_standards(self):
        try:
            conn = get_db_conn()
            with conn.cursor() as cursor:
                cursor.execute("SELECT name, ranges FROM product_standards")
                self.product_standards = []
                for row in cursor.fetchall():
                    self.product_standards.append({
                        'name': row[0],
                        'ranges': json.loads(row[1])
                    })
            self.refresh_standard_table()
        except Exception as e:
            QMessageBox.critical(self, "数据库错误", str(e))
        finally:
            if 'conn' in locals():
                conn.close()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # 创建标签页
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # 废料管理标签页
        self.init_waste_tab()
        
        # 产品标准标签页
        self.init_standard_tab()
        
        # 合成方案标签页
        self.init_optimization_tab()

    def init_waste_tab(self):
        waste_widget = QWidget()
        layout = QVBoxLayout(waste_widget)
        
        title = QLabel("仓库废料库存")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        self.waste_table = QTableWidget(0, len(WASTE_FIELDS))
        self.waste_table.setHorizontalHeaderLabels(WASTE_FIELDS)
        layout.addWidget(self.waste_table)
        
        btn_layout = QHBoxLayout()
        self.btn_add = QPushButton("添加废料")
        self.btn_edit = QPushButton("编辑废料")
        self.btn_delete = QPushButton("删除废料")
        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_edit)
        btn_layout.addWidget(self.btn_delete)
        layout.addLayout(btn_layout)
        
        self.btn_add.clicked.connect(self.add_waste)
        self.btn_edit.clicked.connect(self.edit_waste)
        self.btn_delete.clicked.connect(self.delete_waste)
        
        self.tab_widget.addTab(waste_widget, "废料管理")

    def init_standard_tab(self):
        standard_widget = QWidget()
        layout = QVBoxLayout(standard_widget)
        
        title = QLabel("产品标准管理")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        self.standard_table = QTableWidget(0, 2)
        self.standard_table.setHorizontalHeaderLabels(["产品名称", "操作"])
        layout.addWidget(self.standard_table)
        
        btn_layout = QHBoxLayout()
        self.btn_add_standard = QPushButton("添加产品标准")
        self.btn_edit_standard = QPushButton("编辑产品标准")
        self.btn_delete_standard = QPushButton("删除产品标准")
        btn_layout.addWidget(self.btn_add_standard)
        btn_layout.addWidget(self.btn_edit_standard)
        btn_layout.addWidget(self.btn_delete_standard)
        layout.addLayout(btn_layout)
        
        self.btn_add_standard.clicked.connect(self.add_product_standard)
        self.btn_edit_standard.clicked.connect(self.edit_product_standard)
        self.btn_delete_standard.clicked.connect(self.delete_product_standard)
        
        self.tab_widget.addTab(standard_widget, "产品标准")

    def init_optimization_tab(self):
        optimization_widget = QWidget()
        layout = QVBoxLayout(optimization_widget)
        
        title = QLabel("合成方案计算")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # 选择产品标准
        select_layout = QHBoxLayout()
        select_layout.addWidget(QLabel("选择产品标准:"))
        self.standard_combo = QComboBox()
        select_layout.addWidget(self.standard_combo)
        layout.addLayout(select_layout)
        
        # 区域筛选
        area_layout = QHBoxLayout()
        area_layout.addWidget(QLabel("区域筛选:"))
        self.area_combo = QComboBox()
        self.area_combo.addItem("全部区域")
        self.area_combo.currentTextChanged.connect(self.update_area_filter)
        area_layout.addWidget(self.area_combo)
        layout.addLayout(area_layout)
        
        # 计算按钮
        self.btn_calc = QPushButton("计算最佳合成方案")
        self.btn_calc.clicked.connect(self.calculate_optimization)
        layout.addWidget(self.btn_calc)
        
        # 结果显示区域
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        layout.addWidget(self.result_text)
        
        self.tab_widget.addTab(optimization_widget, "合成方案")

    def refresh_waste_table(self):
        self.waste_table.setRowCount(len(self.waste_data))
        for row, data in enumerate(self.waste_data):
            for col, value in enumerate(data):
                self.waste_table.setItem(row, col, QTableWidgetItem(str(value)))

    def refresh_standard_table(self):
        self.standard_table.setRowCount(len(self.product_standards))
        self.standard_combo.clear()
        
        for row, standard in enumerate(self.product_standards):
            # 产品名称
            self.standard_table.setItem(row, 0, QTableWidgetItem(standard['name']))
            
            # 操作按钮
            btn_layout = QHBoxLayout()
            view_btn = QPushButton("查看")
            view_btn.clicked.connect(lambda checked, s=standard: self.view_standard(s))
            btn_layout.addWidget(view_btn)
            
            btn_widget = QWidget()
            btn_widget.setLayout(btn_layout)
            self.standard_table.setCellWidget(row, 1, btn_widget)
            
            # 添加到下拉框
            self.standard_combo.addItem(standard['name'])
        
        # 更新区域筛选下拉框
        self.update_area_combo()

    def update_area_combo(self):
        """更新区域筛选下拉框"""
        self.area_combo.clear()
        self.area_combo.addItem("全部区域")
        
        # 获取所有区域
        areas = set()
        for row in self.waste_data:
            if len(row) > 1:  # 确保有区域字段
                areas.add(row[1])
        
        for area in sorted(areas):
            self.area_combo.addItem(area)

    def update_area_filter(self):
        """更新区域筛选"""
        # 这个方法会在区域选择改变时被调用
        # 可以在这里添加区域筛选逻辑
        pass

    def add_waste(self):
        dlg = WasteDialog(self)
        if dlg.exec():
            data = dlg.get_data()
            try:
                conn = get_db_conn()
                with conn.cursor() as cursor:
                    sql = ("INSERT INTO wastes (名称, 区域, Si, Fe, Cu, Mn, Mg, Zn, Ti, Cr, Ni, Zr, Sr, Bi, Na, Al, 重量, 单价) "
                           "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")
                    cursor.execute(sql, data)
                    conn.commit()
                self.load_waste_data()
            except Exception as e:
                QMessageBox.critical(self, "数据库错误", str(e))
            finally:
                if 'conn' in locals():
                    conn.close()

    def edit_waste(self):
        row = self.waste_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "提示", "请先选择要编辑的废料")
            return
        dlg = WasteDialog(self, self.waste_data[row])
        if dlg.exec():
            data = dlg.get_data()
            try:
                conn = get_db_conn()
                with conn.cursor() as cursor:
                    sql = ("UPDATE wastes SET 区域=%s, Si=%s, Fe=%s, Cu=%s, Mn=%s, Mg=%s, Zn=%s, Ti=%s, Cr=%s, Ni=%s, "
                           "Zr=%s, Sr=%s, Bi=%s, Na=%s, Al=%s, 重量=%s, 单价=%s WHERE 名称=%s")
                    cursor.execute(sql, data[1:] + [data[0]])
                    conn.commit()
                self.load_waste_data()
            except Exception as e:
                QMessageBox.critical(self, "数据库错误", str(e))
            finally:
                if 'conn' in locals():
                    conn.close()

    def delete_waste(self):
        row = self.waste_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "提示", "请先选择要删除的废料")
            return
        name = self.waste_data[row][0]
        try:
            conn = get_db_conn()
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM wastes WHERE 名称=%s", (name,))
                conn.commit()
            self.load_waste_data()
        except Exception as e:
            QMessageBox.critical(self, "数据库错误", str(e))
        finally:
            if 'conn' in locals():
                conn.close()

    def add_product_standard(self):
        dlg = ProductStandardDialog(self)
        if dlg.exec():
            data = dlg.get_data()
            try:
                conn = get_db_conn()
                with conn.cursor() as cursor:
                    sql = "INSERT INTO product_standards (name, ranges) VALUES (%s, %s)"
                    cursor.execute(sql, (data['name'], json.dumps(data['ranges'])))
                    conn.commit()
                self.load_product_standards()
            except Exception as e:
                QMessageBox.critical(self, "数据库错误", str(e))
            finally:
                if 'conn' in locals():
                    conn.close()

    def edit_product_standard(self):
        row = self.standard_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "提示", "请先选择要编辑的产品标准")
            return
        standard = self.product_standards[row]
        dlg = ProductStandardDialog(self, standard)
        if dlg.exec():
            data = dlg.get_data()
            try:
                conn = get_db_conn()
                with conn.cursor() as cursor:
                    sql = "UPDATE product_standards SET ranges=%s WHERE name=%s"
                    cursor.execute(sql, (json.dumps(data['ranges']), data['name']))
                    conn.commit()
                self.load_product_standards()
            except Exception as e:
                QMessageBox.critical(self, "数据库错误", str(e))
            finally:
                if 'conn' in locals():
                    conn.close()

    def delete_product_standard(self):
        row = self.standard_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "提示", "请先选择要删除的产品标准")
            return
        name = self.product_standards[row]['name']
        try:
            conn = get_db_conn()
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM product_standards WHERE name=%s", (name,))
                conn.commit()
            self.load_product_standards()
        except Exception as e:
            QMessageBox.critical(self, "数据库错误", str(e))
        finally:
            if 'conn' in locals():
                conn.close()

    def view_standard(self, standard):
        dlg = ProductStandardDialog(self, standard)
        dlg.name_edit.setReadOnly(True)
        for element_edits in dlg.edits.values():
            element_edits['min'].setReadOnly(True)
            element_edits['max'].setReadOnly(True)
        dlg.exec()

    def calculate_optimization(self):
        if not self.waste_data:
            QMessageBox.warning(self, "提示", "没有废料数据")
            return
        
        if self.standard_combo.currentText() == "":
            QMessageBox.warning(self, "提示", "请选择产品标准")
            return
        
        # 获取选中的产品标准
        selected_standard_name = self.standard_combo.currentText()
        selected_standard = None
        for standard in self.product_standards:
            if standard['name'] == selected_standard_name:
                selected_standard = standard
                break
        
        if not selected_standard:
            QMessageBox.warning(self, "提示", "产品标准数据错误")
            return
        
        # 获取选中的区域
        selected_area = self.area_combo.currentText()
        
        # 执行优化计算
        result = self.optimize_mix(selected_standard, selected_area)
        
        # 显示结果
        dlg = OptimizationResultDialog(self, result)
        dlg.exec()

    def optimize_mix(self, standard, selected_area="全部区域"):
        """优化混合方案"""
        try:
            # 根据区域筛选废料数据
            filtered_waste_data = self.waste_data
            if selected_area != "全部区域":
                filtered_waste_data = [row for row in self.waste_data if row[1] == selected_area]
            
            if not filtered_waste_data:
                return {
                    'feasible': False,
                    'message': f'在区域 "{selected_area}" 中没有找到废料数据'
                }
            
            # 准备数据
            waste_names = [row[0] for row in filtered_waste_data]
            waste_areas = [row[1] for row in filtered_waste_data]  # 区域
            waste_weights = [float(row[16]) for row in filtered_waste_data]  # 重量
            waste_prices = [float(row[17]) for row in filtered_waste_data]   # 单价
            
            # 元素含量矩阵 (废料数量 x 元素数量)
            element_matrix = []
            for row in filtered_waste_data:
                element_row = []
                for i in range(2, 16):  # Si到Al的14个元素（跳过名称和区域）
                    try:
                        element_row.append(float(row[i]) / 100.0)  # 转换为小数
                    except:
                        element_row.append(0.0)
                element_matrix.append(element_row)
            
            element_matrix = np.array(element_matrix)
            
            # 目标范围
            target_ranges = standard['ranges']
            
            # 定义目标函数：最小化总成本
            def objective(x):
                return np.sum(x * waste_prices)
            
            # 约束条件
            constraints = []
            
            # 元素含量约束
            for i, element in enumerate(ELEMENT_FIELDS):
                if element in target_ranges:
                    min_val = target_ranges[element]['min'] / 100.0
                    max_val = target_ranges[element]['max'] / 100.0
                    
                    # 最小含量约束
                    constraints.append({
                        'type': 'ineq',
                        'fun': lambda x, i=i, min_val=min_val: 
                              np.sum(x * element_matrix[:, i]) - min_val * np.sum(x)
                    })
                    
                    # 最大含量约束
                    constraints.append({
                        'type': 'ineq',
                        'fun': lambda x, i=i, max_val=max_val: 
                              max_val * np.sum(x) - np.sum(x * element_matrix[:, i])
                    })
            
            # 重量约束
            for i in range(len(waste_names)):
                constraints.append({
                    'type': 'ineq',
                    'fun': lambda x, i=i, max_weight=waste_weights[i]: max_weight - x[i]
                })
            
            # 非负约束
            bounds = [(0, None)] * len(waste_names)
            
            # 初始猜测
            x0 = np.array(waste_weights) * 0.1  # 使用10%的库存作为初始值
            
            # 优化
            result = minimize(
                objective, x0, 
                method='SLSQP',
                bounds=bounds,
                constraints=constraints,
                options={'maxiter': 1000}
            )
            
            if result.success:
                # 计算结果
                optimal_weights = result.x
                total_weight = np.sum(optimal_weights)
                total_cost = result.fun
                avg_price = total_cost / total_weight if total_weight > 0 else 0
                
                # 计算元素含量
                element_analysis = {}
                for i, element in enumerate(ELEMENT_FIELDS):
                    if element in target_ranges:
                        content = np.sum(optimal_weights * element_matrix[:, i]) / total_weight * 100
                        target_min = target_ranges[element]['min']
                        target_max = target_ranges[element]['max']
                        in_range = target_min <= content <= target_max
                        
                        element_analysis[element] = {
                            'content': content,
                            'target_min': target_min,
                            'target_max': target_max,
                            'in_range': in_range
                        }
                
                # 废料配比
                waste_mix = {}
                for i, name in enumerate(waste_names):
                    if optimal_weights[i] > 0.001:  # 忽略很小的值
                        waste_mix[name] = {
                            'weight': optimal_weights[i],
                            'area': waste_areas[i]
                        }
                
                return {
                    'feasible': True,
                    'total_weight': total_weight,
                    'total_cost': total_cost,
                    'avg_price': avg_price,
                    'waste_mix': waste_mix,
                    'element_analysis': element_analysis
                }
            else:
                return {
                    'feasible': False,
                    'message': '无法找到可行解'
                }
                
        except Exception as e:
            return {
                'feasible': False,
                'message': f'计算错误: {str(e)}'
            }
