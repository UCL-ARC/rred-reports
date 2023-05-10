# Redcap functionality

## Extracting redcap data on the data safe haven (DSH)

- Assuming that you have transferred the latest version of the repo to the DSH,
  copied it to `S:\ReadingRecoveryEvalDB\ARC\rred-reports` and installed it in a
  conda environment following the setup instructions in the
  [repo readme](../../../README.md)
- In the DSH Desktop, start a new conda prompt on the `S:` drive and navigate to
  the installed repo
- Activate the conda environment
  ```shell
  conda activate rred
  ```
- Create a subdirectory in `input/downloaded` for the study year, e.g. `2021`
- Copy the latest dispatch list into this subdirectory and name it so that
  matches the [redcap_config.toml](redcap_config.toml) (Adding in all details
  for a new year if required), or you may also create a custom config file
- Open up redcap from the DSH desktop start bar and log in using your DSH
  credentials
- For each study period (e.g. current year is 2021, so _2021-22_ and _2020-21_
  periods)
  - Open the study period and under the `Applications` sidebar, click on the
    `Data Exports, Reports and Stats` link
  - Under the `All Data (all records and fields)` Report name, click
    `Export Data`
  - Choose the export format `CSV / Microsoft Excel (raw data)` and click
    `Export Data`.
  - When the modal window changes to say the export was successful, click on the
    icon to download the file
  - Rename it so that it matches the expected filename from
    [redcap_config.toml](redcap_config.toml) for the `coded_data_file` and copy
    it to this year's input path
  - Click close, going through the `Export data` again, and this time select the
    `CSV / Microsoft Excel (labels)`, following the same steps and renaming
    according to the `label_data_file` for the year, remember to copy this in.
  - Remember to do this for the current study period and the previous one!
- Back in the conda prompt, run `rred redcap extract {year}`, for example:
  ```shell
  rred redcap extract 2021
  ```
- This should take a couple of minutes, then copy output masterfile to the
  outgoing folder for RRED and ask the research group to add this to the R:
  drive or email it to you!
