from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.core.window import Window
import requests
import mysql.connector
from datetime import datetime
from kivy.uix.scrollview import ScrollView
API_URL = "http://186.225.224.185:5000"


class AppState:
    usuario_get = ""
    nome_usuario_letreiro = ''
    matricula_get = ''
    id_ocorrido_get = ''
    popup_atual = None

app_state = AppState()

def show_popup(titulo, mensagem):
    content = BoxLayout(orientation='vertical', spacing=10, padding=10)
    lbl_mensagem = Label(
        text=mensagem,
        size_hint_y=None,
        height=50,
        text_size=(400, None),
        halign='center',
        valign='center'
    )
    content.add_widget(lbl_mensagem)
    btn_layout = BoxLayout(orientation='horizontal', spacing=20, size_hint_y=0.3)
    btn_layout.add_widget(Label())
    btn_layout.add_widget(Button(text="Fechar", size_hint=(1, 0.5), on_release=lambda x: AppState.popup_atual.dismiss()))
    btn_layout.add_widget(Label())
    content.add_widget(btn_layout)
    AppState.popup_atual = Popup(
        title=titulo,
        content=content,
        size_hint=(0.8, 0.35),
        auto_dismiss=False
    )
    AppState.popup_atual.open()


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
            app_state.matricula_get = dados.get("matricula", "")
            return dados.get("cargo", "usuario_nao_encontrado")
        elif response.status_code == 401:
            return "senha_incorreta"
        elif response.status_code == 403:
            return "usuario_ja_conectado"
        else:
            return "usuario_nao_encontrado"
    except requests.exceptions.RequestException as e:
        return f"erro_conexao_api {e}"


def logout_usuario():
    if not app_state.usuario_get:
        return "nenhum_usuario_conectado"
    try:
        response = requests.post(f"{API_URL}/logout", json={"username": app_state.matricula_get})
        if response.status_code == 200:
            app_state.usuario_get = ""
            app_state.nome_usuario_letreiro = ""
            app_state.matricula_get = ""
            return "logout_sucesso"
        else:
            return "erro_logout"
    except requests.exceptions.RequestException as e:
        return "erro_conexao_api"


class LoginScreen(Screen):
    def on_pre_enter(self):
        Window.bind(on_keyboard=self.fechar_app)


    def on_pre_leave(self):
        Window.unbind(on_keyboard=self.fechar_app)


    def fechar_app(self, window, key, *args):
        if key == 27:
            if self.name == 'login_screen':
                App.get_running_app().stop()
                return True
            return False
        return False


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
            show_popup("Erro de senha", "Senha incorreta")
        elif cargo == "usuario_nao_encontrado":
            show_popup("Erro de Login", "Usuário não encontrado")
        elif cargo == "usuario_ja_conectado":
            show_popup("Erro de Login", "Usuário já conectado em outro dispositivo.")
        elif cargo == "erro_conexao_api":
            show_popup("Erro de Login", "Servidor indisponível no momento.")


class SupervisorScreen(Screen):
    def on_pre_enter(self):
        Window.bind(on_keyboard=self.voltar_tela)


    def on_pre_leave(self):
        Window.unbind(on_keyboard=self.voltar_tela)
    

    def atualizar_label(self):
        self.ids.letreiro.text = f'BEM VINDO {app_state.nome_usuario_letreiro}'


    def desconectar(self):
        if app_state.usuario_get:
            resultado = logout_usuario()
            if resultado == "logout_sucesso":
                app_state.usuario_get = ""
                self.manager.current = "login_screen"


    def voltar_tela(self, window, key, *args):
        if key == 27:
            self.desconectar()
            return True


