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

    def increment(self, ctx, gid, col_name):
        tmp = self.query(ctx, gid, col_name)
        self.update(ctx, gid, **{col_name: tmp+1})

    def query_raw(self, ctx, gid):
        with self.con.cursor() as cur:
            sql_q = "SELECT raw_data FROM mtm_user_raw WHERE author_id = %s AND guild_id = %s AND game_id = %s;"
            data_q = (str(ctx.author.id), str(ctx.guild.id), gid)
            cur.execute(sql_q, data_q)
            return cur.fetchone()[0]

    def incr_raw(self, ctx, gid, result):
        with self.con.cursor() as cur:
            new_raw = self.query_raw(ctx, gid) + str(result)
            sql_u = "UPDATE mtm_user_raw SET raw_data = %s WHERE author_id = %s AND guild_id = %s AND game_id = %s;"
            data_u = (new_raw, str(ctx.author.id), str(ctx.guild.id), gid)
            cur.execute(sql_u, data_u)
            self.con.commit()

    # TODO do something about this
    def calc_streak(self, ctx, gid, result):
        prev = self.query(ctx, gid, "prev_result")
        cur_win = self.query(ctx, gid, "cur_win")
        cur_loss = self.query(ctx, gid, "cur_loss")

        if result:
            cur_win += 1
            self.increment(ctx, gid, "cur_win")
            self.increment(ctx, gid, "wins")

            if not prev:
                self.update(ctx, gid, cur_loss=0)

            self.update(ctx, gid, current_streak=cur_win)

        else:
            cur_loss += 1
            self.increment(ctx, gid, "cur_loss")
            self.increment(ctx, gid, "losses")

            if prev:  # Won previous game
                self.update(ctx, gid, cur_win=0)

            self.update(ctx, gid, current_streak=cur_loss)

        self.update(ctx, gid, longest_win_streak=max(self.query(ctx, gid, "longest_win_streak"), cur_win))
        self.update(ctx, gid, longest_loss_streak=max(self.query(ctx, gid, "longest_loss_streak"), cur_loss))
        self.update(ctx, gid, prev_result=result)

    def user_in_db(self, ctx):
        with self.con.cursor() as cur:
            cur.execute(f"SELECT EXISTS (SELECT 1 FROM mtm_user WHERE author_id = '{ctx.author.id}' AND guild_id = '{ctx.guild.id}' LIMIT 1);")
            return cur.fetchone()[0]
