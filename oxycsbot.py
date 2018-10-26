#!/usr/bin/env python3
"""A tag-based chatbot framework."""

import re
from collections import Counter
import random
import time


class ChatBot:
    """A tag-based chatbot framework

    This class is not meant to be instantiated. Instead, it provides helper
    functions that subclasses could use to create a tag-based chatbot. There
    are two main components to a chatbot:

    * A set of STATES to determine the context of a message.
    * A set of TAGS that match on words in the message.

    Subclasses must implement two methods for every state (except the
    default): the `on_enter_*` method and the `respond_from_*` method. For
    example, if there is a state called "confirm_delete", there should be two
    methods `on_enter_confirm_delete` and `respond_from_confirm_delete`.

    * `on_enter_*()` is what the chatbot should say when it enters a state.
        This method takes no arguments, and returns a string that is the
        chatbot's response. For example, a bot might enter the "confirm_delete"
        state after a message to delete a reservation, and the
        `on_enter_confirm_delete` might return "Are you sure you want to
        delete?".

    * `respond_from_*()` determines which state the chatbot should enter next.
        It takes two arguments: a string `message`, and a dictionary `tags`
        which counts the number of times each tag appears in the message. This
        function should always return with calls to either `go_to_state` or
        `finish`.

    The `go_to_state` method automatically calls the related `on_enter_*`
    method before setting the state of the chatbot. The `finish` function calls
    a `finish_*` function before setting the state of the chatbot to the
    default state.

    The TAGS class variable is a dictionary whose keys are words/phrases and
    whose values are (list of) tags for that word/phrase. If the words/phrases
    match a message, these tags are provided to the `respond_from_*` methods.
    """

    STATES = []
    TAGS = {}

    def __init__(self, default_state):
        """Initialize a Chatbot.

        Arguments:
            default_state (str): The starting state of the agent.
        """
        if default_state not in self.STATES:
            print(' '.join([
                f'WARNING:',
                f'The default state {default_state} is listed as a state.',
                f'Perhaps you mean {self.STATES[0]}?',
            ]))
        self.default_state = default_state
        self.state = self.default_state
        self.tags = {}
        self._check_states()
        self._check_tags()

    def _check_states(self):
        """Check the STATES to make sure that relevant functions are defined."""
        for state in self.STATES:
            prefixes = []
            if state != self.default_state:
                prefixes.append('on_enter')
            prefixes.append('respond_from')
            for prefix in prefixes:
                if not hasattr(self, f'{prefix}_{state}'):
                    print(' '.join([
                        f'WARNING:',
                        f'State "{state}" is defined',
                        f'but has no response function self.{prefix}_{state}',
                    ]))

    def _check_tags(self):
        """Check the TAGS to make sure that it has the correct format."""
        for phrase in self.TAGS:
            tags = self.TAGS[phrase]
            if isinstance(tags, str):
                self.TAGS[phrase] = [tags]
            tags = self.TAGS[phrase]
            assert isinstance(tags, (tuple, list)), ' '.join([
                'ERROR:',
                'Expected tags for {phrase} to be str or List[str]',
                f'but got {tags.__class__.__name__}',
            ])

    def go_to_state(self, state):
        """Set the chatbot's state after responding appropriately.

        Arguments:
            state (str): The state to go to.

        Returns:
            str: The response of the chatbot.
        """
        assert state in self.STATES, f'ERROR: state "{state}" is not defined'
        assert state != self.default_state, ' '.join([
            'WARNING:',
            f"do not call `go_to_state` on the default state {self.default_state};",
            f'use `finish` instead',
        ])
        on_enter_method = getattr(self, f'on_enter_{state}')
        response = on_enter_method()
        self.state = state
        return response

    def chat(self):
        """Start a chat with the chatbot."""
        try:
            message = input('> ')
            while message.lower() not in ('exit', 'quit'):
                print()
                print(f'{self.__class__.__name__}: {self.respond(message)}')
                print()
                message = input('> ')
        except (EOFError, KeyboardInterrupt):
            print()
            exit()

    def respond(self, message):
        """Respond to a message.

        Arguments:
            message (str): The message from the user.

        Returns:
            str: The response of the chatbot.
        """
        respond_method = getattr(self, f'respond_from_{self.state}')
        return respond_method(message, self._get_tags(message))

    def finish(self, manner):
        """Set the chatbot back to the default state

        This function will call the appropriate `finish_*` method.

        Arguments:
            manner (str): The type of exit from the flow.

        Returns:
            str: The response of the chatbot.
        """
        response = getattr(self, f'finish_{manner}')()
        self.state = self.default_state
        return response

    def _get_tags(self, message):
        """Find all tagged words/phrases in a message.

        Arguments:
            message (str): The message from the user.

        Returns:
            Dict[str, int]: A count of each tag found in the message.
        """
        counter = Counter()
        msg = message.lower()
        for phrase, tags in self.TAGS.items():
            if re.search(r'\b' + phrase.lower() + r'\b', msg):
                counter.update(tags)
        return counter