class CadastroVigilanteScreen(Screen):
    def on_pre_enter(self):
        Window.bind(on_keyboard=self.voltar_tela)


    def on_pre_leave(self):
        Window.unbind(on_keyboard=self.voltar_tela)
        self.ids.nome_completo.text = ''
        self.ids.login_vigilante.text = ''
        self.ids.matricula.text = ''
        self.ids.senha1_vigilante.text = ''
        self.ids.senha2_vigilante.text = ''


    def voltar_tela(self, window, key, *args):
        if key == 27:
            if AppState.popup_atual and AppState.popup_atual.parent:
                AppState.popup_atual.dismiss()
                AppState.popup_atual = None
                return True
            self.manager.current = 'supervisor_screen'
            return True
        

    def cadastrar_vigilante(self):
        nome_completo = self.ids.nome_completo.text.strip().upper()
        login_vigilante = self.ids.login_vigilante.text.strip()
        matricula = self.ids.matricula.text.strip()
        senha1 = self.ids.senha1_vigilante.text.strip()
        senha2 = self.ids.senha2_vigilante.text.strip()
        if not nome_completo or not login_vigilante or not senha1 or not senha2 or not matricula:
            show_popup('Erro', 'Preencha todos os campos')
            return
        elif senha1 != senha2:
            show_popup('Erro', 'As senhas devem ser iguais')
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
                show_popup('Sucesso', 'Vigilante cadastrado com sucesso')
                self.ids.nome_completo.text = ""
                self.ids.login_vigilante.text = ""
                self.ids.matricula.text = ""
                self.ids.senha1_vigilante.text = ""
                self.ids.senha2_vigilante.text = ""
            elif response.status_code == 400:
                show_popup('Erro', 'Nome ou usuário já cadastrado')
            else:
                show_popup('Erro', 'Erro desconhecido ao cadastrar o vigilante')
        except requests.exceptions.RequestException as e:
            show_popup('Erro', f'{e}')


class RemoverVigilanteScreen(Screen):
    def on_pre_enter(self):
        Window.bind(on_keyboard=self.voltar_tela)


    def on_pre_leave(self):
        Window.unbind(on_keyboard=self.voltar_tela)


    def voltar_tela(self, window, key, *args):
        if key == 27:
            if AppState.popup_atual and AppState.popup_atual.parent:
                AppState.popup_atual.dismiss()
                AppState.popup_atual = None
                return True
            self.manager.current = 'supervisor_screen'
            return True


    def remover_vigilante(self):
        self.matricula_vigilante = self.ids.matricula_vigilante_remover.text.strip()
        if not self.matricula_vigilante:
            show_popup('Erro', 'Preencha a matrícula do vigilante')
            return
        try:
            response = requests.post(f"{API_URL}/vigilantes/buscar", json={"matricula": self.matricula_vigilante})
            if response.status_code == 200:
                nome_vigilante = response.json().get("nome_vigilante", "Vigilante")
                content = BoxLayout(orientation='vertical', spacing=10, padding=10)
                content.add_widget(Label(text=f"Tem certeza que deseja remover:\n{nome_vigilante}?"))
                buttons = BoxLayout(orientation='horizontal', spacing=10, size_hint=(1, 0.3))
                btn_confirmar = Button(text="Sim", on_release=self.confirmar_remocao)
                btn_cancelar = Button(text="Cancelar", on_release=self.fechar_popup)
                buttons.add_widget(btn_confirmar)
                buttons.add_widget(btn_cancelar)
                content.add_widget(buttons)
                AppState.popup_atual = Popup(title="Confirmação", content=content, size_hint=(0.8, 0.4), auto_dismiss=False)
                AppState.popup_atual.open()
                Window.bind(on_keyboard=self.fechar_popup_com_tecla)
            elif response.status_code == 404:
                show_popup('Erro', 'Vigilante não encontrado')
            elif response.status_code == 403:
                show_popup('Erro', 'Operação não autorizada!')
            else:
                show_popup('Erro', 'Erro ao buscar vigilante')
        except requests.exceptions.RequestException as e:
            show_popup('Erro', f'Erro de conexão com a API: {e}')


    def confirmar_remocao(self, instance):
        self.fechar_popup()
        try:
            response = requests.delete(f"{API_URL}/vigilantes", json={"matricula": self.matricula_vigilante})
            if response.status_code == 200:
                show_popup('Sucesso', 'Vigilante removido com sucesso')
                self.ids.matricula_vigilante_remover.text = ""
            elif response.status_code == 404:
                show_popup('Erro', 'Vigilante não encontrado')
            elif response.status_code == 403:
                show_popup('Erro', 'Operação não autorizada')
        except requests.exceptions.RequestException as e:
            show_popup('Erro', f'Erro de conexão com a API {e}')


    def fechar_popup_com_tecla(self, window, key, *args):
        if key == 27:
            self.fechar_popup()
            Window.bind(on_keyboard=self.voltar_tela)
            return True


    def fechar_popup(self, *args):
        if AppState.popup_atual:
            AppState.popup_atual.dismiss()
            AppState.popup_atual = None
            Window.unbind(on_keyboard=self.voltar_tela)



