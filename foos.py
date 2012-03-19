"""
The Foosball App

"""
import json
import functools
from datetime import datetime

import bson
import bottle
import static
from minimongo import Model
from bottle import request, response, template, redirect

# Direct call to bottle's helper function to avoid false import errors
get = bottle.make_default_app_wrapper('get')
post = bottle.make_default_app_wrapper('post')

############
# Settings #
############

DATABASE = 'foos'
STATIC_MOUNT = '/static/'
API_MOUNT = '/api/v1/json'

##############
# Exceptions #
##############

class FoosException(Exception):
    """ Base Exception for all Foos Exceptions. """

##########
# Models #
##########

class BaseModelException(FoosException):
    """ Base exception for models. """

class ModelMixin(object):
    """ Common methods for minimongo :class:`Model` subclasses. """
    def store(self, key, value):
        """ Assigns directly to __dict__. """
        self.__dict__[key] = value

    @classmethod
    def mongo(cls):
        """ Wrapper around Model.collection. """
        return getattr(cls, 'collection')

    @classmethod
    def one(cls, query=None, _id=None):
        """ Wrapper around `find_one`. """
        if not _id and not query:
            raise ValueError("Get what now?")
        if _id:
            try:
                query = {'_id': bson.ObjectId(_id)}
            except bson.errors.InvalidId:
                return None
        return cls.mongo().find_one(query)

    @classmethod
    def find(cls, ids=None, cursor=False):
        """ Wrapper around `find`. """
        if not cursor:
            cursor = list
        else:
            cursor = lambda l: l
        if ids:
            try:
                ids = [bson.ObjectId(_) for _ in ids]
            except bson.errors.InvalidId:
                return []
            return cursor(cls.mongo().find({'_id': {'$in': ids}}))
        return cursor(cls.mongo().find())

    def delete(self):
        """ Wrapper around remove. """
        self.mongo().remove({'_id': self._id})

    def __repr__(self):
        return "%s(%s)" % (self.mongo().document_class.__name__,
                Model.__repr__(self))


class Player(ModelMixin, Model):
    """ Player model. """
    class Meta(object):
        """ Minimongo settings. """
        database = DATABASE

    def __init__(self, *args, **kwargs):
        self.name = 'Anonymous'
        self.games = 0
        self.wins = 0
        self.losses = 0
        self.incomplete = 0
        self.points_for = 0
        self.points_against = 0
        self.playtime = 0
        self.last_played = None
        super(Player, self).__init__(*args, **kwargs)

    @classmethod
    def fetch(cls, _id):
        """ Fetches a player by id.

            :param _id: Player._id to look up.
            :returns: Player if found.
            :raises: Player.Error if not found.

        """
        player = cls.one(_id=_id)
        if not player:
            raise cls.Error("Who're you looking for?")
        return player

    @classmethod
    def exists(cls, name):
        """ Check if a player already exists with the given name.

            :param str name: Player's name.
            :return: `bool`

        """
        return bool(cls.mongo().find({'name':name}).limit(1).count())

    @classmethod
    def valid_name(cls, name):
        """ Validates a name.

            :param str name: Name to validate.
            :raises: :exc:`Player.Error` if the name is None or empty.
            :raises: :exc:`Player.Error` if the name is too long.
            :raises: :exc:`Player.DupeError` if the name is not unique.

        """
        if not name:
            raise cls.Error("Tell me your name!")
        if cls.exists(name):
            raise cls.DupeError("That name is already taken!")
        if len(name) > 24:
            raise cls.Error("That name is way too long!")
        return True

    @classmethod
    def create(cls, name):
        """ Creates a new player. Calls :meth:`Player.valid_name` to check the
            name.

            :param str name: Player's name. Must be unique. Must be less than \
                 25 characters.
            :returns: Player instance created.

        """
        if cls.valid_name(name):
            return cls(name=name).save()

    def recent_games(self, count=3):
        """ Returns a `list` of recently played games for this player.

            :param int count: Number of games returned.

        """
        return list(Game.mongo().find(
                {'start': {'$ne': None}, 'players': str(self._id)},
                sort=[('start', -1)])
                        .limit(count))

    def rename(self, name):
        """ Renames the current player. Calls :exc:`Player.valid_name` to
            check the name.

            :param str name: New name.

        """
        if self.valid_name(name):
            self.name = name
            return self.save()

    @property
    def win_percent(self):
        """ Percentage of wins. """
        return round(1.0 * self.wins / self.games, 3)

    @property
    def url(self):
        """ Url for the player. """
        return '/player/%s' % self._id

    @property
    def stats(self):
        """ Returns the stat string. """
        return "(%s-%s-%s)" % (self.wins, self.losses, self.incomplete)

    class Error(BaseModelException):
        """ Base Error class for a Player. """
        pass

    class DupeError(Error):
        """ Error raised for a duplicate Player name. """
        pass


