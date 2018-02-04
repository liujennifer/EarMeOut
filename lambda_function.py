import random


# --------------- Helpers that build all of the responses ----------------------
def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': "SessionSpeechlet - " + title,
            'content': "SessionSpeechlet - " + output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }


def get_welcome_response():
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """

    session_attributes = {}
    card_title = "Welcome"
    speech_output = "Welcome to Ear Me Out. " \
                    "What do you want to practice?"

    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "Please tell me what you want to practice"

    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "Thank you for trying the Ear Me Out!" \
                    "Have a great day!"
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))


def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """

    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_welcome_response()


def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.

    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])


def on_session_started(session_started_request, session):
    """ Called when the session starts """
    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])


# ---------- Custom intents-----------------------------------------------------
def check_answer(answer, interval_number: int):
    correct_interval = interval_names[interval_number]
    if correct_interval == str(answer):
        output = "Correct!"
    else:
        output = f'Incorrect! This is a {correct_interval}. You said {answer}.'

    title = f'Answer: {correct_interval}, response: {answer}'

    return build_response({}, build_speechlet_response(title,
                          output, None, False))


def play_sound():
    interval_num = random.randint(0, len(interval_names))
    session_attributes = {"interval_num": interval_num}
    interval_url = interval_names[interval_num].replace(' ', '_')
    url = 'https://raw.githubusercontent.com/liujennifer/EarTrainer/master/' \
          'intervals/' + interval_url + '.mp3'

    response = {
        'outputSpeech': {
            'type': 'SSML',
            'ssml': "<speak>What is this interval?"
                    "<audio src='" + url + "'/></speak>"
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'SSML',
                'text': "<speak>What is this interval?"
                        "<audio src='" + url + "'/></speak>"
            }
        },
        'shouldEndSession': False
    }
    return build_response(session_attributes, response)


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "PlaySound":
        return play_sound()
    elif intent_name == "CheckAnswer":
        answer = intent['slots']['IntervalName']['value']
        interval_number = session['attributes']['interval_num']
        return check_answer(answer, interval_number)
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == \
            "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")


def lambda_handler(event, context):
    print("event.session.application.applicationId=" + event['session']
          ['application']['applicationId'])

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])
    # KEEP IT AS IF
    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])


# interval_names = {0: "major 6th", 1: "minor 3rd", 2: "perfect 4th",
#                   3: "unison", 4: "tritone"}
interval_names = {0: "unison", 1: "minor 2nd", 2: "major 2nd",
                  3: "minor 3rd", 4: "major 3rd", 5: "perfect 4th",
                  6: "tritone", 7: "perfect 5th", 8: "minor 6th",
                  9: "major 6th", 10: "minor 7th", 11: "major 7th",
                  12: "octave"}