class VigilanteScreen(Screen):
    def on_pre_enter(self):
        Window.bind(on_keyboard=self.voltar_tela)


    def on_pre_leave(self):
        Window.unbind(on_keyboard=self.voltar_tela)


    def voltar_tela(self, window, key, *args):
        if key == 27:
            self.desconectar()
            return True
        

    def atualizar_label(self):
        self.ids.letreiro_vigilante.text = f'BEM VINDO {app_state.nome_usuario_letreiro}'


    def desconectar(self):
        if app_state.usuario_get:
            resultado = logout_usuario()
            if resultado == "logout_sucesso":
                app_state.usuario_get = ""
                self.manager.current = "login_screen"


class OcorrenciaScreen(Screen):
    def on_pre_enter(self):
        Window.bind(on_keyboard=self.voltar_tela)


    def on_pre_leave(self):
        Window.unbind(on_keyboard=self.voltar_tela)


    def voltar_tela(self, window, key, *args):
        if key == 27:
            if AppState.popup_atual and AppState.popup_atual.parent:
                AppState.popup_atual.dismiss()
                AppState.popup_atual = None
                return True
            self.manager.current = 'vigilante_screen'
            return True
        

    def registrar_ocorrencia(self):
        posto = self.ids.posto.text.strip().upper()
        vigilante = app_state.nome_usuario_letreiro
        matricula = app_state.matricula_get
        ocorrido = self.ids.ocorrido.text.strip().upper()
        if not all([ posto, vigilante,  matricula, ocorrido]):
            show_popup('Erro', 'Por favor preencha todos os campos')
            return
        dados_ocorrencia = {
            'posto': posto,
            'vigilante': vigilante,
            'matricula': matricula,
            'ocorrido': ocorrido
        }
        try:
            response = requests.post(f'{API_URL}/ocorrencias', json=dados_ocorrencia)
            if response.status_code == 201:
                show_popup('Sucesso', 'Ocorrência registrada com sucesso')
                self.ids.posto.text = ''
                self.ids.ocorrido.text = ''
            else:
                show_popup('Erro', 'Erro desconhecido')
        except requests.exceptions.RequestException as e:
            show_popup('Erro', f'Erro de conexão {e}')
        

    def confirmar_registro_ocorrencia(self):
        box = BoxLayout(orientation="vertical", padding=5, spacing=5)
        mensagem = Label(
            text="Aviso:\nAo prosseguir, você confirma toda a verdade contida no campo de ocorrência\n"
             "e que você é responsável pelo conteúdo apontado.",
             halign="center",
             valign="center",
             size_hint=(1, None),
             text_size=(350, None),
             height=120,
             pos_hint={"center_y": 3}
             )
        mensagem2 = Label(text='')
        mensagem3 = Label(text='')
        botoes = BoxLayout(size_hint_y=None, height=50, spacing=10)
        btn_confirmar = Button(text="Confirmar", on_release=self.registrar_ocorrencia)
        btn_cancelar = Button(text="Cancelar")
        botoes.add_widget(btn_confirmar)
        botoes.add_widget(btn_cancelar)
        box.add_widget(mensagem2)
        box.add_widget(mensagem)
        box.add_widget(mensagem3)
        box.add_widget(botoes)
        popup = Popup(
            title="Confirmação",
            content=box,
            size_hint=(None, None),
            size=(400, 450),
            auto_dismiss=False
        )
        btn_cancelar.bind(on_release=popup.dismiss)
        btn_confirmar.bind(on_release=lambda *args: (self.registrar_ocorrencia(), popup.dismiss()))
        popup.open()


class RelatorioOcorrenciaScreen(Screen):
    def on_pre_enter(self):
        self.ids.pesquisa_matricula.text = ''
        Window.bind(on_keyboard=self.voltar_tela)


    def on_pre_leave(self):
        Window.unbind(on_keyboard=self.voltar_tela)


    def carregar_ocorrencias(self):
        pesquisa_matricula = self.ids.get("pesquisa_matricula")
        if pesquisa_matricula is None:  
            show_popup('Erro', 'Erro interno: Campo de matrícula não encontrado!')
            return
        matricula = pesquisa_matricula.text.strip()
        if not matricula:
            show_popup('Erro', 'Insira a matrícula')
            return
        self.manager.get_screen('relatorio_ocorrencia2').carregar_ocorrencias(matricula)
        self.manager.current = 'relatorio_ocorrencia2'


    def voltar(self):
        self.ids.pesquisa_matricula.text = ''
        self.manager.current = "supervisor_screen"


    def voltar_tela(self, window, key, *args):
        if key == 27:
            if AppState.popup_atual and AppState.popup_atual.parent:
                AppState.popup_atual.dismiss()
                AppState.popup_atual = None
                return True
            self.voltar()
            return True


