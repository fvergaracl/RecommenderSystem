import mysql.connector
import Conf as conf
import pandas as pd
import sys
sys.path.append("/home/ubuntu/carpeta_compartida_docker/RecommenderSystem/src")
# data = [
#   ('Jane', date(2005, 2, 12)),
#   ('Joe', date(2006, 5, 23)),
#   ('John', date(2010, 10, 3)),
# ]
# stmt = "INSERT INTO employees (first_name, hire_date) VALUES (%s, %s)"
# cursor.executemany(stmt, data)
from Servicio_intento.app.Clases import *


class Connexion:

    def __init__(self):
        self.client = None
        self.cursor = None

    def start(self):
        if self.client == None:
            try:
                self.client = mysql.connector.connect(host='localhost', user='root', passwd=conf.passwd, db='SocioBee')
                self.cursor = self.client.cursor()
                return True
            except Exception as err:
                print("No se ha podido establecer la conexión: ", err)
                return False
        else:
            return True

    def close(self):
        if self.client is None:
            return True
        else:
            try:
                self.client.close()
                self.client = None
                self.cursor = False
                return True
            except:
                print("No se ha podido cerrar la conexión")
                return False

    # def insertParticipant(self, name="NULL", surname="NULL", age="NULL", gender="'I dont want to answer'"):
    #     try:
    #         self.cursor.execute(f"INSERT INTO Participant (name,surname,age,gender) value ({name},{surname},{age},{gender})")
    #         self.client.commit()
    #         id = int(self.cursor.lastrowid)
    #         return id
    #     except Exception as err:
    #         print(err)   
            
            
                       
    # def insertQueenBee(self, name='NULL', surname='NULL', age='NULL', gender="I dont want to answer"):   
      
    #     self.cursor.execute(
    #         f"INSERT INTO QueenBee (name,surname,age,gender) value ({name},{surname},{age},'{gender}')")
    #     self.client.commit()
    #     id = int(self.cursor.lastrowid)
    #     return id



    # def insertCampaign(self, manager_id="NULL", city="NULL", start_timestamp="NULL", cell_edge="NULL",
    #                    min_samples="NULL", sampling_period="NULL", planning_limit_time="NULL",
    #                    campaign_duration="NULL"):

    #     self.cursor.execute(
    #         f"INSERT INTO Campaign (manager_id,city,start_timestamp,cell_edge,min_samples,"
    #         f" sampling_period,planning_limit_time,campaign_duration) value"
    #         f"({manager_id},{city},{start_timestamp},{cell_edge},{min_samples},{sampling_period},"
    #         f"{planning_limit_time},{campaign_duration})")

    #     self.client.commit()
    #     id = int(self.cursor.lastrowid)
    #     return id

    # def insertSurface(self, campaign_id="Null"):
    #     self.cursor.execute(f"INSERT INTO Surface (campaign_id) value ({campaign_id})")
    #     self.client.commit()
    #     id = int(self.cursor.lastrowid)

    #     return id

    # def insertBoundary(self,surface_id="Null",boundary="Null"):
    #     self.cursor.execute(f"INSERT INTO Boundary (surface_id,boundary) value ({surface_id},{boundary})")
    #     self.client.commit()
    #     id = int(self.cursor.lastrowid)

    #     return id
    def insertCell(self, surface_id: int, center= None,  inferior_coord=None, superior_coord=None,cell_type="Dynamic"):
        try:    
            self.cursor.execute(
                        "INSERT INTO Cell (center,cell_type,inferior_coord,superior_coord,surface_id) value (%s,%s,%s,%s,%s)" % (
                        "Point({}, {})".format(
                                center.x, center.y)if center != None else "NULL",
                            "'{}'".format(
                                cell_type) if cell_type != None else "'Dynamic'",
                            "Point({}, {})".format(
                                inferior_coord.p.get_x, inferior_coord.p.get_y) if inferior_coord != None else "NULL",
                            "Point({}, {})".format(
                                superior_coord.p.get_xd, superior_coord.p.get_y
                                ) if superior_coord != None else "NULL",
                            "{}".format(
                                surface_id) if surface_id != None else "'Dynamic'"))
            self.client.commit()
            self.id = int(self.cursor.lastrowid)
        except Exception as err:
                print(err)
        return id

    # def insertCellPriorityMeasurement(self,cell_id,timestamp,temporal_priority="Null",trend_priority="Null"):
    #     self.cursor.execute(f"INSERT INTO CellPriorityMeasurement (cell_id,timestamp,temporal_priority,trend_priority) "
    #                         f"value ({cell_id},{timestamp},{temporal_priority},{trend_priority})")
    #     self.client.commit()
    #     id = int(self.cursor.lastrowid)
    #     return id
    # #Cuidado hay funciones que no tienene id
    # def insertCellMeasurementPromise(self, cell_id,participant_id,sampling_limit,is_active="TRUE"):
    #     self.cursor.execute(
    #         f"INSERT INTO CellMeasurementPromise (cell_id,participant_id,sampling_limit,is_active) "
    #         f"value ({cell_id},{participant_id},{sampling_limit},{is_active})")
    #     self.client.commit()
    #     id = int(self.cursor.lastrowid)
    #     return id

    # def insertCellMeasurement(self,cell_id="Null",participant_id="Null",timestamp="Null",measurement_type="'AirData'",
    #                           data_id="Null",location="Null"):
    #     self.cursor.execute(
    #         f"INSERT INTO  CellMeasurement (cell_id,participant_id,timestamp,measurement_type,data_id,location) "
    #         f"value ({cell_id},{participant_id},{timestamp},{measurement_type},{data_id},{location})")
    #     self.client.commit()
    #     id = int(self.cursor.lastrowid)
    #     return id

    # def insertAirData(self,measurement_id="Null",No2="Null",Co2="Null"):
    #     self.cursor.execute(
    #         f"INSERT INTO  AirData (measurement_id,No2,Co2) "
    #         f"value ({measurement_id},{No2},{Co2})")
    #     self.client.commit()
    #     id = int(self.cursor.lastrowid)
    #     return id

    # def insertRecommendation(self, cell_id,participant_id, recommendation_timestamp="NULL", state="'"+"Rejected"+"'"):
    #     self.cursor.execute(
    #         f"INSERT INTO  Recommendation (cell_id,participant_id,recommendation_timestamp,state) "
    #         f"value ({cell_id},{participant_id},{recommendation_timestamp},{state})")
    #     self.client.commit()
    #     id = int(self.cursor.lastrowid)
    #     return id
    
    def vaciarDatos(self):
        try:
            self.cursor.execute("Delete from AirData;")  # ;'
            self.client.commit()
            self.cursor.execute("ALTER TABLE AirData AUTO_INCREMENT = 1;")  # ;'
            self.cursor.execute("Delete from CellMeasurement;")  # ;'
            self.client.commit()
            self.cursor.execute("ALTER TABLE CellMeasurement AUTO_INCREMENT = 1;")  # ;'
            self.cursor.execute("Delete from CellMeasurementPromise;")  # ;'
            self.client.commit()
            self.cursor.execute("Delete from CellPriorityMeasurement;")  # ;'
            self.client.commit()
            self.cursor.execute("Delete from Cell;")
            self.client.commit()
            self.cursor.execute("ALTER TABLE Cell AUTO_INCREMENT = 1;")  # ;'
            self.cursor.execute("Delete from Boundary;")
            self.client.commit()
            self.cursor.execute("ALTER TABLE Boundary AUTO_INCREMENT = 1;")  # ;'
            self.cursor.execute("Delete from Surface;")
            self.client.commit()
            self.cursor.execute("ALTER TABLE Surface AUTO_INCREMENT = 1;")  # ;'
            self.cursor.execute("Delete from Campaign;")
            self.client.commit()
            self.cursor.execute("ALTER TABLE Campaign AUTO_INCREMENT = 1;")  # ;'
            self.cursor.execute("Delete from QueenBee;")
            self.client.commit()
            self.cursor.execute("ALTER TABLE QueenBee AUTO_INCREMENT = 1;")  # ;'
            self.cursor.execute("Delete from Participant;")
            self.client.commit()
            self.cursor.execute("ALTER TABLE Participant AUTO_INCREMENT = 1;")  # ;'
            self.client.commit()

            return True
        except Exception as err:
            print(err)
            return False


if __name__ == '__main__':

    bd = Connexion()
    con = bd.start()
    print(con)
    if con==True:
        print(bd.vaciarDatos())
        a="hola"
    
        print(bd.insertParticipant())
        print(bd.insertQueenBee())
        print(bd.vaciarDatos())
        bd.close()


# Tendria que hacer lo msimo con los alters pero no lo voy a hacer porque no los voy a usar creo
