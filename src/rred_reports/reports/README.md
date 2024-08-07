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

- We should have received this year's template for school report documents
  (based on the previous years because we've edited it to make it consistent)
  from the RRED team. The report template should be added to
  `input/templates/{year}/{year-range}_template.docx` and the
  [report_config.toml](report_config.toml) updated to the current year.
- Copy the masterfile export from the Data Safe Haven
  `MFT Outbound/ReadingRecoveryEvalDB/` to the repo's `input/processed/{year}`
  so that it matches the settings in [report_config.toml](report_config.toml).
  - Update this file and make a PR if the current year doesn't exist in the
    config.
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
  - If you get an error during conversion of word docs to pdfs that contains
    `'result': 'error', 'error': 'Error: Message not understood.'`, then chances
    are the file in the message is opened in word. Close the file and then rerun
    `rred reports convert output/reports/{year}/schools`
  - If you get a warning about a report having an unexpected number of pages,
    open the Word document and check that a table hasn't been split over
    multiple lines. If this happens ask the RRED team if we want to decrease the
    font size for it to fit, or select the table and in the layout tab, split it
    so that it breaks over multiple pages, starting under table heading.
  - If you get errors which aren't clear, you can run the reports/interface.py
    file in debug mode in your IDE, altering the `if __name__ == "__main__":` to
    call the `create` function.
- If prompted, grant access to the `schools` directory in Microsoft (this will
  only happen the first time when you create reports for this year)
- At the end of the run, the output User Acceptance Testing (UAT) pdf of all
  reports joined together will be created and its filepath logged.
- Review the UAT file for any errors and send it to the study team for sign off.

## User Acceptance Testing of emails with MFA

The email body text may be changed and emailed to us, if so update it in
`src/rred_reports/reports/emails.py` in the `formatted_mail_content` function,
replacing any hardcoded years with the templating and ensuring all html
formatting is still being followed.

We can override all email addresses with a single email for testing. In order to
make sure that the report emailing works, you can do this first to your own
email for the year following this pattern:

```shell
rred reports send-school {year} --override-mailto="{your username}@ucl.ac.uk"
```

If you encounter any errors, you can run the reports/interface.py file in debug
mode in your IDE, altering the `if __name__ == "__main__":` to call the
`send_school` function, overriding the email addresses. There's an example of
this already in the current code block.

Once you have reviewed the emails to check that the subject, email body and
attachments look correct, you can send the reports to the RRED study team

```shell
rred reports send-school {year} --override-mailto="ilc.comms@ucl.ac.uk"
```

You will receive a message saying,
`"Please follow the authentication flow by visiting this link and entering the final redirect URL: {some URL}"`.
Click on this link to open a Microsoft login page in your web browser. Once
logged in, you will see a 2-digit number. Use the Microsoft Authenticator app on
your mobile device to authenticate the app by entering this number. After
authentication, the Microsoft sign-in page should redirect to a blank screen.

Copy the URL from the browser's address bar and save it to `access_link.txt`.

Next, return to the command line and enter any text:

`Please follow auth flow by going to this link, then enter in the final redirect URL: {some URL}`
: `type something here (it doesn't matter what)`

After completing these steps, a new file named `my_cache.bin` will have been
created. This file contains your access tokens necessary for sending out emails.
The process should now begin sending emails; please check your inbox.

## Emailing of reports to teachers

Once the RRED study team has reviewed the reports, we can run the full email to
teachers and teacher leaders.

```shell
rred reports send-school {year}
```

If there are any errors while reports are sending, then the logging will tell
you which email IDs failed to send, which you can either copy the list to run
via the reports/interface.py `if __name__ == "__main__":` block, or you can use
the CLI arguments given by the logging.

Let the RRED team know about the emails being sent out and transfer the
masterfile and dispatch list to the RRED R drive.