class RelatorioOcorrenciaScreen2(Screen):
    def on_pre_enter(self):
        Window.bind(on_keyboard=self.voltar_tela)


    def on_pre_leave(self):
        Window.unbind(on_keyboard=self.voltar_tela)


    def voltar_tela(self, window, key, *args):
        if key == 27:
            if AppState.popup_atual and AppState.popup_atual.parent:
                AppState.popup_atual.dismiss()
                AppState.popup_atual = None
                return True
            self.manager.current = 'relatorio_ocorrencia'
            return True


    def mostrar_item(self, texto):
        partes = texto.split()
        if partes:
            self.id_selecionado = partes[0]
            self.manager.get_screen('relatorio_ocorrencia3').ids.conteudo_ocorrido.text = f"{self.id_selecionado}"
            self.manager.current = 'relatorio_ocorrencia3'


    def carregar_ocorrencias(self, matricula):
        try:
            response = requests.get(f'{API_URL}/ocorrencias', params={"matricula": matricula})
            if response.status_code == 200:
                ocorrencias = response.json()
                rv = self.ids.rv_ocorrencias
                if not ocorrencias:
                    show_popup('Erro', 'Nenhuma ocorrencia cadastrada')
                    ocorrencias = ''
                    if rv.data:
                        rv.data = ''
                else:
                    ocorrencias.sort(key=lambda oc: datetime.strptime(oc['data_ocorrencia'], "%a, %d %b %Y %H:%M:%S GMT"), reverse=True)
                    rv.data = [
                        {"text": f"{oc['id']} - {self.formatar_data(oc['data_ocorrencia'])}"}
                        for oc in ocorrencias
                    ]
            else:
                self.ids.rv_ocorrencias.data = [{"text": f"Erro {response.status_code} ao buscar ocorrências."}]
        except requests.exceptions.RequestException as e:
            self.ids.rv_ocorrencias.data = [{"text": "Erro de conexão com a API!"}]
            show_popup('Erro', f'{e}')


    def formatar_data(self, data_str):
        try:
            data_obj = datetime.strptime(data_str, "%a, %d %b %Y %H:%M:%S GMT")
            return data_obj.strftime("%d/%m/%Y %H:%M:%S")
        except ValueError:
            return data_str


    def buscar_ocorrido(self, texto):
        partes = texto.split()
        if partes:
            self.id_selecionado = int(partes[0])
            self.manager.get_screen('relatorio_ocorrencia3').ids.conteudo_ocorrido.text = f"Selecionado: {self.id_selecionado}"
        if not hasattr(self, "id_selecionado") or not self.id_selecionado:
            show_popup("Erro", "Nenhum ID selecionado!")
        try:
            response = requests.get(f'{API_URL}/ocorrencia/{self.id_selecionado}')
            if response.status_code == 200:
                dados = response.json()
                ocorrido = dados.get("ocorrido", "Sem detalhes")
                self.manager.get_screen('relatorio_ocorrencia3').ids.conteudo_ocorrido.text = f"Ocorrido {self.id_selecionado}\n\n{ocorrido}"
                self.manager.current = 'relatorio_ocorrencia3'
            else:
                show_popup('Erro', 'Erro ao buscar o ocorrido')
        except requests.exceptions.RequestException as e:
            show_popup('Erro', f'{e}')


class RelatorioOcorrenciaScreen3(Screen):
    def on_pre_enter(self):
        Window.bind(on_keyboard=self.voltar_tela)


    def on_pre_leave(self):
        Window.unbind(on_keyboard=self.voltar_tela)


    def voltar_tela(self, window, key, *args):
        if key == 27:
            if AppState.popup_atual and AppState.popup_atual.parent:
                AppState.popup_atual.dismiss()
                AppState.popup_atual = None
                return True
            self.manager.current = 'relatorio_ocorrencia2'
            return True


class MeuGerenciador(ScreenManager):
    pass


GUI = Builder.load_file('tela.kv')
class MeuAplicativo(App):
    def build(self):
        return GUI


    def on_stop(self):
        logout_usuario()


    def fechar_aplicativo(self):
        App.get_running_app().stop()


MeuAplicativo().run()