class OxyCSBot(ChatBot):
    """A simple chatbot that directs students to office hours of CS professors."""

    STATES = [
        'waiting',
        'introduction',
        #'greeting',
        #'good_transition',
        'bad_transition',
        'sciac',
        #'good_sciac',
        'bad_sciac',
        'yes_coach',
        'no_coach',
        #'sciac_matchup',
        #'sciac_response',
        'sport',
        'team_sport',
        'good_team',
        'good_team1',
        'almost_end_rec_coach',
        'no_team',
        'yes_team'
    ]

    TAGS = {
        # greeting
        'hello': 'greeting',

        # intent
        'office hours': 'office-hours',
        'help': 'office-hours',

        # loneliness sources
        'no friends': 'no_friends',

        # professors
        'kathryn': 'kathryn',
        'leonard': 'kathryn',
        'justin': 'justin',
        'li': 'justin',
        'jeff': 'jeff',
        'miller': 'jeff',
        'celia': 'celia',
        'hsing-hau': 'hsing-hau',

        # generic
        'thanks': 'thanks',
        'okay': 'success',
        'bye': 'success',
        'yes': 'yes',
        'yep': 'yes',
        'no': 'no',
        'nope': 'no',
        'awful': 'no',
        'good': 'yes',
        'great': 'yes',
        'bad': 'no',

        # comfort
        'homesickness': 'family',

        # suggest
        'social': 'social',
        'soccer': ['sports', 'soccer'],
        'football': ['sports', 'football'],
        'sports': 'sports',
        'baseball': ['sports', 'baseball'],

        # other help needed
        'die': 'failure',
        'depression': 'failure',
        'schizophrenia': 'failure',
    }

    TEAM_SPORTS = {
        'soccer',
        'basketball',
        'football',
        'baseball',
        'lacrose',
        'water polo',
        'cross country',
        'softball',
        'volleyball',
    }

    INDIVIDUAL_SPORTS = [
        'track and field',
        'golf',
        'swimming',
        'tennis'
    ]

    RESPONSES = {
        'introductions' : [
        # If you\'re feeling isolated at Oxy, I can help you with that.'
        'Hello, I\'m Santi.\nI help college student athletes better transition to college sports at Oxy\n',
        'Hello, I\'m Santi.\n',
        ],
        'greetings': [
            'How has your transition been?',
            'How has your transition in sports been?',
        ],
        'good transition': [
            ':grinning: Good to hear! How\'s your team doing in the SCIAC conference this year?',
        ],
        'bad transition': [
            ':cry: I\'m sorry you feel that way. Have you told your coach?',
        ],
        'good sciac': [
            'Do you think you all can keep the momentum?',
            'Do you think y\'all can keep the momentum?',
            'Do you think you all can keep up the momentum?',
            'Do you think y\'all can keep up the momentum?',
            'Do you think you all can keep the momentum going?',
            'Do you think y\'all can keep the momentum going?',
        ],
        'bad sciac': [
            'Have you voiced your concern',
        ],
        'yes coach': [
            'That\'s what I\'d do too!',
        ],
        'no coach': [
            'Okay, have you brought that up to your team?',
            'Okay, have you brought that up to your teammates?',
        ],
        'sciac matchup': [
            'Who\'s your next SCIAC matchup?',
        ],
        'sciac response': [
            'That\'ll be a good one. Good luck and IO TRIUMPHE!',
        ],
        'sport': [
            'What sport do you play?', #fixme
        ],
        'team': [
            'That\'s the best sport! How\'s your team chemistry?',
        ],
        'good team': [
            'Tell me more!',
        ],
        'good team1': [
            'That\'s perfect! Your team chemistry is extremely significant to your transition. '
            'I would recommend to continue talking to your coach and hear your team\'s transition journey.'
        ],
        'yes team': [
            'What kind of captain do you have - junior or senior?'
            'What kind of captain do you have on your team - junior or senior?'
        ],
        'no team': [
            'I would recommend talking to your teammates. That might help with your transition. '
                'Do you have any of your teammates\' contact information?',
        ],
        'captain': [
            'no'
        ],
        'confused': [

        ],
    }

    COACHES = {
        "Jack Stanebnfeldt": ["men's and women's water polo", "head coach", "(415) 328-0685", "stabenfeldt@oxy.edu"],
        "Sean Grab": ["men's and women's water polo", "head assistant coach", "", ""],
        "Nanea Fujiyama": ["men's and women's water polo", "centers coach", "", ""],
        "Christian Fischer": ["men's and women's water polo", "goalie coach and recruiting coordinator", "", ""],
        "Gilbert Millanes": ["men's and women's water polo", "volunteer assistant coach", "", ""],
        "Heather Collins": ["women's volleyball", "head coach", "(323) 259-2702", "hcollins@oxy.edu"]
    }

    def __init__(self):
        """Initialize the OxyCSBot.

        The `professor` member variable stores whether the target
        professor has been identified.
        """
        super().__init__(default_state='waiting')
        self.professor = None
        # fixme get rid of extra variables and make/rename relevant ones
        self.current = None


    def get_office_hours(self, professor):
        """Find the office hours of a professor.

        Arguments:
            professor (str): The professor of interest.

        Returns:
            str: The office hours of that professor.
        """
        office_hours = {
            'celia': 'F 12-1:45pm; F 2:45-4:00pm',
            'hsing-hau': 'T 1-2:30pm; Th 10:30am-noon',
            'jeff': 'unknown',
            'justin': 'T 1-2pm; W noon-1pm; F 3-4pm',
            'kathryn': 'MWF 4-5pm',
        }
        return office_hours[professor]

    def get_office(self, professor):
        """Find the office of a professor.

        Arguments:
            professor (str): The professor of interest.

        Returns:
            str: The office of that professor.
        """
        office = {
            'celia': 'Swan 216',
            'hsing-hau': 'Swan 302',
            'jeff': 'Fowler 321',
            'justin': 'Swan B102',
            'kathryn': 'Swan B101',
        }
        return office[professor]



    def go_to_help(self, tags):
        if 'failure' in tags:
            return self.go_to_state('other_help1')


    def route_interests(self, tags):
        for interest in self.INTERESTS:
            if (interest in tags) and (interest not in self.interests):
                self.interests.append(interest) # keeping track of interests
        if 'social' in self.interests:
            return self.go_to_state('social') # go to social
        if len(self.interests) > 0:
            return self.go_to_state(self.interests[random.randint(0, len(self.interests) - 1)]) # go to state with that interest
        return self.go_to_state('other')


    def route_interest_answer(self,tags):
        """
        Set the chatbot's state after getting a response from a yes/no question

        Arguments:
            state (str): The state to go to.

        Returns:
            state (function): The state to go to based off of the response
        """
        if 'no' in tags: # if they definitely don't want to talk about the current topic, go to a different interest
            return self.route_interests(tags)
        # else go back to the same state; might need to change this
        go = self.current
        self.current = None
        return self.go_to_state(go)
        # just in case we need this function later because of chatbot logic
        # if 'yes' in tags and self.current:
        #     go = self.current
        #     self.current = None
        #     return self.go_to_state(go)

    def get_random_state_response(self, state):
        """
                Set the chatbot's state after getting a response from a yes/no question

                Arguments:
                    state (str): The state to go to.

                Returns:
                    state (function): The state to go to based off of the response
        """
        return self.RESPONSES[state][random.randint(0, len(self.RESPONSES[state]) - 1)]


    # "waiting" state functions

    def respond_from_waiting(self, message, tags):

        if 'office-hours' in tags: # change tags to be possible sources of loneliness fixme
            for professor in self.PROFESSORS: # loneliness
                if professor in tags:
                    self.professor = professor
                    return self.go_to_state('specific_faculty') # loneliness
            return self.go_to_state('unknown_loneliness')
        elif 'greeting' in tags:
            self.greeting = True # might not need fixme
            return self.go_to_state('introduction')
        elif 'thanks' in tags:
            return self.finish('thanks')
        else:
            return self.finish('confused')

    def on_enter_introduction(self):
        return ':shocked_face_with_exploding_head:' + self.get_random_state_response('introductions') + self.get_random_state_response('greetings')

    def respond_from_introduction(self, message, tags):
        if 'no' in tags:
            return self.go_to_state('bad_transition')
        else:
            return self.go_to_state('sciac')


