from PyQt5.QtWidgets import QLabel
from QualityTable import Quality_Table


class Quality_Section():
    def __init__(self, label, ts_list, tables_list, layout, size_policy):
        self.layout = layout
        self.policy = size_policy
        self.label = label
        self.ts_list = ts_list
        self.tables_list = tables_list

    def setup_quality_tables(self):
        """
        Method to add the gage height quality tables dynamically to the gage height
        tab based upon however many sensor exist at the site which was requested.
        """

        first_run = len(self.tables_list) == 0
        one_table = len(self.ts_list) == 1
        multiple_tables = len(self.ts_list) > 1
        same_number_of_tables = len(self.ts_list) == len(self.tables_list) == 1
        more_tables =  len(self.ts_list) > len(self.tables_list)
        less_tables =  len(self.ts_list) < len(self.tables_list)

        if first_run and one_table:
            self._add_one_table()  

        elif first_run and multiple_tables:
            self._add_multiple_tables()

        elif not first_run and same_number_of_tables and one_table:
            self._restore_the_old_table()

        elif not first_run and same_number_of_tables and not one_table:
            self._update_multiple_table_labels()

        elif more_tables:
            self._add_more_tables_and_update_labels()
        
        elif less_tables:
            self._remove_extra_tables_update_labels()

    def _add_buttons(self, table):
        """
        Add the remove and add buttons to the bottom of the provided table.

        Args:
            table (QualityTable): The table for which the buttons will be below.
        """
        add_button = table.create_add_button()
        remove_button = table.create_remove_button()
        add_button.setSizePolicy(self.policy)
        remove_button.setSizePolicy(self.policy)

        self.layout.addRow(table)
        self.layout.addRow(add_button, remove_button)  
        self.add_widget_spacer()
    
    def _add_label(self, section_label):
        """
        Add the remove and add buttons to the bottom of the provided table.

        Args:
            section_label (str): The table section's label
        """
        table_label = QLabel(section_label)
        table_label.setSizePolicy(self.policy)
        self.layout.addRow(table_label)

    def _add_one_table(self):
        self._add_label(self.label)

        gh_table = Quality_Table("")
        gh_table.setSizePolicy(self.policy)
        self.tables_list.append(gh_table)
        
        self._add_buttons(gh_table)

    def _add_multiple_tables(self):
        for gh_ts in self.ts_list:
            self._add_label(f"{self.label} ({gh_ts.TS_identifier})")

            gh_table = Quality_Table(f"{gh_ts.TS_sublocation}")            
            self.tables_list.append(gh_table)
            self._add_buttons(gh_table)
    
    def _restore_the_old_table(self):
        self._add_label(self.label)

        gh_table = self.tables_list[0]
        gh_table.setSizePolicy(self.policy)

        self._add_buttons(gh_table)

        self.tables_list = []
        self.tables_list.append(gh_table)

    def _update_multiple_table_labels(self):
        new_gh_tables = []
        for gh_ts, old_gh_table in zip(self.ts_list, self.tables_list):
            self._add_label(f"{self.label} ({gh_ts.TS_identifier})")
            old_gh_table.setSizePolicy(self.policy)
            new_gh_tables.append(old_gh_table)
            
            self._add_buttons(old_gh_table)
            
            self.tables_list = new_gh_tables

    def _add_more_tables_and_update_labels(self):
        new_gh_tables = []
        for old_gh_index, old_gh_table in enumerate(self.tables_list):
            self._add_label(f"{self.label} ({self.ts_list[old_gh_index].TS_identifier})")
            old_gh_table.setSizePolicy(self.policy)
            new_gh_tables.append(old_gh_table)

            self._add_buttons(old_gh_table)
        
        for new_site_ts_index in range(len(self.tables_list), len(self.ts_list)):
            new_ts = self.ts_list[new_site_ts_index]
            
            ts_label = QLabel(self.label)
            if len(self.ts_list) > 1:
                ts_label = QLabel(f"{self.label} ({new_ts.TS_identifier})")
            self.layout.addRow(ts_label)

            gh_table = Quality_Table(f"{new_ts.TS_sublocation}")            
            self._add_buttons(gh_table)
        
        self.tables_list = new_gh_tables

    def _remove_extra_tables_update_labels(self):
        new_gh_tables = []
        for old_gh_index, old_gh_table in enumerate(self.tables_list):
            if old_gh_index < len(self.ts_list):
                self._add_label(f"{self.label} ({self.ts_list[old_gh_index].TS_identifier})")
                old_gh_table.setSizePolicy(self.policy)
                new_gh_tables.append(old_gh_table)
                
                self._add_buttons(old_gh_table)
        
        self.tables_list = new_gh_tables
    
    def add_widget_spacer(self):
        """
        Helper method to simply two newlines to the field form
        """
        self.layout.addRow(QLabel(""))