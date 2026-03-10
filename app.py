## Librerias
from flask import Flask, redirect, render_template, request, session
import  mysql.connector 

## Crear objeto con la clase Flask de macro-framework flask
app = Flask(__name__)

## Crear clave
app.secret_key = "YxOmS6"

## Conección con la base de datos
conexion = mysql.connector.connect(host="localhost", user="root", password="admin", database="s_tickets")

## Decorador para la ruta de acceso
@app.route("/login", methods=["GET", "POST"])
def login():
    ## Crear objeto con conexión de db
    cursor = conexion.cursor()

    ## condiciónal en caso de que el decorador venga con datos POST
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        cursor.execute("""select * from usuarios where username = %s and password = %s """, (username, password))

        usuario = cursor.fetchone()

        if usuario:
            session["usuario"] = usuario[1]
            session["rol"] = usuario[3]

            return redirect("/")
        else: 
            return "usuario o contraseña incorrectos"
        
    ## Retorno si la fusion no detecta evento POST
    return render_template("login.html")

## Decorador para logout
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

## Decorador para indicarle a flask a partir de donde ejecute la siguiente función 
@app.route("/")
def home():
    ## Condición para que solo usuario acceda a este apartado
    if "usuario" not in session:
        return redirect("/login")

    ## Aquí flask recibe el valor del input del formulario
    buscar = request.args.get("buscar", "")
    ## Crear un objeto con la conexión a la db
    cursor = conexion.cursor()

    ## Condición para realizar consulta deacuerdo con el buscardor
    if buscar:
        cursor.execute("""select * from tickets where titulo like %s or usuario like %s""", (f"%{buscar}%", f"%{buscar}%"))
    else:
        cursor.execute("Select * from tickets")
    ## Traer los resultados de la consulta
    tickets = cursor.fetchall()

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

        ## Crear objeto para conexión con db
        cursor = conexion.cursor()
        ## Crear consulta y almacenarla en arreglo sql
        sql = """insert into tickets (titulo, descripcion, prioridad, usuario) values (%s, %s, %s, %s)"""
        cursor.execute(sql, valores) 
        conexion.commit()

        return redirect("/")
    return render_template("crear_ticket.html")

## Decorador para marcar completo un ticket
@app.route("/eliminar/<int:id_ticket>")
def borrar_ticket(id_ticket):
    ## Crear condición para que solo administradores accedan a la siguiente acción
    if session["rol"] != "admin":
        return "no tienes permisos"
    
    ## Crear objeto con conexión a la db
    cursor = conexion.cursor()
    sql = """Update tickets set estado = 'cerrado' where id_ticket = %s """
    cursor.execute(sql, (id_ticket,))

    conexion.commit()
    return redirect("/")


## Al chile no me acuerdo pero es de ahuevo pa que jale el flask
if __name__ == "__main__":  
    app.run(debug=True)