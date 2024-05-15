# canvas_leganto_sync
Retrieve module details from Canvas and update course information in Alma/Leganto.
Tim Graves. t.c.graves@sussex.ac.uk. University of Sussex Library

# Before starting, you will need:
- A role in Canvas of 'Account Admin' that allows you to access all modules. (Otherwise your API calls will only retrieve the modules to which you are attached).
- An access token for your Canvas API. (You can set this up for yourself in Canvas: User->Settings->Approved Integrations->New access token).
- An Ex Libris API key that allows you read/write access to Courses. (From the Developer's Network - https://developers.exlibrisgroup.com).
- To find out which course 'accounts' you have in Canvas and decide which you want to include.
- To work out how you will identify the courses you want to include. You will need a common search term: e.g. University of Sussex courses carry a reference to the year '24_25'.

# Things you will need to change in the Python script:
- Line 18: Change the value of 'this_year' to the search term you will use to identify your courses in Canvas. e.g. "24_25".
- Line 19: Change the 'display_year' to however you want it displayed in the course record in Alma.
- Lines 22-23: Default start and end dates for a course, in case they are not yet added in Canvas, in the format YYYY-MM-DD.
- Line 26: enter your Ex Libris API key.
- Line 29: enter your Canvas authorisation token.
- Line 98 and 112: Change to point at your instance of Canvas. e.g. https://YOUR.CANVAS.AC.UK:443/api/v1/users/{canvas_id}"
- Line 237: you might not need the function 'formatTerm' at all. (In Sussex we have to rename the term names given in Canvas to match those in Alma/Leganto).
- Line 289. Replace with the account ids in your Canvas that you want included.

# Useful links when testing
- The Ex Libris Developer's Network - https://developers.exlibrisgroup.com. The 'API Console' will allow you to make test calls against the courses API and make sure that you are retrieving the correct data.
- The Canvas Live API - https://canvas.YOUR_SITE.ac.uk/doc/api/live. This will allow you make test calls against the Canvas API: useful for identifying which 'accounts' you want to include, and to work out your search term to identify courses you want included.
