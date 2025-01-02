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
import requests

API_URL = "http://192.168.255.88:5000"
nome_usuario_letreiro = ''

#Função de login
def login_usuario(nome_usuario, senha):
    payload = {
        "username": nome_usuario,
        "password": senha
    }
    try:
        response = requests.post(f"{API_URL}/login", json=payload)
        if response.status_code == 200:
            dados = response.json()
            global nome_usuario_letreiro
            nome_usuario_letreiro = dados.get("nome", "")
            return dados.get("cargo", "usuario_nao_encontrado")
        elif response.status_code == 401:
            return "senha_incorreta"
        else:
            return "usuario_nao_encontrado"
    except requests.exceptions.RequestException as e:
        print(f"Erro ao se conectar à API: {e}")
        return "erro_conexao_api"


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
        payload = {
            "nome": nome_completo,
            "login": login_vigilante,
            "senha": senha1
        }
        try:

            response = requests.post(f"{API_URL}/vigilantes", json=payload)
            if response.status_code == 201:
                self.ids.letreiro_feed_back.text = "Vigilante cadastrado com sucesso!"
                self.ids.letreiro_feed_back.color = (0, 1, 0, 1)
                self.ids.nome_completo.text = ""
                self.ids.login_vigilante.text = ""
                self.ids.senha1_vigilante.text = ""
                self.ids.senha2_vigilante.text = ""
            elif response.status_code == 400:
                erro = response.json().get("error", "Erro ao cadastrar vigilante!")
                self.ids.letreiro_feed_back.text = erro
                self.ids.letreiro_feed_back.color = (1, 0, 0, 1)
            else:
                self.ids.letreiro_feed_back.text = "Erro desconhecido ao cadastrar!"
                self.ids.letreiro_feed_back.color = (1, 0, 0, 1)
        except requests.exceptions.RequestException as e:
            self.ids.letreiro_feed_back.text = "Erro ao se conectar à API!"
            self.ids.letreiro_feed_back.color = (1, 0, 0, 1)
            print(f"Erro de conexão com a API: {e}")


class RemoverVigilanteScreen(Screen):
    def remover_vigilante(self):
        nome_vigilante = self.ids.nome_vigilante_remover.text.strip().upper()
        if not nome_vigilante:
            self.ids.letreiro_feed_back.text = "Preencha o nome do vigilante!"
            self.ids.letreiro_feed_back.color = (1, 0, 0, 1)
            return
        def confirmar_remocao(instance):
            popup.dismiss()
            try:
                response = requests.delete(f"{API_URL}/vigilantes", json={"nome": nome_vigilante})
                if response.status_code == 200:
                    self.ids.letreiro_feed_back.text = "Vigilante removido com sucesso!"
                    self.ids.letreiro_feed_back.color = (0, 1, 0, 1)
                    self.ids.nome_vigilante_remover.text = ""
                elif response.status_code == 400:
                    erro = response.json().get("error", "Erro ao remover vigilante!")
                    self.ids.letreiro_feed_back.text = erro
                    self.ids.letreiro_feed_back.color = (1, 0, 0, 1)
                else:
                    self.ids.letreiro_feed_back.text = "Erro desconhecido ao remover!"
                    self.ids.letreiro_feed_back.color = (1, 0, 0, 1)
            except requests.exceptions.RequestException as e:
                self.ids.letreiro_feed_back.text = "Erro ao se conectar à API!"
                self.ids.letreiro_feed_back.color = (1, 0, 0, 1)
                print(f"Erro de conexão com a API: {e}")
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        content.add_widget(Label(text=f"Tem certeza que deseja remover '{nome_vigilante}'?"))
        buttons = BoxLayout(orientation='horizontal', spacing=10, size_hint=(1, 0.3))
        btn_confirmar = Button(text="Sim", on_release=confirmar_remocao)
        btn_cancelar = Button(text="Cancelar", on_release=lambda instance: popup.dismiss())
        buttons.add_widget(btn_confirmar)
        buttons.add_widget(btn_cancelar)
        content.add_widget(buttons)
        popup = Popup(title="Confirmação", content=content, size_hint=(0.6, 0.4), auto_dismiss=False)
        popup.open()


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