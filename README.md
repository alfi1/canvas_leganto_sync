# canvas_leganto_sync
Retrieve course details from Canvas and update Alma/Leganto.

Tim Graves
University of Sussex Library
t.c.graves@sussex.ac.uk

# Before starting, you will need:
- Canvas access (what sort do I have??) so that you can access all courses.
- An access token for your Canvas API.
- An Ex Libris API key that allows you read/write access to Courses.
- To find out which course'accounts' you have in Canvas and decide which you want to include.
- To work out how you will identify the courses you want to include. You will need a common search term that can be found in them.

# Things you will need to change in the script:

- Line 18: Change the value of 'this_year' to be the sesrch term you will use to identify your courses in Canvas. (In Sussex all our course codes can be identified by containing the academic year: e.g. "24_25").
- Line 19: Change the 'display_year' to however you want it displayed in the course record in Alma.
- Lines 22-23: Default start and end dates for a course, in case they are not yet given in Canvas, in the format YYYY-MM-DD.
- Line 26: enter your Ex Libris API key.
- Line 29: enter your Canvas authorisation token.
- Line 98 and 112: Change to point at your instance of Canvas. e.g. https://YOUR.CANVAS.AC.UK:443/api/v1/users/{canvas_id}"
- Line 237: you might not need the function 'formatTerm'. In Sussex we have to rename the term names given in Canvas to match those in Alma/Leganto.
- Line 289. Replace with the account ids in your Canvas that you want included.
