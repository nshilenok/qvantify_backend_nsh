from flask import g

function = [{
    	"type": "function",
    	"function":{
			"name": "interview_topic_over",
			"description": "Call it when you consider the information provided by the user to be sufficient according to the system prompt earlier.",
			"parameters": {
				"type": "object",
				"properties": {
					"status": 
						{"type": "string", "enum": ["done"],
						"description": "Topic status, where done means that all information have been provided by the user."}
                }}}
                }]

def switchTopic(response):
	response_message = response.choices[0].message
	if response_message.tool_calls:
		available_functions = {"interview_topic_over": g.th.forceSwitchTopic,}
		function_name = response_message.tool_calls[0].function.name
		function_to_call = available_functions[function_name]
		function_response = function_to_call()
		return function_response