% rebase layout

<div id="topbar">
    <div id="leftnav">
        <a href="/"><img alt="home" src="/static/images/home.png" /></a>
    </div>
    <div id="title">Recent</div>
</div>
<div id="tributton">
	<div class="links">
        <a href="/">Home</a><a href="/players">Players</a><a id="pressed" href="#">Recent</a>
    </div>
</div>
<div id="content">
    % if recent_games:
    <ul class="pageitem">
        % for game in recent_games:
        <li class="menu">
            <a href="{{game.url}}">
                <span class="name">
                    {{game.player1.score}} - {{game.player2.score}} :
                    {{!game.player1.name}} vs. {{!game.player2.name}}
                    % if game.incomplete:
                    <span class="gray">(Abandoned)</span>
                    % end
                    % if not game.end:
                    <span class="gray">(In Progress)</span>
                    % end
                </span>
            </a>
        </li>
        % end
    </ul>
    % else:
    <span class="graytitle">No Recent Games</span>
    % end
</div>
