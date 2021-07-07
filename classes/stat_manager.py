class StatManager:
    def __init__(self, con):
        self.con = con

    def query(self, ctx, gid, col_name):
        """Returns the value of `col_name` in the database"""

        with self.con.cursor() as cur:
            sql = f"SELECT {col_name} FROM mtm_user WHERE author_id = %s AND guild_id = %s AND game_id = %s;"
            data = (str(ctx.author.id), str(ctx.guild.id), gid)
            cur.execute(sql, data)
            return cur.fetchone()[0]

    def update(self, ctx, gid, **kwargs):
        """Changes any value of the database via **kwargs by setting `col_name=value`"""

        with self.con.cursor() as cur:
            key, value = kwargs.popitem()  # Only 1 keyword argument will be passed in
            sql = f"UPDATE mtm_user SET {key} = %s WHERE author_id = %s AND guild_id = %s AND game_id = %s;"
            data = (value, str(ctx.author.id), str(ctx.guild.id), gid)
            cur.execute(sql, data)
            self.con.commit()

    def increment(self, ctx, gid, col_name):
        """Increments the value of `col_name` in the database by 1"""

        tmp = self.query(ctx, gid, col_name)
        self.update(ctx, gid, **{col_name: tmp+1})

    def query_raw(self, ctx, gid):
        """Returns the binary string that represents a user's game history"""

        with self.con.cursor() as cur:
            sql = "SELECT raw_data FROM mtm_user_raw WHERE author_id = %s AND guild_id = %s AND game_id = %s;"
            data = (str(ctx.author.id), str(ctx.guild.id), gid)
            cur.execute(sql, data)
            return cur.fetchone()[0]

    def incr_raw(self, ctx, gid, result):
        """Updates the binary string that represents a user's game history"""

        with self.con.cursor() as cur:
            new_raw = self.query_raw(ctx, gid) + str(result)
            sql = "UPDATE mtm_user_raw SET raw_data = %s WHERE author_id = %s AND guild_id = %s AND game_id = %s;"
            data = (new_raw, str(ctx.author.id), str(ctx.guild.id), gid)
            cur.execute(sql, data)
            self.con.commit()

    def calc_streak(self, ctx, gid, result):
        """Calculates all types of streaks (win/lose/current) and updates wins and losses"""

        prev = self.query(ctx, gid, "prev_result")
        cur_win = self.query(ctx, gid, "cur_win")
        cur_loss = self.query(ctx, gid, "cur_loss")

        if result:  # Win
            cur_win += 1
            self.increment(ctx, gid, "cur_win")
            self.increment(ctx, gid, "wins")

            if not prev:  # Lost previous game, reset current loss streak since won current game
                self.update(ctx, gid, cur_loss=0)

            # Update current win streak
            self.update(ctx, gid, current_streak=cur_win)

        else:  # Lose
            cur_loss += 1
            self.increment(ctx, gid, "cur_loss")
            self.increment(ctx, gid, "losses")

            if prev:  # Won previous game, reset current win streak since lost current game
                self.update(ctx, gid, cur_win=0)

            # Update current loss streak
            self.update(ctx, gid, current_streak=cur_loss)

        # Constant time streak processing
        self.update(ctx, gid, longest_win_streak=max(self.query(ctx, gid, "longest_win_streak"), cur_win))
        self.update(ctx, gid, longest_loss_streak=max(self.query(ctx, gid, "longest_loss_streak"), cur_loss))
        self.update(ctx, gid, prev_result=result)

    def user_in_db(self, ctx):
        """Checks if the user exists in the database"""

        with self.con.cursor() as cur:
            sql = "SELECT EXISTS (SELECT 1 FROM mtm_user WHERE author_id = %s AND guild_id = %s LIMIT 1);"
            data = (str(ctx.author.id), str(ctx.guild.id))
            cur.execute(sql, data)
            return cur.fetchone()[0]
