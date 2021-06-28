# TODO add comments ~~assuming it exists~~
class StatManager:
    def __init__(self, con):
        self.con = con

    # TODO test query for sql injection
    def query(self, ctx, gid, col_name):
        with self.con.cursor() as cur:
            sql = f"SELECT {col_name} FROM mtm_user WHERE author_id = %s AND guild_id = %s AND game_id = %s;"
            data = (str(ctx.author.id), str(ctx.guild.id), gid)
            cur.execute(sql, data)
            return cur.fetchone()[0]

    def update(self, ctx, gid, **kwargs):
        with self.con.cursor() as cur:
            key, value = kwargs.popitem()
            sql = f"UPDATE mtm_user SET {key} = %s WHERE author_id = %s AND guild_id = %s AND game_id = %s;"
            data = (value, str(ctx.author.id), str(ctx.guild.id), gid)
            cur.execute(sql, data)
            self.con.commit()

    def incr_stats(self, ctx, gid, result):
        # with self.con.cursor() as cur:
        #     cur.execute(f"UPDATE mtm_user SET raw_data = {temp} WHERE author_id = '{ctx.author.id}' AND guild_id = '{ctx.guild.id}' AND game_id = {gid};")
        #     self.con.commit
        ...

    # TODO do something about this
    def calc_streak(self, ctx, gid, result):
        prev = self.query(ctx, gid, "prev_result")
        win = self.query(ctx, gid, "wins")
        lose = self.query(ctx, gid, "losses")
        c_win = self.query(ctx, gid, "cur_win")
        c_lose = self.query(ctx, gid, "cur_loss")

        if result:
            c_win += 1
            win += 1

            self.update(ctx, gid, cur_win=c_win)
            self.update(ctx, gid, wins=win)

            if not prev:
                self.update(ctx, gid, cur_loss=0)

            self.update(ctx, gid, current_streak=c_win)

        else:
            c_lose += 1
            lose += 1

            self.update(ctx, gid, cur_loss=c_lose)
            self.update(ctx, gid, losses=lose)

            if prev:  # Won previous game
                self.update(ctx, gid, cur_win=0)

            self.update(ctx, gid, current_streak=c_lose)

        self.update(ctx, gid, longest_win_streak=max(self.query(ctx, gid, "longest_win_streak"), c_win))
        self.update(ctx, gid, longest_loss_streak=max(self.query(ctx, gid, "longest_loss_streak"), c_lose))
        self.update(ctx, gid, prev_result=result)

    def user_in_db(self, ctx):
        with self.con.cursor() as cur:
            cur.execute(f"SELECT EXISTS (SELECT 1 FROM mtm_user WHERE author_id = '{ctx.author.id}' AND guild_id = '{ctx.guild.id}' LIMIT 1);")
            return cur.fetchone()[0]
