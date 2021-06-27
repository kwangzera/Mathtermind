# TODO add comments ~~assuming it exists~~
class StatManager:
    def __init__(self, con):
        self.con = con

    def query(self, ctx, gid, col_name):
        with self.con.cursor() as cur:
            cur.execute(f"SELECT {col_name} FROM mtm_user WHERE author_id = '{ctx.author.id}' AND guild_id = '{ctx.guild.id}' AND game_id = {gid};")
            return cur.fetchone()[0]

    def update(self, ctx, gid, **kwargs):
        with self.con.cursor() as cur:
            key, value = kwargs.popitem()
            cur.execute(f"UPDATE mtm_user SET {key} = {value} WHERE author_id = '{ctx.author.id}' AND guild_id = '{ctx.guild.id}' AND game_id = {gid};")
            self.con.commit()

    def increment(self, ctx, gid, col_name):
        with self.con.cursor() as cur:
            cur.execute(f"UPDATE mtm_user SET {col_name} = {col_name}+1 WHERE author_id = '{ctx.author.id}' AND guild_id = '{ctx.guild.id}' AND game_id = {gid};")
            self.con.commit()

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
