#!/usr/bin/env python3

# Connects to Canvas API and retrieves courses that meet a specified criteria
# Then updates ALma/Leganto course record using API
# Tim Graves. University of Sussex Library. t.c.graves@sussex.ac.uk

import requests
import json
import logging
from datetime import datetime

# Set the logging level so that we see INFO ones
logging.getLogger().setLevel(logging.INFO)

# A few variables that hold the current academic year.
# These will need changing every year.

this_year = "24_25"
display_year = "2025"

# Term dates if none found in Canvas
default_start = "2024-08-31"
default_stop = "2025-08-31"

# Leganto api key
leganto_api_key = "EX_LIBRIS_APIS_KEY_THAT_GIVES_WRITE_PERMISSION_TO_COURSES"

# Canvas access code.
headers = {"Authorization": "Bearer <YOUR_CANVAS_ACCESS_TOKEN_HERE>"}


def getLegantoCourseID(SIS_ID):
    # Function to get a course_id from Leganto based on an SIS_ID from Canvas

    leganto_call = requests.get(
        f"https://api-eu.hosted.exlibrisgroup.com/almaws/v1/courses?q=code~{SIS_ID}&limit=10&offset=0&status=ALL&order_by=code&direction=ASC&exact_search=true&apikey={leganto_api_key}&format=json"
    )

    leganto_results = json.loads(leganto_call.text)

    # Skip any courses not found in Leganto

    if leganto_results["total_record_count"] == 0:
        logging.warning(f"Skipping {SIS_ID} - 0 records found in Alma")
        return_value = "skip"
        return return_value

    leganto_course_id = leganto_results["course"][0]["id"]

    # Set the 'searchable_id'
    searchable_id = SIS_ID.split("_")[0]

    return leganto_course_id, searchable_id


# Function to update a course in Leganto
def updateLegantoCourse(
    leganto_course_code,
    SIS_ID,
    module_name,
    term_date_start,
    term_date_end,
    total_students,
    academic_dept,
    searchable_id,
    term_code,
    instructors,
):
    update_url = f"https://api-eu.hosted.exlibrisgroup.com/almaws/v1/courses/{leganto_course_code}?apikey={leganto_api_key}"

    payload = json.dumps(
        {
            "code": SIS_ID,
            "name": module_name,
            "processing_department": {"value": "MAIN", "desc": "MAIN"},
            "term": [{"value": term_code, "desc": term_code}],
            "academic_department": {"value": academic_dept, "desc": academic_dept},
            "searchable_id": [searchable_id],
            "start_date": term_date_start,
            "end_date": term_date_end,
            "status": "ACTIVE",
            "participants": total_students,
            "year": display_year,
            "instructor": instructors,
        }
    )
    headers = {"Accept": "application/json",
               "Content-Type": "application/json"}

    # Run the update in Alma
    requests.request("PUT", update_url, headers=headers, data=payload)
    logging.info(f"Updated {SIS_ID}")


def get_teacher_pid(canvas_id):
    # Function to get the PID for a teacher based on their Canvas 'id'

    call_user_url = f"https://canvas.sussex.ac.uk:443/api/v1/users/{canvas_id}"

    teacher_response = requests.get(call_user_url, headers=headers)

    teacher_data = teacher_response.json()
    teacher_details = teacher_data

    return teacher_details.get("sis_user_id")


