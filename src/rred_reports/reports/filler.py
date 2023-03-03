from pathlib import Path

import pandas as pd
from docx import Document
from docx.table import Table, _Row


class TemplateFillerException(Exception):
    """Custom exception generator for the TemplateFiller class"""

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

    def __repr__(self) -> str:
        return self.message


class TemplateFiller:
    """TemplateFiller class to modify tables in .docx files.

    Provides save/loading, table modification and input verification.
    """

    def __init__(self, template_path: Path):
        self.doc = Document(template_path)
        self.tables = self.doc.tables
        self.clean_tables()

    @staticmethod
    def remove_row(table: Table, row: _Row) -> Table:
        """Remove a single row from a Table object

        Args:
            table (Table): Table object representing a table within a .docx file

        Returns:
            table (Table): Table object representing a table within a .docx file
        """

        tbl = table._tbl  # pylint: disable=protected-access
        table_row = row._tr  # pylint: disable=protected-access
        tbl.remove(table_row)
        return table

    @staticmethod
    def remove_all_rows(table: Table):
        """Remove all rows in a table except for title

        Args:
            table (Table): Table within a .docx file
        """
        total_rows = len(table.rows) - 1
        for row_number in range(total_rows, 0, -1):
            row = table.rows[row_number]
            row._element.getparent().remove(row._element)  # pylint: disable=protected-access

    @staticmethod
    def view_header(table: Table) -> list[Table.row_cells]:
        """View header text
        Can't read comments with python-docx

        Args:
            table (Table): Table object representing a table within a .docx file

        Returns:
            list[Table.row_cells]: List of table row cells
        """
        return table.row_cells(0)

    def clean_tables(self):
        """Perform any necessary table cleaning steps"""
        self.remove_duplicated_columns()

    def remove_duplicated_columns(self):
        """Remove duplicated columns in tables.
        Observed in some test tables, some tables contain columns that appear
        to be hidden when viewed in MS Word.
        """
        updated_tables = []
        for table in self.tables:
            table_header = self.__class__.view_header(table)
            header_text = [cell.text.strip() for cell in table_header]

            headers_df = pd.DataFrame({"duplicate_cols": header_text}).drop_duplicates(keep="first")

            headers = headers_df["duplicate_cols"].to_list()

            if headers != header_text:
                # Duplicate header found...
                self.__class__.remove_all_rows(table)
                row = table.rows[0]
                table = self.__class__.remove_row(table, row)
                table = self.doc.add_table(rows=0, cols=len(headers), style=table.style)
                table.add_row()
                for column, header in enumerate(headers):
                    table.cell(0, column).text = header

            updated_tables.append(table)
        self.tables = updated_tables

    def populate_table(self, table: Table, data: pd.DataFrame):
        """Populate a table with the contents of a pandas dataframe

        Args:
            table (Table): Table object representing a table within a .docx file
            df (pd.DataFrame): Pandas dataframe of future table contents
        """
        self.remove_all_rows(table)
        self._verify_new_rows(table, data)

        for i in range(data.shape[0]):
            table.add_row()
            for j in range(data.shape[-1]):
                table.cell(i + 1, j).text = str(data.values[i, j])

    def _verify_new_rows(self, table: Table, data: pd.DataFrame):
        """Verify dimension of new rows to be added to existing table
        Pandas dataframe width should be the columnar dimension of the table
        i.e. the number of columns should match in both

        Args:
            table (Table): Table object representing a table within a .docx file
            df (pd.DataFrame): Pandas dataframe of future table contents

        Raises:
            TemplateFillerException: DataFrame dimensions do not match table
        """
        table_header = self.__class__.view_header(table)
        contents = [cell.text.strip() for cell in table_header]
        message = f"Pandas dataframe with {data.shape[-1]} columns. Table has {len(table.columns)} columns - dimension mismatch. Table columns are {contents}."
        if not data.shape[1] == len(table.columns):
            raise TemplateFillerException(message)

    def verify_tables_filled(self):
        """Verify all cells in a table are filled

        Args:
            table (Table): Table object representing a table within a .docx file
        """
        for table_idx, table in enumerate(self.tables):
            for i, _row in enumerate(table.rows):
                for j, _col in enumerate(table.columns):
                    cell_content = table.cell(i, j).text
                    if cell_content == "":
                        message = f"Empty cell ({i},{j}) (row, col) found in table {table_idx+1}"
                        raise TemplateFillerException(message)

    def save_document(self, output_path: Path):
        """Save the document to the defined output path

        Args:
            output_path (Path): Output file path
        """
        self.doc.save(output_path)
