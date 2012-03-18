% rebase layout

<div id="topbar">
    <div id="leftnav">
        <a href="/"><img alt="home" src="/static/images/home.png" /></a>
    </div>
    <div id="title">New Player</div>
</div>
<div id="content">
    <form id="newplayer" name="newplayer" method="POST">
        <ul class="pageitem">
            <li class="bigfield">
                <input type="text" name="name" placeholder="Player Name" />
            </li>
        </ul>
        <a href="javascript:newplayer.submit()" class="button">Create</a>
    </form>
</div>
