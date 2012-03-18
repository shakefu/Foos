% rebase layout

<div id="topbar">
    <div id="leftnav">
        <a href="/"><img alt="home" src="/static/images/home.png" /></a>
        <a href="{{get('back', '/')}}">Back</a>
    </div>
    <div id="title">Ruh-roh!</div>
</div>
<div id="content">
    <span class="graytitle">A wild error has appeared!</a>
    <ul class="pageitem">
        <li class="menu">
            <a href="{{get('back', '/')}}">
                <span class="name">{{get('error', "I have no idea what happend.")}}</span>
                <span class="arrow"></span>
            </a>
        </li>
    </ul>
</div>
