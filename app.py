## Librerias
from flask import Flask, redirect, render_template, request, session, flash
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
            flash("⚠ usuario o contraseña incorrectos", "danger")
            return redirect("/login")
        
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
    ## Condición para que solo usuario validado acceda a este apartado
    if "usuario" not in session:
        return redirect("/login")

    ## Aquí flask recibe el valor del input del formulario
    buscar = request.args.get("buscar", "")
    ## Crear un objeto con la conexión a la db
    cursor = conexion.cursor()

    pagina = request.args.get("pagina", 1, type=int)
    limite = 4
    offset = (pagina - 1) * limite

    ## Condición para realizar consulta deacuerdo con el buscardor
    if buscar:
        cursor.execute("""select * from tickets where titulo like %s or usuario like %s order by id_ticket desc limit %s offset %s""", 
                       (f"%{buscar}%", f"%{buscar}%", limite, offset))
    else:
        cursor.execute("Select * from tickets order by id_ticket desc limit %s offset %s", (limite, offset))
    ## Traer los resultados de la consulta
    tickets = cursor.fetchall()

    # return "Sistema de tickets funcionando 🔥"
    return render_template("ver_tickets.html", tickets = tickets, pagina = pagina)

## Crear decorador para... Get: mostrar formulario o POST: recivir datos enviados
@app.route("/crear", methods = ["GET", "POST"])
def crear_ticket():

    ## Condición para que solo usuario validado acceda a este apartado
    if "usuario" not in session:
        return redirect("/login")
    
    ## Condicional para saber si antes la función leyó un metodo tipo POST
    if request.method == "POST":
        # reques.form obtiene los datos del formulario HTML
        titulo = request.form.get("titulo")
        descripcion = request.form.get("descripcion")
        prioridad = request.form.get("prioridad")
        usuario = request.form.get("usuario")

        ## Condición para validar que los campos no vnegan sin datos o valores
        if not titulo or not descripcion or not prioridad or not usuario:
            flash("Todos los campos son obligatorios", "danger")
            return redirect("/crear")
        
        ## Almacenar los datos mandados del template en la variable "valores"
        valores = (titulo, descripcion, prioridad, usuario)

        ## Crear objeto para conexión con db
        cursor = conexion.cursor()
        ## Crear consulta y almacenarla en arreglo sql
        sql = """insert into tickets (titulo, descripcion, prioridad, usuario) values (%s, %s, %s, %s)"""
        cursor.execute(sql, valores) 
        conexion.commit()

        flash("ticket creado correctamente", "success")
        return redirect("/")
    return render_template("crear_ticket.html")

## Decorador para marcar completo un ticket
@app.route("/eliminar/<int:id_ticket>")
def borrar_ticket(id_ticket):
    ## Crear condición para que solo administradores accedan a la siguiente acción
    if session["rol"] != "admin":
        flash("⛔ No tienes permisos para realizar esta acción", "warning")
        return redirect("/")
    
    ## Crear objeto con conexión a la db
    cursor = conexion.cursor()
    sql = """Update tickets set estado = 'cerrado' where id_ticket = %s """
    cursor.execute(sql, (id_ticket,))

    conexion.commit()
    return redirect("/")


## Al chile no me acuerdo pero es de ahuevo pa que jale el flask
if __name__ == "__main__":  
    app.run(debug=True)