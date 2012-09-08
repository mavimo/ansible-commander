import psycopg2
import ConfigParser
import psycopg2.extras as extras
import json

# TODO: make a seperate config class
parser  = ConfigParser.ConfigParser()
parser.read("/etc/ansible/commander.cfg")

dbname  = 'ansible_commander'
dbuser  = 'ansible_commander'
dbpass  = parser.get('database', 'password')
connstr = "dbname='%s' user='%s' host='localhost' password='%s'" % (dbname,dbuser,dbpass)

conn = psycopg2.connect(connstr)

class DataException(Exception):
   pass

class AlreadyExists(DataException):
   pass

class InvalidInput(DataException):
   pass

class Base(object):

    def __init__(self):
        self.type = None

    def cursor(self):
        return conn.cursor()

    def check_required_fields(self, fields):
 
        if fields.get(self.FIELDS['primary'], None) is None:
            raise InvalidInput("missing primary field: %s" % self.FIELDS['primary'])
     
        # all required fields are set
        for f in self.FIELDS['required']:
            if f not in fields:
                raise InvalidInput("field %s if required" % f)

        # any optional fields get set to defaults if missing
        for f in self.FIELDS['optional']:
            if f not in fields:
                fields[f] = spec['optional'][f] 

        # no unexpected fields
        for f in fields:
            if f not in self.FIELDS['required'] and f not in self.FIELDS['optional'] and f != self.FIELDS['primary']:
                raise InvalidInput("invalid field %s" % f)

    def get_by_id(self, id):
        raise exceptions.NotImplementedError # yet

    def add(self, properties):
 
        self.check_required_fields(properties)
        primary = self.FIELDS['primary']
        matches = self.lookup(properties[primary])
        if len(matches) != 0:
            raise AlreadyExists()
        return self._insert(properties)

    def _insert(self, properties):
        primary = self.FIELDS['primary']
        cur = self.cursor()
        sth = """
            INSERT INTO thing (type) VALUES (%s)
            RETURNING id
        """
        cur.execute(sth, [self.TYPE])
        tid = cur.fetchone()[0]

        inserts = []
        for (k,v) in properties.iteritems():
            inserts.append((tid, k, json.dumps(v))) 
       
        sth = """
            INSERT INTO properties (thing_id,key,value) VALUES(%s,%s,%s)
        """
        cur.executemany(sth, inserts)
        conn.commit()
        matches = self.find(primary, properties[primary])
        return matches[0]

    def list(self):
        cur = self.cursor()
        sth = """
             SELECT t.id, p.id, p.key, p.value 
             FROM thing t
             LEFT JOIN properties p
             ON p.thing_id = t.id
             WHERE type    = %s

        """

        cur.execute(sth, [self.TYPE])
        db_results = cur.fetchall()
        return self._reformat(db_results)

    def _reformat(self, db_results):

        results = {}
        for (tid, pid, key, value) in db_results:
            if not tid in results:
                results[tid] = {}
            results[tid][key] = json.loads(value) 
            results[tid]['id'] = tid
        return results.values()
        
    def find(self, key, value):
        cur = self.cursor()
        # all values are stored in JSON in the DB, so ookups must also jsonify first
        value = json.dumps(value)
        sth = """
             SELECT t.id, p.id, p.key, p.value 
             FROM thing t, properties p
             WHERE p.thing_id = t.id
             AND t.id IN (
                 SELECT t.id
                 FROM thing t
                 LEFT JOIN properties p
                 ON p.thing_id = t.id
                 WHERE type  = %s
                 AND p.key   = %s
                 AND p.value = %s
             )
        """
        cur.execute(sth, [self.TYPE,key,value])
        db_results = cur.fetchall()
        matches = self._reformat(db_results)
        return matches
  
    def lookup(self, value):
        return self.find(self.FIELDS['primary'], value)    

    def clear(self):
        cur = self.cursor()
        sth = """
            DELETE from thing where type=%s
        """
        cur.execute(sth, [self.TYPE])
        conn.commit()
            

class Groups(Base):

   def __init__(self):

       self.TYPE = 'group'
       self.FIELDS = dict(
           primary  = 'name',
           required = [ 'parent' ],
           optional = {},
           private = [
               'cached_direct_child_groups',
               'cached_direct_child_hosts',
               'cached_all_child_groups',
               'cached_all_child_hosts'
           ]
       )

class Junk(Base):
   
    def __init__(self):
    
        self.TYPE = 'group'
        self.FIELDS = dict(
            primary  = 'name',
            required = [ 'info' ],
            optional = {},
            private = []
        )


if __name__ == '__main__':

    j = Junk()

    j.clear()

    print 'insert pinky'
    print j.add(dict(name='pinky', info='narf'))

    try:
        print 'insert pinky'
        print j.add(dict(name='pinky', info='narf'))
    except AlreadyExists:
        print 'already exists'

    print 'insert brain'
    print j.add(dict(name='brain', info='aypwip'))

    print 'list'
    print j.list()

    print 'lookup pinky'
    print j.lookup('pinky')

    print 'lookup brain'
    print j.find('name','brain')

    print 'lookup snowball'
    print j.find('name','snowball')


