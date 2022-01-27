from otree.api import *


doc = """
TThis is a standard 2-player trust game where the amount sent by player 1 gets
tripled. The trust game was first proposed by
<a href="http://econweb.ucsd.edu/~jandreon/Econ264/papers/Berg%20et%20al%20GEB%201995.pdf" target="_blank">
    Berg, Dickhaut, and McCabe (1995)
</a>.

This variation includes the possibility for players to rate each other with respect to their decision.
It is also implemented as a game with fixed roles over 10 rounds and random pairing in each round.
"""

author = 'Tim Bonowski'

class C(BaseConstants):

    NAME_IN_URL = 'trust_worthiness'
    PLAYERS_PER_GROUP = 2
    NUM_ROUNDS = 3
    # C does not have access to the session config,
    # (it is loaded when the server starts, rather than for each session)
    ENDOWMENT = cu(40)
    #MULTIPLICATION_FACTOR = 3

    LIKERT_CHOICES = [0, ENDOWMENT*0.25, ENDOWMENT*0.5, ENDOWMENT*0.75, ENDOWMENT]
    TRIPLED_CHOICES = [choice*3 for choice in LIKERT_CHOICES]
    CONFIDENCE_CHOICES = ['0%', '25%', '50%', '75%', '100%']

    #Roles
    A_ROLE = 'Teilnehmer A'
    B_ROLE = 'Teilnehmer B'

    #Rating choices
    PARTNER_FAIRNESS = ['Sehr unfair', 'Unfair', 'Weder fair noch unfair', 'Fair', 'Sehr fair']
    AMOUNT_APPROPRIATE = ['Viel zu klein', 'Zu klein', 'Genau angemessen', 'Zu groß', 'Viel zu groß']

    #Template


class Player(BasePlayer):
    multiplied_endowment = models.CurrencyField()
    prev_sent = models.CurrencyField()
    prev_sent_back = models.CurrencyField()
    prev_sent_back_available = models.CurrencyField()
    prev_role = models.StringField()
    partner_fairness = models.StringField(
        label=C.PARTNER_FAIRNESS,
        choices=C.PARTNER_FAIRNESS,
        widget=widgets.RadioSelectHorizontal)
    amount_appropriate = models.StringField(
        label=C.AMOUNT_APPROPRIATE,
        choices=C.AMOUNT_APPROPRIATE,
        widget=widgets.RadioSelectHorizontal)


class Group(BaseGroup):
    sent_amount = models.CurrencyField(
        doc="""Amount sent by P1""",
        label=C.LIKERT_CHOICES,
        min=0,
        max=C.ENDOWMENT,
        widget=widgets.RadioSelectHorizontal,
        choices=C.LIKERT_CHOICES
    )
    sent_back_amount = models.CurrencyField(
        doc="""Amount sent back by P2""",
        label='',
        min=cu(0)
    ) #try to do calculation and stuff
    feedback_treatment = models.BooleanField()


def creating_session(subsession): #this creates C.NUM_ROUNDS subsessions
    subsession.group_randomly(fixed_id_in_group=True) #group players randomly each round, keep id fixed

    import itertools
    feedback = itertools.cycle([True, False]) #this cycle between True ^ False forever, but not start until you hit 'next' function
    session = subsession.session
    session_treatment = session.config['feedback_treatment']
    if session_treatment.lower() == 'half':
        for group in subsession.get_groups():
            #print(group)
            group.feedback_treatment=next(feedback)
            #print(group.feedback_treatment)
    elif session_treatment.lower() == 'all':
        for group in subsession.get_groups():
            group.feedback_treatment=True
    else:
        for group in subsession.get_groups():
            group.feedback_treatment=False


def sent_back_amount_max(group): # {formfields}_max
    session = group.session
    max_amount = group.sent_amount * session.config['multiplication_factor'] + C.ENDOWMENT
    return cu(max_amount)