def call_canvas_account(this_year, each_account):
    # Function that calls Canvas for all courses
    # in a given account, and updates Leganto

    api_url = f"https://canvas.sussex.ac.uk:443/api/v1/accounts/{each_account}/courses?search_term={this_year}&include[]=total_students&include[]=teachers&search_by=course"

    # Set up the parameters
    params = {
        "per_page": 100,  # Set to the maximum number of results per page,
        "include[]": ["total_students", "term", "account", "start_at"],
    }

    # Make the initial API call to get the first page of results
    response = requests.get(api_url, headers=headers, params=params)

    # Create empty default values in case needed:
    term_date_start_tidied = ("",)
    term_date_end_tidied = ("",)

    if response.status_code == 200:
        # Response was successful, parse JSON data and get pagination
        # information, i.e. see if "next" button appears as a link
        # if it does then add all that pages json data together
        data = response.json()
        courses = data

        # While loop to page through the results 100 at a time.

        while "next" in response.links:
            # Make additional API calls to get subsequent pages of data
            url = response.links["next"]["url"]
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                # Append retrieved courses to the main list
                data = response.json()
                courses += data
            else:
                # Response was unsuccessful, handle error
                print(f"Error: {response.status_code} - {response.text}")
                break

        # Loop through the complete set of courses: process and update Leganto

        for course in courses:
            SIS_ID = course.get("sis_course_id")

            # Useful to see which course is about to be processed in case it fails
            logging.info(f"About to check Leganto for {SIS_ID}")

            # Check whether there are 0 courses found in Leganto and skip
            anything_on_leganto = getLegantoCourseID(SIS_ID)

            if anything_on_leganto == "skip":
                logging.warning(f"Skipping {SIS_ID} - zero results in Leganto")
                continue

            total_students = course.get("total_students", 0)

            module_name = course.get("name")

            academic_dept = course.get("account", {}).get("name", "")

            term_date_start = course.get("term", {}).get("start_at", "")

            if term_date_start is not None:
                term_date_start_tidied = term_date_start[0:10]
            else:
                term_date_start_tidied = default_start

            term_date_end = course.get("term", {}).get("end_at", "")

            if term_date_end is not None:
                term_date_end_tidied = term_date_end[0:10]
            else:
                term_date_end_tidied = default_stop

            all_the_teachers = course.get("teachers")

            # Create a list to hold all the teachers in JSON
            json_formatted_teachers = []

            for each_teacher in all_the_teachers:
                teacher_id = each_teacher.get("id")

                # Call the function that gets the PID from the user's Canvas id
                the_teacher = get_teacher_pid(teacher_id)

                json_formatted_teachers.append({"primary_id": the_teacher})

            # Add the term code from Canvas
            term_details = course.get("term")
            term_from_canvas = term_details.get("name")
            term_code = formatTerm(term_from_canvas)

            # Get details from, and subsequently update, Leganto.
            try:
                # Call function to get the course_id stored in Alma
                leganto_course_details = getLegantoCourseID(SIS_ID)

                leganto_course_code = leganto_course_details[0]

                searchable_id = SIS_ID.split("_")[0]

                # Get the Canvas version of the teachers
                instructors = json_formatted_teachers

                # Call the function to update the course in Leganto

                updateLegantoCourse(
                    leganto_course_code,
                    SIS_ID,
                    module_name,
                    term_date_start_tidied,
                    term_date_end_tidied,
                    total_students,
                    academic_dept,
                    searchable_id,
                    term_code,
                    instructors,
                )

            except ValueError:
                logging.warning("Failed to get details of this course!")

    else:
        # If response was unsuccessful, print error code andresponse text
        print(f"Error: {response.status_code} - {response.text}")


def formatTerm(term):

    # Function to reformat the term name from Canvas into
    # something that will map our terms in Leganto

    incoming_term = term

    if "Autumn Teaching" in term:
        return "AUTUMN"

    elif "All Year Teaching" in term:
        return "YEARLY"

    elif "Default term" in term:
        return "YEARLY"

    elif "Autumn & Spring Teaching" in term:
        return "SEMESTER1"

    elif "Flexible Learning Year" in term:
        return "TERM1"

    elif "P/G Academic Year" in term:
        return "TERM3"

    elif "PGCE Academic Year" in term:
        return "TERM4"

    elif "Spring & Summer Teaching" in term:
        return "SEMESTER2"

    elif "Spring Teaching" in term:
        return "SPRING"

    elif "Summer Teaching" in term:
        return "SUMMER"

    elif "Summer Vacation" in term:
        return "TERM5"

    elif "U/G Academic Year" in term:
        return "TERM2"

    else:
        # If no matches found, return the same value that came in
        return incoming_term


# Start of main processing ##

# The 'accounts' we need to API-check in Canvas

canvas_accounts = [45, 49, 271]

# Show start and end time to help troubleshoot errors

start = datetime.now()
start_string = start.strftime("%d/%m/%Y %H:%M:%S")
logging.info("Start time: %s", start_string)

# Loop through the accounts: getting courses for each one from Canvas

for each_account in canvas_accounts:
    call_canvas_account(this_year, each_account)

end = datetime.now()
end_string = end.strftime("%d/%m/%Y %H:%M:%S")

logging.info("Start time: %s", start_string)
logging.info("End time: %s", end_string)
