from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
import mysql.connector
import bcrypt
import sys
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button

nome_usuario_letreiro = ''
#Função de login
def login_usuario(nome_usuario, senha):
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Aec91a427r02j03b",
            database="banco_vigilantes")
        cursor = conn.cursor()
        cursor.execute("SELECT senha_hash, cargo, nome FROM vigilantes WHERE login = %s", (nome_usuario,))
        resultado = cursor.fetchone()
        if resultado:
            global nome_usuario_letreiro
            senha_hash_banco, cargo, nome_usuario_letreiro = resultado
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
            self.ids.nome_usuario.text = ''
            self.ids.senha_usuario.text = ''
            supervisor_screen = self.manager.get_screen("supervisor_screen")
            supervisor_screen.atualizar_label()
            self.manager.current = "supervisor_screen"
        elif cargo == "VIGILANTE":
            self.ids.nome_usuario.text = ''
            self.ids.senha_usuario.text = ''
            vigilante_screen = self.manager.get_screen('vigilante_screen')
            vigilante_screen.atualizar_label()
            self.manager.current = "vigilante_screen"
        elif cargo == "senha_incorreta":
            self.show_popup("Erro de senha", "Senha incorreta")
        elif cargo == "usuario_nao_encontrado":
            self.show_popup("Erro de Login", "Usuário não encontrado")
    

    def show_popup(self, titulo, mensagem):
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        content.add_widget(Label(text=mensagem))
        btn_layout = BoxLayout(orientation='horizontal', spacing=20, size_hint_y=0.3)
        btn_layout.add_widget(Label())
        btn_layout.add_widget(Button(text="Fechar", size_hint=(0.5, 1), on_release=lambda x: popup.dismiss()))
        btn_layout.add_widget(Label())
        content.add_widget(btn_layout)
        popup = Popup(
            title=titulo,
            content=content,
            size_hint=(0.6, 0.4),
            auto_dismiss=False,)
        popup.open()


class SupervisorScreen(Screen):
    def atualizar_label(self):
        global nome_usuario_letreiro
        self.ids.letreiro.text = f'BEM VINDO {nome_usuario_letreiro}'
    pass


class CadastroVigilanteScreen(Screen):
    def cadastrar_vigilante(self):
        nome_completo = self.ids.nome_completo.text.strip().upper()
        login_vigilante = self.ids.login_vigilante.text.strip()
        senha1 = self.ids.senha1_vigilante.text.strip()
        senha2 = self.ids.senha2_vigilante.text.strip()
        if not nome_completo or not login_vigilante or not senha1 or not senha2:
            self.ids.letreiro_feed_back.text = "Preencha todos os campos!"
            self.ids.letreiro_feed_back.color = (1, 0, 0, 1)
            return
        if senha1 != senha2:
            self.ids.letreiro_feed_back.text = "As senhas não coincidem!"
            self.ids.letreiro_feed_back.color = (1, 0, 0, 1)
            return
        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="Aec91a427r02j03b",
                database="banco_vigilantes")
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM vigilantes WHERE nome = %s OR login = %s", (nome_completo, login_vigilante))
            if cursor.fetchone():
                self.ids.letreiro_feed_back.text = "Nome ou Login já existentes!"
                self.ids.letreiro_feed_back.color = (1, 0, 0, 1)
                conn.close()
                return
            senha_criptografada = bcrypt.hashpw(senha1.encode("utf-8"), bcrypt.gensalt())
            cargo = 'VIGILANTE'
            cursor.execute(
                "INSERT INTO vigilantes (nome, cargo, senha_hash, login) VALUES (%s, %s, %s, %s)",
                (nome_completo,cargo, senha_criptografada, login_vigilante))
            conn.commit()
            conn.close()
            self.ids.letreiro_feed_back.text = "Vigilante cadastrado com sucesso!"
            self.ids.letreiro_feed_back.color = (0, 1, 0, 1)
            self.ids.nome_completo.text = ""
            self.ids.login_vigilante.text = ""
            self.ids.senha1_vigilante.text = ""
            self.ids.senha2_vigilante.text = ""
        except mysql.connector.Error as e:
            self.ids.letreiro_feed_back.text = "Erro ao acessar o banco de dados!"
            self.ids.letreiro_feed_back.color = (1, 0, 0, 1)
            print(f"Erro MySQL: {e}")
        finally:
            if conn.is_connected():
                conn.close()
    pass


