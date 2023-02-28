import datetime
from dataclasses import dataclass


@dataclass
class Pupil:
    pupilno: complex
    assessi_engtest2: int
    assessi_iretest1: int
    assessi_iretype1: int
    assessi_maltest1: int
    assessi_outcome: int
    assessi_scotest1: int
    assessi_scotest2: int
    assessi_scotest3: int
    assessii_engcheck1: int
    assessii_engtest4: int
    assessii_engtest5: int
    assessii_engtest6: int
    assessii_engtest7: int
    assessii_engtest8: int
    assessii_scotest4: int
    assessii_iretest2: int
    assessii_iretype2: int
    assessiii_engtest10: int
    assessiii_engtest11: int
    assessiii_engtest9: int
    assessiii_iretest4: int
    entry_dob: datetime.datetime
    Summer: str
    entry_date: datetime.datetime
    entry_testdate: datetime.datetime
    exit_date: datetime.datetime
    exit_outcome: str
    entry_year: str
    entry_gender: str
    entry_ethnicity: str
    entry_language: str
    entry_poverty: str
    entry_sen_status: str
    entry_special_cohort: str
    entry_bl_result: int
    entry_li_result: int
    entry_cap_result: int
    entry_wt_result: int
    entry_wv_result: int
    entry_hrsw_result: int
    entry_bas_result: int
    exit_num_weeks: int
    exit_num_lessons: int
    exit_lessons_missed_ca: int
    exit_lessons_missed_cu: int
    exit_lessons_missed_ta: int
    exit_lessons_missed_tu: int
    exit_bl_result: int
    exit_li_result: int
    exit_cap_result: int
    exit_wt_result: int
    exit_wv_result: int
    exit_hrsw_result: int
    exit_bas_result: int
    month3_testdate: datetime.datetime
    month3_bl_result: int
    month3_wv_result: int
    month3_bas_result: int
    month6_testdate: datetime.datetime
    month6_bl_result: int
    month6_wv_result: int
    month6_bas_result: int
    RRED_QC_Parameters: str


@dataclass
class Teacher:
    reg_rr_title: str
    RREDUserID: str
    pupil: Pupil


@dataclass
class Main:
    school_id: int
    rrcp_school: str
    rrcp_area: int
    rrcp_country: int
    teacher: Teacher
