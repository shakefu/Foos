% rebase layout

<div id="topbar">
    <div id="leftnav">
        <a href="/"><img alt="home" src="/static/images/home.png" /></a>
    </div>
    <div id="title">Players</div>
</div>
<div id="tributton">
	<div class="links">
        <a href="/">Home</a><a id="pressed" href="#">Players</a><a href="/recent">Recent</a>
    </div>
</div>
<div id="content">
    % if players:
    <ul class="pageitem">
        % for player in players:
        <li class="menu">
            <a href="{{player.url}}">
                <span class="name">{{player.name}} {{player.stats}}</span>
                <span class="arrow"></span>
            </a>
        </li>
        % end
    </ul>
    % else:
    <span class="graytitle">No Players</span>
    % end
</div>
