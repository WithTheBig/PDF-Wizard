import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QListWidget, QFileDialog, QMessageBox, QHBoxLayout, QTabWidget,
    QTextEdit, QLabel
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
from PyPDF2 import PdfReader, PdfWriter


class PDFMergerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('PDF-Wizard 🧙‍♂️')
        self.setWindowIcon(QIcon('PDFRM.ico'))
        self.setGeometry(100, 100, 500, 400)

        self.tabs = QTabWidget()

        self.merge_tab = QWidget()
        self.order_tab = QWidget()
        self.remove_tab = QWidget()

        self.tabs.addTab(self.merge_tab, "Merge PDFs")
        self.tabs.addTab(self.order_tab, "Custom Order")
        self.tabs.addTab(self.remove_tab, "Remove Pages")

        self.init_merge_tab()
        self.init_order_tab()
        self.init_remove_tab()

        layout = QVBoxLayout()
        layout.addWidget(self.tabs)
        self.setLayout(layout)

        self.file_paths = []

    def init_merge_tab(self):
        layout = QVBoxLayout()

        self.file_list_widget = QListWidget()
        self.file_list_widget.setAcceptDrops(True)
        self.file_list_widget.setDragDropMode(QListWidget.InternalMove)
        self.file_list_widget.setSelectionMode(QListWidget.SingleSelection)

        add_button = QPushButton('Add PDFs')
        add_button.clicked.connect(self.add_pdfs)

        remove_button = QPushButton('Remove Selected')
        remove_button.clicked.connect(self.remove_selected)

        up_button = QPushButton('▲')
        up_button.clicked.connect(self.move_up)

        down_button = QPushButton('▼')
        down_button.clicked.connect(self.move_down)

        self.merge_button = QPushButton('Merge PDFs')
        self.merge_button.clicked.connect(self.merge_pdfs)

        button_layout = QHBoxLayout()
        button_layout.addWidget(add_button)
        button_layout.addWidget(remove_button)
        button_layout.addWidget(up_button)
        button_layout.addWidget(down_button)

        layout.addWidget(self.file_list_widget)
        layout.addLayout(button_layout)
        layout.addWidget(self.merge_button)

        self.merge_tab.setLayout(layout)

    def move_up(self):
        current_row = self.file_list_widget.currentRow()
        if current_row > 0:
            self.file_paths[current_row], self.file_paths[current_row - 1] = self.file_paths[current_row - 1], self.file_paths[current_row]
            self.file_list_widget.insertItem(current_row - 1, self.file_list_widget.takeItem(current_row))
            self.file_list_widget.setCurrentRow(current_row - 1)

    def move_down(self):
        current_row = self.file_list_widget.currentRow()
        if current_row < self.file_list_widget.count() - 1:
            self.file_paths[current_row], self.file_paths[current_row + 1] = self.file_paths[current_row + 1], self.file_paths[current_row]
            self.file_list_widget.insertItem(current_row + 1, self.file_list_widget.takeItem(current_row))
            self.file_list_widget.setCurrentRow(current_row + 1)

    def init_order_tab(self):
        layout = QVBoxLayout()

        self.order_input = QTextEdit()
        self.order_input.setPlaceholderText(
            "First number is which pdf, second number is page of the PDF, e.g. 11, 21, 12, 22")

        self.add_order_pdfs_button = QPushButton("Add PDFs to Order")
        self.add_order_pdfs_button.clicked.connect(self.add_pdfs_to_order_tab)

        self.order_merge_button = QPushButton("Merge with Custom Order")
        self.order_merge_button.clicked.connect(self.merge_pdfs_custom_order)

        self.order_list_widget = QListWidget()

        # Buttons for removing PDFs and changing order
        remove_selected_button = QPushButton('Remove Selected')
        remove_selected_button.clicked.connect(self.remove_selected_from_order)

        up_button = QPushButton('▲')
        up_button.clicked.connect(self.move_up)

        down_button = QPushButton('▼')
        down_button.clicked.connect(self.move_down)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.add_order_pdfs_button)
        button_layout.addWidget(remove_selected_button)
        button_layout.addWidget(up_button)
        button_layout.addWidget(down_button)

        layout.addWidget(self.order_list_widget)
        layout.addLayout(button_layout)
        layout.addWidget(self.order_input)
        layout.addWidget(self.order_merge_button)

        self.order_tab.setLayout(layout)

    def init_remove_tab(self):
        layout = QVBoxLayout()

        self.remove_file_label = QLabel("No file selected")
        self.remove_file_button = QPushButton("Select PDF")
        self.remove_file_button.clicked.connect(self.select_pdf_to_remove_pages)

        self.pages_input = QTextEdit()
        self.pages_input.setPlaceholderText("Enter page or more to remove e.g. 1,3,5)")

        self.remove_pages_button = QPushButton("Remove Pages and Save")
        self.remove_pages_button.clicked.connect(self.remove_pages_from_pdf)

        layout.addWidget(self.remove_file_label)
        layout.addWidget(self.remove_file_button)
        layout.addWidget(self.pages_input)
        layout.addWidget(self.remove_pages_button)

        self.remove_tab.setLayout(layout)

    def add_pdfs(self):
        selected_files, _ = QFileDialog.getOpenFileNames(self, 'Select PDFs', '', 'PDF Files (*.pdf)')
        if selected_files:
            for file_path in selected_files:
                if file_path not in self.file_paths:
                    self.file_paths.append(file_path)
                    self.file_list_widget.addItem(os.path.basename(file_path))

    def remove_selected(self):
        selected_row = self.file_list_widget.currentRow()
        if selected_row >= 0:
            self.file_list_widget.takeItem(selected_row)
            del self.file_paths[selected_row]

    def merge_pdfs(self):
        if not self.file_paths:
            QMessageBox.warning(self, 'Error', 'No PDFs added to merge.')
            return

        pdf_writer = PdfWriter()
        for pdf_path in self.file_paths:
            try:
                pdf_reader = PdfReader(pdf_path)
                for page in pdf_reader.pages:
                    pdf_writer.add_page(page)
            except Exception as e:
                QMessageBox.critical(self, 'Error', f'Failed to read {pdf_path}: {str(e)}')
                return

        output_filename, _ = QFileDialog.getSaveFileName(self, 'Save Merged PDF', '', 'PDF Files (*.pdf)')
        if output_filename:
            try:
                with open(output_filename, 'wb') as output_pdf:
                    pdf_writer.write(output_pdf)
                QMessageBox.information(self, 'Success', 'PDFs merged successfully!')
            except Exception as e:
                QMessageBox.critical(self, 'Error', f'Failed to save PDF: {str(e)}')

    def merge_pdfs_custom_order(self):
        if not self.order_file_paths:
            QMessageBox.warning(self, 'Error', 'No PDFs added to Custom Order.')
            return

        order_text = self.order_input.toPlainText().replace(" ", "")
        order_list = order_text.split(",")

        pdf_writer = PdfWriter()

        for order in order_list:
            try:
                pdf_index = int(order[0]) - 1  # Welches PDF?
                page_index = int(order[1]) - 1  # Welche Seite?

                if 0 <= pdf_index < len(self.order_file_paths):
                    pdf_reader = PdfReader(self.order_file_paths[pdf_index])
                    if 0 <= page_index < len(pdf_reader.pages):
                        pdf_writer.add_page(pdf_reader.pages[page_index])
                    else:
                        QMessageBox.warning(self, 'Error',
                                            f'Invalid page number {page_index + 1} for PDF {pdf_index + 1}.')
                        return
                else:
                    QMessageBox.warning(self, 'Error', f'Invalid PDF index {pdf_index + 1}.')
                    return

            except Exception as e:
                QMessageBox.critical(self, 'Error', f'Invalid order input: {str(e)}')
                return

        output_filename, _ = QFileDialog.getSaveFileName(self, 'Save Custom Ordered PDF', '', 'PDF Files (*.pdf)')
        if output_filename:
            try:
                with open(output_filename, 'wb') as output_pdf:
                    pdf_writer.write(output_pdf)
                QMessageBox.information(self, 'Success', 'PDFs merged with custom order successfully!')
            except Exception as e:
                QMessageBox.critical(self, 'Error', f'Failed to save PDF: {str(e)}')

    def select_pdf_to_remove_pages(self):
        file_path, _ = QFileDialog.getOpenFileName(self, 'Select PDF', '', 'PDF Files (*.pdf)')
        if file_path:
            self.pdf_to_edit = file_path
            self.remove_file_label.setText(os.path.basename(file_path))

    def remove_pages_from_pdf(self):
        if not hasattr(self, 'pdf_to_edit') or not self.pdf_to_edit:
            QMessageBox.warning(self, 'Error', 'No PDF selected.')
            return

        pages_text = self.pages_input.toPlainText().replace(" ", "")
        try:
            pages_to_remove = set(int(page) - 1 for page in pages_text.split(",") if page.isdigit())
        except ValueError:
            QMessageBox.critical(self, 'Error', 'Invalid page numbers.')
            return

        pdf_reader = PdfReader(self.pdf_to_edit)
        pdf_writer = PdfWriter()

        for i, page in enumerate(pdf_reader.pages):
            if i not in pages_to_remove:
                pdf_writer.add_page(page)

        output_filename, _ = QFileDialog.getSaveFileName(self, 'Save Edited PDF', '', 'PDF Files (*.pdf)')
        if output_filename:
            with open(output_filename, 'wb') as output_pdf:
                pdf_writer.write(output_pdf)
            QMessageBox.information(self, 'Success', 'Pages removed successfully!')

    def add_pdfs_to_order_tab(self):
        selected_files, _ = QFileDialog.getOpenFileNames(self, 'Select PDFs', '', 'PDF Files (*.pdf)')
        if selected_files:
            for file_path in selected_files:
                if file_path not in self.file_paths:
                    self.file_paths.append(file_path)
                    self.order_list_widget.addItem(os.path.basename(file_path))

    def remove_selected_from_order(self):
        selected_row = self.order_list_widget.currentRow()
        if selected_row >= 0:
            self.order_list_widget.takeItem(selected_row)
            del self.file_paths[selected_row]

    def move_up(self):
        current_row = self.order_list_widget.currentRow()
        if current_row > 0:
            self.file_paths[current_row], self.file_paths[current_row - 1] = self.file_paths[current_row - 1], \
                                                                             self.file_paths[current_row]
            self.order_list_widget.insertItem(current_row - 1, self.order_list_widget.takeItem(current_row))
            self.order_list_widget.setCurrentRow(current_row - 1)

    def move_down(self):
        current_row = self.order_list_widget.currentRow()
        if current_row < self.order_list_widget.count() - 1:
            self.file_paths[current_row], self.file_paths[current_row + 1] = self.file_paths[current_row + 1], \
                                                                             self.file_paths[current_row]
            self.order_list_widget.insertItem(current_row + 1, self.order_list_widget.takeItem(current_row))
            self.order_list_widget.setCurrentRow(current_row + 1)


def main():
    app = QApplication(sys.argv)
    merger_app = PDFMergerApp()
    merger_app.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
