% rebase layout

<div id="topbar">
    <div id="leftnav">
        <a href="/"><img alt="home" src="/static/images/home.png" /></a>
    </div>
    <div id="title">New Game</div>
</div>
<div id="content">
    % if not players:
    <span class="graytitle">No Players</span>
    % else:
    <span class="graytitle">Choose Players</span>
    <form id="newgame" name="newgame" method="POST">
        <ul class="pageitem">
            % for player in players:
            <li class="checkbox">
                <label>
                    <span class="name">{{player.name}} {{player.stats}}</span>
                    <input type="checkbox" name="players" value="{{player._id}}" />
                </label>
            </li>
            % end
        </ul>
        <a href="javascript:newgame.submit()" class="button">Start Game</a>
    </form>
    % end
</div>
