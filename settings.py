from os import environ


SESSION_CONFIGS = [
    dict(
        name='trust_worthiness',
        display_name='Trust Worthiness',
        app_sequence=['trust_worthiness', 'payment_info'],
        num_demo_participants=4,
        num_rounds=5,
        multiplication_factor=5,
        feedback_treatment='half',
        doc='''
        Edit the 'feedback_treatment' parameter to choose which treatment to play. Default is 'half': Half of the subsession participants
        will play with the feedback treatment. Type 'All' to make all of them play with the feedback treatment, and 'None' so that there is
        no feedback treatment.
        '''
     )
]

# if you set a property in SESSION_CONFIG_DEFAULTS, it will be inherited by all configs
# in SESSION_CONFIGS, except those that explicitly override it.
# the session config can be accessed from methods in your apps as self.session.config,
# e.g. self.session.config['participation_fee']

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=1.00, participation_fee=0.00, doc=""
)

PARTICIPANT_FIELDS = []
SESSION_FIELDS = []

# ISO-639 code
# for example: de, fr, ja, ko, zh-hans
LANGUAGE_CODE = 'en'

# e.g. EUR, GBP, CNY, JPY
REAL_WORLD_CURRENCY_CODE = 'EUR'
USE_POINTS = True

ROOMS = [
    dict(
        name='econ101',
        display_name='Econ 101 class',
        participant_label_file='_rooms/econ101.txt',
    ),
    dict(name='live_demo', display_name='Room for live demo (no participant labels)'),
    dict(name='trust_worthiness', display_name='Trust Worthiness'),
]

ADMIN_USERNAME = 'admin'
# for security, best to set admin password in an environment variable
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')

DEMO_PAGE_INTRO_HTML = """
Here are some oTree games.
"""


SECRET_KEY = '2798189647344'

INSTALLED_APPS = ['otree']