# fixme, respond from functions are filled in with a filler
    def on_enter_sciac(self):
        return self.get_random_state_response('good transition')

    def respond_from_sciac(self, message, tags):
        if 'no' in tags:
            return self.go_to_state('bad_transition')
        else:
            return self.go_to_state('sport')

    def on_enter_bad_transition(self):
        return self.get_random_state_response('bad transition')

    def respond_from_bad_transition(self, message, tags):
        if 'no' in tags:
            return self.go_to_state('no_coach')
        else:
            return self.go_to_state('yes_coach')

    def on_enter_yes_coach(self):
        return self.get_random_state_response('yes coach')

    def respond_from_yes_coach(self, message, tags):
        return self.finish('thanks')

    def on_enter_no_coach(self):
        return self.get_random_state_response('no coach')

    def respond_from_no_coach(self, message, tags):
        return self.finish('thanks')

    def on_enter_bad_sciac(self):
        return self.get_random_state_response('bad sciac')

    def respond_from_bad_sciac(self, message, tags):
        if 'no' in tags:
            return self.on_enter_bad_transition()
        else:
            pass

    def on_enter_sport(self):
        return 'some question about teams'

    def respond_from_sport(self, message, tags):
        for sport in self.INDIVIDUAL_SPORTS:
            if sport in tags:
                return self.go_to_state('individual_sport')
        return self.go_to_state('team_sport')

    def on_enter_team_sport(self):
        return self.get_random_state_response('sport')

    def respond_from_team_sport(self, message, tags):
        if 'no' in tags:
            return 'something'
        return self.go_to_state('good_team')

    def on_enter_good_team(self):
        return self.get_random_state_response('good team')

    def respond_from_good_team(self, message, tags):
        return self.go_to_state('good_team1')

    def on_enter_good_team1(self):
        return self.get_random_state_response('good team1')

    def respond_from_good_team1(self, message, tags):
        if 'no' in tags:
            return self.go_to_state('no_coach') #fixme think it's the wrong state
        return self.finish('woo')
    #
    # def on_enter_almost_end_rec_coach(self):
    #     return self.get_random_state_response('almost end rec coach')
    #
    # def respond_from_almost_end_rec_coach(self, message, tags):
    #     if 'no' in tags:
    #         return self.go_to_state('no_coach') #fixme think it's the wrong state
    #     return self.finish('woo')

    def on_enter_no_team(self):
        return self.get_random_state_response('no team')

    def respond_from_no_team(self, message, tags):
        return self.finish('woo')

    def on_enter_yes_team(self):
        return 'woo'

    def respond_from_yes_team(self):
        return self.finish('woo')




    # "finish" functions

    def finish_confused(self):
        return "Sorry, I'm just a simple Santi that understands a few things. I can help you if you're feeling a bit isolated though!"

    def finish_location(self):
        return f"{self.professor.capitalize()}'s office is in {self.get_office(self.professor)}"

    def finish_success(self):
        return 'Great, let me know if you need anything else!'

    def finish_fail(self):
        return "I've tried my best but I still don't understand. Maybe try asking other students?"

    def finish_thanks(self):
        return "You're welcome!"

    def finish_woo(self):
        return self.get_random_state_response('woo')



if __name__ == '__main__':
    OxyCSBot().chat()
