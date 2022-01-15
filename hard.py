"""
Inside conditions.json, you will see a subset of UNSW courses mapped to their 
corresponding text conditions. We have slightly modified the text conditions
to make them simpler compared to their original versions.

Your task is to complete the is_unlocked function which helps students determine 
if their course can be taken or not. 

We will run our hidden tests on your submission and look at your success rate.
We will only test for courses inside conditions.json. We will also look over the 
code by eye.

NOTE: This challenge is EXTREMELY hard and we are not expecting anyone to pass all
our tests. In fact, we are not expecting many people to even attempt this.
For complete transparency, this is worth more than the easy challenge. 
A good solution is favourable but does not guarantee a spot in Projects because
we will also consider many other criteria.
"""
import json
import re

# NOTE: DO NOT EDIT conditions.json
with open("./conditions.json") as f:
    CONDITIONS = json.load(f)
    f.close()

def is_unlocked(courses_list, target_course):
    """Given a list of course codes a student has taken, return true if the target_course 
    can be unlocked by them.
    
    You do not have to do any error checking on the inputs and can assume that
    the target_course always exists inside conditions.json

    You can assume all courses are worth 6 units of credit
    """
    
    # If no courses have been taken, the only course that is unlocked is COMP1511.
    if courses_list == []:
        return bool(target_course == "COMP1511")

    # Remove unecessary characters and words and convert text to uppercase.
    cond = CONDITIONS[target_course].upper().replace(".", "")
    cond = " ".join([word for word in cond.split() if not word.startswith("PRE")])

    # If the condition is only one course, check if that course is in the course list.
    if cond in courses_list:
        return True
    
    # If course code is missing a prefix, append "COMP" to the course code 
    # and check if that course is in the course list.
    if re.findall(r"^\d{4}$", cond):
        return bool("COMP" + cond in courses_list)
  
    return check_conditions(courses_list, cond)



def check_conditions(courses_list, condition):
    """
    Check if the condition is satisfied given the courses list.
    """
    # Split the condition into a list.
    cond = split_condition(condition)
    
    # Determine the logic of the condition.
    logic = "AND" if any(word == "AND" for word in cond) else "OR"

    # Check the condition of any section that are in brackets.
    for word in [x for x in cond if has_bracket(x) and not "," in x]:
        result = check_conditions(courses_list, word[1:-1])
        if logic == "AND" and not result:
            return False
        elif logic == "OR" and result:
            return True
        cond = [x for x in cond if not has_bracket(x) or "," in x]

    # Check any uoc requirements.
    result = []
    for word in [x for x in cond if not (has_bracket(x) or is_special(x))]:
        check_uoc_requirements(cond, logic, word, courses_list, result)
    if logic == "AND" and not all(result):
        return False
    elif logic == "OR" and any(result):
        return True
    cond = [s for s in cond if is_special(s)]

    # Condition now only includes course code and logical operatorss
    if logic == "OR":
        return any(word in courses_list for word in cond)
    else:
        return all([word in courses_list or word == "AND" for word in cond])


def split_condition(condition):
    """
    Splits the condition into a list where course codes (e.g. "COMP521"), logic 
    words (i.e. "AND" and "OR") and condition strings (e.g. "COMPLETION OF 18
    UNITS OF CREDIT") are each elements of the list except when surrounded by
    more than one level of brackets, and in that case everything within the 
    first level of brackets is one element. 
    """
    cond = []
    depth = 0
    for word in condition.split():
        if cond == [] or (depth == 0 and can_split(cond, word)):
            cond.append(word)
            depth += word.count("(")
        else:
            cond[-1] += " " + word
            depth -= word.count(")")
    return cond


def check_uoc_requirements(cond, logic, word, courses_list, result):
    """
    Checks if the units of credit requirements are satisfied. 
    """
    uoc_req = int(re.findall(r"[0-9]+\sUNITS\sO(?:F|C)\sCREDIT", word)[0].split()[0])
    taken_courses = 0
    level = re.findall(r"\s[1-3]\s", word)
    if level != []:
        taken_courses = sum(int(c[4]) == int(level[0]) for c in courses_list)
    elif "COMP" in word:
        taken_courses = sum("COMP" in c for c in courses_list)
    elif "IN" in word:
        courses_req = cond[-1][1:-1].split(", ")
        taken_courses = sum(c in courses_list for c in courses_req)
    elif word != logic:
        taken_courses = len(courses_list)
    result.append(bool(taken_courses * 6 >= uoc_req))


def can_split(cond, word):
    """
    Word can be split into its own element if it satifies the following.
    """
    return bool((is_special(word) or is_special(cond[-1]) or "(" in word))

def is_special(word):
    """
    Word is special if it is a logic word or a course code.
    """
    return bool(re.findall(r"^[A-Z]{4}\d{4}$", word) or word == "AND" or word == "OR")

def has_bracket(word):
    """
    Determines if the word has brackets. 
    """
    return bool("(" in word or ")" in word)
    




    