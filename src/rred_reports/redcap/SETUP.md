# Setup of RRED on the Data Safe Haven (DSH)

A sane workflow once we have stable versions would be to publish to PyPi and
install the application via the DSH artifactory. For now, we can use the DSH
file transfer of the zipped repository to move code over.

## Transfer code to DSH

- From the github repo, click on the green "code" and click "Download zip"
  - On the
    [DSH file transfer portal](https://filetransfer.idhs.ucl.ac.uk/webclient/Login.xhtml),
    transfer this zip file to the `rred` directory to upload it to the DSH. If
    you don't have a `rred` directory in `/home`, then click on `New Folder` to
    create one
  - In the [DSH desktop](https://accessgateway.idhs.ucl.ac.uk/),
  - Rename the existing `S:\ReadingRecoveryEvalDB\ARC\rred-reports` with today's
    date in the format: `rred-reports_<YYYY-MM-DD>`
    - Navigate to `MFT_Arrivals\<ucl_username>\rred`, and then extract the zip
      file to `S:\ReadingRecoveryEvalDB\ARC`
    - Navigate to `S:\ReadingRecoveryEvalDB\ARC` and rename the extracted
      directory to `rred-reports`

## Setup of package in the DSH

- Follow the
  [How do I install packages on Anaconda using Artifactory](https://www.ucl.ac.uk/isd/services/file-storage-sharing/data-safe-haven/data-safe-haven-user-guide-faqs)
  section of the DSH FAQ, setting up the `.condarc` (Set up Anaconda with conda)
  and `pip.ini` (Set up Anaconda with PyPi) file in the N: drive
- Run an anaconda prompt from the S drive and navigate to the project directory
- Create a new conda environment called rred and activate it and install the
  package in editable mode. The creation and installation may give some retry
  errors, that's fine.
  ```shell
  conda create python=3.9 -n rred
  conda activate rred
  pip install -e .
  ```
- The `rred` CLI will now exist within this conda environment
