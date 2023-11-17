from flask import Flask, render_template, request, redirect, session

import sqlite3 as sql
import uuid

app = Flask(__name__)
app.secret_key = "quitandazezinho"

# FUNÇÃO PARA VERIFICAR SESSÃO
def verifica_sessao():
    return "login" in session and session["login"]

# CONEXÃO COM O BANCO DE DADOS
def conecta_database():
    conexao = sql.connect("db_quitanda.db")
    conexao.row_factory = sql.Row
    return conexao

# INICIAR O BANCO DE DADOS
def iniciar_db():
    conexao = conecta_database()
    with app.open_resource('esquema.sql', mode='r') as comandos:
        conexao.cursor().executescript(comandos.read())
    conexao.commit()
    conexao.close()

# ROTA DA PÁGINA INICIAL
@app.route("/")
def index():
    iniciar_db()
    conexao = conecta_database()
    produtos = conexao.execute('SELECT * FROM produtos ORDER BY id_prod DESC').fetchall()
    conexao.close()
    title = "Home"
    return render_template("home.html", produtos=produtos, title=title)

# ROTA DA PÁGINA ACESSO
@app.route("/acesso", methods=['post'])
def acesso():
    usuario = "zezinho"
    senha = "1234"
    usuario_informado = request.form["usuario"]
    senha_informada = request.form["senha"]
    if usuario == usuario_informado and senha == senha_informada:
        session["login"] = True
        return redirect('/adm')
    else:
        return render_template("login.html", msg="Usuário/Senha estão incorretos!")

# ROTA DA PÁGINA LOGIN
@app.route("/login")
def login():
    title = "Login"
    return render_template("login.html", title=title)

# ROTA DA PÁGINA ADM
@app.route("/adm")
def adm():
    if verifica_sessao():
        iniciar_db()
        conexao = conecta_database()
        produtos = conexao.execute('SELECT * FROM produtos ORDER BY id_prod DESC').fetchall()
        conexao.close()
        title = "Administração"
        return render_template("adm.html", produtos=produtos, title=title)
    else:
        return redirect("/login")

# CÓDIGO DO LOGOUT
@app.route("/logout")
def logout():
    session.clear()
    return redirect('/')

# ROTA DA PÁGINA DE CADASTRO
@app.route("/cadprodutos")
def cadprodutos():
    if verifica_sessao():
        title = "Cadastro de Produtos"
        return render_template("cadprodutos.html", title=title)
    else:
        return redirect("/login")

# ROTA DA PÁGINA DE CADASTRO NO BANCO
@app.route("/cadastro", methods=["post"])
def cadastro():
    if verifica_sessao():
        try:
            nome_prod = request.form['nome_prod']
            desc_prod = request.form['desc_prod']
            preco_prod = request.form['preco_prod']
            img_prod = request.files['img_prod']

            id_foto = str(uuid.uuid4().hex)
            filename = id_foto + nome_prod + '.png'
            img_prod.save("static/img/produtos/" + filename)

            conexao = conecta_database()
            conexao.execute('INSERT INTO produtos (nome_prod, desc_prod, preco_prod, img_prod) VALUES (?, ?, ?, ?)',(nome_prod, desc_prod, preco_prod, filename))
            conexao.commit()
            conexao.close()

            return redirect("/adm")
        except Exception as e:
            print(f"Erro ao salvar a imagem: {e}")
            return redirect("/cadprodutos")
    else:
        return redirect("/login")

# ROTA PARA EXCLUIR PRODUTO
@app.route("/excluir/<int:produto_id>", methods=["GET"])
def excluir_produto(produto_id):
    if verifica_sessao():
        try:
            conexao = conecta_database()
            conexao.execute('DELETE FROM produtos WHERE id_prod = ?', (produto_id,))
            conexao.commit()
            conexao.close()
            return redirect("/adm")
        except Exception as e:
            print(f"Erro ao excluir o produto: {e}")
            return redirect("/adm")
    else:
        return redirect("/login")

# CRIAR A ROTA PARA TRATAR A EDIÇÃO
@app.route("/editarprodutos", methods=['POST'])
def editprod():
    id_prod = request.form['id_prod']
    nome_prod = request.form['nome_prod']
    desc_prod = request.form['desc_prod']
    preco_prod = request.form['preco_prod']
    img_prod = request.files['img_prod']
    id_foto = str(uuid.uuid4().hex)
    filename = id_foto + nome_prod + '.png'
    img_prod.save("static/img/produtos/" + filename)
    conexao = conecta_database()
    conexao.execute('UPDATE produtos SET nome_prod=?, desc_prod=?, preco_prod=?, img_prod=? WHERE id_prod=?',(nome_prod, desc_prod, preco_prod, filename, id_prod))
    conexao.commit()
    conexao.close()
    return redirect('/adm')

# ROTA DA PÁGINA DE BUSCA
@app.route("/busca", methods=["post"])
def busca():
    busca = request.form['buscar']
    conexao = conecta_database()
    produtos = conexao.execute('SELECT * FROM produtos WHERE nome_prod LIKE "%" || ? || "%"', (busca,)).fetchall()
    conexao.close()
    title = "Home"
    return render_template("home.html", produtos=produtos, title=title)

# CRIAR A ROTA DO EDITAR
@app.route("/editprodutos/<id_prod>")
def editar(id_prod):
    if verifica_sessao():
        iniciar_db()
        conexao = conecta_database()
        produtos = conexao.execute('SELECT * FROM produtos WHERE id_prod = ?', (id_prod,)).fetchall()
        conexao.close()
        title = "Edição de produtos"
        return render_template("editprodutos.html", produtos=produtos, title=title)
    else:
        return redirect("/login")


# FINAL DO CÓDIGO - EXECUTANDO O SERVIDOR
if __name__ == "__main__":
    app.run(debug=True)