from pathlib import Path

import pandas as pd
from docx import Document
from docx.table import Table


class TemplateFiller:
    def __init__(self, template_path: Path):
        self.doc = Document(template_path)
        self.tables = self.doc.tables

    @staticmethod
    def remove_all_rows(table: Table):
        """Remove all rows in a table except for title

        Args:
            table (Table): Table within a .docx file
        """
        total_rows = len(table.rows) - 1
        for row_number in range(total_rows, 0, -1):
            row = table.rows[row_number]
            row._element.getparent().remove(row._element)
        return

    def view_header(self, table: Table) -> list[Table.row_cells]:
        """View header text
        Can't read comments with python-docx

        Args:
            table (Table): Table within a .docx file

        Returns:
            list[Table.row_cells]: List of table row cells
        """
        return table.row_cells(0)

    def populate_table(self, table: Table, df: pd.DataFrame):
        """Populate a table with the contents of a pandas dataframe

        Args:
            table (Table): Table within a .docx file
            df (pd.DataFrame): Pandas dataframe of table contents
        """
        self.__class__.remove_all_rows(table)
        assert len(df) == 0
        # Add a new row and populate the text value
        new_row = table.add_row()
        cell_count = 0
        for cell in new_row.cells:
            cell.text = f"{cell_count}: long text values wrap as expected based on their width"
            cell_count += 1

    def save_document(self, output_path: Path):
        """Save the document"""
        self.doc.save(output_path)
