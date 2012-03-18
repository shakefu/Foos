% rebase layout

<div id="topbar">
    <div id="title">Foosball</div>
</div>
<div id="tributton">
	<div class="links">
        <a id="pressed" href="#">Home</a><a href="/players">Players</a><a href="/recent">Recent</a>
    </div>
</div>
<div id="content">
    <ul class="pageitem">
        % if players:
        <li class="menu">
            <a href="/new_game">
                <span class="name">New Game</span>
                <span class="arrow"></span>
            </a>
        </li>
        % end
        <li class="menu">
            <a href="/new_player">
                <span class="name">New Player</span>
                <span class="arrow"></span>
            </a>
        </li>
    </ul>
</div>
