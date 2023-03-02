# import datetime
# from datetime import date
from dataclasses import dataclass

import pandas as pd
from pandas_dataclasses import AsFrame, Data, Index


@dataclass
class Pupil(AsFrame):
    """Pupil information"""

    pupil_no: Index[str]
    rred_user_id: Data[str]
    assessi_engtest2: Data[float]
    assessi_iretest1: Data[float]
    assessi_iretype1: Data[float]
    assessi_maltest1: Data[float]
    assessi_outcome: Data[float]
    assessi_scotest1: Data[float]
    assessi_scotest2: Data[float]
    assessi_scotest3: Data[float]
    assessii_engcheck1: Data[float]
    assessii_engtest4: Data[float]
    assessii_engtest5: Data[float]
    assessii_engtest6: Data[float]
    assessii_engtest7: Data[float]
    assessii_engtest8: Data[float]
    assessii_scotest4: Data[float]
    assessii_iretest2: Data[float]
    assessii_iretype2: Data[float]
    assessiii_engtest10: Data[float]
    assessiii_engtest11: Data[float]
    assessiii_engtest9: Data[float]
    assessiii_iretest4: Data[float]
    entry_dob: Data[str]
    summer: Data[str]
    entry_date: Data[str]
    entry_testdate: Data[str]
    exit_date: Data[str]
    exit_outcome: Data[str]
    entry_year: Data[str]
    entry_gender: Data[str]
    entry_ethnicity: Data[str]
    entry_language: Data[str]
    entry_poverty: Data[str]
    entry_sen_status: Data[str]
    entry_special_cohort: Data[str]
    entry_bl_result: Data[float]
    entry_li_result: Data[float]
    entry_cap_result: Data[float]
    entry_wt_result: Data[float]
    entry_wv_result: Data[float]
    entry_hrsw_result: Data[float]
    entry_bas_result: Data[float]
    exit_num_weeks: Data[float]
    exit_num_lessons: Data[float]
    exit_lessons_missed_ca: Data[float]
    exit_lessons_missed_cu: Data[float]
    exit_lessons_missed_ta: Data[float]
    exit_lessons_missed_tu: Data[float]
    exit_bl_result: Data[float]
    exit_li_result: Data[float]
    exit_cap_result: Data[float]
    exit_wt_result: Data[float]
    exit_wv_result: Data[float]
    exit_hrsw_result: Data[float]
    exit_bas_result: Data[float]
    month3_testdate: Data[str]
    month3_bl_result: Data[float]
    month3_wv_result: Data[float]
    month3_bas_result: Data[float]
    month6_testdate: Data[str]
    month6_bl_result: Data[float]
    month6_wv_result: Data[float]
    month6_bas_result: Data[float]
    rred_qc_parameters: Data[str]


@dataclass
class Teacher(AsFrame):
    """Teacher information, can link with Pupil df with rreduserID"""

    rred_user_id: Index[str]
    reg_rr_title: Data[str]
    school_id: Data[str]


@dataclass
class School(AsFrame):
    """School information can link with Teacher df with school_id"""

    school_id: Index[str]
    rrcp_school: Data[str]
    rrcp_area: Data[int]
    rrcp_country: Data[int]


# function for getting list from df columns


def createdf(file):
    # read the file
    df = pd.read_excel(file)

    def clmnlist(i):
        return list(df.iloc[:, i])

    """ For the school df, showing:
        school_id
        rrcp_school
        rrcp_area
        rrcp_country
    """
    school_df = School.new(clmnlist(6), clmnlist(5), clmnlist(4), clmnlist(3))

    """ For the teacher df, showing:
        rred_user_id
        red_rr_title
        school_id
    """
    teach_df = Teacher.new(clmnlist(1), clmnlist(2), clmnlist(6))
    """
    I feel like below could be a for loop but not quite sure how
    """
    pupil_df = Pupil.new(
        clmnlist(0),
        clmnlist(1),
        clmnlist(7),
        clmnlist(8),
        clmnlist(9),
        clmnlist(10),
        clmnlist(11),
        clmnlist(12),
        clmnlist(13),
        clmnlist(14),
        clmnlist(15),
        clmnlist(16),
        clmnlist(17),
        clmnlist(18),
        clmnlist(19),
        clmnlist(20),
        clmnlist(21),
        clmnlist(22),
        clmnlist(23),
        clmnlist(24),
        clmnlist(25),
        clmnlist(26),
        clmnlist(27),
        clmnlist(28),
        clmnlist(29),
        clmnlist(30),
        clmnlist(31),
        clmnlist(32),
        clmnlist(33),
        clmnlist(34),
        clmnlist(35),
        clmnlist(36),
        clmnlist(37),
        clmnlist(38),
        clmnlist(39),
        clmnlist(40),
        clmnlist(41),
        clmnlist(42),
        clmnlist(43),
        clmnlist(44),
        clmnlist(45),
        clmnlist(46),
        clmnlist(47),
        clmnlist(48),
        clmnlist(49),
        clmnlist(50),
        clmnlist(51),
        clmnlist(52),
        clmnlist(53),
        clmnlist(54),
        clmnlist(55),
        clmnlist(56),
        clmnlist(57),
        clmnlist(58),
        clmnlist(59),
        clmnlist(60),
        clmnlist(61),
        clmnlist(62),
        clmnlist(63),
        clmnlist(64),
        clmnlist(65),
        clmnlist(66),
        clmnlist(67),
        clmnlist(68),
        clmnlist(69),
    )

    return school_df, teach_df, pupil_df


school_test_df, teach_test_df, pupil_test_df = createdf("example_dataset.xlsx")

school_test_df
teach_test_df
pupil_test_df
