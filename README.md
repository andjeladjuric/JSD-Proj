# Calendar DSL for Google Calendar

The aim of this project is to introduce a Domain-specific language that helps handling events in Google Calendar (time-management and scheduling calendar service developed by Google).

# Overview

A defined Domain-specific language is created with goal to provide easier usage of Google Calendar. In order to achive this goal language needs to support basic Google Calendar functions, such as creation and maintainence of events, tasks and task lists for user. Defined language has that ability and, in addition to that, it goes one step further with queries that offers. These queris have simple human language inspired syntax for filltering users events based on time of occurance, owner and tasklist.

# Example of Usage

# How to use

Inside your virtual environment it is possible to install our interpreter using the next command:

`pip install git+https://github.com/andjeladjuric/JSD-Proj.git`

With this command, all the necessary requirements to run the project, like Google API or Auth packages, should be installed in your virtual env.
In order to check, please start the next command:

`pip list`

The result should look something like this:

    Package                  Version
    ------------------------ -----------
    Arpeggio                 2.0.0
    calendarlang             0.1.0.dev0
    google-api-core          2.11.0
    google-api-python-client 2.81.0
    google-auth              2.16.2
    google-auth-httplib2     0.1.0
    google-auth-oauthlib     1.0.0
    googleapis-common-protos 1.58.0
    httplib2                 0.21.0
    oauthlib                 3.2.2
    pip                      22.3.1
    pytz                     2022.7.1
    requests                 2.28.2
    requests-oauthlib        1.3.1
    setuptools               65.5.0
    textX                    3.1.1
    tzlocal                  4.3

Next, you need to add your config file which will contain the API key that is necessary to use the Google APIs.

Afterwards, you can write your `.cal` file. You can use the one we provided as an example.

Next, you can write a python script which will generate all events or tasks with all necessary properties inside them in your calendar. We also provide the possibility for writing simple queries to read events or tasks from your calendars. \
Here's an example:

    from calendarlang import cal
    cal.main('calendarExample.cal')

Instead of `calendarExample.cal` please provide your own `.cal` file.

If you want to make writing files easier, you can use our VSCode syntax highlighting extension. In order to do so please copy the contents of `syntax-highlight-ext/calendarlang` folder into `.vscode/extensions` in your `home` directory.
