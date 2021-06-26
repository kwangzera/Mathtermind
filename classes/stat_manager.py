from contextlib import closing


class StatManager:
    def __init__(self, con):
        self.con = con

    # def get_log_status(self, ctx):
    #     """Returns a user's logging status, assuming it exists"""

    #     with closing(self.con.cursor()) as cur:
    #         cur.execute(f"SELECT logging FROM mtm_user WHERE author_id = '{ctx.author.id}' AND guild_id = '{ctx.guild.id}' AND game_id = 0")
    #         return cur.fetchone()[0]
    #     ...

    def update_log_status(self, ctx, toggle):
        """Changes a user's logging status to `toggle`. Assumes user exists in database and `toggle` is a boolean"""

        with closing(self.con.cursor()) as cur:
            cur.execute(f"UPDATE mtm_user SET logging = {toggle} WHERE author_id = '{ctx.author.id}' AND guild_id = '{ctx.guild.id}' AND game_id = 0")
            self.con.commit()

    def toggle_log(self, ctx, toggle):
        if not self.table_exists(ctx):
            return False

        self.update_log_status(ctx, toggle)
        return True

    def table_exists(self, ctx):
        """If `mtm_user` exists, `mtm_user_raw` exists and stats for any also exists"""

        with closing(self.con.cursor()) as cur:
            cur.execute(f"SELECT EXISTS (SELECT 1 FROM mtm_user WHERE author_id = '{ctx.author.id}' AND guild_id = '{ctx.guild.id}' LIMIT 1);")
            return cur.fetchone()[0]