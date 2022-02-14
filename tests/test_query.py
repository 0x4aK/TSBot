import pytest

from tsbot import query


def test_add_options():
    q = query.TSQuery("channellist")
    assert q._options == []  # type: ignore

    q.option("topic", "flags", "voice")
    assert q._options == ["topic", "flags", "voice"]  # type: ignore


def test_add_params():
    q = query.TSQuery("channelmove")
    assert q._parameters == {}  # type: ignore

    q.params(cid=16, cpid=1, order=0)
    assert q._parameters == {"cid": "16", "cpid": "1", "order": "0"}  # type: ignore


def test_app_param_blocks():
    q = query.TSQuery("permidgetbyname")
    assert q._parameter_blocks == []  # type: ignore

    q.param_block(permsid="b_serverinstance_help_view")
    q.param_block(permsid="b_serverinstance_info_view")

    assert {"permsid": "b_serverinstance_help_view"} in q._parameter_blocks  # type: ignore
    assert {"permsid": "b_serverinstance_info_view"} in q._parameter_blocks  # type: ignore


@pytest.mark.parametrize(
    ("input_query", "excepted"),
    (
        pytest.param(query.TSQuery("serverlist"), "serverlist", id="test_command_only"),
        pytest.param(
            query.TSQuery("clientlist").option("uid", "away").option("groups"),
            "clientlist -uid -away -groups",
            id="test_options",
        ),
        pytest.param(
            query.TSQuery("sendtextmessage").params(targetmode=2, target=12).params(msg="Hello World!"),
            r"sendtextmessage targetmode=2 target=12 msg=Hello\sWorld!",
            id="test_params",
        ),
        pytest.param(
            query.TSQuery("clientkick")
            .params(reasonid=5, reasonmsg="Go away!")
            .param_block(clid=1)
            .param_block(clid=2)
            .param_block(clid=3),
            r"clientkick reasonid=5 reasonmsg=Go\saway! clid=1|clid=2|clid=3",
            id="test_param_block_single",
        ),
        pytest.param(
            query.TSQuery("servergroupaddperm")
            .params(sgid=13)
            .param_block(permid=17276, permvalue=50, permnegated=0, permskip=0)
            .param_block(permid=21415, permvalue=20, permnegated=0),
            "servergroupaddperm sgid=13 permid=17276 permvalue=50 permnegated=0 permskip=0|permid=21415 permvalue=20 permnegated=0",
            id="test_param_block_multiple",
        ),
        pytest.param(
            query.TSQuery("ftdeletefile")
            .params(cid=2, cpw="")
            .param_block(name="/Pic1.PNG")
            .param_block(name="/Pic2.PNG"),
            r"ftdeletefile cid=2 cpw= name=\/Pic1.PNG|name=\/Pic2.PNG",
            id="test_empty_param",
        ),
    ),
)
def test_query_compile(input_query: query.TSQuery, excepted: str) -> None:
    assert input_query.compile() == excepted


def test_empty_query():
    with pytest.raises(ValueError):
        query.TSQuery("")