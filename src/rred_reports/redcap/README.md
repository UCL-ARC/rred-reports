# Redcap functionality

## Extracting redcap data on the data safe haven (DSH)

- If the current year isn't in [redcap_config.toml](redcap_config.toml), add it
  and make a PR to get this into the `main` branch.
- Assuming that you have transferred the latest version of the repo to the DSH,
  copied it to `S:\ReadingRecoveryEvalDB\ARC\rred-reports` and installed it in a
  conda environment following the setup instructions in the [setup.md](SETUP.md)
- In the DSH Desktop, start a new anaconda prompt on the `S:` drive (look in
  Start > Anaconda3 64-bit) and navigate to the installed repo
- Activate the conda environment
  ```shell
  conda activate rred
  ```
- Create a subdirectory in `input/downloaded` for the study year, e.g. `2021`
- Copy the latest dispatch list into this subdirectory and name it so that
  matches the [redcap_config.toml](redcap_config.toml)
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
  - Copy these files to your `input/downloaded/{year}` directory that you
    created above
  - N.B. Both files should be exported from RedCap at the end of the survey
    period, because the previous year will also be updated (we shouldn't reuse
    last year's exports!)
- Copy the dispatch list from the research team
  - We require the `UserID`, `School Label`, `RRED School ID`, `Email` and
    `TL Email` columns in the dispatch list. Update the column names if required
    to match this.
  - Copy the dispatch list Excel file into `input/dispatch_lists`, renaming it
    to match the [redcap_config.toml](redcap_config.toml) `dispatch_list`
    filename
- Back in the conda prompt, run `rred redcap extract {year}`, for example:
  ```shell
  rred redcap extract 2021
  ```
- This should take a couple of minutes, then copy output masterfile to the
  outgoing folder for RRED
  - If you get a `DispatchlistException` then email the RRED study group to ask
    for the correct school information for us to update the dispatch list. This
    means our work is blocked
- Transfer the output data, and if there are any issues the issues file to
  `R:\ReadingRecoveryEvalDB\ARC` and download these to your machine using the
  [DSH file transfer portal](https://filetransfer.idhs.ucl.ac.uk/webclient/Login.xhtml)
- Email the research group with any issues and the masterfile, explaining the
  issues and asking for them to look into and fix them.
  - Any schools which aren't in the dispatch list but have `in_current_survey`
    as `FALSE` do not need to be corrected because they won't be reported on
    this year.
  - Any issues with the dispatch list need to be addressed and then this should
    be used to re-run the redcap extraction on the DSH (as school names come
    from the dispatch list).
  - If there are still issues that are important after the dispatch list has
    been corrected then the masterfile will need to be edited, and we should use
    that version downstream. Any schools that don't exist in the dispatch list
    will not make it into the report processing stage as they won't have a
    school name.
  - You may need to create a school alias file using the
    [template](../../../input/school_aliases/template.toml). You can then rerun
    using the `--school-aliases` flag. For example:
    `rred redcap extract 2022 --school-aliases input\school_aliases\2022-23_school_aliases.toml`
- Copy the extract to your local machine's version of the `rred-reports` in
  `input/processed/{year}/`, naming the file to match
  [src/rred_reports/reports/report_config.toml](../reports/report_config.toml)