class RemoverVigilanteScreen(Screen):
    conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Aec91a427r02j03b",
            database="banco_vigilantes")
    cursor = conn.cursor()


    def remover_vigilante(self):
        nome_vigilante = self.ids.nome_vigilante_remover.text.strip().upper()
        if not nome_vigilante:
            self.show_popup("Erro", "Por favor, insira o nome completo do vigilante.")
            return
        try:
            query = "SELECT nome, cargo FROM vigilantes WHERE nome = %s"
            self.cursor.execute(query, (nome_vigilante,))
            dados = self.cursor.fetchone()
            if not dados:
                self.show_popup("Aviso", f"Usuário '{nome_vigilante}' não encontrado.")
                return
            nome_do_vigilante, cargo_do_vigilante = dados
            if cargo_do_vigilante == "SUPERVISOR":
                self.show_popup("Erro", f"Você não tem permissão para remover o usuário '{nome_do_vigilante}'")
                return
            content = BoxLayout(orientation='vertical', spacing=10, padding=10)
            content.add_widget(Label(text=f"Tem certeza que deseja remover o usuário '{nome_vigilante}'?"))
            btn_layout = BoxLayout(orientation='horizontal', spacing=10)
            btn_confirmar = Button(text="Confirmar", size_hint=(0.5, None), height=40)
            btn_cancelar = Button(text="Cancelar", size_hint=(0.5, None), height=40)
            popup = Popup(
                title="Confirmação",
                content=content,
                size_hint=(0.6, 0.4),
                auto_dismiss=False,)
            btn_confirmar.bind(on_release=lambda x: self.confirmar_remocao(popup, nome_vigilante))
            btn_cancelar.bind(on_release=popup.dismiss)
            btn_layout.add_widget(btn_confirmar)
            btn_layout.add_widget(btn_cancelar)
            content.add_widget(btn_layout)
            popup.open()
        except mysql.connector.Error as e:
            self.show_popup("Erro", f"Erro ao acessar o banco de dados: {str(e)}")
    

    def confirmar_remocao(self, popup, nome_vigilante):
        try:
            query = "DELETE FROM vigilantes WHERE nome = %s"
            self.cursor.execute(query, (nome_vigilante,))
            self.conn.commit()
            self.show_popup("Sucesso", f"Usuário '{nome_vigilante}' removido com sucesso.")
        except mysql.connector.Error as e:
            self.show_popup("Erro", f"Erro ao remover o vigilante: {str(e)}")
        finally:
            popup.dismiss()
        
    
    def show_popup(self, titulo, mensagem):
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        content.add_widget(Label(text=mensagem))
        btn_layout = BoxLayout(orientation='horizontal', spacing=20, size_hint_y=0.3)
        btn_layout.add_widget(Label())
        btn_layout.add_widget(Button(text="Fechar", size_hint=(0.5, 1), on_release=lambda x: popup.dismiss()))
        btn_layout.add_widget(Label())
        content.add_widget(btn_layout)
        popup = Popup(
            title=titulo,
            content=content,
            size_hint=(0.6, 0.4),
            auto_dismiss=False,)
        popup.open()
    pass


class VigilanteScreen(Screen):
    def atualizar_label(self):
        global nome_usuario_letreiro
        self.ids.letreiro_vigilante.text = f'BEM VINDO {nome_usuario_letreiro}'
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