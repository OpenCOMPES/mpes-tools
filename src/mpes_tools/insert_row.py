from PyQt5.QtWidgets import QTableWidgetItem, QHBoxLayout, QCheckBox, QWidget
from PyQt5.QtCore import Qt

def insert_row(table_widget, pos,name, handle_checkbox_state_change_callback):
    c = table_widget.rowCount()
    table_widget.insertRow(pos)
    label_item = QTableWidgetItem(name)
    checkbox_widget = QWidget()
    checkbox_layout = QHBoxLayout()
    checkbox_layout.setAlignment(Qt.AlignCenter)
    checkbox = QCheckBox()
    # connect the checkbox's state change to your callback
    checkbox.stateChanged.connect(lambda state, row=pos: handle_checkbox_state_change_callback(state, row))
    checkbox_layout.addWidget(checkbox)
    checkbox_widget.setLayout(checkbox_layout)
    table_widget.setCellWidget(pos, 3, checkbox_widget)
    table_widget.setVerticalHeaderItem(pos , label_item)