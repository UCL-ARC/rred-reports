# rred-reports

[![Actions Status][actions-badge]][actions-link]

<!-- prettier-ignore-start -->
[actions-badge]:            https://github.com/UCL-ARC/rred-reports/workflows/CI/badge.svg
[actions-link]:             https://github.com/UCL-ARC/rred-reports/actions

<!-- prettier-ignore-end -->

Extracts RRED data from REDCap, transforms and populates templates. Allows
automated sending of reports via email

## Extracting data from the UCL Data Safe Haven (DSH)

- To set up the RRED package for the first time in DSH follow the instruction in
  [src/rred_reports/redcap/SETUP.md](src/rred_reports/redcap/SETUP.md)
- For running the steps in the DSH, follow the instructions in
  [src/rred_reports/redcap/README.md](src/rred_reports/redcap/README.md)

## Generation of reports and emailing on your local machine

- To set up the RRED package for the first time on your local machine follow the
  instructions in
  [src/rred_reports/reports/SETUP.md](src/rred_reports/reports/SETUP.md)
- Follow the
  [Generate PDF Reports](src/rred_reports/reports/README.md#generate-pdf-reports)
  section of the reports README
- Follow the
  [User Acceptance Testing of emails](src/rred_reports/reports/README.md#user-acceptance-testing-of-emails)
  section of the reports README
- Follow the
  [Emailing of reports to teachers](src/rred_reports/reports/README.md#emailing-of-reports-to-teachers)
  section of the reports README