class Game(ModelMixin, Model):
    """ Game model. """
    class Meta(object):
        """ Minimongo settings. """
        database = DATABASE

    def __init__(self, *args, **kwargs):
        self.start = datetime.now()
        self.end = None
        self.players = []
        self.scores = None
        self.winner = None
        self.loser = None
        self.timeline = []
        self.incomplete = False
        super(Game, self).__init__(*args, **kwargs)

    @classmethod
    def fetch(cls, _id):
        """ Fetches a game by id.

            :param _id: Game._id to look up.
            :returns: Game if found.
            :raises: Game.Error if not found.

        """
        game = cls.one(_id=_id)
        if not game:
            raise cls.Error("Which game are you looking for?")
        return game

    @classmethod
    def begin(cls, players):
        """ Starts a game. """
        if not players:
            raise cls.Error("Nobody wants to play?")
        if len(players) == 1:
            raise cls.Error("Playing with yourself?")
        if len(players) > 2:
            raise cls.Error("Only two at a time!")
        if Player.find(players, cursor=True).count() != 2:
            raise cls.Error("One or more players aren't really players.")
        return cls(
                players=players,
                scores=dict(zip(players, (0, 0)))
                ).save()

    @classmethod
    def play(cls, game, scorer):
        """ Records a score. """
        if not scorer:
            raise cls.Error("Who scored?")
        game = game.fetch(game)
        if game.end:
            raise cls.GameOver("That game's already over.")
        if scorer == 'nobody':
            return
        if scorer not in game.players:
            raise cls.Error("Who did you say scored?")

        game.timeline.append([scorer, datetime.now()])
        game.scores[scorer] += 1

        if game.scores[scorer] < 5:
            # Play continues
            return game.save()

        # We have a winner
        game.end = datetime.now()
        playtime = (game.end - game.start).total_seconds()

        game.winner = scorer
        if game.players[0] == game.winner:
            game.loser = game.players[1]
        else:
            game.loser = game.players[0]

        loser = game.player(game.loser)
        loser.points_for += game.scores[game.loser]
        loser.points_against += game.scores[game.winner]
        loser.playtime += playtime
        loser.games += 1
        loser.losses += 1
        loser.last_played = game.end

        winner = game.player(game.winner)
        winner.points_for += game.scores[game.winner]
        winner.points_against += game.scores[game.loser]
        winner.playtime += playtime
        winner.games += 1
        winner.wins += 1
        winner.last_played = game.end

        game = game.save()
        loser.save()
        winner.save()

        return game

    @classmethod
    def abort(cls, game):
        """ Ends a game as incomplete. """
        game = Game.fetch(game)
        if game.end:
            raise cls.Error("Games can't end twice.")
        game.winner = game.players[0]
        game.loser = game.players[1]
        game.incomplete = True
        game.end = datetime.now()
        playtime = (game.end - game.start).total_seconds()

        for player in game.player1, game.player2:
            player.incomplete += 1
            player.playtime += playtime
            player.save()

        return game.save()

    @classmethod
    def recent_games(cls, count=5):
        """ Returns a list of recent games. """
        return list(cls.mongo().find(
                {'start': {'$ne': None}},
                sort=[('start', -1)])
                        .limit(count))

    def _load_players(self):
        """ Loads players into local storage. """
        if not self.players:
            return
        if getattr(self, '_player_lookup', None):
            return
        players = Player.find(self.players)
        if len(players) != len(self.players):
            # Add Anonymous players if someone got deleted
            while len(players) < len(self.players):
                players.append(Player())
        self.store('_player_lookup', dict((str(_['_id']), _) for _ in players))

    def player(self, _id):
        """ Return a player from an id. """
        if not self.players:
            return None
        self._load_players()
        player = self._player_lookup[_id]
        object.__setattr__(player, 'score', self.scores[_id])
        return player

    @property
    def player1(self):
        """ Get player one. """
        if self.end:
            return self.player(self.winner)
        return self.player(self.players[0])

    @property
    def player2(self):
        """ Get player two. """
        if self.end:
            return self.player(self.loser)
        return self.player(self.players[1])

    @property
    def url(self):
        """ Return the game url. """
        return '/game/%s' % self._id

    def offset(self, timestamp):
        """ Return the offset for a timestamp from the start of the game. """
        return timestamp - self.start

    class Error(BaseModelException):
        """ Base class for Game exceptions. """
        pass

    class GameOver(Error):
        """ Raised when a game is over. """
        pass


