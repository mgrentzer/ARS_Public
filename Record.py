from API_Session_V3 import SynchronousAquariusAPISession, SynchronousSIMsAPISession
from datetime import datetime
import SiteV3
import html_table
from User_Inputs import User_Inputs


class Record():
    
    '''
    The object representing the surface water record and all its elements (for 
    gage height only during this iteration).
    
    Args:
        record_start_date(datetime.date): Date of when the record begins
        record_end_date(datetime.date): Date of when the record ends
    '''
    def __init__(self, record_start_date: datetime.date, record_end_date: datetime.date) -> None:
        self.start_date = record_start_date
        self.end_date = record_end_date
        self.record_html = ""
        self.backup_tables = []

        self.field_visit_section = ""
    
    def create_html_record(self, site_obj: SiteV3.Site, User_Inputs):
        '''
        Main method to construct the html version of the record and calls upon helper methods to
        ask for needed information when needed.

        Args:
            site_obj(Site3.Site): The site object representing a site and alls its sensors, attributes, and data
        '''

        if User_Inputs.special_notes != "":
            self.create_special_notes_section(User_Inputs.special_notes)
        else:
            self.special_notes_section = ""

        self.create_hydro_comparison_section(User_Inputs.hydro_comp)

        self.full_html = (self.create_header(site_obj.site_no, site_obj.site_name, User_Inputs.author)
                        + self.special_notes_section
                        + self.field_visit_section
                        + self.create_gh_section(User_Inputs.gh_tables_list)
                        + self.datum_section
                        + self.checkbar_section
                        + self.backup_data_section
                        + self.ice_section
                        + self.edits_section
                        + self.gh_corrections_section
                        + self.data_gaps_section
                        + self.other_gh_corrections_section
                        + self.peak_verifications_section
                        + self.peak_recorder_stage_section
                        + self.create_stage_discharge_header()
                        + self.rating_section
                        + self.qm_section
                        + self.shift_section
                        + self.create_computed_discharge_header()
                        + self.create_discharge_record_section(User_Inputs.q_tables_list)
                        + self.hydro_comp_section
                        + self.peak_recorder_streamflow_section
                        + self.water_year_section
                        ) 
        return self.full_html
        
        '''self._create_gage_height_record_html_section(site_obj)
        
        if len(site_obj.discharge_timeseries_list) > 0:
            self._create_stage_discharge_html_section(site_obj)
            self._create_computed_discharge_html_section(site_obj)
        
        self._create_wy_extremes_tables(site_obj)'''

    def _create_gage_height_record_html_section(self, site_obj: SiteV3.Site):
        '''
        Method to create the html for the gage height record section. This method
        calls various methods to construct the subsections.

        Args:
            site_obj(Site3.Site): The site object representing a site and alls its sensors, attributes, and data
        '''
        for ts in site_obj.gage_height_timeseries_list:
            if ts.primary:
                self.create_gh_section(ts.record_dataset.gaps)
                self.create_gh_section()
        
        self.create_datum_section(site_obj.levels_description)
        
        self.create_checkbar_section(site_obj.field_visits, site_obj.sensors)
        
        self.create_backup_data_section(site_obj.primary_gh_ts.record_dataset.general_corrections)
        self.create_ice_affected_section(site_obj.primary_gh_ts.record_dataset.qualifiers)
        self.create_edits_section(site_obj.primary_gh_ts.record_dataset.general_corrections)
        self.create_gh_correction_section(site_obj.primary_gh_ts.record_dataset.multipoint_corrections)
        self.create_data_gaps_section(site_obj.primary_gh_ts.record_dataset.gaps)
        self.create_other_corrections_section(site_obj.primary_gh_ts.record_dataset.multipoint_corrections)
        self.create_peak_verifications_section(site_obj.field_visits)
        self.create_peak_recorder_stage_section(site_obj.primary_gh_ts.record_dataset)
    
    def _create_stage_discharge_html_section(self, site_obj: SiteV3.Site):
        '''
        Method to create the html for the stage-discharge section. This method
        calls various methods to construct the subsections.

        Args:
            site_obj(Site3.Site): The site object representing a site and alls its sensors, attributes, and data
        '''
        self.create_stage_discharge_header()
        self.create_rating_description(site_obj.ratings_description)
        self.create_qm_section(site_obj.field_visits)
        self.create_shift_curves_section(site_obj.rating_model.ratings_list)
    
    def _create_computed_discharge_html_section(self, site_obj: SiteV3.Site):
        '''
        Method to create the html for the computed discharge section. This method
        calls various methods to construct the subsections.

        Args:
            site_obj(Site3.Site): The site object representing a site and alls its sensors, attributes, and data
        '''
        self.create_computed_discharge_header()
        self.create_discharge_record_section(site_obj.primary_q_ts.record_dataset.gaps, site_obj.primary_q_ts.record_dataset.qualifiers)
        self.create_q_data_gaps_section(site_obj.primary_q_ts.record_dataset.gaps)
        self.create_estimate_section(site_obj.primary_q_ts.record_dataset.general_corrections)
        self.create_backwater_section(site_obj.primary_q_ts.record_dataset.qualifiers)
        self.create_hydro_comparison_section()
        self.create_peak_record_discharge_table(site_obj.primary_q_ts.record_dataset)
    
    def _create_wy_extremes_tables(self, site_obj: SiteV3.Site):
        '''
        Method to create the html for the stage-discharge section. This method
        calls various methods to construct the subsections.

        Args:
            site_obj(Site3.Site): The site object representing a site and alls its sensors, attributes, and data
        '''
        self._create_wy_extremes_table_section(site_obj)
    
    def create_header(self, site_no: str, site_name: str, author:str) -> None:
        '''
        Method to create the html for the stage-discharge section. This method
        calls various methods to construct the subsections.

        Args:
            site_no (str): The ID number of the site.
            site_name(str): The common name of the site describing location and stream
        '''
        # self.author = input("What is your name as the author?\n")
        self.author = author
        self.header = "<p><strong>Station Number: </strong>" + site_no + "\n" \
            "<p><strong>Site Name: </strong>" + site_name + "</p>\n" \
            "<p><strong>Period: </strong>" + self.start_date.strftime("%m/%d/%Y") + "-" + self.end_date.strftime("%m/%d/%Y") + "</p>\n" \
            "<p><strong>Analyst:</strong> " + self.author + "</p>\n" \
            
        return self.header
    
    def create_special_notes_section(self, special_notes: str):
        """
        Method to create the optional hteml for a special notes section as
        provided from the user.
        
        Args:
            special_nots(str): The user's provided special notes
        """
        self.special_notes_section = "<br />\n" + "<p><strong><span style=\"text-decoration: underline;\">Special Notes</span></strong></p>\n" \
        "<div style=\"padding-left:30px;\">\n"

        self.special_notes_section += "<p>" + special_notes + "</p>\n"
        self.special_notes_section += "</div>\n"
        self.record_html += self.special_notes_section

    @staticmethod
    def _return_list_of_field_visit_findings(field_visit):
        '''
        Helper method to return basic findings from a provided field visit object.
        Pertinent findings include recorder resets, discharge measurements, levels,
        and, stage-readings (if not Qm collected).

        Args:
            field_visit (Field_Visit): The initialized field visit being inspected
        '''
        visit_findings_list: list[str] = []
        
        if field_visit.reset_amount != None:
                reset_str = "Reset: "
                if len(field_visit.reset_amount) > 1:
                    for index, reset in enumerate(field_visit.reset_amount):
                        end_of_list = index == len(field_visit.reset_amount) - 1
                        if not end_of_list:
                            reset_str += str(reset) + "\', "
                        else:
                            reset_str += str(reset) + "\'"
                else:
                    reset_str = "Reset: " + str(field_visit.reset_amount[0]) + "\'"
                
                visit_findings_list.append(reset_str)
        
        if len(field_visit.dischage_measurements) == 0 and field_visit.has_stage_reading:
            visit_findings_list.append("Stage-Only Visit")
        
        for qm in field_visit.dischage_measurements:
            Qm_str = "Qm " + str(qm.qm_num)
            visit_findings_list.append(Qm_str)
        
        if field_visit.levels_performed:
            visit_findings_list.append("Levels")
        
        return visit_findings_list
    
    @staticmethod
    def _return_string_of_field_visit_findings(field_visit_findings_list: list[str]):
        '''
        Helper method to take a visit's field visits and format them into
        a single string to be placed in the field visit tables.

        Args:
            field_visit_findings_list(list[str]): List of field visit findings
        '''
        visit_findings_str = ""
            
        if len(field_visit_findings_list) == 1:
            visit_findings_str = field_visit_findings_list[0]
        
        elif len(field_visit_findings_list) > 1:
            for index, finding in enumerate(field_visit_findings_list):
                visit_findings_str = visit_findings_str + finding
                if index < len(field_visit_findings_list) - 1:
                    visit_findings_str = visit_findings_str + ", "
                    
        return visit_findings_str
    
    def create_field_visits_table_section(self, field_visit_list):
        '''
        Method to construct the field visits table with their respect
        findings in html format and append them to the html document.

        Args:
            field_visit_list(list[Field_Visit]): List of field visits during record period
        '''
        self.field_visit_section = "<span style=\"text-decoration: underline;\"><strong>Site Visits</strong></span>\n" \
            "<br />\n" \
            "<br />\n" \
            "<div style=\"padding-left: 30px;\">\n" 
            
        table_header_row = html_table.html_table_row(["Date", "Visitor(s)", "Activities"])
        body_rows_list = []
        
        field_visit_list.sort(key=lambda x: x.date, reverse = False)

        for visit in field_visit_list:
            visit_findings_list: list[str] = Record._return_list_of_field_visit_findings(visit)
            visit_findings_str: str = Record._return_string_of_field_visit_findings(visit_findings_list)

            visit_row = html_table.html_table_row([str(visit.date)[0:10], visit.party, visit_findings_str])
            body_rows_list.append(visit_row)
        
        field_visit_table = html_table.html_table(table_header_row, body_rows_list, 380)
        
        self.field_visit_section = self.field_visit_section + field_visit_table.return_html() + "</div>\n"
        self.record_html = self.record_html + self.field_visit_section

        return self.field_visit_section
    
    def create_gh_section(self, gh_quality_tables: list):
        """
        Method to construct the gage height record description section. User must be prompted for
        their interpretation of the record's quality.

        Args:
            list_gaps(list[Gaps]): List of gaps in the gage height timeseries.
        """

        self.gh_description = "<p><span style=\"text-decoration: underline;\"><strong>Gage Height Record</strong></span></p>\n" \
        "<div style=\"padding-left:30px;\">\n"

        for gh_quality_table in gh_quality_tables:
            table_title = ""
            if gh_quality_table.name != "":
                table_title = f"<p>{gh_quality_table.name}</p>\n"
            self.gh_description += table_title + gh_quality_table.return_html_table()

        return self.gh_description
  
    def create_datum_section(self, datum_description: str):
        """
        Method to construct the datum/levels section using the SLAP description
        from SIMs.

        Args:
            datum_description(str): The SIMS levels/datum description
        """
        self.datum_section = "<div><strong>Datum</strong></div>\n" \
            "<div>\n" \
            "<p>" + datum_description + "</p>\n</div>\n"
        self.record_html = self.record_html + self.datum_section
        
    def create_checkbar_section(self, field_visits_list, sensors_list):
        """
        Method to construct the description of the checkbar readings during
        the period if they exist. If none exist, then the user will be asked
        if a WWG was present during the period. I assume there is only one WWG.

        Args:
            field_visits_list(list[Field_Visit]): List of field visits from the period.
            sensors_list(list[Sensor]): List of active sensors at the site
        """
        
        self.checkbar_section = ""
        if Record._has_wwg(sensors_list):
            self.checkbar_section += "<p><strong>Checkbar Readings</strong></p>\n"
            if self._count_checkbar_readings(field_visits_list) == 0:
                self.checkbar_section += "<p>No checkbar readings were recorded during the analysis period.</p>\n"
            else:
                table_header_row = html_table.html_table_row(["Date", "Read"])
                body_rows_list = []
                for visit in field_visits_list:
                    if visit.checkbar_reading != None:
                        checkbar_body_row = html_table.html_table_row([str(visit.checkbar_reading.datetime)[0:10], "{:.3f}".format(visit.checkbar_reading.value) + "\'"])
                        body_rows_list.append(checkbar_body_row)
                
                checkbar_table = html_table.html_table(table_header_row, body_rows_list, 240)
                
                self.checkbar_section += checkbar_table.return_html()
        
        self.record_html = self.record_html + self.checkbar_section
    
    @staticmethod
    def _has_wwg(sensors_list):
        """
        Helper method to check whether site has a wire-weight gage
        """
        for sensor in sensors_list:
            if sensor.method == "Gage height, wire weight gage":
                return True
        return False
    
    @staticmethod
    def _count_checkbar_readings(field_visits_list):
        """
        Helper method to count the number of checkbar readings from a given set of field visit objects
        """
        checkbar_reading_cnt = 0
        
        for visit in field_visits_list:
            if visit.checkbar_reading != None:
                checkbar_reading_cnt = checkbar_reading_cnt + 1
        
        return checkbar_reading_cnt

    def create_backup_data_section(self, gh_ts_list, edl_data_condition_combo_box_array):
        """
        Method to construct the backup data section pertaining to use
        of EDL data in filling gaps. If no EDL data was evidently used,
        then the user will be asked if any was available.

        Args:
            corrections_list(list[General_Correction]): List of corrections during the period.
        """
        self.backup_data_section = ""
        self.backup_tables = []

        if len(gh_ts_list) == 1:
            archivalCondition = edl_data_condition_combo_box_array[0].currentText()
            correctionsList = gh_ts_list[0].record_dataset.general_corrections
            hasPastedData = Record._has_pasted_data(correctionsList)
            hasGaps = Record._ts_has_record_period_gaps(gh_ts_list[0])

            self.backup_data_section = "<p><strong>Backup Data</strong></p>\n"
            self._process_ts(correctionsList, archivalCondition, False, hasGaps)
        
        elif len(gh_ts_list) > 1:
            for ts, comboBox in zip(gh_ts_list, edl_data_condition_combo_box_array):
                archivalCondition = comboBox.currentText()
                correctionsList = ts.record_dataset.general_corrections
                hasPastedData = Record._has_pasted_data(correctionsList)
                hasGaps = Record._ts_has_record_period_gaps(ts)

                self.backup_data_section += f"<p><strong>Backup Data ({ts.TS_sublocation})</strong></p>\n"
                self._process_ts(correctionsList, archivalCondition, False, hasGaps)

        self.record_html = self.record_html + self.backup_data_section

    @staticmethod
    def _has_pasted_data(corrections_list: list[str]):
        for correction in corrections_list:
            if correction.correction_type == 'CopyPaste':
                return True
        return False
    
    @staticmethod
    def _return_copy_paste_table(corrections_list):
        table_header_row = html_table.html_table_row(["Beginning Date/Time", "Ending Date/Time"])
        body_rows_list = []
        for correction in corrections_list:
            if correction.correction_type == 'CopyPaste':
                edl_body_row = html_table.html_table_row([str(correction.start_datetime), str(correction.end_datetime)])
                body_rows_list.append(edl_body_row)
        
        backup_table = html_table.html_table(table_header_row, body_rows_list, 380)
        return backup_table

    @staticmethod
    def _ts_has_record_period_gaps(gh_ts):
        if len(gh_ts.record_dataset.gaps) != 0:
            return True
        return False

    def _process_ts(self, corrections_list, archivalCondition: bool, hasPastedData: bool, hasGaps: bool):
        archivedProperly = archivalCondition == "Archived Properly"
        partiallyArchived = archivalCondition == "Partially Archived"
        notArchivedProperly = archivalCondition == "Not Archived Properly"
        
        if archivedProperly and hasPastedData and not hasGaps:
            self.backup_data_section += "<p>Backup data was properly archived and used to fill in all gaps during the period.</p>\n"
            table = Record._return_copy_paste_table(corrections_list)
            self.backup_tables.append(table)
            self.backup_data_section += table.return_html()
        elif archivedProperly and hasPastedData and hasGaps:
            self.backup_data_section += "<p>Backup data was properly archived and used to fill in gaps where possible. Not all gaps could be successfully filled.</p>\n"
            table = Record._return_copy_paste_table(corrections_list)
            self.backup_tables.append(table)
            self.backup_data_section += table.return_html()
        elif archivedProperly and not hasPastedData and not hasGaps:
            self.backup_data_section += "<p>Backup data was properly archived but not needed during the analysis period.</p>\n"
        elif archivedProperly and not hasPastedData and hasGaps:
            self.backup_data_section += "<p>Backup data was properly archived but not usable in filling gaps during the period.</p>\n"
        
        
        elif partiallyArchived and hasPastedData and not hasGaps:
            self.backup_data_section += "<p>Backup data was partially available and used to fill in all gaps during the analysis period.</p>\n"
            table = Record._return_copy_paste_table(corrections_list)
            self.backup_data_section += table.return_html()
            self.backup_tables.append(table)
        elif partiallyArchived and hasPastedData and hasGaps:
            self.backup_data_section += "<p>Backup data was partially available and used to fill in gaps where possible. Not all gaps could be successfully filled.</p>\n"
            table = Record._return_copy_paste_table(corrections_list)
            self.backup_data_section += table.return_html()
            self.backup_tables.append(table)
        elif partiallyArchived and not hasPastedData and not hasGaps:
            self.backup_data_section += "<p>Backup data was partially available but also not needed during the analysis period.</p>\n"
        elif partiallyArchived and not hasPastedData and hasGaps:
            self.backup_data_section += "<p>Backup data was partially available and not usable in filling in gaps during the analysis period.</p>\n"


        elif notArchivedProperly and not hasGaps:
            self.backup_data_section += "<p>Backup data was not available or not archived properly; however, it was also not needed during the analysis period.</p>\n"
        elif notArchivedProperly and hasGaps:
            self.backup_data_section += "<p>Backup data was not available or not archived properly and gaps occurred during the period.</p>\n"

    def create_ice_affected_section(self, gh_ts_list):
        """
        Method to construct the ice affected section pertaining to periods of 
        gage height record affected by ice. This requires that such periods be
        deleted and qualified for ice.

        Args:
            qualifiers_list(list[Qualifier]): List of gage height qualifiers during record period.
        """
        self.ice_section = ""
        if len(gh_ts_list) == 1:
            qualifiers_list = gh_ts_list[0].record_dataset.qualifiers
            self.ice_section = "<p><strong>Ice Affected</strong></p>\n"
            ice_count = 0
        
            for qualifier in qualifiers_list:
                if qualifier.identifier == "ICE":
                    ice_count = ice_count + 1
            
            if ice_count == 0:
                self.ice_section = self.ice_section + "<p>No periods of ice were evident during the analysis period.</p>\n"
            else:
                self.ice_section = self.ice_section + "<p>Ice was evident upon further review of the hydrograph and meteorlogical data.</p>\n"
                table_header_row = html_table.html_table_row(["Beginning Date/Time", "Ending Date/Time", "Supplemental Comments"])
                body_rows_list = []
                for qualifier in qualifiers_list:
                    if qualifier.identifier == "ICE":
                        ice_body_row = html_table.html_table_row([str(qualifier.start_datetime), str(qualifier.end_datetime), ""])
                        body_rows_list.append(ice_body_row)
                
                ice_table = html_table.html_table(table_header_row, body_rows_list, 800, [175, 175, 450])
                self.ice_section = self.ice_section + ice_table.return_html()
                
            self.record_html = self.record_html + self.ice_section

        elif len(gh_ts_list) > 1:
            for ts in gh_ts_list:
                qualifiers_list = ts.record_dataset.qualifiers
                self.ice_section += f"<p><strong>Ice Affected ({ts.TS_sublocation})</strong></p>\n"
                ice_count = 0
            
                for qualifier in qualifiers_list:
                    if qualifier.identifier == "ICE":
                        ice_count = ice_count + 1
                
                if ice_count == 0:
                    self.ice_section = self.ice_section + "<p>No periods of ice were evident during the analysis period.</p>\n"
                else:
                    self.ice_section = self.ice_section + "<p>Ice was evident upon further review of the hydrograph and meteorlogical data.</p>\n"
                    table_header_row = html_table.html_table_row(["Beginning Date/Time", "Ending Date/Time", "Supplemental Comments"])
                    body_rows_list = []
                    for qualifier in qualifiers_list:
                        if qualifier.identifier == "ICE":
                            ice_body_row = html_table.html_table_row([str(qualifier.start_datetime), str(qualifier.end_datetime), ""])
                            body_rows_list.append(ice_body_row)
                    
                    ice_table = html_table.html_table(table_header_row, body_rows_list, 800, [175, 175, 450])
                    self.ice_section = self.ice_section + ice_table.return_html()
                    
                self.record_html = self.record_html + self.ice_section
    
    def create_edits_section(self, gh_ts_list):
        """
        Method to construct a tabulated edits section if any edits were warranted
        during the period.

        Args:
            general_corrections_list(list[General_Correction]): list of general corrections
            from during the period.
        """
        self.edits_section = ""
        if len(gh_ts_list) == 1:
            general_corrections_list = gh_ts_list[0].record_dataset.general_corrections
            self.edits_section = "<p><strong>Edits</strong></p>\n"
            edit_cnt = 0
            
            for gen_corr in general_corrections_list:
                edit_cnt = edit_cnt + 1
            
            if edit_cnt == 0:
                self.edits_section = self.edits_section + "<p>No edits to the gage height record were warranted during the analysis period.</p>\n"
            
            else:
                table_header_row = html_table.html_table_row(["Beginning Date/Time", "Ending Date/Time", "Type of Edit", "Processing Order", "Comment"])
                body_rows_list = []
                for gen_corr in general_corrections_list:
                    correction_type = gen_corr.correction_type
                    if correction_type == "CopyPaste":
                        correction_type = "Copy & Paste"
                    elif correction_type == "DeleteRegion":
                        correction_type = "Deletion"
                    
                    processing_order = gen_corr.processing_order
                    if processing_order == "PreProcessing":
                        processing_order = "Pre-Processing"
                    elif processing_order == "PostProcessing":
                        processing_order = "Post-Processing"
                        
                    gen_corr_body_row = html_table.html_table_row([str(gen_corr.start_datetime), str(gen_corr.end_datetime), correction_type, processing_order, gen_corr.description])
                    body_rows_list.append(gen_corr_body_row)
                
                edits_table = html_table.html_table(table_header_row, body_rows_list, 900, [175, 175, 150, 150, 250])
                self.edits_section = self.edits_section + edits_table.return_html()
                
            self.record_html = self.record_html + self.edits_section
        
        elif len(gh_ts_list) > 1:
            for ts in gh_ts_list:
                general_corrections_list = ts.record_dataset.general_corrections
                self.edits_section += f"<p><strong>Edits ({ts.TS_sublocation})</strong></p>\n"
                edit_cnt = 0
                
                for gen_corr in general_corrections_list:
                    edit_cnt = edit_cnt + 1
                
                if edit_cnt == 0:
                    self.edits_section = self.edits_section + "<p>No edits to the gage height record were warranted during the analysis period.</p>\n"
                
                else:
                    table_header_row = html_table.html_table_row(["Beginning Date/Time", "Ending Date/Time", "Type of Edit", "Processing Order", "Comment"])
                    body_rows_list = []
                    for gen_corr in general_corrections_list:
                        correction_type = gen_corr.correction_type
                        if correction_type == "CopyPaste":
                            correction_type = "Copy & Paste"
                        elif correction_type == "DeleteRegion":
                            correction_type = "Deletion"
                        
                        processing_order = gen_corr.processing_order
                        if processing_order == "PreProcessing":
                            processing_order = "Pre-Processing"
                        elif processing_order == "PostProcessing":
                            processing_order = "Post-Processing"
                            
                        gen_corr_body_row = html_table.html_table_row([str(gen_corr.start_datetime), str(gen_corr.end_datetime), correction_type, processing_order, gen_corr.description])
                        body_rows_list.append(gen_corr_body_row)
                    
                    edits_table = html_table.html_table(table_header_row, body_rows_list, 900, [175, 175, 150, 150, 250])
                    self.edits_section = self.edits_section + edits_table.return_html()
                    
                self.record_html = self.record_html + self.edits_section
    
    @staticmethod
    def _gh_correction_input_pt_list_to_string(input_list):
        """
        Helper method to convert a list of multi-point correction input points
        and their magnitudes into a clean string to be placed in an HTML table.

        Args:
            input_list(list[[double, double]]): List of input and magnitude couplets for
            a multi-point correction.
        """
        tuple_list = ""
        if len(input_list) == 0:
            tuple_list = "None"
        else:
            for index, shift_tuple in enumerate(input_list):
                tuple_list = tuple_list + f"({shift_tuple[0]:.2f}\', {shift_tuple[1]:.2f}\')"
                if index + 1 < len(input_list):
                    tuple_list = tuple_list + ", "

        return tuple_list
        
    
    def create_gh_correction_section(self, gh_ts):
        """
        Method to generate a tabulated section for the set 2 gage height corrections
        from during the period.

        Args:
            gh_corrections_list(list[Multi_Point_Correction]): List of gage height corrections
            from during the period.
        """

        self.gh_corrections_section = ""
        if len(gh_ts) == 1:
            gh_corrections_list = gh_ts[0].record_dataset.multipoint_corrections
            self.gh_corrections_section = "<p><strong>Gage-Height Corrections</strong></p>\n"
            gh_corr_cnt = 0
            
            for corr in gh_corrections_list:
                if corr.processing_order == "Set 2":
                    gh_corr_cnt = gh_corr_cnt + 1
            
            if gh_corr_cnt == 0:
                self.gh_corrections_section = self.gh_corrections_section + "<p>No gage height corrections were warranted during the analysis period. All visit primary readings were considered to be in agreement with their respective recorder readings.</p>\n"
            else:
                table_header_row = html_table.html_table_row(["Set Type", "Starting Date/Time", "Ending Date/Time", "Starting Corr. Points (GH, Magnitude)", "Ending Corr. Points (GH, Magnitude)", "Comment"])
                body_rows_list = []
                for corr in gh_corrections_list:
                    if corr.processing_order == "Set 2":
                        string_starting_shifts = Record._gh_correction_input_pt_list_to_string(corr.start_shifts)
                        string_ending_shifts = Record._gh_correction_input_pt_list_to_string(corr.end_shifts)
                        gen_corr_body_row = html_table.html_table_row([str(corr.processing_order), str(corr.start_datetime), str(corr.end_datetime), string_starting_shifts, string_ending_shifts, corr.description])
                        body_rows_list.append(gen_corr_body_row)
                
                gh_corr_table = html_table.html_table(table_header_row, body_rows_list, 900, [100, 150, 150, 150, 150, 200])
                self.gh_corrections_section = self.gh_corrections_section + gh_corr_table.return_html()
            
            self.record_html = self.record_html + self.gh_corrections_section
        
        if len(gh_ts) > 1:
            for ts in gh_ts:
                gh_corrections_list = ts.record_dataset.general_corrections
                self.gh_corrections_section += f"<p><strong>Gage Height Corrections ({ts.TS_sublocation})</strong></p>\n"
                gh_corr_cnt = 0
                
                for corr in gh_corrections_list:
                    if corr.processing_order == "Set 2":
                        gh_corr_cnt = gh_corr_cnt + 1
                
                if gh_corr_cnt == 0:
                    self.gh_corrections_section = self.gh_corrections_section + "<p>No gage height corrections were warranted during the analysis period. All visit primary readings were considered to be in agreement with their respective recorder readings.</p>\n"
                else:
                    table_header_row = html_table.html_table_row(["Set Type", "Starting Date/Time", "Ending Date/Time", "Starting Corr. Points (GH, Magnitude)", "Ending Corr. Points (GH, Magnitude)", "Comment"])
                    body_rows_list = []
                    for corr in gh_corrections_list:
                        if corr.processing_order == "Set 2":
                            string_starting_shifts = Record._gh_correction_input_pt_list_to_string(corr.start_shifts)
                            string_ending_shifts = Record._gh_correction_input_pt_list_to_string(corr.end_shifts)
                            gen_corr_body_row = html_table.html_table_row([str(corr.processing_order), str(corr.start_datetime), str(corr.end_datetime), string_starting_shifts, string_ending_shifts, corr.description])
                            body_rows_list.append(gen_corr_body_row)
                    
                    gh_corr_table = html_table.html_table(table_header_row, body_rows_list, 900, [100, 150, 150, 150, 150, 200])
                    self.gh_corrections_section = self.gh_corrections_section + gh_corr_table.return_html()
                
                self.record_html = self.record_html + self.gh_corrections_section
            
    def create_data_gaps_section(self, gh_ts_list):
        """
        Method to crate the data gaps section for the records period.

        Args:
            gaps_list(list[Gap]): List of gaps in the gage height timeseries during the period.
        """
        self.data_gaps_section = ""

        if len(gh_ts_list) == 1:
            gaps_list = gh_ts_list[0].record_dataset.gaps
            self.data_gaps_section = "<p><strong>Data Gaps</strong></p>\n"
            
            if len(gaps_list) == 0:
                self.data_gaps_section = self.data_gaps_section + "<p>No gaps in the gage height record were observed during the analysis period.</p>\n"
        
            else:
                table_header_row = html_table.html_table_row(["Starting Date/Time", "Ending Date/Time", "Length"])
                body_rows_list = []
                for gap in gaps_list:
                    gap_body_row = html_table.html_table_row([str(gap.start_datetime), str(gap.end_datetime), str(gap.length)])
                    body_rows_list.append(gap_body_row)
                
                gap_table = html_table.html_table(table_header_row, body_rows_list, 500)
                self.data_gaps_section = self.data_gaps_section + gap_table.return_html()
                
            self.record_html = self.record_html + self.data_gaps_section
        
        if len(gh_ts_list) > 1:
            for ts in gh_ts_list:
                gaps_list = ts.record_dataset.gaps
                self.data_gaps_section += f"<p><strong>Gaps ({ts.TS_sublocation})</strong></p>\n"
                
                if len(gaps_list) == 0:
                    self.data_gaps_section = self.data_gaps_section + "<p>No gaps in the gage height record were observed during the analysis period.</p>\n"
            
                else:
                    table_header_row = html_table.html_table_row(["Starting Date/Time", "Ending Date/Time", "Length"])
                    body_rows_list = []
                    for gap in gaps_list:
                        gap_body_row = html_table.html_table_row([str(gap.start_datetime), str(gap.end_datetime), str(gap.length)])
                        body_rows_list.append(gap_body_row)
                    
                    gap_table = html_table.html_table(table_header_row, body_rows_list, 500)
                    self.data_gaps_section = self.data_gaps_section + gap_table.return_html()
                    
                self.record_html = self.record_html + self.data_gaps_section
         
    def create_other_corrections_section(self, gh_ts_list):
        """
        Method to construct the other corrections section which will pertain to
        set 1 and set 3 corrections which are usually abnormal corrections.

        Args:
            multi_point_list (list[multi_point_correction]): List of multi-point
            corrections from during the record period.
        """
        self.other_gh_corrections_section = ""
        
        if len(gh_ts_list) == 1: 
            multi_point_list = gh_ts_list[0].record_dataset.multipoint_corrections
            self.other_gh_corrections_section = "<p><strong>Other Corrections</strong></p>\n"
            
            other_corr_cnt = 0
            
            for corr in multi_point_list:
                    if corr.processing_order != "Set 2":
                        other_corr_cnt = other_corr_cnt + 1 
            
            if other_corr_cnt == 0:
                self.other_gh_corrections_section = self.other_gh_corrections_section + "<p>No other gage height corrections were warranted during the analysis period.</p>\n"
            else:
                table_header_row = html_table.html_table_row(["Set Type", "Starting Date/Time", "Ending Date/Time", "Starting Corr. Points (GH, Magnitude)", "Ending Corr. Points (GH, Magnitude)", "Comment"])
                body_rows_list = []
                for corr in multi_point_list:
                    if corr.processing_order != "Set 2":
                        string_starting_shifts = Record._gh_correction_input_pt_list_to_string(corr.start_shifts)
                        string_ending_shifts = Record._gh_correction_input_pt_list_to_string(corr.end_shifts)
                        other_corr_body_row = html_table.html_table_row([str(corr.processing_order), str(corr.start_datetime), str(corr.end_datetime), string_starting_shifts, string_ending_shifts, corr.description])
                        body_rows_list.append(other_corr_body_row)
                
                other_gh_corr_table = html_table.html_table(table_header_row, body_rows_list, 1050, [100, 150, 150, 200, 200, 250])
                self.other_gh_corrections_section = self.other_gh_corrections_section + other_gh_corr_table.return_html()
            
            self.record_html = self.record_html + self.other_gh_corrections_section
        
        elif len(gh_ts_list) > 1: 
            for ts in gh_ts_list:
                multi_point_list = ts.record_dataset.multipoint_corrections
                self.other_gh_corrections_section += f"<p><strong>Other Corrections ({ts.TS_sublocation})</strong></p>\n"
                
                other_corr_cnt = 0
                
                for corr in multi_point_list:
                        if corr.processing_order != "Set 2":
                            other_corr_cnt = other_corr_cnt + 1 
                
                if other_corr_cnt == 0:
                    self.other_gh_corrections_section = self.other_gh_corrections_section + "<p>No other gage height corrections were warranted during the analysis period.</p>\n"
                else:
                    table_header_row = html_table.html_table_row(["Set Type", "Starting Date/Time", "Ending Date/Time", "Starting Corr. Points (GH, Magnitude)", "Ending Corr. Points (GH, Magnitude)", "Comment"])
                    body_rows_list = []
                    for corr in multi_point_list:
                        if corr.processing_order != "Set 2":
                            string_starting_shifts = Record._gh_correction_input_pt_list_to_string(corr.start_shifts)
                            string_ending_shifts = Record._gh_correction_input_pt_list_to_string(corr.end_shifts)
                            other_corr_body_row = html_table.html_table_row([str(corr.processing_order), str(corr.start_datetime), str(corr.end_datetime), string_starting_shifts, string_ending_shifts, corr.description])
                            body_rows_list.append(other_corr_body_row)
                    
                    other_gh_corr_table = html_table.html_table(table_header_row, body_rows_list, 1050, [100, 150, 150, 200, 200, 250])
                    self.other_gh_corrections_section = self.other_gh_corrections_section + other_gh_corr_table.return_html()
                
                self.record_html = self.record_html + self.other_gh_corrections_section
    
    def create_peak_verifications_section(self, field_visit_list):
        """
        Method to create the peak verifications section in tabulated form.

        Args:
            field_visit_list(list[Field_Visit]): List of field visits during record period
        """
        self.peak_verifications_section = "<p><strong>Peak Verification Marks</strong></p>\n"
        
        marks_found = False
        
        for visit in field_visit_list:
            if len(visit.high_water_marks) > 0:
                marks_found = True
        
        if not marks_found:
            self.peak_verifications_section = self.peak_verifications_section + "<p>No peak verification marks were recorded during the analysis period.</p>\n"
    
        else:
            table_header_row = html_table.html_table_row(["Sensor Type", "Date Read", "Date/Time Occurred", "Value", "Discrepancy", "Comment"])
            body_rows_list = []
            for field_visit in field_visit_list:
                for hwm in field_visit.high_water_marks:
                    hwm_type = hwm.monitoring_method
                    if hwm_type == "Gage height, crest stage gage":
                        hwm_type = "CSG"
                    peaks_body_row = html_table.html_table_row([hwm_type, str(field_visit.date)[0:10], str(hwm.datetime), str(hwm.value)+"\'", str(hwm.discrepancy)+"\'", hwm.comment])
                    body_rows_list.append(peaks_body_row)
            
            peaks_table = html_table.html_table(table_header_row, body_rows_list, 800, [100, 100, 150, 100, 100, 250])
            subsection = "<em style=\"box-sizing: border-box; color: #333333; font-family: Ubuntu; font-size: 15px; background-color: #ffffff;\">Special Note: Independent peak verifications within ±0.05' of the recorder peak and within 8% of the peak computed discharge are considered to have verified the recorder peak. Independent peak verifications exceeding either of the aforementioned criteria warrant input into the gage height time series according to SW Memo 2014.05. Peaks verifications that fall in line with a pattern of instability may not be added to the gage height time series. Verifications that fall in line with a pattern of consistent offset from the recorder peak may also be considered to have verified the recorder peak.&nbsp;</em>\n"
            self.peak_verifications_section = self.peak_verifications_section + peaks_table.return_html() + subsection
        
        self.record_html = self.record_html + self.peak_verifications_section
    
    def create_peak_recorder_stage_section(self, gh_ts_list, combobox_array):
        """
        Method to tabulate the peak stage reading from during the record period.

        Args:
            primary_record_gh_dataset(list[Unit_Value]): List of UVs to inspect
        """

        self.peak_recorder_stage_section = ""
        self.backup_tables = []

        if len(gh_ts_list) == 1:
            verifiedCondition = combobox_array[0].currentText()
            record_dataset = gh_ts_list[0].record_dataset
            self.peak_recorder_stage_section = "<p><strong>Peak Recorder Stage</strong></p>\n" 
            
            if verifiedCondition == 'Yes':
                self.peak_recorder_stage_section = self.peak_recorder_stage_section + "<p>The analysis period's recorder peak was considered verified by a collected high water mark.</p>\n"
            elif verifiedCondition == 'No':
                self.peak_recorder_stage_section = self.peak_recorder_stage_section + "<p>The analysis period's recorder peak was not considered verified.</p>\n"
            
            table_header_row = html_table.html_table_row(["", "Date/Time", "Value"])
            body_rows_list = []
            max_point_datetime_str = str(record_dataset.max_point.datetime)
            min_point_datetime_str = str(record_dataset.min_point.datetime)
            
            if record_dataset.max_point.unique == False:
                max_point_datetime_str = max_point_datetime_str + "*"
            if record_dataset.min_point.unique == False:
                min_point_datetime_str = min_point_datetime_str + "*"

            body_rows_list.append(html_table.html_table_row(["Max Gage Height", max_point_datetime_str, "{:.2f}".format(record_dataset.max_point.value) + "\'"]))
            body_rows_list.append(html_table.html_table_row(["Min Gage Height", min_point_datetime_str, "{:.2f}".format(record_dataset.min_point.value) + "\'"]))
            extremes_table = html_table.html_table(table_header_row, body_rows_list, 580)
            
            subcaption = "<em style=\"box-sizing: border-box; color: #333333; font-family: Ubuntu; font-size: 15px; background-color: #ffffff;\">* Multiple occurrences of the same extreme in selected dataset. First occurrence listed.</em></div>\n"
            
            self.peak_recorder_stage_section = self.peak_recorder_stage_section + extremes_table.return_html() + subcaption        
            self.record_html = self.record_html + self.peak_recorder_stage_section
        
        if len(gh_ts_list) > 1:
            for ts, comboBox in zip(gh_ts_list, combobox_array):
                verifiedCondition = comboBox.currentText()
                record_dataset = gh_ts_list[0].record_dataset
                self.peak_recorder_stage_section += f"<p><strong>Other Corrections ({ts.TS_sublocation})</strong></p>\n"
                
                if verifiedCondition == 'Yes':
                    self.peak_recorder_stage_section = self.peak_recorder_stage_section + "<p>The analysis period's recorder peak was considered verified by a collected high water mark.</p>\n"
                elif verifiedCondition == 'No':
                    self.peak_recorder_stage_section = self.peak_recorder_stage_section + "<p>The analysis period's recorder peak was not considered verified.</p>\n"
                
                table_header_row = html_table.html_table_row(["", "Date/Time", "Value"])
                body_rows_list = []
                max_point_datetime_str = str(record_dataset.max_point.datetime)
                min_point_datetime_str = str(record_dataset.min_point.datetime)
                
                if record_dataset.max_point.unique == False:
                    max_point_datetime_str = max_point_datetime_str + "*"
                if record_dataset.min_point.unique == False:
                    min_point_datetime_str = min_point_datetime_str + "*"

                body_rows_list.append(html_table.html_table_row(["Max Gage Height", max_point_datetime_str, "{:.2f}".format(record_dataset.max_point.value) + "\'"]))
                body_rows_list.append(html_table.html_table_row(["Min Gage Height", min_point_datetime_str, "{:.2f}".format(record_dataset.min_point.value) + "\'"]))
                extremes_table = html_table.html_table(table_header_row, body_rows_list, 580)
                
                subcaption = "<em style=\"box-sizing: border-box; color: #333333; font-family: Ubuntu; font-size: 15px; background-color: #ffffff;\">* Multiple occurrences of the same extreme in selected dataset. First occurrence listed.</em></div>\n"
                
                self.peak_recorder_stage_section = self.peak_recorder_stage_section + extremes_table.return_html() + subcaption        
                self.record_html = self.record_html + self.peak_recorder_stage_section
        
    def create_stage_discharge_header(self):
        """
        Helper Method to create the stage-discharge header.
        """
        return "<br />\n" + "<p><strong><span style=\"text-decoration: underline;\">Stage-Discharge Relation</span></strong></p>\n" \
        "<div style=\"padding-left:30px;\">\n"
        
    def create_rating_description(self, ratings_description):
        """
        Method to create the rating description section using the description provided from
        SIMs. Changes will require changes to be made to the SIMs description.

        Args:
            ratings_description(str): The SIMs rating descriptions for the site.
        """
        self.rating_section = "<p><strong>Stage-Discharge Rating(s)</strong></p>\n" + ratings_description + "\n"
        
        self.record_html = self.record_html + self.rating_section
    
    def create_qm_section(self, field_visit_list):
        """
        Method to construct the Qm section with summary of the measurement and its findings.
        Commentary on quality of the measurement needs to be input into the Aquarius measurement
        comments section in order for them to appear in the final table.

        Args:
             field_visit_list(list[Field_Visit]): List of field visits during record period
        """
        self.qm_section = "<p><strong>Discharge Measurements and Control Conditions</strong></p>\n"
        
        table_header_row = html_table.html_table_row(["Qm #", "Date/Time", "MGH", "GH Change", "Discharge", "Quality", "Rating", "Rating Error", "Control Conditions", "Comments"])
        body_rows_list = []
        
        field_visit_list.sort(key=lambda x: x.date, reverse=False)

        for visit in field_visit_list:
            for qm in visit.dischage_measurements:
                if qm.diff_during_visit == None:
                    User_Inputs.warning_message("No gage height difference recorded for Qm " + str(qm.qm_num) + "!\n")
                    qm_row = html_table.html_table_row([str(qm.qm_num), str(qm.qm_time), str(qm.mgh) + "\'", "", str(round(qm.discharge, 2)), qm.quality, qm.rating_num_compared, "", visit.control_condition, qm.comment])
                else:
                    qm_row = html_table.html_table_row([str(qm.qm_num), str(qm.qm_time), str(qm.mgh) + "\'", "{:.2f}".format(qm.diff_during_visit) + "\'", str(round(qm.discharge, 2)), qm.quality, qm.rating_num_compared, str(round(qm.difference_from_base_rating,1))+"%", visit.control_condition, qm.comment])
                body_rows_list.append(qm_row)
        
        qm_table = html_table.html_table(table_header_row, body_rows_list, 1300, [50, 175, 50, 50, 75, 75, 75, 75, 200, 475])
        
        self.qm_section = self.qm_section + qm_table.return_html()
        self.record_html = self.record_html + self.qm_section
    
    @staticmethod
    def _shift_point_gh_values_to_string(shift_input_list):
        """
        Helper function to take a list of shift input points and convert them to
        a clean string to be placed in the shift table.

        Args:
            shift_input_list(list[[double, double]]): List of shift input points
        """
        tuple_list = ""
        if len(shift_input_list) == 0:
            tuple_list = "None"
        else:
            for index, shift_tuple in enumerate(shift_input_list):
                tuple_list = tuple_list + f"{shift_tuple[0]:.2f}\'"
                if index + 1 < len(shift_input_list):
                    tuple_list = tuple_list + ", "

        return tuple_list
    
    def create_shift_curves_section(self, ratings_list):
        """
        Method to create the shift curves section of the record in tabular form.

        Args:
            ratings_list(list[Rating]): List of ratings for the record's period.
        """
        self.shift_section = "<p><strong>Shift Curves</strong></p>\n" \
            "<p>The shift curves used throughout the analysis period are predominately low-water shifts that resemble a half-house shape or null-shifts that perform no further adjustments to the base rating's computed discharge values. The gage height values for the shift input points were meant to represent the transition from full section control to section/channel to full channel control conditions.</p>\n"
        table_header_row = html_table.html_table_row(["Start Date/Time", "Diagram Shape", "Input Point Gage Heights", "Shift Magnitude*", "Comments/Explanation"])
        body_rows_list = []
        
        longer_mag_row_table = False
        
        for rating in ratings_list:
            for index, shift_curve in enumerate(rating.shift_curve_list):
                not_at_end = index + 1 < len(rating.shift_curve_list)
                shift_effective_end_datetime = None
                
                if not_at_end:
                    shift_effective_end_datetime = rating.shift_curve_list[index + 1].start_datetime
                
                if shift_effective_end_datetime == None:
                    shift_in_period = self.start_date <= shift_curve.start_datetime
                else:
                    before_period = shift_effective_end_datetime < self.start_date
                    after_period = shift_curve.start_datetime > self.end_date
                    shift_in_period = not (before_period or after_period)
                
                if shift_in_period:
                    if(shift_curve.long_reported_values):
                        longer_mag_row_table = True
                    shift_row = html_table.html_table_row([str(shift_curve.start_datetime), shift_curve.shape, Record._shift_point_gh_values_to_string(shift_curve.shift_point_list), shift_curve.reported_magnitude, shift_curve.comment])
                    body_rows_list.append(shift_row)
                    
        if(longer_mag_row_table):
            shift_table = html_table.html_table(table_header_row, body_rows_list, 1075, [150, 100, 150, 275, 400])
        else:
            shift_table = html_table.html_table(table_header_row, body_rows_list, 900, [150, 100, 150, 100, 400])
        subcaption = "<em style=\"box-sizing: border-box; color: #333333; font-family: Ubuntu; font-size: 15px; background-color: #ffffff;\">* Single magnitude values pertain to the shift magnitude of a half-house shifts whereby no changes to the gage height of input points occurred compared to the previous shift.</em></div>\n"
        self.shift_section = self.shift_section + shift_table.return_html()
        self.record_html = self.record_html + self.shift_section + subcaption + "</div>\n"
        
    def create_computed_discharge_header(self):
        """
        Method to create the header for the computed discharge record subsection.
        """
        return "</div>\n<br />\n" + "<p><strong><span style=\"text-decoration: underline;\">Computed Discharge Record</span></strong></p>\n" \
        "<div style=\"padding-left:30px;\">\n"
    
    def create_discharge_record_section(self, q_quality_tables):
        """
        Method to create the descriptor section of the computed discharge record.
        Will prompt the user for their assessed quality and also mention any
        gaps or periods of estimation.

        Args:
            list_gaps(list[Gap]): List of gaps during the analysis period for the Q TS.
            q_qualifier_list(list[Qualifier]): List of qualifiers for the Q TS.
        """
        self.discharge_description = "<div style=\"padding-left: 30px;\">"
        
        for q_quality_table in q_quality_tables:
            table_title = ""
            if q_quality_table.name != "":
                table_title = f"<p>{q_quality_table.name}</p>\n"
            self.discharge_description += table_title + q_quality_table.return_html_table()

        return self.discharge_description

    
    def create_q_data_gaps_section(self, gaps_list):
        """
        Method to construct a supplemental section pertaining to gaps in the
        discharge record. Rarely are gaps allowed except for periods of 
        unmanageable backwater.

        Args:
            gaps_list(list[Gap]): List of gaps in the Q timeseries.
        """
        self.q_data_gaps_section = "<p><strong>Data Gaps</strong></p>\n"
        
        if len(gaps_list) == 0:
            self.q_data_gaps_section = self.q_data_gaps_section + "<p>No gaps in the computed discharge record were observed during the analysis period.</p>\n"
    
        else:
            table_header_row = html_table.html_table_row(["Starting Date/Time", "Ending Date/Time", "Length"])
            body_rows_list = []
            for gap in gaps_list:
                gap_body_row = html_table.html_table_row([str(gap.start_datetime), str(gap.end_datetime), str(gap.length)])
                body_rows_list.append(gap_body_row)
            
            gap_table = html_table.html_table(table_header_row, body_rows_list, 500)
            self.q_data_gaps_section = self.q_data_gaps_section + gap_table.return_html()
            
        self.record_html = self.record_html + self.q_data_gaps_section
    
    def create_estimate_section(self, general_corrections_list):
        """
        Method to construct the estimates section for the discharge timeseries
        in tabular form. I moved this to the discharge section because our
        office's policy is to not estimate GH (Ohio does though).

        Args:
            general_corrections_list(list[General_Correction]): List of corrections
            to the discharge timeseries during the record period.
        """
        self.estimates_section = "<p><strong>Estimates</strong></p>\n"
        edit_cnt = 0
        
        for gen_corr in general_corrections_list:
            if gen_corr.correction_type == "CopyPaste":
                edit_cnt = edit_cnt + 1
        
        if edit_cnt == 0:
            self.estimates_section = self.estimates_section + "<p>No estimates were warranted during the analysis period.</p>\n"
        
        else:
            table_header_row = html_table.html_table_row(["Beginning Date/Time", "Ending Date/Time", "Processing Order", "Comment"])
            body_rows_list = []
            for gen_corr in general_corrections_list:
                if gen_corr.correction_type == "CopyPaste":
                    gen_corr_body_row = html_table.html_table_row([str(gen_corr.start_datetime), str(gen_corr.end_datetime), gen_corr.processing_order, gen_corr.description])
                    body_rows_list.append(gen_corr_body_row)
            
            edits_table = html_table.html_table(table_header_row, body_rows_list, 750, [175, 175, 150, 250])
            self.estimates_section = self.estimates_section + edits_table.return_html()
            
        self.record_html = self.record_html + self.estimates_section
        
    def create_backwater_section(self, q_qualifiers_list):
        """
        Method to create the backwater section in tabular for if backwater
        occurred at anypoint. Backwater must be qualified to be populated in
        this method. This section was moved down to the discharge section
        because it is a discharge phenomena.

        Args:
            q_qualifiers_list(list[Qualifier]): List of qualifiers for the discharge
            timeseries.
        """
        self.backwater_section = "<p><strong>Backwater</strong></p>\n"
        backwater_Count = 0
        
        for qualifier in q_qualifiers_list:
            if qualifier.identifier == "BACKWATER":
                backwater_Count = backwater_Count + 1
        
        if backwater_Count == 0:
            self.backwater_section = self.backwater_section + "<p>No periods of backwater were evident during the analysis period.</p>\n"
        
        else:
            table_header_row = html_table.html_table_row(["Beginning Date/Time", "Ending Date/Time", "Supplemental Comments"])
            body_rows_list = []
            for qualifier in q_qualifiers_list:
                if qualifier.identifier == "BACKWATER":
                    bw_body_row = html_table.html_table_row([str(qualifier.start_datetime), str(qualifier.end_datetime), ""])
                    body_rows_list.append(bw_body_row)
            
            backwater_table = html_table.html_table(table_header_row, body_rows_list, 900, [175, 175, 550])
            self.estimates_section = self.estimates_section + backwater_table.return_html()
            
        self.record_html = self.record_html + self.backwater_section
    
    
    def create_hydro_comparison_section(self, hydro_comp_text):
        """
        Method to construct the hydrographic comparison section using a user's provided
        input. This section is usually copy and pasted from the previous analysis because
        SIMs does not record this nor is it kept in AQ.
        """
        self.hydro_comp_section = "<p><strong>Hydrographic Comparison</strong></p>\n"
        self.hydro_comp_section = self.hydro_comp_section + "<p>" + hydro_comp_text + "</p>\n"
        return self.hydro_comp_section
    
    def create_peak_record_discharge_table(self, primary_record_q_dataset):
        """
        Method to construct the table peak discharges during the record period.

        Args:
            primary_record_q_dataset(list[Unit_Value]): list of UVs for the discharge
            timeseries to be analyzed.
        """
        self.peak_recorder_streamflow_section = "<p><strong>Peak Recorder Streamflow</strong></p>\n" 

        table_header_row = html_table.html_table_row(["", "Date/Time", "Value"])
        body_rows_list = []
        max_point_datetime_str = str(primary_record_q_dataset.max_point.datetime)
        min_point_datetime_str = str(primary_record_q_dataset.min_point.datetime)
        
        if primary_record_q_dataset.max_point.unique == False:
            max_point_datetime_str = max_point_datetime_str + "*"
        if primary_record_q_dataset.max_point.estimated == True:
            max_point_datetime_str = max_point_datetime_str + ", E"
            
        if primary_record_q_dataset.min_point.unique == False:
            min_point_datetime_str = min_point_datetime_str + "*"
        if primary_record_q_dataset.min_point.estimated == True:
            min_point_datetime_str = min_point_datetime_str + ", E"

        body_rows_list.append(html_table.html_table_row(["Max Discharge", max_point_datetime_str, "{:.2f}".format(primary_record_q_dataset.max_point.value) + " cfs"]))
        body_rows_list.append(html_table.html_table_row(["Min Discharge", min_point_datetime_str, "{:.2f}".format(primary_record_q_dataset.min_point.value) + " cfs"]))
        extremes_table = html_table.html_table(table_header_row, body_rows_list, 580)
        
        subcaption = "<em style=\"box-sizing: border-box; color: #333333; font-family: Ubuntu; font-size: 15px; background-color: #ffffff;\">* Multiple occurrences of the same extreme in selected dataset. First occurrence listed., E = Estimated</em></div>\n"
            
        
        self.peak_recorder_streamflow_section = self.peak_recorder_streamflow_section + extremes_table.return_html() + subcaption
        
        self.record_html = self.record_html + self.peak_recorder_streamflow_section + "</div>" +  "<br />\n"    


    def _create_wy_extremes_table_section(self, site_obj: SiteV3.Site):
        """
        Method to construct the water-year extremes tables for the record period. If
        the record spans multiple periods, then it will construct multiple tables.

        Args:
            site_obj(Site): The site object representing the site and its data. This
            was done to make it easier to handle.
        """
        self.water_year_section = ""
        water_years = []
        
        for water_year in site_obj.gage_height_timeseries_list[0].water_year_datasets.keys():
            water_years.append(water_year)
        
        water_years.sort()

        for water_year in water_years:
            self.water_year_section += "</div>\n" + f"<p><strong><span style=\"text-decoration: underline;\">Extremes for {water_year} Water-Year</strong></p>\n" + "<div style=\"padding-left:30px;\">\n"
            table_header_row = html_table.html_table_row(["", "Date/Time", "Value"])
            body_rows_list = []

            if len(site_obj.gage_height_timeseries_list) == 1:
                water_year_gh_dataset = site_obj.gage_height_timeseries_list[0].water_year_datasets[water_year]
                max_gh_point_datetime_str = str(water_year_gh_dataset.max_point.datetime)
                min_gh_point_datetime_str = str(water_year_gh_dataset.min_point.datetime)
                
                if water_year_gh_dataset.max_point.unique == False:
                    max_gh_point_datetime_str = max_gh_point_datetime_str + "*"
                    
                if water_year_gh_dataset.min_point.unique == False:
                    min_gh_point_datetime_str = min_gh_point_datetime_str + "*"

                body_rows_list.append(html_table.html_table_row(["Max Gage Height", max_gh_point_datetime_str, "{:.2f}".format(water_year_gh_dataset.max_point.value) + "\'"]))
                body_rows_list.append(html_table.html_table_row(["Min Gage Height", min_gh_point_datetime_str, "{:.2f}".format(water_year_gh_dataset.min_point.value) + "\'"]))

            elif len(site_obj.gage_height_timeseries_list) > 1:
                for gh_ts in site_obj.gage_height_timeseries_list:
                    water_year_gh_dataset = gh_ts.water_year_datasets[water_year]
                    max_gh_point_datetime_str = str(water_year_gh_dataset.max_point.datetime)
                    min_gh_point_datetime_str = str(water_year_gh_dataset.min_point.datetime)
                    
                    if water_year_gh_dataset.max_point.unique == False:
                        max_gh_point_datetime_str = max_gh_point_datetime_str + "*"
                        
                    if water_year_gh_dataset.min_point.unique == False:
                        min_gh_point_datetime_str = min_gh_point_datetime_str + "*"

                    body_rows_list.append(html_table.html_table_row([f"Max Gage Height ({gh_ts.TS_sublocation})", max_gh_point_datetime_str, "{:.2f}".format(water_year_gh_dataset.max_point.value) + "\'"]))
                    body_rows_list.append(html_table.html_table_row([f"Min Gage Height ({gh_ts.TS_sublocation})", min_gh_point_datetime_str, "{:.2f}".format(water_year_gh_dataset.min_point.value) + "\'"]))
            
            if len(site_obj.discharge_timeseries_list) == 1:
                water_year_q_dataset = site_obj.discharge_timeseries_list[0].water_year_datasets[water_year]
                max_q_point_datetime_str = str(water_year_q_dataset.max_point.datetime)
                min_q_point_datetime_str = str(water_year_q_dataset.min_point.datetime)
                
                if water_year_q_dataset.max_point.unique == False:
                    max_q_point_datetime_str = max_q_point_datetime_str + "*"
                    
                if water_year_q_dataset.min_point.unique == False:
                    min_q_point_datetime_str = min_q_point_datetime_str + "*"

                body_rows_list.append(html_table.html_table_row(["Max Discharge", max_q_point_datetime_str, "{:.2f}".format(water_year_q_dataset.max_point.value) + "\'"]))
                body_rows_list.append(html_table.html_table_row(["Min Discharge", min_q_point_datetime_str, "{:.2f}".format(water_year_q_dataset.min_point.value) + "\'"]))
                
            elif len(site_obj.discharge_timeseries_list) > 1:
                for q_ts in site_obj.discharge_timeseries_list:
                    water_year_q_dataset = q_ts.water_year_datasets[water_year]
                    max_q_point_datetime_str = str(water_year_q_dataset.max_point.datetime)
                    min_q_point_datetime_str = str(water_year_q_dataset.min_point.datetime)
                    
                    if water_year_q_dataset.max_point.unique == False:
                        max_q_point_datetime_str = max_q_point_datetime_str + "*"
                        
                    if water_year_q_dataset.min_point.unique == False:
                        min_q_point_datetime_str = min_q_point_datetime_str + "*"

                    body_rows_list.append(html_table.html_table_row([f"Max Gage Height ({q_ts.TS_sublocation})", max_q_point_datetime_str, "{:.2f}".format(water_year_q_dataset.max_point.value) + "\'"]))
                    body_rows_list.append(html_table.html_table_row([f"Min Gage Height ({q_ts.TS_sublocation})", min_q_point_datetime_str, "{:.2f}".format(water_year_q_dataset.min_point.value) + "\'"]))

            extremes_table = html_table.html_table(table_header_row, body_rows_list, 580)
            subcaption = "<em style=\"box-sizing: border-box; color: #333333; font-family: Ubuntu; font-size: 15px; background-color: #ffffff;\">* Multiple occurrences of the same extreme in selected dataset. First occurrence listed. E = Estimated</em></div>\n"
            self.water_year_section = self.water_year_section + extremes_table.return_html() + subcaption + "</div>\n"
                
                


