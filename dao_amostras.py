from amostra import*
SQL_BUSCA = 'SELECT Ident, Numeracao, Nome, Peso, Recipiente, Tipo, Localizacao, Observacoes, Data_amostra FROM amostras'
SQL_DELETA = 'DELETE FROM amostras WHERE Ident = %s'
SQL_CRIA = 'INSERT INTO amostras (Numeracao, Nome, Tipo, Peso, Recipiente, Localizacao) VALUES (%s, %s, %s, %s, %s, %s)'
SQL_ATUALIZAR = 'UPDATE amostras SET Nome=%s, Peso=%s, Recipiente=%s, Tipo=%s, Localizacao=%s WHERE Ident = %s'
SQL_POR_ID = 'SELECT Ident, Numeracao, Nome, Peso, Recipiente, Tipo, Localizacao, Observacoes, Data_amostra FROM amostras WHERE Ident = %s'
SQL_COUNT = 'SELECT Nome, COUNT(Nome) AS Contagem FROM amostras GROUP BY Nome;'
SQL_USUARIO = 'SELECT Chave, Senha FROM Sessoes'


class DAO:
    def __init__(self, db):
        self.__db = db

    def listar(self):
        cursor = self.__db.connection.cursor()
        cursor.execute(SQL_BUSCA)
        atividade = traduz_atividade(cursor.fetchall())
        return atividade

    def apagar(self,ide):
        cursor = self.__db.connection.cursor()
        cursor.execute(SQL_DELETA, (ide,))
        self.__db.connection.commit()

    def busca_por_id(self, ide):
        cursor = self.__db.connection.cursor()
        cursor.execute(SQL_POR_ID, (ide,))
        tupla = cursor.fetchone()
        return Amostras(tupla[1],tupla[2],tupla[3], tupla[4], tupla[5], tupla[6], tupla[7], tupla[8], ide=tupla[0])

    def salvar(self,lista):
        cursor = self.__db.connection.cursor() #cursor para acessar o db
        if lista.ide:
            cursor.execute(SQL_ATUALIZAR,(lista.nome,lista.peso,lista.recipiente,lista.tipo,lista.local,lista.ide))
        else:
            cursor.execute(SQL_CRIA, (lista.numeracao, lista.nome, lista.tipo, lista.peso, lista.recipiente, lista.local))
        self.__db.connection.commit()
        return lista

    def usuario(self):
        cursor = self.__db.connection.cursor()
        cursor.execute(SQL_USUARIO)
        a = cursor.fetchall()
        return a

    def dash_count(self):
        cursor = self.__db.connection.cursor()
        cursor.execute(SQL_COUNT)
        atividade_count = cursor.fetchall()
        return atividade_count

    def dash_select(self):
        cursor = self.__db.connection.cursor()
        cursor.execute(SQL_BUSCA)
        atividade_select = cursor.fetchall()
        return atividade_select

def traduz_atividade(atividades):
    def cria_atividade_com_tupla(tupla):
        return Amostras(tupla[1],tupla[2],tupla[3], tupla[4], tupla[5], tupla[6], tupla[7], tupla[8], ide=tupla[0])
        
    return list(map(cria_atividade_com_tupla, atividades))   