###########
# Helpers #
###########

def format_timedelta(stamp):
    """ Strip fractional seconds from a timestamp. """
    return str(stamp).split('.')[0]


def http_referer():
    """ Return the referrer to the current page. """
    return request.environ.get('HTTP_REFERER', '/?default')


def base_context():
    """ Create a base context dictionary. """
    return {
            'time': format_timedelta,
            'back': http_referer(),
            }


def error_template(*args, **kwargs):
    """ Renders an error template. """
    defaults = (('error', "Check back later, maybe I'll fix this."),)
    context = base_context()
    context.update(dict(defaults))
    if args:
        context.update(dict(zip((_[0] for _ in defaults), args)))
    context.update(kwargs)
    return template('error', context)


def error_json(*args, **kwargs):
    """ Returns an error message as JSON. """
    defaults = (('error', "Check back later, maybe I'll fix this."),)
    obj = {}
    obj.update(dict(defaults))
    if args:
        obj.update(dict(zip((_[0] for _ in defaults), args)))
    obj.update(kwargs)
    return json.dumps(obj)


def validate(data, validator):
    """ Validates a value. """
    try:
        return validator(data)
    except ValueError:
        raise FoosException("Invalid parameter.")


def as_json(obj, set_content_type=True):
    """ Wrapper around json.dumps. """
    if set_content_type:
        response.content_type = 'text'
        # response.content_type = 'text/json' # Causes downloads

    class _encoder(json.JSONEncoder):
        """ Encoder helper class for datetimes and ObjectIds."""
        def default(self, _obj):
            """ Handles datetime and ObjectId instances. """
            if hasattr(_obj, 'isoformat'):
                return _obj.isoformat()
            if isinstance(_obj, bson.ObjectId):
                return str(_obj)
            return json.JSONEncoder.default(self, _obj)

    return json.dumps(obj, cls=_encoder)


def catch_json(func):
    """ Catches FoosException errors and returns a pretty JSON message. """
    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        """ Wrapper function. """
        try:
            return func(*args, **kwargs)
        except FoosException, exc:
            return error_json(exc.message)

    return wrapped


def catch_template(func):
    """ Catches FoosException errors and returns a pretty error template. """
    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        """ Wrapper function. """
        try:
            return func(*args, **kwargs)
        except FoosException, exc:
            return error_template(exc.message)

    return wrapped


###############
# Controllers #
###############

# Homepage #
@get('/')
def index():
    """ Serves up the homepage. """
    context = base_context()
    context['players'] = Player.mongo().find().limit(1).count()
    return template('index', context)


# Games #
@get('/new_game')
def new_game():
    """ Selecting players for a new game. """
    players = Player.find()
    context = base_context()
    context['players'] = sorted(players, key=lambda p: p.last_played)
    return template('new_game', context)


@post('/new_game')
@catch_template
def start_game():
    """ Begins a game. """
    game = Game.begin(request.POST.dict.get('players', None))
    redirect('/game/%s' % game['_id'])


@get('/game/<game>')
@catch_template
def show_game(game):
    """ Display a game. """
    game = Game.fetch(game)
    context = base_context()
    context['game'] = game
    return template('game', context)


@post('/game/<game>')
@catch_template
def play_game(game):
    """ Record a score. """
    game = Game.play(game, request.POST.scorer)
    context = base_context()
    context['game'] = game
    return template('game', context)


@post('/game/<game>/end')
@catch_template
def end_game(game):
    """ End a game prematurely. """
    game = Game.abort(game)
    return redirect(game.url)


@get('/recent')
def show_recent_games():
    """ List recent games. """
    context = base_context()
    context['recent_games'] = Game.recent_games()
    return template('recent', context)


# Players #
@get('/new_player')
def new_player():
    """ New player. """
    return template('new_player', base_context())


