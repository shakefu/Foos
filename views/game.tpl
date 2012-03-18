% rebase layout

<div id="topbar">
    <div id="leftnav">
        <a href="/"><img alt="home" src="/static/images/home.png" /></a>
        % if game.end:
        <a href="/recent">Recent</a>
        % end
    </div>
    <div id="title">{{"Game" if game.end else "Play Foosball!"}}</div>
</div>
<div id="content">
    % if game.incomplete:
    <span class="graytitle">Game Abandoned</span>
    % end
    % if game.end:
    <ul class="pageitem">
        <li class="menu">
            <a href="{{game.player1.url}}">
                <span class="name">
                    {{game.player1.score}} : {{game.player1.name}}
                </span>
                <span class="arrow"></span>
            </a>
        </li>
        <li class="menu">
            <a href="{{game.player2.url}}">
                <span class="name">
                    {{game.player2.score}} : {{game.player2.name}}
                </span>
                <span class="arrow"></span>
            </a>
        </li>
    </ul>
    % else:
    <form id="player1score" name="player1score" method="POST">
        <input type="hidden" name="scorer" value={{game.player1._id}} />
        <a href="javascript:player1score.submit()" class="button">
            {{game.player1.name}} : {{game.player1.score}}
        </a>
    </form>
    <div style="height: 75px"></div>
    <form id="player2score" name="player2score" method="POST">
        <input type="hidden" name="scorer" value={{game.player2._id}} />
        <a href="javascript:player2score.submit()" class="button">
            {{game.player2.name}} : {{game.player2.score}}
        </a>
    </form>
    % end
    % if game.timeline:
    <span class="graytitle">Scoring</span>
    <ul class="pageitem">
        % if game.end:
        <li class="textbox">
            Duration : {{time(game.end - game.start)}}.
        </li>
        % end
        % for score in game.timeline:
        <li class="textbox">
            {{time(game.offset(score[1]))}} : {{game.player(score[0]).name}}
        </li>
        % end
    </ul>
    % else:
    <div style="height: 75px"></div>
    % end
    % if not game.end:
    <form id="endgame" name="endgame" method="POST" action="/game/{{game._id}}/end">
        <a href="javascript:endgame.submit()" class="button">End Game</a>
    </form>
    % end
</div>
