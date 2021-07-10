import logging
import string
from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable

class App:

    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        
        self.driver.close()

    def create_newnode(self, newnode):
        with self.driver.session() as session:
            # Write transactions allow the driver to handle retries and transient errors
            i=0
            for labelname in newnode['labels']:
                labelnamelist=labelname.split()
                labelname_='_'.join(labelnamelist)
                newnode['labels'][i]=labelname_
                i=i+1
            result=session.write_transaction(
                self._create_and_return_newnode, self,newnode)
            session.write_transaction(
                    self._createnamenode, result[0])
            i=1
            for labelname in newnode['labels']:
                if(self.find_label(labelname)==0):  
                    self.create_labelnode(labelname)
                session.write_transaction(
                    self._create_and_return_relationship, labelname, result[0],i)
                i=i+1


    def create_labelnode(self, labelname):
        with self.driver.session() as session:
            # Write transactions allow the driver to handle retries and transient errors
            session.write_transaction(
                self._create_and_return_labelnode, labelname)

    def find_label(self, labelname):
        with self.driver.session() as session:
            result = session.read_transaction(self._find_and_return_label, labelname)
            return len(result)

    def delete_node(self,nodename):
        with self.driver.session() as session:
            session.write_transaction(self._delete_node, nodename)

    def delete_all(self):
        with self.driver.session() as session:
            session.write_transaction(self._delete_all)

    @staticmethod
    def _createnamenode(tx,id):
        query=("MATCH (n) WHERE n.id = "+str(id)+
                " CREATE (m:Label { name: n.name}) "+
                " CREATE (n)-[r1:tag]->(m) RETURN m"
        )
        tx.run(query)

    @staticmethod      
    def _create_and_return_relationship(tx, labelname, id, tag_num):
        query = (
            "MATCH (n:FILE) WHERE n.id="+str(id)+
            " MATCH (m:Label) WHERE m.name=\'"+ labelname+"\' " 
            "CREATE (n)-[r1:tag]->(m) "
            # "CREATE (m)-[r2:tag"+"]->(n) "
            "RETURN n,m"
        )
        tx.run(query)

    @staticmethod
    def _create_and_return_newnode(tx, graph, newnode):
        labellist=newnode['labels']
        query = "CREATE (p:FILE"
        for labelname in labellist:
            query=query+':'+labelname
        query=query+newnode['property']+") "
        query=query+"SET p.id=id(p) RETURN p.id AS id"
        result = tx.run(query)
        return [record["id"] for record in result]

    @staticmethod
    def _create_and_return_labelnode(tx, labelname):
        query = (
            "CREATE (p1:Label{ name: $labelname }) "
            "RETURN p1"
        )
        tx.run(query, labelname=labelname)


    @staticmethod
    def _find_and_return_label(tx, labelname):
        query = (
            "MATCH (p:Label) "
            "WHERE p.name=\'"+labelname+"\' RETURN p"
        )
        result = tx.run(query)
        return [record["p"] for record in result]

    @staticmethod
    def _delete_node(tx, nodename):
        query = (
            "MATCH (p:FILE) "
            "WHERE p.name=\'"+nodename+"\' "
            "DETACH DELETE p"
        )
        tx.run(query)

    @staticmethod
    def _delete_all(tx):
        tx.run("match (n) detach delete n")

if __name__ == "__main__":
    #端口名、用户名、密码根据需要改动
    #create_newnode(node)用于创建结点（包括检测标签、创建标签节点、添加相应的边等功能）
    #delete_node(node.name)用于删去名为node.name的结点
    scheme = "bolt"  # Connecting to Aura, use the "neo4j+s" URI scheme
    host_name = "localhost"
    port = 7687
    url = "bolt://localhost:7687".format(scheme=scheme, host_name=host_name, port=port)
    user = "neo4j"
    password = "disgrafs"
    
    app = App(url, user, password)
    app.delete_node("USTCHORUSCAT.TXT".lower())
    app.close()
    