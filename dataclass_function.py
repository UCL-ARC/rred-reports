import datetime
from dataclasses import dataclass

from pandas_dataclasses import AsFrame, Data, Index


@dataclass
class Pupil(AsFrame):
    """Pupil information"""

    pupilno: Index[complex]
    rreduserID: Data[str]
    assessi_engtest2: Data[int]
    assessi_iretest1: Data[int]
    assessi_iretype1: Data[int]
    assessi_maltest1: Data[int]
    assessi_outcome: Data[int]
    assessi_scotest1: Data[int]
    assessi_scotest2: Data[int]
    assessi_scotest3: Data[int]
    assessii_engcheck1: Data[int]
    assessii_engtest4: Data[int]
    assessii_engtest5: Data[int]
    assessii_engtest6: Data[int]
    assessii_engtest7: Data[int]
    assessii_engtest8: Data[int]
    assessii_scotest4: Data[int]
    assessii_iretest2: Data[int]
    assessii_iretype2: Data[int]
    assessiii_engtest10: Data[int]
    assessiii_engtest11: Data[int]
    assessiii_engtest9: Data[int]
    assessiii_iretest4: Data[int]
    entry_dob: Data[datetime.datetime]
    summer: Data[str]
    entry_date: Data[datetime.datetime]
    entry_testdate: Data[datetime.datetime]
    exit_date: Data[datetime.datetime]
    exit_outcome: Data[str]
    entry_year: Data[str]
    entry_gender: Data[str]
    entry_ethnicity: Data[str]
    entry_language: Data[str]
    entry_poverty: Data[str]
    entry_sen_status: Data[str]
    entry_special_cohort: Data[str]
    entry_bl_result: Data[int]
    entry_li_result: Data[int]
    entry_cap_result: Data[int]
    entry_wt_result: Data[int]
    entry_wv_result: Data[int]
    entry_hrsw_result: Data[int]
    entry_bas_result: Data[int]
    exit_num_weeks: Data[int]
    exit_num_lessons: Data[int]
    exit_lessons_missed_ca: Data[int]
    exit_lessons_missed_cu: Data[int]
    exit_lessons_missed_ta: Data[int]
    exit_lessons_missed_tu: Data[int]
    exit_bl_result: Data[int]
    exit_li_result: Data[int]
    exit_cap_result: Data[int]
    exit_wt_result: Data[int]
    exit_wv_result: Data[int]
    exit_hrsw_result: Data[int]
    exit_bas_result: Data[int]
    month3_testdate: Data[datetime.datetime]
    month3_bl_result: Data[int]
    month3_wv_result: Data[int]
    month3_bas_result: Data[int]
    month6_testdate: Data[datetime.datetime]
    month6_bl_result: Data[int]
    month6_wv_result: Data[int]
    month6_bas_result: Data[int]
    rred_QC_Parameters: Data[str]


@dataclass
class Teacher(AsFrame):
    """Teacher information, can link with Pupil df with rreduserID"""

    rreduserID: Index[str]
    reg_rr_title: Data[str]
    school_id: Data[int]


@dataclass
class School:
    """School information can link with Teacher df with school_id"""

    school_id: Index[int]
    rrcp_school: Data[str]
    rrcp_area: Data[int]
    rrcp_country: Data[int]
