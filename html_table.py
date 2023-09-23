class html_table_cell():
    def __init__(self, contents):
        self.contents = contents
       
        
class html_table_row():
    def __init__(self, cell_values_list):
        self.row_cell_list = []
        for column_title in cell_values_list:
            self.row_cell_list.append(html_table_cell(str(column_title)))
        
class html_table():
    def __init__(self, header_row, body_row_list, table_width, column_width_list = []):
        self.header_row = header_row
        self.body_row_list = body_row_list
        self.table_width = str(table_width)
        self.column_width_list = column_width_list
        
    def _create_table_header_html(self) -> str:
        header_str = "<table class=\"table table-condensed\" style=\"box-sizing: border-box; border-collapse: collapse; border-spacing: 0px; background-color: #ffffff; width: " + self.table_width + "px; max-width: 100%; margin-bottom: 20px; color: #333333; font-family: Ubuntu; font-size: 15px;\">\n" \
            "<thead style=\"box-sizing: border-box;\">\n" \
            "<tr class=\"header\" style=\"box-sizing: border-box;\">\n"
        
        for index, header_cell in enumerate(self.header_row.row_cell_list):
            col_width = ""
            if self.column_width_list != []:
                col_width = " width: " + str(self.column_width_list[index]) + "px;"
            header_str = header_str + "<th style=\"border: 1px solid #7f7f7f; box-sizing: border-box; padding: 5px; line-height: 15px; vertical-align: center; text-align: left;" + col_width + "\">" + header_cell.contents + "</th>\n"
        
        header_str = header_str + "</tr>\n" \
            "</thead>\n" \
            
        return header_str
    
    def _create_table_body_html(self) -> str:
        body_str = "<tbody style=\"box-sizing: border-box;\">\n"
        
        for table_row in self.body_row_list:
            body_str = body_str + "<tr class=\"odd\" style=\"box-sizing: border-box;\">\n"
            for cell in table_row.row_cell_list:
                body_str = body_str + "<td style=\"padding: 5px; border: 1px solid #7f7f7f; box-sizing: border-box; line-height: 15px; vertical-align: center; text-align: left;\">" + cell.contents + "</td>\n"
            body_str = body_str + "</tr>\n"
        
        body_str = body_str + "</tbody>\n</table>\n"  
        
        return body_str
    
    def return_html(self) -> str:
         header_str = self._create_table_header_html()
         body_str = self._create_table_body_html()
         table_html = header_str + body_str
         return table_html
