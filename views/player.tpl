% rebase layout

<div id="topbar">
    <div id="leftnav">
        <a href="/"><img alt="home" src="/static/images/home.png" /></a>
        <a href="/players">Players</a>
    </div>
    <div id="title">{{player.name}}</div>
</div>
<div id="content">
    <span class="graytitle">Stats</a>
    <ul class="pageitem">
        % for stat in ('wins', 'losses', 'incomplete', 'points_for', 'points_against'):
        <li class="textbox">
            {{stat.replace('_',' ').capitalize()}}
            : {{player[stat]}}
        </li>
        % end
    </ul>
    % if recent_games:
    <span class="graytitle">Recent Games</a>
    <ul class="pageitem">
        % for game in recent_games:
        <li class="menu">
            <a href="{{game.url}}">
                <span class="name">
                {{game.player1.score}} - {{game.player2.score}}
                : {{game.player1.name}} vs. {{game.player2.name}}
                </span>
                <span class="arrow"></span>
            </a>
        </li>
        % end
    </ul>
    % end
</div>