@post('/new_player')
@catch_template
def create_player():
    """ Creates a new player. """
    Player.create(request.POST.name)
    return redirect('/')


@get('/player/<player>')
@catch_template
def show_player(player):
    """ Show an individual player. """
    player = Player.fetch(player)
    context = base_context()
    context['player'] = player
    context['recent_games'] = player.recent_games()
    return template('player', context)


@get('/players')
def show_players():
    """ List players. """
    players = Player.find()
    context = base_context()
    context['players'] = sorted(players, key=lambda p: -1000 * p.win_percent)
    return template('players', context)


#######
# API #
#######

# Push default app stack to create new JSON API app
bottle.default_app.push()


# Player API methods #
@get('/')
def api_description():
    """ Returns a description of API calls. """
    return as_json({
        'GET': {
            '/player/exists': {
                'param': 'name',
                'description': api_player_exists.__doc__,
                },
            '/player/valid_name': {
                'param': 'name',
                'description': api_valid_name.__doc__,
                },
            '/players': {
                'description': api_list_players.__doc__,
                },
            '/player/<player>': {
                'description': api_get_player.__doc__,
                },
            '/player/<player>/recent/<count>': {
                'description': api_player_recent_games.__doc__,
                },
            '/game/<game>': {
                'description': api_game.__doc__,
                },
            },
        'POST': {
            '/player/create': {
                'param': 'name',
                'description': api_create_player.__doc__,
                },
            '/player/<player>/rename': {
                'param': 'name',
                'description': api_player_rename.__doc__,
                },
            '/game/begin': {
                'params': ['player', 'player'],
                'description': api_game_begin.__doc__,
                },
            '/game/<game>/score/<scorer>': {
                'description': api_game_play.__doc__,
                },
            '/game/<game>/abort': {
                'description': api_game_abort.__doc__,
                },
            },
        })


@get('/player/exists')
def api_player_exists():
    """ Check if a player with a given name exists. """
    return as_json({'exists': Player.exists(request.GET.name)})


@get('/player/valid_name')
@catch_json
def api_valid_name():
    """ Validates a name. """
    return as_json({'valid': Player.valid_name(request.GET.name)})


@post('/player/create')
@catch_json
def api_create_player():
    """ Creates a player. """
    return as_json({'player': str(Player.create(request.POST.name))})


@post('/player/<player>/rename')
@catch_json
def api_player_rename(player):
    """ Renames a player. """
    return as_json(Player.fetch(player).rename(request.POST.name))


@get('/players')
def api_list_players():
    """ Lists all players. """
    players = Player.find()
    return as_json(players)


@get('/player/<player>')
@catch_json
def api_get_player(player):
    """ Returns a specific player. """
    player = Player.fetch(player)
    return as_json(player)


@get('/player/<player>/recent/<count>')
@catch_json
def api_player_recent_games(player, count):
    """ Returns `count` recent games for a player. """
    count = validate(count, int)
    player = Player.fetch(player)
    games = player.recent_games(int(count))
    return as_json(games)


# Game API methods #
@get('/game/<game>')
@catch_json
def api_game(game):
    """ Returns a game. """
    return as_json(Game.fetch(game))


@get('/games/<count>')
@catch_json
def api_recent_games(count):
    """ Returns `count` recent games played. """
    count = validate(count, int)
    return as_json(Game.recent_games(count))


@post('/game/begin')
@catch_json
def api_game_begin():
    """ Begins a new game. """
    return as_json(Game.begin(request.POST.dict.get('players', None)))


@post('/game/<game>/score/<scorer>')
@catch_json
def api_game_play(game, scorer):
    """ Records a game score. """
    return as_json(Game.play(game, scorer))


@post('/game/<game>/abort')
@catch_json
def api_game_abort(game):
    """ Aborts a game in progress. """
    return as_json(Game.abort(game))


# Retrieve JSON API app to mount
json_api_app = bottle.default_app.pop()


########
# WSGI #
########

def make_app(serve_static=True, json_api=True):
    """ Builds the WSGI app. """
    foos_app = bottle.default_app()

    if serve_static:
        foos_app.mount(STATIC_MOUNT, static.Cling('./static'))

    if json_api:
        foos_app.mount(API_MOUNT, json_api_app)

    return foos_app


app = make_app()


if __name__ == '__main__':
    bottle.run(app=app, host='0.0.0.0', port=8080, server='auto')
