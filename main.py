from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
import mysql.connector
import sys
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
import requests

API_URL = "http://186.225.224.185:5000"


class AppState:
    usuario_get = ""
    nome_usuario_letreiro = ''

app_state = AppState()


def login_usuario(nome_usuario, senha):
    payload = {
        "username": nome_usuario,
        "password": senha
    }
    try:
        response = requests.post(f"{API_URL}/login", json=payload)
        if response.status_code == 200:
            dados = response.json()
            app_state.nome_usuario_letreiro = dados.get("nome", "")
            app_state.usuario_get = dados.get("login", "")
            return dados.get("cargo", "usuario_nao_encontrado")
        elif response.status_code == 401:
            return "senha_incorreta"
        elif response.status_code == 403:
            return "usuario_ja_conectado"
        else:
            return "usuario_nao_encontrado"
    except requests.exceptions.RequestException as e:
        return "erro_conexao_api"


def logout_usuario():
    if not app_state.usuario_get:
        print("Erro: Nenhum usuário conectado para desconectar.")
        return "nenhum_usuario_conectado"

    try:
        response = requests.post(f"{API_URL}/logout", json={"username": app_state.usuario_get})
        if response.status_code == 200:
            print(f"Usuário desconectado: {app_state.usuario_get}")
            app_state.usuario_get = ""
            return "logout_sucesso"
        else:
            print("Erro ao desconectar o usuário.")
            return "erro_logout"
    except requests.exceptions.RequestException as e:
        print("Erro de conexão com a API.")
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
        elif cargo == "usuario_ja_conectado":
            self.show_popup("Erro de Login", "Usuário já conectado em outro dispositivo.")
        elif cargo == "erro_conexao_api":
            self.show_popup("Erro de Login", "Servidor indisponível no momento.")


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
        self.ids.letreiro.text = f'BEM VINDO {app_state.nome_usuario_letreiro}'


    def desconectar(self):
        if app_state.usuario_get:
            resultado = logout_usuario()
            if resultado == "logout_sucesso":
                app_state.usuario_get = ""
                self.manager.current = "login_screen"


class CadastroVigilanteScreen(Screen):
    def cadastrar_vigilante(self):
        nome_completo = self.ids.nome_completo.text.strip().upper()
        login_vigilante = self.ids.login_vigilante.text.strip()
        matricula = self.ids.matricula.text.strip()
        senha1 = self.ids.senha1_vigilante.text.strip()
        senha2 = self.ids.senha2_vigilante.text.strip()
        if not nome_completo or not login_vigilante or not senha1 or not senha2 or not matricula:
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
            'matricula': matricula,
            "senha": senha1
        }
        try:

            response = requests.post(f"{API_URL}/vigilantes", json=payload)
            if response.status_code == 201:
                self.ids.letreiro_feed_back.text = "Vigilante cadastrado com sucesso!"
                self.ids.letreiro_feed_back.color = (0, 1, 0, 1)
                self.ids.nome_completo.text = ""
                self.ids.login_vigilante.text = ""
                self.ids.matricula.text = ""
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
        self.ids.letreiro_vigilante.text = f'BEM VINDO {app_state.nome_usuario_letreiro}'
    

    def desconectar(self):
        if app_state.usuario_get:
            resultado = logout_usuario()
            if resultado == "logout_sucesso":
                app_state.usuario_get = ""
                self.manager.current = "login_screen"

    pass


class OcorrenciaScreen(Screen):
    pass


class MeuGerenciador(ScreenManager):
    pass


GUI = Builder.load_file('tela.kv')
class MeuAplicativo(App):
    def build(self):
        return GUI
    

    def fechar_aplicativo(self):
        App.get_running_app().stop()


MeuAplicativo().run()