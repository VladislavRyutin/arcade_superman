import json
class DataBase():

  def __init__(self, name):
    self.filename = name
    
  def addUser(self, userName):
    new_data = {
      "name":userName,
      "stat":"0"
    }
    with open(self.filename, "r+") as stats:
      base_json = json.load(stats)
      is_find = False
      for stat in base_json['stats']:
        if (stat.get("name") == userName):
          is_find = True
          break
      if not is_find:        
        base_json['stats'].append(new_data)
        stats.seek(0)
        json.dump(base_json,stats, indent=4)
        stats.truncate()

  def addScore(self, user_name, scores):
    new_data = {
      "name":user_name,
      "stat":scores
    }
    with open(self.filename, "r+") as stats:
      base_json = json.load(stats)
      for stat in base_json['stats']:
        if (stat.get("name") == user_name):
          if ( not int(stat['stat']) > scores):
            stat['stat'] = scores
            stats.seek(0)
            json.dump(base_json,stats, indent=4)
            stats.truncate()
          break

  def getAllScores(self):
    with open(self.filename, "r") as stats:
      base_json = stats.read()
    base = json.loads(base_json)
    def sort_by_key(list):
      return list['stat']
    base = (sorted(base['stats'], key=sort_by_key, reverse=True))
    return base

