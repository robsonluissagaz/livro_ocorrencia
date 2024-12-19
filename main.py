from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
import mysql.connector
import bcrypt
import sys


#Função de login
def login_usuario(nome_usuario, senha):
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Aec91a427r02j03b",
            database="banco_vigilantes")
        cursor = conn.cursor()
        cursor.execute("SELECT senha_hash, cargo FROM vigilantes WHERE login = %s", (nome_usuario,))
        resultado = cursor.fetchone()
        if resultado:
            senha_hash_banco, cargo = resultado
            if bcrypt.checkpw(senha.encode('utf-8'), senha_hash_banco.encode('utf-8')):
                cursor.close()
                conn.close()
                return cargo
            else:
                cursor.close()
                conn.close()
                return 'senha_incorreta'
        else:
            cursor.close()
            conn.close()
            return "usuario_nao_encontrado"



class LoginScreen(Screen):
    def verificar_login(self):
        nome = self.ids.nome_usuario.text
        senha = self.ids.senha_usuario.text
        cargo = login_usuario(nome, senha)
        if cargo == "SUPERVISOR":
            self.manager.current = "supervisor_screen"
        elif cargo == "VIGILANTE":
            self.manager.current = "vigilante_screen"
        elif cargo == "senha_incorreta":
            self.manager.current = "erro_senha_usuario"
        elif cargo == "usuario_nao_encontrado":
            self.manager.current = "erro_senha_usuario"


class SupervisorScreen(Screen):
    pass


class VigilanteScreen(Screen):
    pass


class ErroSenhaUsuarioScreen(Screen):
    pass


class MeuGerenciador(ScreenManager):
    pass


GUI = Builder.load_file('tela.kv')

class MeuAplicativo(App):

    def build(self):
        return GUI
    

    def fechar_aplicativo(self):
        App.get_running_app().stop()
        sys.exit() 


MeuAplicativo().run()