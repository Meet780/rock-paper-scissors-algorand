from pyteal import *

def approval_program():
    player1 = Bytes("p1")
    player2 = Bytes("p2")
    p1_commit = Bytes("c1")
    p2_commit = Bytes("c2")
    p1_reveal = Bytes("r1")
    p2_reveal = Bytes("r2")
    p1_won = Bytes("w1")
    p2_won = Bytes("w2")
    game_state = Bytes("gs")

    gs_none = Int(0)
    gs_commit = Int(1)
    gs_reveal = Int(2)
    gs_done = Int(3)

    on_create = Seq([
        App.globalPut(game_state, gs_none),
        Return(Int(1))
    ])

    is_p1 = Txn.sender() == App.globalGet(player1)
    is_p2 = Txn.sender() == App.globalGet(player2)

    commit_move = Txn.application_args[1]
    reveal_move = Txn.application_args[1]
    reveal_nonce = Txn.application_args[2]

    commit_hash = Sha256(Concat(reveal_move, reveal_nonce))

    commit = Seq([
        If(App.globalGet(game_state) != gs_none)
        .Then(Return(Int(0))),
        App.globalPut(player1, Txn.accounts[1]),
        App.globalPut(player2, Txn.accounts[2]),
        App.globalPut(p1_commit, Bytes("")),
        App.globalPut(p2_commit, Bytes("")),
        App.globalPut(p1_reveal, Bytes("")),
        App.globalPut(p2_reveal, Bytes("")),
        App.globalPut(p1_won, Int(0)),
        App.globalPut(p2_won, Int(0)),
        App.globalPut(game_state, gs_commit),
        Return(Int(1))
    ])

    p1_commit_move = Seq([
        If(And(is_p1, App.globalGet(game_state) == gs_commit, App.globalGet(p1_commit) == Bytes("")))
        .Then(Seq([
            App.globalPut(p1_commit, commit_move),
            Return(Int(1))
        ]))
        .Else(Return(Int(0)))
    ])

    p2_commit_move = Seq([
        If(And(is_p2, App.globalGet(game_state) == gs_commit, App.globalGet(p2_commit) == Bytes("")))
        .Then(Seq([
            App.globalPut(p2_commit, commit_move),
            If(And(App.globalGet(p1_commit) != Bytes(""), App.globalGet(p2_commit) != Bytes(""))
            ).Then(App.globalPut(game_state, gs_reveal)),
            Return(Int(1))
        ]))
        .Else(Return(Int(0)))
    ])

    verify_reveal = Seq([
        If(And(is_p1, App.globalGet(game_state) == gs_reveal, App.globalGet(p1_reveal) == Bytes("")))
        .Then(Seq([
            Assert(Sha256(Concat(reveal_move, reveal_nonce)) == App.globalGet(p1_commit)),
            App.globalPut(p1_reveal, reveal_move),
            Return(Int(1))
        ]))
        .ElseIf(And(is_p2, App.globalGet(game_state) == gs_reveal, App.globalGet(p2_reveal) == Bytes("")))
        .Then(Seq([
            Assert(Sha256(Concat(reveal_move, reveal_nonce)) == App.globalGet(p2_commit)),
            App.globalPut(p2_reveal, reveal_move),
            Return(Int(1))
        ]))
        .Else(Return(Int(0)))
    ])

    decide_winner = Seq([
        Assert(App.globalGet(game_state) == gs_reveal),
        If(Or(App.globalGet(p1_reveal) == Bytes(""), App.globalGet(p2_reveal) == Bytes("")))
        .Then(Return(Int(0))),
        App.globalPut(game_state, gs_done),
        Cond(
            [App.globalGet(p1_reveal) == App.globalGet(p2_reveal), Seq([
                App.globalPut(p1_won, Int(0)),
                App.globalPut(p2_won, Int(0)),
                Return(Int(1))
            ])],
            [And(App.globalGet(p1_reveal) == Bytes("rock"), App.globalGet(p2_reveal) == Bytes("scissors")), Seq([
                App.globalPut(p1_won, Int(1)),
                App.globalPut(p2_won, Int(0)),
                Return(Int(1))
            ])],
            [And(App.globalGet(p1_reveal) == Bytes("paper"), App.globalGet(p2_reveal) == Bytes("rock")), Seq([
                App.globalPut(p1_won, Int(1)),
                App.globalPut(p2_won, Int(0)),
                Return(Int(1))
            ])],
            [And(App.globalGet(p1_reveal) == Bytes("scissors"), App.globalGet(p2_reveal) == Bytes("paper")), Seq([
                App.globalPut(p1_won, Int(1)),
                App.globalPut(p2_won, Int(0)),
                Return(Int(1))
            ])],
            [Int(1), Seq([
                App.globalPut(p1_won, Int(0)),
                App.globalPut(p2_won, Int(1)),
                Return(Int(1))
            ])]
        )
    ])

    reset_game = Seq([
        App.globalPut(player1, Bytes("")),
        App.globalPut(player2, Bytes("")),
        App.globalPut(p1_commit, Bytes("")),
        App.globalPut(p2_commit, Bytes("")),
        App.globalPut(p1_reveal, Bytes("")),
        App.globalPut(p2_reveal, Bytes("")),
        App.globalPut(p1_won, Int(0)),
        App.globalPut(p2_won, Int(0)),
        App.globalPut(game_state, gs_none),
        Return(Int(1))
    ])

    program = Cond(
        [Txn.application_id() == Int(0), on_create],
        [Txn.on_completion() == OnComplete.DeleteApplication, Return(Int(0))],
        [Txn.on_completion() == OnComplete.UpdateApplication, Return(Int(0))],
        [Txn.on_completion() == OnComplete.CloseOut, Return(Int(1))],
        [Txn.on_completion() == OnComplete.OptIn, Return(Int(0))],
        [Txn.application_args[0] == Bytes("commit_init"), commit],
        [Txn.application_args[0] == Bytes("p1_commit"), p1_commit_move],
        [Txn.application_args[0] == Bytes("p2_commit"), p2_commit_move],
        [Txn.application_args[0] == Bytes("reveal"), verify_reveal],
        [Txn.application_args[0] == Bytes("decide"), decide_winner],
        [Txn.application_args[0] == Bytes("reset"), reset_game]
    )

    return program

def clear_state_program():
    return Return(Int(1))

if __name__ == "__main__":
    with open("approval.teal", "w") as f:
        compiled = compileTeal(approval_program(), mode=Mode.Application, version=5)
        f.write(compiled)

    with open("clear.teal", "w") as f:
        compiled = compileTeal(clear_state_program(), mode=Mode.Application, version=5)
        f.write(compiled)
