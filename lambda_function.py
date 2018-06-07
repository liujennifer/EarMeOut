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


def get_continue_response():
    session_attributes = {}
    card_title = "Play again"
    speech_output = "What do you want to practice?"

    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "Please tell me what you want to practice"

    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def get_welcome_response():
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """

    session_attributes = {}
    card_title = "Welcome"
    speech_output = "Welcome to Ear Me Out, an ear trainig skill made by " \
                    "Oscar, Jennifer and Michelle. " \
                    "What would you like to practice?"

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
def check_interval(answer, interval_number: int):
    correct_interval = interval_names[interval_number]
    if correct_interval == str(answer):
        output = "Correct!"
    else:
        if answer is None:
            output = f'This is a {correct_interval}.'
        else:
            output = f'Incorrect! This is a {correct_interval}.'

    title = f'Answer: {correct_interval}, response: {answer}'

    return build_response({}, build_speechlet_response(title,
                          output, None, False))


def check_chord(answer: str, chord: int):
    correct_chord = chord_names[chord][0]
    if correct_chord == str(answer):
        output = "Correct!"
    else:
        if answer is None:
            output = f'This is a {correct_chord} chord'
        else:
            output = f'Incorrect! This is a {correct_chord} chord.'

    title = f'Answer: {correct_chord}, response: {answer}'

    return build_response({}, build_speechlet_response(title,
                          output, None, False))


def _note_to_url(note: int):
    return 'https://raw.githubusercontent.com/liujennifer/EarTrainer/master/' \
           'notes-mp3/' + str(note) + '.mp3'


def play_chord():
    base_note = random.randint(15, 49)
    chord = random.randint(0, len(chord_names) - 1)
    chord_notes = chord_names[chord][1]
    session_attributes = {"chord": chord}

    urls = [_note_to_url(base_note)]
    for interval in chord_notes:
        urls.append(_note_to_url(base_note + interval))

    audio_urls = "".join(["<audio src='" + url + "'/>" for url in urls])
    response = {
        'outputSpeech': {
            'type': 'SSML',
            'ssml': "<speak>What is this chord?" + audio_urls + "</speak>"
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'SSML',
                'text': "<speak>What is this chord?" + audio_urls +
                        "</speak>"
            }
        },
        'shouldEndSession': False
    }
    return build_response(session_attributes, response)


def play_interval():
    base_note = random.randint(15, 49)
    interval_num = random.randint(0, len(interval_names) - 1)
    session_attributes = {"interval_num": interval_num}

    url1 = 'https://raw.githubusercontent.com/liujennifer/EarTrainer/master/' \
           'notes-mp3/' + str(base_note) + '.mp3'
    url2 = 'https://raw.githubusercontent.com/liujennifer/EarTrainer/master/' \
           'notes-mp3/' + str(base_note + interval_num) + '.mp3'

    response = {
        'outputSpeech': {
            'type': 'SSML',
            'ssml': "<speak>What is this interval?"
                    "<audio src='" + url1 + "'/>"
                    "<audio src='" + url2 + "'/></speak>"
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'SSML',
                'text': "<speak>What is this interval?"
                        "<audio src='" + url1 + "'/>"
                        "<audio src='" + url2 + "'/></speak>"
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
    if intent_name == "PlayInterval":
        return play_interval()
    elif intent_name == "PlayChord":
        return play_chord()
    elif intent_name == "CheckAnswer":
        answer = intent['slots']['Answer']['value']
        if answer == "know":
            answer = None

        if session['attributes'].get('chord') is not None:
            chord = session['attributes']['chord']
            return check_chord(answer, chord)
        elif session['attributes'].get('interval_num') is not None:
            interval_number = session['attributes']['interval_num']
            return check_interval(answer, interval_number)
    elif intent_name == "Continue":
        return get_continue_response()
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


interval_names = {0: "unison", 1: "minor 2nd", 2: "major 2nd",
                  3: "minor 3rd", 4: "major 3rd", 5: "perfect 4th",
                  6: "tritone", 7: "perfect 5th", 8: "minor 6th",
                  9: "major 6th", 10: "minor 7th", 11: "major 7th",
                  12: "octave"}
chord_names = [["major", [4, 7]], ["minor", [3, 7]], ["major 7th", [4, 7, 11]],
                ["minor 7th", [3, 7, 10]], ["diminished 7th", [3, 6, 9]],
                ["dominant 7th", [4, 7, 10]], ["diminished", [3, 6]],
                ["augmented", [4, 8]]]
