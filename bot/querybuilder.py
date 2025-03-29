class QueryBuilder:
    def __init__(self, args):
        self.args = []
        self.selectclause = self.setSelectClause()
        self.fromclause = self.setFromClause()
        self.whereclause = self.setWhereClause()
        self.groupbyclause = ""
        self.limitclause = ""

    
    def setSelectClause(self, columns):
        self.selectclause = "SELECT " + columns

    def setFromClause(self):
        self.fromclause = " FROM scoreLive inner join beatmapLive on scoreLive.beatmap_id = beatmapLive.beatmap_id inner join userLive on scoreLive.user_id = userLive.user_id"
    
    def setWhereClause(self):
        whereClause = ""
        if self.args.__contains__("-accuracy-min"):
            whereClause += " AND accuracy >= " + self.args["-accuracy-min"]
        if self.args.__contains__("-accuracy-max"):
            whereClause += " AND accuracy < " + self.args["-accuracy-max"]
        if self.args.__contains__("-mode"):
            whereClause += " AND mode = " + self.args["-mode"]
        if self.args.__contains__("-username"):
            whereClause += " AND username = '" + self.args["-username"] + "'"

        if len(whereClause) > 0:
            self.whereclause = " WHERE " + whereClause[5:]
        

