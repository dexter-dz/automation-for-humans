import re
import json

# This is language of the english statements that can be written.
patterns = [
    # Regex for click actions.
    # click on "Select" -> ('click', None, None, None, 'Select')
    # click on 2nd "Remove" -> ('click', '2nd ', '2', 'nd', 'Remove')
    "(click)\s*on\s+((\d*)(st|nd|rd|th)\s+)?\"([^\"]+)\"(\s+\"(.+)\")?",

    # Regex for hover actions.
    "(hover)\s*on\s+((\d*)(st|nd|rd|th)\s+)?\"([^\"]+)\"(\s+\"(.+)\")?",

    # Regex for type actions.
    "(type)\s*\"(.+)\"\s*in\s*\"([^\"]+)\"(\s+\"(.+)\")?",

    # Regex for URL. We are not validating the url itself
    "(url)\s*\"(.+)\"",

    # Regex for wait.
    "(wait)\s*for\s*\"(.+)\"",

    # Regex for execjs.
    "(execjs)\s+\"(.+)\"",

    # Regex for assert actions.
    # "(assert)\s*\"(.+)\"\s*in\s*\"([^\"]+)\"(\s+\"(.+)\"){1}",
]

# The tyope of the command will always be index 0
TYPE_INDEX = 0

# These are the indices of the click groups
CLICK_TYPE_INDEX = 0
CLICK_INDEX_INDEX = 2
CLICK_ARGS_INDEX = 4
CLICK_ATTRIBUTE_INDEX = 6

# These are the indices of the type groups
TYPE_TYPE_INDEX = 0
TYPE_ARGS_WHAT_INDEX = 1
TYPE_ARGS_WHERE_INDEX = 2
TYPE_ATTRIBUTE_INDEX = 4

# These are the indices of the url groups
URL_WHERE_INDEX = 1

# These are the indices of the wait groups
WAIT_TIME_INDEX = 1

EXECJS_WHAT_INDEX = 1

def parse_english_to_json(input_file, output_file) :
    with  open(input_file, "r") as english_text :
        program = {}
        commands = []
        for line in english_text :
            did_match = False
            for pattern in patterns :
                p = re.compile(pattern)
                matches = p.match(line)
                if matches != None :
                    did_match = True
                    groups = matches.groups()
                    print (groups)
                    command_value = {}
                    # Find out the type of the command
                    if groups[TYPE_INDEX] == "click" or groups[TYPE_INDEX] == "hover" :
                        command_value["type"] = groups[TYPE_INDEX]
                        command_value["args"] = [groups[CLICK_ARGS_INDEX]]
                        if groups[CLICK_INDEX_INDEX] != None :
                            command_value["index"] = groups[CLICK_INDEX_INDEX]
                        if groups[CLICK_ATTRIBUTE_INDEX] != None :
                            command_value["attribute"] = groups[CLICK_ATTRIBUTE_INDEX]
                        commands.append(command_value)
                    elif groups[TYPE_INDEX] == "type" :
                        command_value["type"] = "type"
                        command_value["args"] = [
                            groups[TYPE_ARGS_WHAT_INDEX],
                            groups[TYPE_ARGS_WHERE_INDEX]
                        ]
                        if groups[TYPE_ATTRIBUTE_INDEX] != None :
                            command_value["attribute"] = groups[TYPE_ATTRIBUTE_INDEX]
                        commands.append(command_value)
                    elif groups[TYPE_INDEX] == "url" :
                        program["url"] = groups[URL_WHERE_INDEX]
                    elif groups[TYPE_INDEX] == "wait" :
                        command_value["type"] = "wait"
                        command_value["time"] = int(groups[WAIT_TIME_INDEX])
                        commands.append(command_value)
                    elif groups[TYPE_INDEX] == "execjs" :
                        command_value["type"] = "execjs"
                        command_value["js"] = groups[EXECJS_WHAT_INDEX]
                        commands.append(command_value)
                    else :
                        raise Exception("Unknown command type")
            if did_match == False :
                raise Exception("Invalid syntax in command")
        program["commands"] = commands
        if "url" not in program :
            raise Exception("URL not given for automation")
        with open (output_file, "w") as json_file :
            row = json.dump(program, json_file, indent=4)