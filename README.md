# rred-reports

[![Actions Status][actions-badge]][actions-link]

<!-- prettier-ignore-start -->
[actions-badge]:            https://github.com/UCL-ARC/rred-reports/workflows/CI/badge.svg
[actions-link]:             https://github.com/UCL-ARC/rred-reports/actions

<!-- prettier-ignore-end -->

Extracts RRED data from REDCap, transforms and populates templates. Allows
automated sending of reports via email

## Setting up a development version on UCL Data Safe Haven

- A sane workflow once we have stable versions would be to publish to PyPi and
  install the application via the DSH artifactory. For now, we can use the DSH
  file transfer of the zipped repository to move code over.
- Follow the
  [How do I install packages on Anaconda using Artifactory](https://www.ucl.ac.uk/isd/services/file-storage-sharing/data-safe-haven/data-safe-haven-user-guide-faqs)
  section of the DSH FAQ, setting up the `.condarc` (Set up Anaconda with conda)
  and `pip.ini` (Set up Anaconda with PyPi) file in the N: drive
- Run an anaconda prompt from the S drive and navigate to the project directory
- Create a new conda environment called rred and activate it and install the
  package in editable mode
  ```shell
  conda create python=3.9 -n rred
  conda activate rred
  pip install -e .
  ```
- The `rred` CLI will now exist within this conda environment