def set_payoffs(group): #self here ResultsWaitPage object
    session = group.session
    p1 = group.get_player_by_id(1)
    p2 = group.get_player_by_id(2)
    p1.payoff = C.ENDOWMENT - group.sent_amount + group.sent_back_amount
    p2.payoff = group.sent_amount * session.config['multiplication_factor'] - group.sent_back_amount + C.ENDOWMENT

def vars_for_admin_report(subsession):
    players = [player for player in subsession.get_players()]
    payoffs = [player.payoff for player in subsession.get_players()]
    return dict(payoffs=payoffs)

class Subsession(BaseSubsession):
    pass



### PAGES (TEMPLATES)

# oTree automatically passes the following objects to the template: player, group, subsession, participant, session, and C

class Send(Page):
    form_model = 'group'
    form_fields = ['sent_amount']

    @staticmethod
    def is_displayed(player):
        session = player.session
        return player.role == C.A_ROLE and C.NUM_ROUNDS <= session.config['num_rounds']

class SendBack(Page):
    form_model = 'group'
    form_fields = ['sent_back_amount']

    @staticmethod
    def is_displayed(player):
        session = player.session
        return player.role == C.B_ROLE and C.NUM_ROUNDS <= session.config['num_rounds']

    @staticmethod
    def vars_for_template(player):
        round_number = player.round_number
        group = player.group
        session = player.session
        return dict(
            multiplication_factor=session.config['multiplication_factor'],
            tripled_amount=group.sent_amount * session.config['multiplication_factor'],
            tripled_amount_int=int(group.sent_amount * session.config['multiplication_factor']),
            endowment_int=int(C.ENDOWMENT),
            a_remainder_int=int(C.ENDOWMENT-group.sent_amount)
        )

class WaitForP1(WaitPage):
    pass

class ResultsWaitPage(WaitPage):
    after_all_players_arrive = set_payoffs

class Feedback(Page):
    form_model = 'player'
    form_fields = ['partner_fairness', 'amount_appropriate']

    @staticmethod
    def is_displayed(player):
        session = player.session
        group = player.group
        return group.feedback_treatment and C.NUM_ROUNDS <= session.config['num_rounds']

    @staticmethod
    def vars_for_template(player):
        session = player.session
        return dict(
            multiplication_factor=session.config['multiplication_factor'],
        )

class ResultsWithFeedback(Page):
    @staticmethod
    def is_displayed(player):
        group = player.group
        session = player.session
        return group.feedback_treatment and C.NUM_ROUNDS <= session.config['num_rounds']

    @staticmethod
    def vars_for_template(player):
        session = player.session
        return dict(
            multiplication_factor=session.config['multiplication_factor'],
        )

class ResultsWaitPageFeedback(WaitPage):
    @staticmethod
    def after_all_players_arrive(group : Group):
        pass

    @staticmethod
    def is_displayed(player):
        group = player.group
        session = player.session
        return group.feedback_treatment and C.NUM_ROUNDS <= session.config['num_rounds']


class Results(Page):
    @staticmethod
    def vars_for_template(player):
        session = player.session
        group = player.group
        return dict(
            multiplication_factor=session.config['multiplication_factor'],
            tripled_amount=group.sent_amount * session.config['multiplication_factor'],
            feedback_treatment=group.feedback_treatment,
            fairness_feedback=player.get_others_in_group()[0].field_maybe_none('partner_fairness'),
            #fairness_feedback=player.get_others_in_group()[0].partner_fairness, #get_others_in_group returns a list of other players, here just need first and only one
            amount_appropriate_feedback=player.get_others_in_group()[0].field_maybe_none('amount_appropriate'),
        )

    @staticmethod
    def is_displayed(player):
        group = player.group
        session = player.session
        return C.NUM_ROUNDS <= session.config['num_rounds']



page_sequence = [Send,
                WaitForP1,
                SendBack,
                ResultsWaitPage,
                Feedback,
                ResultsWaitPageFeedback,
                Results]
