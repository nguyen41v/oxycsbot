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
        'yes_coach',
        'no_coach',
        'sciac_matchup',
        'sciac_response',
        'sport',
        'team_sport',
        'good_team',
        'good_team1',
        #'almost_end_rec_coach', # fixme?
        'no_team',
        'yes_team',
        'captain',
        'leave',
        'individual_sport',
        'connections',
        'soccer',
        'ms_mentor',
        'ws_mentor',
        'unrecognized_mentor',
        'ask_number',
        'give_number',
        'other_teammates',
        'medium_rare',
        'amber',
        'confused',
        'sad_life',
        'team_chemistry',
        'talk_to_team',
        'advice',
        'other_connections'
    ]

    TAGS = {
        # greeting
        'hello': 'greeting',
        'hi' : 'greeting',
        'howdy': 'greeting',
        'wassup' : 'greeting',
        'hey':'greeting',



        # intent
        'help': 'help',



        # generic
        'thanks': 'thanks',
        'ty': 'thanks',
        'thank': 'thanks',
        'bye': 'thanks',
        'sure thing': 'thanks',
        'team': 'team',
        'teammates': 'team',
        'teammate': 'team',
        'teamate': 'team',
        'teamates': 'team',
        'coach': 'coach',
        'yes': 'yes',
        'ye': 'yes',
        'yea': 'yes',
        'yeah': 'yes',
        'ya': 'yes',
        'yep': 'yes',
        'no': 'no',
        'nope': 'no',
        'awful': 'no',
        'good': 'yes',
        'great': 'yes',
        'well': 'yes',
        'won': 'yes',
        'win': 'yes',
        'sure': 'yes',
        'need': 'yes',
        'fine': 'medium_rare',
        'okay': ['medium_rare', 'thanks', 'yes'],
        'ok': ['medium_rare', 'thanks', 'yes'],
        'guess': 'medium_rare',
        'not bad': 'medium_rare',
        'is there anything': 'question',
        'what': 'question',
        'what else': 'question',
        'anything else': 'question',
        'uh': 'what_the',
        'oh': 'what_the',
        'hm': 'what_the',
        'um': 'what_the',
        'eh': 'what_the',
        'lost': 'no',
        'lose': 'no',
        'bad': 'no',
        'heavens forbid': 'no',
        'difficult': 'no',
        'terrible': 'no',
        'nah': 'no',
        'rough': 'no',
        'not really': 'no',
        'hard': 'no',
        'tough': 'no',
        'wasn\'t' : 'no',
        'not that well': 'no',
        'not that good': 'no',
        'not great': 'no',
        'not good': 'no',
        'not well': 'no',
        'not yet': 'no',
        'not that great': 'no',
        'transferring': ['leave', 'no'],
        'transfer': ['leave', 'no'],
        'leave': ['leave', 'no'],
        'quit': ['leave', 'no'],
        'isn\'t': 'no',
        'doesn\'t: no'
        'don\'t': 'no',
        'havent': 'no',
        'haven\'t': 'no',
        'have not': 'no',
        'scared': 'no',
        'scare': 'no',
        'dont': 'no',
        'wasnt': 'no',
        'isnt': 'no',
        'doesnt': 'no',
        'hell': 'no',
        'shit': 'no',
        'fucking': 'no',
        'fking': 'no',
        'fuck': 'no',
        'sht': 'no',
        'rude': ['no', 'sad_life'],
        'hate': ['no', 'sad_life'],
        'unfriendly': 'sad_life',
        'not nice': 'sad_life',
        'bullying': 'sad_life',
        'bullied': 'sad_life',
        'bully': 'sad_life',
        'bullies': 'sad_life',
        'bullys': 'sad_life',
        'ignore': 'sad_life',
        'mean': 'sad_life',
        'forgot': 'leave_loop',
        'move on': 'leave_loop',
        'forget': 'leave_loop',
        'remember': 'leave_loop',
        'recall': 'leave_loop',
        'memory': 'leave_loop',

        # sports
        'soccer': 'soccer',
        'basketball': 'basketball',
        'football': 'football',
        'futball': 'football',
        'baseball': 'baseball',
        'lacrose': 'lacrose',
        'water polo': 'water polo',
        'cross country': 'cross country',
        'xc': 'cross country',
        'softball': 'softball',
        'volleyball': 'volleyball',
        'track and field': 'track and field',
        'track': 'track and field',
        'golf': 'golf',
        'golfing': 'golf',
        'swimming': 'swimming',
        'swim': 'swimming',
        'tennis': 'tennis',

        # women's soccer mentors
        'sydney': 'sydney tomlinson',
        'syd': 'sydney tomlinson',
        'tomlinson': 'sydney tomlinson',
        'emily': 'emily leonard',
        'leonard': 'emily leonard',
        'em': 'emily leonard',
        'nicole': 'nicole castro',
        'castro': 'nicole castro',
        'nic': 'nicole castro',
        'katherine': 'katherine kim',
        'kat': 'katherine kim',
        'kim': 'katherine kim',
        'sophia': 'sophia vallas',
        'soph': 'sophia vallas',
        'vallas': 'sophia vallas',
        'elleni': 'elleni bekele',
        'bekele': 'elleni bekele',
        'karla': 'karla lopez',
        'lopez': 'karla lopez',
        'berkli': 'berkli manigo',
        'maningo': 'berkli manigo',
        'berk': 'berkli manigo',
        'meredith': 'meredith cook',
        'cook': 'meredith cook',
        'mer': 'meredith cook',
        'devoney': 'devoney amberg',
        'amberg': 'devoney amberg',
        'dev': 'devoney amberg',

        # men's soccer mentors
        'luke': 'luke hass',
        'haas': 'luke hass',
        'scott': 'scott drazan',
        'drazan': 'scott drazan',
        'scottie': 'scott drazan',
        'dra': 'scott drazan',
        'austin': 'austin lee',
        'lee': 'austin lee',
        'ryan': 'ryan wilson',
        'wilson': 'ryan wilson',
        'ariel': 'ariel rosso',
        'rosso': 'ariel rosso',
        'ari': 'ariel rosso',
        'ben': 'ben simon',
        'simon': 'ben simon',
        'benjamin': 'ben simon',
        'liam': 'liam walsh',
        'walsh': 'liam walsh',
        'ethan': 'ethan glass',
        'glass': 'ethan glass',
        'glasser': 'ethan glass',
        'glassinho': 'ethan glass',
        'conal': 'conal dennison',
        'dennison': 'conal dennison',
        'connie': 'conal dennison',
        'matt': 'matthew labrie',
        'matthew': 'matthew labrie',
        'teo': 'matthew labrie',
        'labrie': 'matthew labrie',
        'matty': 'matthew labrie',
        'matt labrie': 'matthew labrie',
        'david': 'david paine',
        'dave': 'david paine',
        'dm': 'david paine',
        'dmp': 'david paine',
        'paine': 'david paine',
        'riley': 'riley mccabe',
        'mccabe': 'riley mccabe',
        'miles': 'miles robertson',
        'robertson': 'miles robertson',

    }



    def __init__(self):
        """Initialize the OxyCSBot.

        The `professor` member variable stores whether the target
        professor has been identified.
        """
        super().__init__(default_state='waiting')

        self.mentor = None
        self.gmentor = None
        self.start = 0
        self.umentor = 0
        # fixme get rid of extra variables and make/rename relevant ones
        self.current = None
        self.positive = None
        self.negative = None
        self.medium_rare = None

        self.TEAM_SPORTS = {
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

        self.INDIVIDUAL_SPORTS = [
            'track and field',
            'golf',
            'swimming',
            'tennis'
        ]

        self.WOMENS_SOCCER = [
            'sydney tomlinson',
            'emily leonard',
            'nicole castro',
            'katherine kim',
            'sophia vallas',
            'elleni bekele',
            'karla lopez',
            'berkli manigo',
            'meredith cook',
            'devoney amberg',
        ]

        self.MENS_SOCCER = {
            'luke hass',
            'scott drazan',
            'austin lee',
            'ryan wilson',
            'ariel rosso',
            'ben simon',
            'liam walsh',
            'ethan glass',
            'conal dennison',
            'matthew labrie',
            'david paine',
            'riley mccabe',
            'miles robertson',
        }

        self.SOCCER_MENTOR_NUMBERS = {
            'devoney amberg': '(923) 477 - 6575',
            'luke haas': '(215) 422-2283',
            'scott drazan': '(240) 472-1131',
            'austin lee': '(760) 705-6663',
            'ryan wilson': '(801) 889 - 8478',
            'ariel rosso': '(559) 361-5246',
            'ben simon': '(650) 223 - 1486',
            'liam walsh': '(202) 465-6304',
            'ethan glass': '(847) 644 - 2827',
            'conal dennison': '(626) 890 - 8844',
            'matthew labrie': '(925) 588 - 4049',
            'david paine': '(310) 977 - 6205',
            'riley mccabe': '(781) 697 - 8005',
            'miles robertson': '(914) 486 - 1653',
            'sydney tomlinson': '(412) 978 - 2839',
            'emily leonard': '(324) 879 - 9009',
            'nicole castro': '(425) 368 - 8154',
            'katherine kim': '(818) 661 - 8360',
            'sophia vallas': '(775) 544 - 4956',
            'elleni bekele': '(214) 478 - 3442',
            'karla lopez': '(124) 879 - 9932',
            'berkli maningo': '(230) 456 - 8799',
            'meredith cook': '(213) 354 - 0094',
        }

        self.RESPONSES = {
            'introductions': [
                'Hello, I\'m Santi.\nI help college student athletes better transition to college sports at Oxy.\n',
            ],
            'greetings': [
                'How has your transition been?',
                'How has your transition in sports been?',
            ],
            'good_transition': [
                ':grinning: Good to hear! How\'s your team doing in the SCIAC conference this year?',
                'I’m glad to hear that you are having a good time! '
                    'The transition is not always easy, so it’s fantastic that you’re off to a strong start. '
                    'How’s the team doing?',
            ],
            'bad_transition': [
                ':cry: I\'m sorry you feel that way. Have you told your coach?',
                ':cry: Have you told your coach?',
                ':cry: Have you voiced your concern?',
                ':cry: I\'m sorry you feel that way. Have you voiced your concern?',
                'I\'m sorry you feel that way. Have you told your coach?',
                'Have you told your coach?',
                'Have you voiced your concern?',
                'I\'m sorry you feel that way. Have you voiced your concern?',
            ],
            'good_sciac': [
                'Do you think you all can keep the momentum?',
                'Do you think y\'all can keep the momentum?',
                'Do you think you all can keep up the momentum?',
                'Do you think y\'all can keep up the momentum?',
                'Do you think you all can keep the momentum going?',
                'Do you think y\'all can keep the momentum going?',
            ],
            'yes_coach': [
                'That\'s what I\'d do too!',
            ],
            'no_coach': [
                'Okay, have you brought that up to your team?',
                'Okay, have you brought that up to your teammates?',
            ],
            'sciac_matchup': [
                'Who\'s your next SCIAC matchup?',
            ],
            'sciac_response': [
                'That\'ll be a good one. Good luck and IO TRIUMPHE!',
            ],
            'sport': [
                'What sport do you play?',  # fixme
            ],
            'team_sport': [
                'That\'s the best sport! How\'s your team chemistry?',
            ],
            'good_team': [
                'Tell me more!',
            ],
            'good_team1': [
                'That\'s perfect! Your team chemistry is extremely significant to your transition. '
                'I would recommend to continue talking to your coach and hear your team\'s transition journey.'
            ],
            'yes_team': [
                'Okay, that\'s good to know. What kind of captain do you have - junior or senior?',
                'Okay, that\'s good to know. What kind of captain do you have on your team - junior or senior?',
                # 'What kind of captain do you have on your team - junior or senior?',
                # 'What kind of captain do you have - junior or senior?',
            ],
            'no_team': [
                'I would recommend talking to your teammates. That might help with your transition.'
                ' Do you have any of your teammates\' contact information?',
                'I would recommend talking to your teammates. That might help with your transition.',
                'Students get homesick so getting close with your team or building a social group helps a ton.',
                # 'If you don\'t agree, tell me a little more about what you\'ve thought about doing as a solution.',
            ],
            'captain': [
                'That\'s important. A senior captain is always someone who should be approachable on your team. '
                    'Similarly, a junior captain should be approachable as well and may even have more insight into what you\'re dealing with since they\'re younger. '
                    'Either way, I would approach your captains.',
            ],
            'confused': [
                'Sorry, I\'m only understands a few things. I can help you in transitioning though!',
                'I don\'t know what\'s going on. I can help you in transitioning though!'
            ],
            'help': [
                'What can I help you with?'
            ],
            'woo': [
                'No problem, feel free to reach out to me in the future.',
                'You\'re welcome, feel free to reach out to me in the future.',
                'Glad I could be of help. Feel free to reach out to me in the future.',
                'No problem! Feel free to reach out to me in the future.',
                'You\'re welcome! Feel free to reach out to me in the future.',
                'Glad I could be of help! Feel free to reach out to me in the future.',
            ],
            'leave': [
                'Hmm . . . I recommend you wait a semester or year and see how things play out. '
                    'If things get worse, maybe then consult with your family, friends, team, or perhaps Emmons.',
                'Hmm . . . I recommend you wait a semester or year and see how things play out. '
                    'If things get worse, maybe then consult with your family, friends, team, and perhaps Emmons.',
                'Hmm . . . I recommend you wait a semester or year and see how things play out. '
                    'If things get worse, then maybe consult with your family, friends, team, or perhaps Emmons.',
                'Hmm . . . I recommend you wait a semester or year and see how things play out. '
                    'If things get worse, then maybe consult with your family, friends, team, and perhaps Emmons.',
                'Hmm . . . I recommend you wait a semester or year and see how things play out. '
                    'If things get worse, then try consulting with your family, friends, team, and perhaps Emmons.',
                'Hmm . . . I recommend you wait a semester or year and see how things play out. '
                    'If things get worse, then try consulting with your family, friends, team, or perhaps Emmons.',
            ],
            'individual_sport': [
                'That\'s a a great sport!'
                '   Even thought it\'s an individual sport, I would recommend talking to some of the other athletes.'
                '   How does that sound?',
            ],
            'connections': [
                'Great, I think you should focus on making some connections. We\'ll see how this plays out.'
            ],
            'other_connections': [
                'I think you should focus on making some connections. We\'ll see how this plays out.',
            ],
            'advice': [
                'Hmm . . . my advice would be to wait for one semester and see how things play out.'
            ],
            'soccer': [
                'Oh! Y\'all have a mentor program on your team. '
                'It\'s very unique and it\'s on the men\'s and women\'s teams. '
                'Who\'s your mentor?',
                'Oh! You have a mentor program on your team. '
                'It\'s very unique and it\'s on the men\'s and women\'s teams. '
                'Who\'s your mentor?',
            ],
            'ms_mentor': [
                ' is awesome. He was a first year at one point in time and I can bet you he had some of the same thoughts '
                'and challenges as you. How do you feel about talking to him about your transition issues?',
                ' is amazing. He was a first year at one point in time and I can bet you he had some of the same thoughts '
                'and challenges as you. How do you feel about talking to him about your transition issues?',
                ' is awesome. He was a first year at one point in time and I can bet you he had some of the same thoughts '
                'and challenges as you. What do you think of talking to him about your transition issues?',
                ' is a great person to approach. He was a first-year at one point in time and I can bet you he had some '
                'of the same thoughts and challenges. Text him!',
            ],
            'ws_mentor': [
                ' is a great person to approach. She was a first-year at one point in time and I can bet you she had some '
                'of the same thoughts and challenges. Text her!',
                ' is awesome. She was a first year at one point in time and I can bet you she had some of the same thoughts '
                'and challenges as you. How do you feel about talking to her about your transition issues?',
                ' is amazing. She was a first year at one point in time and I can bet you she had some of the same thoughts '
                'and challenges as you. How do you feel about talking to her about your transition issues?',
                ' is awesome. She was a first year at one point in time and I can bet you she had some of the same thoughts '
                'and challenges as you. What do you think of talking to her about your transition issues?',
            ],
            'amber': [
                'I wouldn\'t worry too much. Just compete and let\'s see how the rest of the season goes.'
            ],
            'sad_life': [
                'Sorry to hear that. I\'m not certified to handle that kind of situation. However, I recommend that you talk to someone outside of your team such as the athletics director.'
            ],
            'medium_rare': [
                'That\'s good to know. How\'s your team doing in the SCIAC conference this year?',
                'The transition is not always easy, but it gets better over time. '
                    'How’s the team doing?',
            ],
            'unrecognized_mentor': [
                'I haven\'t heard of someone by that name in the soccer team. Are you spelling their name correctly? What\'s their first or last name?.'
            ],
            'more_unrecognized': [
                'Sorry, I still don\'t know who you\'re referring to. Could you type their name again?'
            ],
            'team_chemistry': [
                'How\'s your team chemistry?',
            ],
            'success': [
                'Great, let me know if you need anything else!'
            ],
            'talk_to_team': [
                'Try getting some of your teammates\' contact information. They can especially help you transition considering that they may be going through the same experiences as you are.'
            ],
            'coach': [
                'I recommend that you talk to your coach regardless of your situation just to get a better feel of how you should approach your transition.'
            ],
            'fail': [
                'Sorry I couldn\'t help you.'
            ],
            'ask_user': [
                'Is there anything else I can help you with?'
            ],
            'other_teammates': [
                'What about talking to your other teammates.'
            ],
        }

        self.COACHES = {
            "Jack Stanebnfeldt": ["men's and women's water polo", "head coach", "(415) 328-0685", "stabenfeldt@oxy.edu"],
            "Sean Grab": ["men's and women's water polo", "head assistant coach", "", ""],
            "Nanea Fujiyama": ["men's and women's water polo", "centers coach", "", ""],
            "Christian Fischer": ["men's and women's water polo", "goalie coach and recruiting coordinator", "", ""],
            "Gilbert Millanes": ["men's and women's water polo", "volunteer assistant coach", "", ""],
            "Heather Collins": ["women's volleyball", "head coach", "(323) 259-2702", "hcollins@oxy.edu"]
        }

    def what_the(self, current, positive, negative, medium_rare = None):
        self.current = current
        self.positive = positive
        self.negative = negative
        self.medium_rare = medium_rare
        return self.go_to_state('confused')

    def get_random_state_response(self, state):
        """
                Set the chatbot's state after getting a response from a yes/no question

                Arguments:
                    state (str): The state to go to.

                Returns:
                    state (function): The state to go to based off of the response
        """
        return self.RESPONSES[state][random.randint(0, len(self.RESPONSES[state]) - 1)]

    def get_possesive(self):
        if self.gmentor == 'm':
            return 'his'
        return 'her'

    def get_pronoun(self):
        if self.gmentor == 'm':
            return 'he'
        return 'she'

    def get_directive(self):
        if self.gmentor == 'm':
            return 'him'
        return 'her'


    # "waiting" state functions

    def respond_from_waiting(self, message, tags):
        self.mentor = None
        self.gmentor = None
        # add additional if states to route user based off of what they said
        # if 'teammates' in tags: go to team state
        if 'leave' in tags:
            return self.go_to_state('leave')
        if 'question' in tags:
            return self.finish('coach')
        if 'coach' in tags:
            return self.go_to_state('sad_life')
        if 'team' in tags or 'sad_life' in tags:
            return self.go_to_state('bad_transition')
        if 'greeting' in tags:
            return self.go_to_state('introduction')
        if 'thanks' in tags or (('no' in tags) and (self.start > 0)):
            return self.finish('woo')
        if 'yes' in tags:
            return self.finish('success')
        if ('no' in tags) and (self.start == 0):
            return self.finish('fail')
        return self.finish('confused')

    def on_enter_introduction(self):
        self.start = 0
        return ':shocked_face_with_exploding_head:' + self.get_random_state_response('introductions') + self.get_random_state_response('greetings')

    def respond_from_introduction(self, message, tags):
        if 'no' in tags:
            return self.go_to_state('bad_transition')
        if 'yes' in tags:
            return self.go_to_state('sciac')
        return self.go_to_state('medium_rare') # make new state fixme

    def on_enter_medium_rare(self):
        return self.get_random_state_response('medium_rare')

    def respond_from_medium_rare(self, message, tags):
        if 'yes' in tags and 'no' in tags:
            return self.go_to_state('amber')
        if 'no' in tags:
            return self.go_to_state('bad_transition')
        return self.go_to_state('sport')

    def on_enter_sciac(self):
        return self.get_random_state_response('good_transition')

    def respond_from_sciac(self, message, tags):
        if 'yes' in tags and 'no' in tags:
            return self.go_to_state('amber')
        if 'no' in tags:
            return self.go_to_state('bad_transition')
        return self.go_to_state('sport')

    def on_enter_sciac_matchup(self):
        return self.get_random_state_response('sciac_matchup')

    def respond_from_sciac_matchup(self, message, tags):
        return self.go_to_state('sciac_response') # fixme

    def on_enter_sciac_response(self):
        return self.get_random_state_response('sciac_response')

    def respond_from_sciac_response(self, message, tags):
        if 'thanks' in tags:
            return self.finish('woo')
        return self.finish('ask_user')

    def on_enter_amber(self):
        return self.get_random_state_response('amber') + ' ' + self.get_random_state_response('sciac_matchup')

    def respond_from_amber(self, message, tags):
        return self.go_to_state('sciac_response') # fixme; make same as sciac_matchup fix


    def on_enter_bad_transition(self):
        return self.get_random_state_response('bad_transition')

    def respond_from_bad_transition(self, message, tags):
        if 'no' in tags:
            return self.go_to_state('no_coach')
        if 'yes' in tags:
            return self.go_to_state('yes_coach')
        if 'what_the' in tags:
            return self.what_the('bad_transition', 'yes_coach', 'no_coach')
        return self.go_to_state('yes_coach')

    def on_enter_confused(self):
        return self.get_random_state_response('confused')

    def respond_from_confused(self, message, tags):
        if 'no' in tags:
            return self.go_to_state(self.negative)
        if 'yes' in tags:
            return self.go_to_state(self.positive)
        if 'medium_rare' in tags and self.medium_rare:
            return self.go_to_state(self.medium_rare)
        return self.go_to_state('confused')

    def on_enter_yes_coach(self):
        return self.get_random_state_response('yes_coach') + ' ' + self.get_random_state_response('sport')

    def respond_from_yes_coach(self, message, tags):
        if 'soccer' in tags:
            return self.go_to_state('soccer')
        for sport in self.INDIVIDUAL_SPORTS:
            if sport in tags:
                return self.go_to_state('individual_sport')
        return self.go_to_state('team_sport')

    def on_enter_no_coach(self):
        return self.get_random_state_response('no_coach')

    def respond_from_no_coach(self, message, tags):
        return self.go_to_state('no_team')

    def on_enter_sport(self):
        return self.get_random_state_response('sport')

    def respond_from_sport(self, message, tags):
        if 'soccer' in tags:
            return self.go_to_state('soccer')
        for sport in self.INDIVIDUAL_SPORTS:
            if sport in tags:
                return self.go_to_state('individual_sport')
        return self.go_to_state('team_sport')

    def on_enter_soccer(self):
        return self.get_random_state_response('soccer')

    def respond_from_soccer(self, message, tags):
        for mmentor in self.MENS_SOCCER:
            if mmentor in tags:
                self.mentor = mmentor
                self.gmentor = 'm'
                return self.go_to_state('ms_mentor')
        for fmentor in self.WOMENS_SOCCER:
            if fmentor in tags:
                self.mentor = fmentor
                self.gmentor = 'f'
                return self.go_to_state('ws_mentor')
        return self.go_to_state('unrecognized_mentor')

    def on_enter_ms_mentor(self):
        return self.mentor[:self.mentor.rfind(' ')].capitalize() + self.get_random_state_response('ms_mentor')

    def respond_from_ms_mentor(self, message, tags):
        if 'yes' in tags:
            return self.go_to_state('ask_number')
        return self.go_to_state('other_teammates')

    def on_enter_ws_mentor(self):
        return self.mentor + self.get_random_state_response('ws_mentor')

    def respond_from_ws_mentor(self, message, tags):
        if 'yes' in tags:
            return self.go_to_state('ask_number')
        return self.go_to_state('other_teammates')

    def on_enter_unrecognized_mentor(self):
        self.umentor += 1
        if self.umentor == 1:
            return self.get_random_state_response('unrecognized_mentor')
        return self.get_random_state_response('more_unrecognized')

    def respond_from_unrecognized_mentor(self, message, tags):
        for mentor in self.WOMENS_SOCCER:
            if mentor in tags:
                self.mentor = mentor
                self.gmentor = 'f'
                return self.go_to_state('ws_mentor')
        for mentor in self.MENS_SOCCER:
            if mentor in tags:
                self.mentor = mentor
                self.gmentor = 'm'
                return self.go_to_state('ms_mentor')
        if 'no' in tags or 'leave_loop' in tags:
            return self.go_to_state('team_chemistry')
        return self.go_to_state('unrecognized_mentor')

    def on_enter_team_chemistry(self):
        return self.get_random_state_response('team_chemistry')

    def respond_from_team_chemistry(self, message, tags):
        if 'no' in tags:
            return self.go_to_state('yes_team')
        if 'sad_life' in tags:
            return self.go_to_state('sad_life')
        return self.go_to_state('good_team')

    def on_enter_ask_number(self):
        return f"Would you like {self.get_possesive()} number?"

    def respond_from_ask_number(self, message, tags):
        if 'yes' in tags:
            return self.go_to_state('give_number')
        return self.finish('help')


    def on_enter_give_number(self):
        return f"{self.get_possesive().capitalize()} number is {self.SOCCER_MENTOR_NUMBERS[self.mentor]}."

    def respond_from_give_number(self, message, tags):
        if 'thanks' in tags:
            return self.finish('woo')
        return self.finish('ask_user')

    def on_enter_other_teammates(self):
        return self.get_random_state_response('other_teammates')

    def respond_from_other_teammates(self, message, tags):
        if 'thanks' in tags:
            return self.finish('woo')
        return self.finish('ask_user')

    def on_enter_team_sport(self):
        return self.get_random_state_response('team_sport')

    def respond_from_team_sport(self, message, tags):
        if 'no' in tags:
            return self.go_to_state('yes_team')
        if 'sad_life' in tags:
            return self.go_to_state('sad_life')
        return self.go_to_state('good_team')

    def on_enter_sad_life(self):
        return self.get_random_state_response('bad_transition')

    def respond_from_sad_life(self, message, tags):
        if 'no' in tags:
            return self.go_to_state('no_coach')
        if 'yes' in tags:
            return self.go_to_state('yes_coach')
        if 'what_the' in tags:
            return self.what_the('bad_transition', 'yes_coach', 'no_coach')
        return self.go_to_state('yes_coach')

    def on_enter_individual_sport(self):
        return self.get_random_state_response('individual_sport')

    def respond_from_individual_sport(self, message, tags):
        if 'leave' in tags:
            return self.go_to_state('advice')
        if 'yes' in tags:
            return self.go_to_state('connections')
        return self.go_to_state('other_connections')

    def on_enter_connections(self):
        return self.get_random_state_response('connections')

    def respond_from_connections(self, message, tags):
        if 'thanks' in tags:
            return self.finish('woo')
        return self.finish('ask_user')

    def on_enter_other_connections(self):
        return self.get_random_state_response('other_connections')

    def respond_from_other_connections(self, message, tags):
        if 'thanks' in tags:
            return self.finish('woo')
        return self.finish('ask_user')

    def on_enter_advice(self):
        return self.get_random_state_response('advice')

    def respond_from_advice(self, message, tags):
        if 'no' in tags:
            return self.go_to_state('yes_team')
        if 'thanks' in tags:
            return self.finish('woo')
        return self.finish('ask_user')

    def on_enter_good_team(self):
        return self.get_random_state_response('good_team')

    def respond_from_good_team(self, message, tags):
        return self.go_to_state('good_team1')

    def on_enter_good_team1(self):
        return self.get_random_state_response('good_team1')

    def respond_from_good_team1(self, message, tags):
        if 'no' in tags:
            return self.go_to_state('yes_team') #fixme think it's the wrong state
        if 'thanks' in tags:
            return self.finish('woo')
        return self.finish('ask_user')
    #
    # def on_enter_almost_end_rec_coach(self):
    #     return self.get_random_state_response('almost end rec coach')
    #
    # def respond_from_almost_end_rec_coach(self, message, tags):
    #     if 'no' in tags:
    #         return self.go_to_state('no_coach') #fixme think it's the wrong state
    #     return self.finish('woo')

    def on_enter_no_team(self):
        time.sleep(1)
        return self.get_random_state_response('no_team')

    def respond_from_no_team(self, message, tags):
        if 'leave' in tags:
            return self.go_to_state('leave')
        return self.go_to_state('talk_to_team')

    def on_enter_talk_to_team(self):
        return self.get_random_state_response('talk_to_team')

    def respond_from_talk_to_team(self, message, tags):
        if 'thanks' in tags:
            return self.finish('woo')
        return self.finish('ask_user')

    def on_enter_yes_team(self):
        return self.get_random_state_response('yes_team')

    def respond_from_yes_team(self, message ,tags):
        return self.go_to_state('captain')

    def on_enter_captain(self):
        time.sleep(0.5)
        return self.get_random_state_response('captain')

    def respond_from_captain(self, message, tags):
        if 'thanks' in tags:
            return self.finish('woo')
        return self.finish('ask_user')


    def on_enter_leave(self):
        return self.get_random_state_response('leave')

    def respond_from_leave(self, message, tags):
        if 'thanks' in tags:
            return self.finish('woo')
        return self.finish('ask_user')

    # "finish" functions

    def finish_confused(self):
        return self.get_random_state_response('confused')

    def finish_location(self):
        return f"{self.professor.capitalize()}'s office is in {self.get_office(self.professor)}"

    def finish_success(self):
        return self.get_random_state_response('success')

    def finish_help(self):
        self.start += 1
        return self.get_random_state_response('help')

    def finish_fail(self):
        return self.get_random_state_response('fail')

    def finish_woo(self):
        self.start += 1
        return self.get_random_state_response('woo')

    def finish_coach(self):
        return self.get_random_state_response('coach')

    def finish_ask_user(self):
        self.start += 1
        return self.get_random_state_response('ask_user')



if __name__ == '__main__':
    OxyCSBot().chat()
