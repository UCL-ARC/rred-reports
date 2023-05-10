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
- For running the steps in the DSH, follow the instructions in
  [src/rred_reports/redcap/README.md](src/rred_reports/redcap/README.md)

## Sending emails from a delegated mailbox with Office 365

The process of setting up access to Exchange Web Services (EWS) via OAuth with
Office 365 to enable sending emails from a delegated mailbox is described below.

Access to the delegated mailbox should first be given to any user intending to
follow this process.

An Azure Active Directory App registration must be made in order to email from a
delegated mailbox. When setting up the project from scratch (with no existing
app registration), follow the
[instructions](https://ecederstrand.github.io/exchangelib/#oauth-on-office-365)
provided by the [exchangelib docs](https://ecederstrand.github.io/exchangelib/)
in full.

In brief, new app registrations should be made by:

- Authenticating with your institutional login on
  [https://portal.azure.com](https://portal.azure.com)
- Searching for 'App Registrations'
- Creating a new registration and noting down the tenant ID and
  client/application ID
- Creating a client secret with a sensible name and noting down the secret
- Setting API permissions as described in the exchangelib docs. If you are not
  able to assign the `full_access_as_app` permission as shown in the exchangelib
  docs, add the `EWS.AccessAsUser.All` permission (found under)
  `Office 365 Exchange Online` and `Mail.Send`, `Mail.Send.Shared` and
  `User.Read` from `Microsoft Graph`. Selecting "Delegated" permissions in the
  previous step enables the app registration to authenticate via user sign-in.
- Under `Authentication`, set a redirect URI for "Mobile and desktop
  applications". The default
  `https://login.microsoftonline.com/common/oauth2/nativeclient` will work.
- Also under `Authentication`, ensure "Accounts in this organizational directory
  only" is selected under "Supported Account types" **and** ensure that "Allow
  public client flows" is set to "Yes".

### User sign in and consent

As a user, you must consent to the registered application service by visiting a
URL with the pattern

`https://login.microsoftonline.com/{tenant_id}/oauth2/authorize?client_id={app_id}&redirect_uri=https://login.microsoftonline.com/common/oauth2/nativeclient&response_type=code&prompt=consent`

The `tenant_id` and `app_id` should be the ones noted at the App registration
stage, or documented internally.

Sign in and consent to the requested app permissions.

### Settings to enable email sending

Create a `secrets.toml` from the provided example

```bash
cp src/rred_reports/.example-secrets.toml src/rred_reports/.secrets.toml
```

Fill in `client_id`, `client_secret` and `tenant_id` with the values noted down
from the app registration, or documented internally.

Fill in the username and password combination that will be used to authenticate
the application. `.secrets.toml` has been added to the `.gitignore`, but this
file should **never** be committed to version control.
