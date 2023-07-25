# Report generation and emailing

## Configure Azure and local application

Assuming that you have cloned the repository locally, and created an appropriate
virtualenv/conda env there is some first-time setup required:

- Follow [setup instructions](SETUP.md), authorising the azure application to
  delegate your account and update the `secret.toml` values.
- If you haven't already installed the local version (or dependencies have
  changed) then run `pip install -e .` from the `rred-reports` top level
  directory.

## Generate PDF reports

- Copy the masterfile export from the Data Safe Haven
  `MFT Outbound/ReadingRecoveryEvalDB/` to the repo's `input/processed/{year}`
  so that it matches the settings in [report_config.toml](report_config.toml).
- Copy the dispatch list to `input/dispatch_lists` so that it matches the
  settings in [report_config.toml](report_config.toml).
- Close Microsoft Word if its open (as Word is opened during PDF writing).
- If you have previously run the reports for this year, then its worth deleting
  the existing reports in `output/reports/{year}/schools`.
- From the command line run: `rred reports create school {year}`
  - If you get a pandas error for `Out of bounds nanosecond timestamp` then it
    is most likely a typo in the date, ask the research team for the correct
    value if not obvious. report with the `pupil_no` and `rred_user_id`,
    correcting to a temporarily likely value to be able to check for more errors
  - If you get errors which aren't clear, you can run the reports/interface.py
    file in debug mode in your IDE, altering the `if __name__ == "__main__:` to
    call the `create` function.
- If prompted, grant access to the `schools` directory in Microsoft (this will
  only happen the first time when you create reports for this year)
- At the end of the run, the output User Acceptance Testing (UAT) pdf of all
  reports joined together will be created and its filepath logged. Review this
  for any errors and send it to the study team for sign off.

## User Acceptance Testing of emails

- TODO:

## Emailing of reports to teachers

- TODO:
