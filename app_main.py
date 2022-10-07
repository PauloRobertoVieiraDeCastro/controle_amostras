from flask import Flask, render_template, request, redirect, session, flash, url_for
from flask import send_from_directory,send_file
from flask_mysqldb import MySQL
from flask_bcrypt import check_password_hash
from amostra import*
from dao_amostras import*
import json
import plotly
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd


app = Flask(__name__)
app.config['MYSQL_HOST'] = "localhost"
app.config['MYSQL_USER'] = "root"
app.config['MYSQL_PASSWORD'] = "cimento1"
app.config['MYSQL_DB'] = "petroleo"
app.config['MYSQL_PORT'] = 3306
app.secret_key = 'cimento1' #ela é essencial para deletar dados do banco
db = MySQL(app)
atividade_dao = DAO(db)

@app.route("/login")
def sessao():
    return render_template("sessao.html")

@app.route("/autenticar", methods=['POST',])
def autenticar():
    chave = request.form['chave'].upper()
    senha = request.form['senha']
    ch,password=[],[]
    for x,y in atividade_dao.usuario():
        ch.append(x)
        password.append(y)
    df1=pd.DataFrame([ch,password]).T
    df1.columns = ['Chave','Senha']
    df1.set_index("Chave",inplace=True)

    s = df1.loc[chave]['Senha']#check_password_hash(senha, df1.loc[chave]['Senha'])
    print(s)
    if(chave in df1.index and df1.loc[chave]['Senha']==senha):
        session['usuario_logado'] = chave
        flash(chave + " logado com sucesso")
        return redirect(url_for("teste"))
    else:
        flash("Senha e/ou usuário incorretos")
        return redirect(url_for("sessao"))

@app.route('/logout')
def logout():
    session['usuario_logado'] = None
    #chave = None
    #senha = None
    flash('Logout efetuado com sucesso!')
    return redirect(url_for('sessao'))

@app.route("/",methods=['GET','POST'])
def teste():
    lista = atividade_dao.listar()
    lista_count = atividade_dao.dash_count()
    p,q=[],[]
    for i,j in lista_count:
        p.append(i)
        q.append(j)
    return render_template('lista_amostras.html',lista=lista)

@app.route('/deletar/<int:ide>')
def deletar(ide):
    atividade_dao.apagar(ide)
    flash("A tarefa foi removida com sucesso")
    return redirect(url_for('teste'))

@app.route('/editar/<int:ide>')
def editar(ide):
    lista = atividade_dao.busca_por_id(ide)
    return render_template('edita_amostra.html', lista=lista)

@app.route('/atualizar', methods=['POST',])
def atualizar():
    nome = request.form['nome']
    qtd = request.form['quantidade']
    recipiente = request.form['recipiente']
    tipo = request.form['tipo']
    local = request.form['local']
    numeracao = request.form['numeracao']
    data = ""
    texto = ""
    lista = Amostras(numeracao,nome,float(qtd),recipiente,tipo,local,texto,data,ide=request.form['ide'])
    atividade_dao.salvar(lista)
    return redirect(url_for('teste'))



@app.route('/criar', methods=['POST',])
def criar():
    nome_amostra = request.form['nome_amostra']
    tipo_amostra = request.form['tipo_amostra']
    rec = [i for i in request.form.getlist('rec')]
    qtd = [float(i) for i in request.form.getlist('qtd')]
    local = [i for i in request.form.getlist('local')]
    lista_count = atividade_dao.dash_count()
    p,q=[],[]
    for i,j in lista_count:
        p.append(i)
        q.append(j)
    df=pd.DataFrame([p,q]).T
    numeracao = len(df)+1
    numeracao = [str(numeracao)+chr(65+i) for i in range(len(qtd))]
    data = ""
    texto = ""
    
    for i in range(len(qtd)):
        lista = Amostras(numeracao[i],nome_amostra,qtd[i],rec[i],tipo_amostra,local[i],texto,data)
        atividade_dao.salvar(lista)
    
    return redirect(url_for('teste'))

@app.route('/inserir')
def nova_amostra():
    lista_count = atividade_dao.dash_count()
    p,q=[],[]
    for i,j in lista_count:
        p.append(i)
        q.append(j)
    df=pd.DataFrame([p,q]).T
    return render_template("inserir_amostra.html",amostra_num=len(df)+1)


@app.route('/estatistica',methods=['POST','GET'])
def estatistica():
    lista_count = atividade_dao.dash_count()
    lista_select = atividade_dao.dash_select()
    p,q=[],[]
    for i,j in lista_count:
        p.append(i)
        q.append(j)
    df=pd.DataFrame([p,q]).T
    df.columns=['Amostra','Quantidade']

    n,n1,nome,qtd,tipo,tipo,local,local2,texto,data=[],[],[],[],[],[],[],[],[],[]
    for g,h,i,j,k,l,m,n,o in lista_select:
        nome.append(i)
        qtd.append(j)
        tipo.append(k)
        local.append(l)
        local2.append(m)
    dff=pd.DataFrame([nome,qtd,tipo,local,local2]).T
    dff.columns = ["Nome","Quantidade","Recipiente","Tipo","Local"]
    total = dff['Quantidade'].sum()
    quant = len(df)

    amostra_menor = dff.groupby('Nome')['Quantidade'].sum().sort_index(ascending=True).index[0]
    amostra_qtd_menor = dff.groupby('Nome')['Quantidade'].sum().sort_index(ascending=True)[0]
    print(amostra_qtd_menor)
    
    #configuraçoes dos graficos
    config = {'responsive': True}
    fig1 = px.histogram(dff, y='Quantidade', x='Local',title="Quantidade de amostra por local", hover_data=['Local'],color='Local')
    fig2 = px.pie(dff, values="Quantidade", names="Tipo", title='Quantidade de amostra por tipo', hover_data=['Tipo'])#px.pie(labels=dv.index.values,values=dv.values)
    fig3 = px.histogram(dff, y='Quantidade', x='Nome',title="Quantidade de amostra por local", hover_data=['Local'],color='Local', barmode='group')
    
    graphJSON1 = json.dumps(fig1, cls=plotly.utils.PlotlyJSONEncoder)
    graphJSON2 = json.dumps(fig2, cls=plotly.utils.PlotlyJSONEncoder)
    graphJSON3 = json.dumps(fig3, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template("dashboard.html", graphJSON=[graphJSON1,graphJSON2,graphJSON3], total=round(total,1), quant = quant,
                           amostra_menor = amostra_menor, amostra_qtd_menor = amostra_qtd_menor)



if __name__=="__main__":
    app.run(debug=True)
