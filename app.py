## Librerias
from flask import Flask, redirect, render_template, request 
import  mysql.connector 

## Crear objeto con la clase Flask de macro-framework flask
app = Flask(__name__)

## Conección con la base de datos
conexion = mysql.connector.connect(host="localhost", user="root", password="admin", database="s_tickets")

## Decorador para indicarle a flask a partir de donde ejecute la siguiente función
@app.route("/")
def home():
    cursor = conexion.cursor()
    cursor.execute("Select * from tickets where fin = 1")
    tickets = cursor.fetchall()
    # return str(tickets) 
    # return "Sistema de tickets funcionando 🔥"
    return render_template("ver_tickets.html", tickets = tickets)

## Crear decorador para... Get: mostrar formulario o POST: recivir datos enviados
@app.route("/crear", methods = ["GET", "POST"])
def crear_ticket():
    ## Condicional para saber si antes la función leyó un metodo tipo POST
    if request.method == "POST":
        # reques.form obtiene los datos del formulario HTML
        titulo = request.form["titulo"]
        descripcion = request.form["descripcion"]
        prioridad = request.form["prioridad"]
        usuario = request.form["usuario"]
        valores = (titulo, descripcion, prioridad, usuario)

        cursor = conexion.cursor()
        sql = """insert into tickets (titulo, descripcion, prioridad, usuario) values (%s, %s, %s, %s)"""
        cursor.execute(sql, valores) 
        conexion.commit()

        return redirect("/")
    return render_template("crear_ticket.html")

## Decorador para eliminar o deshabilitar un ticket
@app.route("/eliminar/<int:id_ticket>")
def borrar_ticket(id_ticket):
    cursor = conexion.cursor()
    sql = """Update tickets set fin = 0 where id_ticket = %s """
    cursor.execute(sql, (id_ticket,))

    conexion.commit()
    return redirect("/")


## Al chile no me acuerdo pero es de ahuevo pa que jale el flask
if __name__ == "__main__":  
    app.run(debug=True)