from pathlib import Path

import pandas as pd
from docx import Document
from docx.table import Table


class TemplateFillerException(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

    def __repr__(self) -> str:
        return self.message


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
            table (Table): Table object representing a table within a .docx file

        Returns:
            list[Table.row_cells]: List of table row cells
        """
        return table.row_cells(0)

    def populate_table(self, table: Table, df: pd.DataFrame):
        """Populate a table with the contents of a pandas dataframe

        Args:
            table (Table): Table object representing a table within a .docx file
            df (pd.DataFrame): Pandas dataframe of future table contents
        """
        self.__class__.remove_all_rows(table)
        self._verify_new_rows(table, df)

        for i in range(df.shape[0]):
            table.add_row()
            for j in range(df.shape[-1]):
                table.cell(i + 1, j).text = str(df.values[i, j])

    def _verify_new_rows(self, table: Table, df: pd.DataFrame):
        """Verify dimension of new rows to be added to existing table
        Pandas dataframe width should be the columnar dimension of the table
        i.e. the number of columns should match in both

        Args:
            table (Table): Table object representing a table within a .docx file
            df (pd.DataFrame): Pandas dataframe of future table contents

        Raises:
            TemplateFillerException: DataFrame dimensions do not match table
        """
        message = f"Pandas dataframe with shape {df.shape}. Table has {table.columns} columns - dimension mismatch."
        if not df.shape[1] == len(table.columns):
            raise TemplateFillerException(message)

    def save_document(self, output_path: Path):
        """Save the document to the defined output path

        Args:
            output_path (Path): Output file path
        """
        self.doc.save(output_path)
