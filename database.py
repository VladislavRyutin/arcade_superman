import psycopg2
class DataBase():

  def __init__(self):
    self.conn = None
    self.cursor = None
    
  def addUser(self, userName):
      self.cursor.execute(f"insert into users(name) values ('{userName}');")
      self.conn.commit()

  def addScore(self, userName, scores, level):
    user_id = self.getUserIdByName(userName)
    if (user_id == -1):
      self.addUser(userName)
    user_id = self.getUserIdByName(userName)
    self.cursor.execute(f"select * from scores{level} as sc where sc.id_user = '{user_id}'")
    records = self.cursor.fetchall()
    if len(records) == 0:
      self.cursor.execute(f"insert into scores{level}(id_user, score) VALUES ({user_id}, {scores});")
    else:
      if records[0][2] < scores:
        self.cursor.execute(f"update scores{level} set score = {scores} where id_user = {user_id};")
    self.conn.commit()
  
  def getUserIdByName(self, userName):
    self.cursor.execute(f"select us.id from users as us where us.name = '{userName}'")
    records = self.cursor.fetchall()
    if len(records) == 0:
      return -1
    else:
      return records[0][0]

  def getAllScores(self, level, num = 3):
    self.cursor.execute(f"select us.name, sc.score from users us join scores{level} sc on sc.id_user = us.id order by sc.score DESC ")
    records = self.cursor.fetchmany(size=num)
    return records

  def createConn(self,host = '37.195.213.170', user = 'user1', password = 'user'):
    self.conn = psycopg2.connect(dbname='superman_survival', user=user, 
                        password=password, host=host)
    self.cursor = self.conn.cursor()

  def closeConn(self):
    self.cursor.close()
    self.conn.close()

