
from tkinter import *
from ttkwidgets.autocomplete import AutocompleteEntry
from tkinter import ttk
from datetime import datetime
from tkinter import messagebox
from tkcalendar import Calendar
from reportlab.platypus import SimpleDocTemplate, Image
from PIL import ImageTk, Image

import sqlite3
import os
import base64
import webbrowser
import pygame
import cv2

root = Tk()

try:
    os.remove("nova_foto.png")
    os.remove("visual.png")
except:
    pass

class Funcoes():
    def conect_db_consultas(self):
        self.conexao = sqlite3.connect('agendamento_paciente.sqlite3')
        self.cursor = self.conexao.cursor()
###

    def desconect_db_consultas(self):

        self.conexao.close()

    def tabelaConsulta(self):
        self.conect_db_consultas()

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS paciente1 (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        Nome TEXT NOT NULL,
        dia TEXT NOT NULL UNIQUE,
        telefone TEXT);""")

        self.conexao.commit()
        self.desconect_db_consultas()

    def limpar_agendamento(self):
        self.marcar_id.delete(0, END)
        self.marcar_nome.delete(0, END)
        self.marcar_dia.delete(0, END)
        self.marcar_telefone.delete(0, END)

    def capturar_agendamento(self):
        self.codigo = self.marcar_id.get()
        self.nome = self.marcar_nome.get()
        self.dia= self.marcar_dia.get()
        self.telefone = self.marcar_telefone.get()

    def inserir_marcar_consultas(self):
        #self.limpar_agendamento()
        self.capturar_agendamento()
        self.conect_db_consultas()

        if self.marcar_nome.get() == '':
            msg = 'FAVOR PREENCHER O CAMPO NOME'
            messagebox.showwarning('AGENDAMENTO DE PACIENTE',msg)

            self.marcar_consulta()

        elif self.marcar_dia.get() == '':
            msg = 'FAVOR PREENCHER O CAMPO DATA'
            messagebox.showwarning('AGENDAMENTO DE PACIENTE', msg)
            self.marcar_consulta()

        else:
            try:
                self.conect_db_consultas()
                self.cursor.execute("""INSERT INTO paciente1 (nome,dia,telefone)
                VALUES (?,?,?) """, ((self.nome).upper().strip(), self.dia, self.telefone))

                self.conexao.commit()
                self.desconect_db_consultas()
                self.limpar_agendamento()

                msg = 'PACIENTE AGENDADO'
                messagebox.showinfo('AGENDAMENTO DE PACIENTE', msg)

                self.marcar_consulta()

            except:
                msg = 'HORARIO INDISPONÍVEL'
                messagebox.showwarning('AGENDAMENTO DE PACIENTE', msg)
                self.desconect_db_consultas()

                self.marcar_consulta()

    def listar_agenda(self):
        self.lista_agenda.delete(*self.lista_agenda.get_children())
        self.conect_db_consultas()
        lista = self.cursor.execute("""SELECT id,nome,dia,telefone FROM paciente1 ORDER BY nome ASC;""")

        for l in lista:
            self.lista_agenda.insert("", END, values=l)
        self.desconect_db_consultas()

    def pesquisar_agendamento(self):
        self.lista_agenda.delete(*self.lista_agenda.get_children())
        self.conect_db_consultas()

        nome = '%' + self.marcar_nome.get()

        self.cursor.execute("""SELECT * FROM paciente1 WHERE Nome LIKE '%s' COLLATE NOCASE ORDER BY Nome ASC""" % nome)
        buscar_agenda = self.cursor.fetchmany()
        self.limpar_agendamento()

        try:
            for cliente in buscar_agenda:
                self.lista_agenda.insert("", END, values=cliente)
                self.desconect_db_consultas()

                if buscar_agenda != False:
                    self.click_agendamento()

                    self.desconect_db_consultas()
                    self.limpar_agendamento()
            else:
                self.desconect_db_consultas()
                slice = nome[1::].upper()

                msg = f'PACIENTE **{slice}** NÃO FOI AGENDADO'
                messagebox.showwarning('AGENDAMENTO DO PACIENTE',msg)

                self.marcar_consulta()
        except:
            pass

    def deletar_agenda(self):
        self.capturar_agendamento()
        self.conect_db_consultas()

        self.cursor.execute("""DELETE FROM paciente1 WHERE id = ? """, [self.codigo])

        self.conexao.commit()
        self.limpar_agendamento()
        self.desconect_db_consultas()

        try:
            self.item_selecionado = self.lista_agenda.selection()[0]
            self.lista_agenda.delete(self.item_selecionado)
        except:
            messagebox.showerror('       **** ERROR ****', message='SELECIONE UM ITEM A SER DELETADO')

            self.marcar_consulta()

    def deletar_db_agenda(self):

        deletar = messagebox.askquestion('AGENDAMENTO', 'DESEJA DELETAR TODO O AGENDAMENTO DA SEMANA ?', icon='error')

        if deletar == 'yes':
            self.capturar_agendamento()
            self.conect_db_consultas()

            self.cursor.execute("""DELETE FROM paciente1 """)

            self.conexao.commit()
            self.limpar_agendamento()
            self.desconect_db_consultas()
            self.marcar_consulta()
        else:
            self.marcar_consulta()

    def marcar_consulta(self):
        from agendamento import agenda

        self.root3 = Toplevel()

        self.imageFundo = PhotoImage(data=base64.b64decode(agenda))
        self.labelFundo = Label(self.root3, bd=0, image=self.imageFundo)
        self.labelFundo.pack()

        self.root3.configure(background='green')
        self.root3.geometry('690x476')

        self.widgets_root3()

    def widgets_root3(self):
        self.marcar_id = Entry(self.root3)
        self.marcar_id.place()

        self.marcar_nome = Entry(self.root3, font=('arial', 13, 'bold'))
        self.marcar_nome.place(x=198, y=83, width=280, height=25)

        self.marcar_dia = ttk.Combobox(self.root3, font=('arial', 13, 'bold'),
                                       values=["SEGUNDA  ÀS    8:30", "SEGUNDA  ÀS   9:00", "SEGUNDA  ÀS   9:30",
                                                  "SEGUNDA  ÀS  10:00", "SEGUNDA  ÀS  10:30", "SEGUNDA  ÀS  11:00",
                                                  "SEGUNDA  ÀS  14:00", "SEGUNDA  ÀS  14:30", "SEGUNDA  ÀS  15:00",
                                                  "SEGUNDA  ÀS  15:30",
                                                  "TERÇA        ÀS  8:30", "TERÇA        ÀS  9:00", "TERÇA        ÀS  9:30",
                                                  "TERÇA        ÀS 10:00", "TERÇA        ÀS 10:30", "TERÇA       ÀS 11:00",
                                                  "TERÇA       ÀS 14:00", "TERÇA       ÀS 14:30", "TERÇA       ÀS 15:00",
                                                  "TERÇA       ÀS 15:30",
                                                  "QUARTA    ÀS  8:30", "QUARTA    ÀS  9:00", "QUARTA    ÀS  9:30",
                                                  "QUARTA    ÀS 10:00", "QUARTA    ÀS 10:30", "QUARTA    ÀS 11:00",
                                                  "QUARTA    ÀS 14:00", "QUARTA    ÀS 14:30", "QUARTA    ÀS 15:00",
                                                  "QUARTA    ÀS 15:30",
                                                  "QUINTA     ÀS  8:30", "QUINTA     ÀS  9:00", "QUINTA     ÀS  9:30",
                                                  "QUINTA    ÀS  10:00", "QUINTA    ÀS  10:30", "QUINTA    ÀS  11:00",
                                                  "QUINTA    ÀS  14:00", "QUINTA    ÀS  14:30", "QUINTA    ÀS  15:00",
                                                  "QUINTA    ÀS  15:30",
                                                  "SEXTA       ÀS    8:30", "SEXTA       ÀS    9:00", "SEXTA       ÀS    9:30",
                                                  "SEXTA       ÀS  10:00", "SEXTA       ÀS  10:30", "SEXTA       ÀS  11:00",
                                                  "SEXTA       ÀS  14:00", "SEXTA       ÀS  14:30", "SEXTA       ÀS  15:00",
                                                  "SEXTA       ÀS  15:30"])
        self.marcar_dia.place(x=198, y=148, width=200, height=25)

        self.marcar_telefone = Entry(self.root3, font=('arial', 13, 'bold'))
        self.marcar_telefone.place(x=198, y=213, width=200, height=25)

        self.bt_marcar = Button(self.root3, text='AGENDAR', command=self.inserir_marcar_consultas)
        self.bt_marcar.place(x=150, y=270, width=80, height=25)

        self.bt_desmarcar = Button(self.root3, text='DESMARCAR', command=self.deletar_agenda)
        self.bt_desmarcar.place(x=250, y=270, width=80, height=25)

        self.bt_pesquisar = Button(self.root3, text='PESQUISAR', command=self.pesquisar_agendamento)
        self.bt_pesquisar.place(x=350, y=270, width=80, height=25)

        self.bt_buscar = Button(self.root3, text='LISTAR', command=self.listar_agenda)
        self.bt_buscar.place(x=450, y=270, width=80, height=25)

        from botoes_image import agendamento7

        self.deletar_db =  PhotoImage(data=base64.b64decode(agendamento7))
        self.deletar_db = self.deletar_db.subsample(3, 3)
        self.deletar_db1 = Label(self.root3, image=self.deletar_db)
        self.deletar_db1.image = self.deletar_db

        self.bt_deletar_db = Button(self.root3, image=self.deletar_db, bd=0, bg='#001500', highlightthickness=0, command=self.deletar_db_agenda, relief=FLAT )
        self.bt_deletar_db.place(x=620, y=300, width=50, height=50)

        self.grid_agendamento()

    def grid_agendamento(self):
        self.lista_agenda = ttk.Treeview(self.root3, columns=('col0', 'col1', 'col2', 'col3', 'col4'))
        self.lista_agenda.heading("#0", text='')
        self.lista_agenda.heading("#1", text='CÓDIGO')
        self.lista_agenda.heading("#2", text='NOME')
        self.lista_agenda.heading("#3", text='DIA /HORA')
        self.lista_agenda.heading("#4", text='TELEFONE')

        self.lista_agenda.column("#0", width=0)
        self.lista_agenda.column("#1", width=180)
        self.lista_agenda.column("#2", width=160)
        self.lista_agenda.column("#3", width=145)
        self.lista_agenda.column("#4", width=145)

        self.lista_agenda.place(x=25, y=350, width=640, height=120)
        self.lista_agenda.bind("<Double-1>", self.click_agendamento)

    def click_agendamento(self, e):
        self.limpar_agendamento()

        self.lista_agenda.selection()

        for x in self.lista_agenda.selection():
            col0, col1, col2, col3 = self.lista_agenda.item(x, 'values')

            self.marcar_id.insert(END, col0)
            self.marcar_nome.insert(END, col1)
            self.marcar_dia.insert(END, col2)
            self.marcar_telefone.insert(END, col3)

    def limpar_campos(self):

        try:
            os.remove("nova_foto.png")
            os.remove("visual.png")
        except:

            self.entry_codigo.delete(0, END)
            self.entry_nome.delete(0, END)
            self.entry_nascimento.delete(0, END)
            self.entry_civil.delete(0, END)
            self.entry_religiao.delete(0, END)
            self.entry_profissao.delete(0, END)
            self.entry_cidade.delete(0, END)
            self.entry_estado.delete(0, END)
            self.entry_dataConsulta.delete(0, END)
            self.entry_observacao.delete('1.0', END)
            #self.entry_receita.delete('1.0', END)
            self.entry_anos.delete(0, END)
            self.entry_telefone.delete(0, END)
            self.entry_tipo.delete(0, END)

            self.entry_idade = Label(self.root, bg=self.lb_bg)
            self.entry_idade.place(x=913, y=123, width=95, height=27)

            from botoes_image import m_fotografica

            self.entry_receita = PhotoImage(data=base64.b64decode(m_fotografica))
            self.entry_receita = self.entry_receita.subsample(5, 5)
            self.entry_receita1 = Label(self.root, image=self.entry_receita)
            self.entry_receita1.image = self.entry_receita

            self.entry_receita = Button(self.root, image=self.entry_receita, bg=self.lb_bg, activebackground=self.lb_bg,
                                        bd=0, highlightthickness=0, command=self.foto)
            self.entry_receita.place(x=710, y=180, width=210, height=140)

    def db_conect(self):
        self.conexao = sqlite3.connect('clientes2_db.sqlite3')
        self.cursor = self.conexao.cursor()

    def db_desconect(self):
        self.conexao.close()

    def criar_tabela(self):
        self.db_conect()

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        Nome TEXT NOT NULL UNIQUE,
        civil TEXT NOT NULL,
        religiao TEXT NOT NULL,
        profissao TEXT NOT NULL,
        cidade TEXT NOT NULL,
        estado TEXT NOT NULL,
        telefone TEXT,
        data TEXT,
        nascimento TEXT NOT NULL,
        idade TEXT,
        tipo TEXT,
        observacao TEXT NOT NULL,
        im BLOB NOT NULL
        );""");

        self.conexao.commit()
        self.db_desconect()

    def capturar_campos(self):
        try:
            self.codigo = self.entry_codigo.get()
            self.nome = self.entry_nome.get()
            self.civil = self.entry_civil.get()
            self.religiao = self.entry_religiao.get()
            self.profissao = self.entry_profissao.get()
            self.cidade = self.entry_cidade.get()
            self.estado = self.entry_estado.get()
            self.telefone = self.entry_telefone.get()
            self.data = self.entry_dataConsulta.get()
            self.nascimento = self.entry_nascimento.get()
            self.idade = self.entry_idade.get()
            self.tipo = self.entry_tipo.get()
            self.observacao = self.entry_observacao.get('1.0', END)

            self.ima = open('nova_foto.png', 'rb').read()

        except:
            pass

    def inserir_dados(self):
        self.capturar_campos()
        self.db_conect()

        if self.entry_nome.get() == '':
            msg = 'FAVOR PREENCHER O CAMPO NOME'
            messagebox.showwarning('Cadastro de paciente',msg)

        elif self.entry_nascimento.get() == '':
            msg = 'FAVOR PREENCHER O CAMPO DATA DE NASCIMENTO'
            messagebox.showwarning('Cadastro de paciente',msg)

        elif self.entry_idade.get() == '':
            msg = 'FAVOR CLICAR NO BOTÃO NASCIMENTO'
            messagebox.showwarning('Cadastro de paciente',msg)

        else:
            try:
                self.db_conect()
                self.cursor.execute("""INSERT INTO clientes (nome,civil,religiao,profissao,cidade,estado,telefone,data,nascimento,idade,tipo,observacao,im)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?) """, ((self.nome).upper().strip(), self.civil, self.religiao, self.profissao, self.cidade, self.estado, self.telefone, self.data, self.nascimento, self.idade, self.tipo , self.observacao, self.ima))

                self.conexao.commit()
                self.db_desconect()
                self.limpar_campos()

                msg = 'PACIENTE CADASTRADO'
                messagebox.showinfo('Cadastro de paciente', msg)
                principal()

            except:
                msg = 'PACIENTE JÁ CADASTRADO'
                messagebox.showwarning('Cadastro de paciente', msg)
                self.db_desconect()
                self.limpar_campos()
                principal()

    def pesquisar(self):
        self.db_conect()

        self.lista_grid.delete(*self.lista_grid.get_children())

        nome = '%' + self.entry_nome.get().strip()

        if self.entry_nome.get() == '':
            msg = 'FAVOR PREENCHER O CAMPO NOME'
            messagebox.showwarning('Cadastro de paciente',msg)

        else:
            self.cursor.execute("""SELECT * FROM clientes WHERE nome LIKE '%s' COLLATE NOCASE  ORDER BY Nome ASC""" % nome)
            self.resultado_busca = self.cursor.fetchmany()

            try:
                for self.cliente in self.resultado_busca:
                    self.lista_grid.insert("", END, values= self.cliente)

                    self.db_desconect()

                    if self.resultado_busca != False:
                        self.click()
                        self.db_desconect()
                        self.limpar_campos()

                else:
                    self.db_desconect()

                    slice = nome[1::].upper()

                    msg = f'PACIENTE  "{slice}"  NÃO ESTÁ CADASTRADO'
                    messagebox.showwarning('Cadastro de Paciente', msg)

                    self.limpar_campos()
            except:
                pass

    def pesquisar2(self):
        self.db_conect()

        nome = '%' + self.entry_nome.get().strip()

        resultado_busca = self.cursor.execute("""SELECT * FROM clientes WHERE nome LIKE '%s' COLLATE NOCASE  ORDER BY Nome ASC""" % nome)

        try:
            for cliente in resultado_busca:
                self.ima = cliente[13]

            with open('visual.png', 'wb') as f:
                f.write(self.ima)

            self.foto_pesquisa()

        except:
            msg = 'CADASTRO INEXISTENTE'
            messagebox.showwarning('nada', msg)
            self.limpar_campos()

    def atualizar(self):
        if self.entry_nome.get() == '':
            msg = 'NECESSÁRIO FAZER A PESQUISA'
            messagebox.showwarning('Cadastro de paciente', msg)

        else:
            self.lista_grid2.insert("", END, values=self.cliente)
            self.mostra_idade()

            self.db_conect()
            self.capturar_campos()

            self.cursor.execute("""UPDATE clientes SET nome = ?, civil = ?, religiao = ?, profissao = ?, cidade = ?, estado = ?, telefone = ?, data = ?, nascimento = ?, idade = ?, tipo = ?, observacao = ?
            WHERE id = ?;
            """, (self.nome, self.civil, self.religiao, self.profissao, self.cidade, self.estado, self.telefone, self.data, self.nascimento, self.idade, self.tipo, self.observacao, self.codigo))

            self.conexao.commit()
            self.db_desconect()
            self.limpar_campos()

    def listar_dados(self):
        self.db_conect()
        self.capturar_campos()

        self.lista_grid.delete(*self.lista_grid.get_children())

        lista = self.cursor.execute("""SELECT id,nome,civil,religiao,profissao,cidade,estado,telefone,data,nascimento,idade,tipo,observacao,im
        FROM clientes ORDER BY id ASC;""")

        for l in lista:
            self.lista_grid.insert("", END, values=l)
        self.db_desconect()

    def click(self, event):
        self.limpar_campos()
        self.lista_grid.selection()

        for x in self.lista_grid.selection():
            col1, col2, col3, col4, col5, col6, col7, col8, col9, col10, col11, col12, col13, col14 = self.lista_grid.item(x, 'values')
            self.entry_codigo.insert(END, col1)
            self.entry_nome.insert(END, col2)
            self.entry_civil.insert(END, col3)
            self.entry_religiao.insert(END, col4)
            self.entry_profissao.insert(END, col5)
            self.entry_cidade.insert(END, col6)
            self.entry_estado.insert(END, col7)
            self.entry_telefone.insert(END, col8)
            self.entry_dataConsulta.insert(END, col9)
            self.entry_nascimento.insert(END, col10)
            self.entry_anos.insert(END, col11)
            self.entry_tipo.insert(END, col12)
            self.entry_observacao.insert(END, col13)

            self.pesquisar2()

    def calendario(self):
        self.calendario2 = Calendar(self.root, locale='pt_br')
        self.calendario2.place(x=200, y=10)

        self.fechar_calendario1 = Button(self.root, text='F\ne\nc\nh\na\nr', font=('arial', 10, 'bold'), command=self.fechar_calendario)
        self.fechar_calendario1.place(x=450, y=10, height=100)

    def fechar_calendario(self):
        self.calendario2.destroy()
        self.fechar_calendario1.destroy()

    def atestado(self):
        os.startfile(r'C:\pdf\ATESTADO.pdf')

    def media_idade(self):
        self.db_conect()

        lista = self.cursor.execute("""SELECT avg(idade) FROM clientes """)

        for l in lista:
            teste = l[0]
            msg = f'MÉDIA DE IDADE ENTRE OS PACIENTES É DE {teste:.0f} ANOS DE IDADE'
            messagebox.showwarning('MÉDIA DE IDADE', msg)
        self.db_desconect()

    def maior_idade(self):
        self.db_conect()

        lista = self.cursor.execute("""SELECT max(idade) FROM clientes """)

        for l in lista:
            teste = l[0]
            msg = f'O PACIENTES COM MAIOR IDADE TEM {teste} ANOS DE IDADE'
            messagebox.showwarning('MÉDIA DE IDADE', msg)
        self.db_desconect()

    def menor_idade(self):
        self.db_conect()

        lista = self.cursor.execute("""SELECT min(idade) FROM clientes """)

        for l in lista:
            teste = l[0]
            msg = f'O PACIENTES COM MENOR IDADE TEM {teste} ANOS DE IDADE'
            messagebox.showwarning('MÉDIA DE IDADE', msg)
        self.db_desconect()

    def google(self):
        webbrowser.open('https://google.com')

    def gmail(self):
        webbrowser.open('https://gmail.com')

    def terra(self):
        webbrowser.open('https://mail.terra.com.br/ozone/#/mailList/INBOX')

    def ouvir_mp3(self):
        from skin_mp3 import imagem_mp3

        self.root2 = Toplevel()
        self.root2.title('TOCAR MP3')

        self.imageFundo = PhotoImage(data=base64.b64decode(imagem_mp3))
        self.labelFundo = Label(self.root2, image=self.imageFundo)
        self.labelFundo.pack()

        self.root2.configure(background='LimeGreen')
        self.root2.geometry('750x450')
        self.root2.overrideredirect(True)

        self.widgets_root2()

    def widgets_root2(self):
        self.sair_root2 = Button(self.root2, text='SAIR', command=self.sair_root2, relief=FLAT)
        self.sair_root2.place(x=513, y=400, height=35)

        self.stop_mp3 = Button(self.root2, text='STOP\nMP3', command=self.stop_mp3, relief=FLAT)
        self.stop_mp3.place(x=512, y=356, height=35, width=38)

        self.tearsForFears_botao = Button(self.root2, text='TEARS\nFOR\nFEARS', bg='red', font=('arial', 8, 'bold'), command=self.tears)
        self.tearsForFears_botao.place(x=15, y=290, width=60, height=53)

        self.depeche_botao = Button(self.root2, text='DEPECHE\nMODE', bg='red', font=('arial', 8, 'bold'), command=self.depeche)
        self.depeche_botao.place(x=77, y=290, width=60, height=53)

        self.weekend_botao = Button(self.root2, text='THE\nWEEKEND', bg='red', font=('arial', 8, 'bold'), command=self.weekend)
        self.weekend_botao.place(x=138, y=290, width=60, height=53)

        self.eddie_botao = Button(self.root2, text='EDDIE\nVEDDER', bg='red', font=('arial', 8, 'bold'), command=self.eddie)
        self.eddie_botao.place(x=505, y=290, width=60, height=53)

        self.cold_botao = Button(self.root2, text='COLDPLAY', bg='red', font=('arial', 8, 'bold'), command=self.coldplay)
        self.cold_botao.place(x=566, y=290, width=68, height=53)

        self.new_botao = Button(self.root2, text='NEW\nORDER', bg='red', font=('arial', 8, 'bold'), command=self.newOrder)
        self.new_botao.place(x=635, y=290, width=60, height=53)

    def stop_mp3(self):
        pygame.quit()

    def tears(self):
        from mp3 import tears
        tears()

    def depeche(self):
        from mp3 import depeche
        depeche()

    def weekend(self):
        from mp3 import weekend
        weekend()

    def eddie(self):
        from mp3 import eddie
        eddie()

    def coldplay(self):
        from mp3 import coldplay
        coldplay()

    def newOrder(self):
        from mp3 import newOrder
        newOrder()

    def sair_root2(self):
        try:
            os.remove('nova_foto.png')
            os.remove("visual.png")
            os._exit(0)
        except:
            try:
                os.remove("visual.png")
                os._exit(0)
            except:
                pass
                #os._exit(0)

        self.root2.destroy()
        principal()

class principal(Funcoes):
    def __init__(self):
        self.root = root
        self.tabelaConsulta()
        self.tela()
        self.cor_widgets()
        self.widgets_frame1()
        self.criar_tabela()
        self.grid_cliente()
        self.grid_cliente2()
        self.menus()

        root.mainloop()

    def tela(self):
        self.root.configure(bg='#008888')
        self.root.geometry("1366x768+0+0")
        self.root.overrideredirect(True)

    def btRevisao(self):
        self.entry_tipo.destroy()

        self.lbrevisao1 = StringVar()
        self.lbrevisao1.set('REVISÃO')

        self.entry_tipo = Entry(self.root, bg=self.lb_bg, fg='#ffffff', textvariable=self.lbrevisao1, font=('arial', 25, 'bold'), relief=FLAT)
        self.entry_tipo.place(x=740, y=343, width=200, height=40)

    def btConsulta(self):
        self.entry_tipo.destroy()

        self.lbconsulta1 = StringVar()
        self.lbconsulta1.set('CONSULTA')

        self.entry_tipo = Entry(self.root, bg=self.lb_bg, fg='#ffffff', textvariable=self.lbconsulta1, font=('arial', 25, 'bold'), relief=FLAT)
        self.entry_tipo.place(x=720, y=350, width=200, height=25)

    def btVideo(self):
        self.entry_tipo.destroy()

        self.lbvideo1 = StringVar()
        self.lbvideo1.set('VIRTUAL')

        self.entry_tipo = Entry(self.root, bg=self.lb_bg, fg='#ffffff', textvariable=self.lbvideo1, font=('arial', 25, 'bold'), relief=FLAT)
        self.entry_tipo.place(x=740, y=350, width=200, height=25)

    def deletar_grid2(self):
        # foi colocado essa exceção para retirar um erro de exceção
        try:
            self.item_selecionado = self.lista_grid2.selection()[0]
            self.lista_grid2.delete(self.item_selecionado)
        except:
            pass

    def limpa_receita(self):
        self.entry_receita.delete('1.0', END)

    def cor_widgets(self):
        # Botões
        self.bt_bg = '#008888'
        self.bt_fg = 'white'
        self.bt_font = ('verdana', 13, 'bold')

        # Label
        self.lb_bg = '#008888'
        self.lb_fg = 'white'
        self.lb_font = ('arial', 15, 'bold')

        # Entrada de dados
        self.et_bg = '#008888'
        self.et_bg_branco = 'white'
        self.et_fg_branco = "#ffffff"
        self.et_fg_preto = '#000000'
        self.et_font = ('arial', 15, 'bold')

    def widgets_frame1(self):

        self.entry_anos = Entry()

        self.entry_idade = Entry()

# Data Local
        self.dia_atual = (datetime.today().strftime('Goiânia, %d de %B de %Y'))

# Label Nome PACIENTE tela principal
        self.lb_cadastro = Label(self.root, text='P  A  C  I  E  N  T  E', bg=self.lb_bg, fg=self.lb_fg, font=('arial black', 40, 'bold'))
        self.lb_cadastro.place(x=395, y=0, height=45)

# Label id
        self.lb_codigo = Label(self.root, text='id:', bg=self.lb_bg, fg=self.lb_fg, font=self.lb_font)
        self.lb_codigo.place(x=153, y=46)

# Label Nome
        self.lb_nome = Label(self.root, text='Nome:', bg=self.lb_bg, fg=self.lb_fg, font=self.lb_font)
        self.lb_nome.place(x=100, y=85)

# Label Est. Civíl
        self.lb_civil = Label(self.root, text='Estado Civíl:', bg=self.lb_bg, fg=self.lb_fg, font=self.lb_font)
        self.lb_civil.place(x=40, y=155)

# Label Religião
        self.lb_religiao = Label(self.root, text='Religião:', bg=self.lb_bg, fg=self.lb_fg, font=self.lb_font)
        self.lb_religiao.place(x=75, y=225)

# Label Profissão
        self.lb_profissao = Label(self.root, text='Profissão:', bg=self.lb_bg, fg=self.lb_fg, font=self.lb_font)
        self.lb_profissao.place(x=58, y=290)

# Label Cidade
        self.lb_cidade = Label(self.root, text='Cidade:', bg=self.lb_bg, fg=self.lb_fg, font=self.lb_font)
        self.lb_cidade.place(x=388, y=155)

# Label Estado
        self.lb_estado = Label(self.root, text='Estado/UF:', bg=self.lb_bg, fg=self.lb_fg, font=self.lb_font)
        self.lb_estado.place(x=355, y=225)

# Label Telefone
        self.lb_telefone = Label(self.root, text='Telefone:', bg=self.lb_bg, fg=self.lb_fg, font=self.lb_font)
        self.lb_telefone.place(x=370, y=290)

# Label Nascimento
        self.lb_nascimento = Label(self.root, text='Data de Nascimento:', bg=self.lb_bg, fg=self.lb_fg, font=self.lb_font)
        self.lb_nascimento.place(x=700, y=80)

# Label Observação
        self.lb_observacao = Label(self.root, text='Obs.:', bg=self.lb_bg, fg=self.lb_fg, font=self.lb_font)
        self.lb_observacao.place(x=20, y=370)

# Entry Código
        self.entry_codigo = Entry(self.root, bg=self.et_bg, fg=self.et_fg_branco, font=self.et_font, relief=FLAT)
        self.entry_codigo.place(x=187, y=48, width=60, height=27)

# Entry Nome
        self.entry_nome = Entry(self.root, bg=self.et_bg_branco, fg=self.et_fg_preto, font=self.et_font)
        self.entry_nome.place(x=170, y=85, width=500, height=25)

        self.entry_nome.focus_force()

# AutoCompleteENtry Estado Civil
        self.civil = ["CASADO", "SOLTEIRO", "DESQUITADO",
                      "AMASIADO", "SEPARADO", "VIÚVO", "DIVORCIADO"
                      ]
        self.entry_civil = AutocompleteEntry(self.root, font=('arial', 13, 'bold'), completevalues=self.civil)
        self.entry_civil.place(x=170, y=155, width=167, height=25)

# AutoCompleteENtry Religião
        self.lista = ["CATÓLICO", "ESPÍRITA", "EVANGÉLICO",
                      "PROTESTANTE", "MORMO", "CAMDOBLÉ", "ATEU"
                      ]
        self.entry_religiao = AutocompleteEntry(self.root, font=('arial', 13, 'bold'), completevalues=self.lista)
        self.entry_religiao.place(x=170, y=225, width=167, height=25)

# AutoCompleteENtry Profissão
        self.profissao = ["ADVOGADO", "JUÍZ", "AGRICULTOR", "DO LAR", "ENGENHEIRO", "ARQUITETO", "GERENTE",
            "BABÁ", "MOTORISTA", "APOSENTADO", "MÉDICO", "TI",
            "PROFESSOR", "DIARISTA", "TAXISTA", "FARMACÊUTICO"
                      ]
        self.entry_profissao = AutocompleteEntry(self.root, font=('arial', 13, 'bold'), completevalues=self.profissao)
        self.entry_profissao.place(x=170, y=290, width=167, height=25)

# AutoCompleteEntry Cidade
        from cidade import cidades
        self.local = cidades

        self.entry_cidade = AutocompleteEntry(self.root,  font=('arial', 13, 'bold'), completevalues=self.local)
        self.entry_cidade.place(x=470, y=155, width=200, height=25)

# AutoCompleteEntry Estado
        self.estado = ["Acre/AC", "Alagoas/AL", "Amapá/AP", "Amazonas/AM", "Bahia/BA", "Ceará/CE",
                       "Esp. Santo/ES", "Goiás/GO", "Maranhão/MA", "M. Grosso/MT",
                       "M. Grosso Sul/MS", "Minas Gerais/MG",
                       "Pará/PA", "Paraíba/PB", "Paraná/PR", "Pernambuco/PE", "Piauí/PI",
                       "Rio de Janeiro/RJ",
                       "Rio G. do Norte/RN", "Rio G. do Sul/RS", "Rondônia/RO", "Roraima/RR",
                       "Santa Catarina/SC",
                       "São Paulo/SP", "Sergipe/SE", "Tocantins/TO", "D. Federal/DF",
                      ]
        self.entry_estado = AutocompleteEntry(self.root, font=('arial', 13, 'bold'), completevalues=self.estado)
        self.entry_estado.place(x=470, y=225, width=198, height=25)

# Entry Telefone
        self.entry_telefone = Entry(self.root, bg=self.et_bg_branco, fg=self.et_fg_preto, font=self.et_font)
        self.entry_telefone.place(x=472, y=290, width=198, height=25)

# Entry Botão Inserir data da Consulta
        self.lb_dataConsulta = Button(self.root, text='DATA  CONSULTA', bg=self.bt_bg, fg=self.bt_fg, font=self.bt_font, command=self.data_consulta)
        self.lb_dataConsulta.place(x=1050, y=15, width=210, height=28)

        self.entry_dataConsulta = Entry(self.root, bg=self.lb_bg, fg='yellow', font=('arial', 18, 'bold'), relief=FLAT)
        self.entry_dataConsulta.place(x=1100, y=50, width=120, height=20)

# Entry Data de Nascimento
        self.entry_nascimento = Entry(self.root, font=('arail', 15, 'bold'))
        self.entry_nascimento.bind("<KeyRelease>", self.format_data)
        self.entry_nascimento.place(x=770, y=120, width=105, height=25)

# Text Observações
        self.entry_observacao = Text(self.root, bg=self.lb_bg, fg=self.lb_fg, font=self.et_font)
        self.entry_observacao.place(x=23, y=420, width=1240, height=78)

# Botão Data Niver
        from botoes_image import dataNiver


        self.bt_calendario = PhotoImage(data=base64.b64decode(dataNiver))
        self.bt_calendario = self.bt_calendario.subsample(3,3)
        self.bt_calendario1 = Label(self.root, image=self.bt_calendario)
        self.bt_calendario1.image = self.bt_calendario

        self.bt_calendario = Button(self.root, image=self.bt_calendario, bg=self.lb_bg, activebackground=self.lb_bg, bd=0, highlightthickness=0, command=self.mostra_idade)
        self.bt_calendario.place(x=730, y=110)

# Botão Tirar Foto
        from botoes_image import m_fotografica
#

        self.entry_receita = PhotoImage(data=base64.b64decode(m_fotografica))
        self.entry_receita = self.entry_receita.subsample(5, 5)
        self.entry_receita1 = Label(self.root, image=self.entry_receita)
        self.entry_receita1.image = self.entry_receita

        self.entry_receita = Button(self.root, image=self.entry_receita, bg=self.lb_bg, activebackground=self.lb_bg, bd=0, highlightthickness=0, command=self.foto)
        self.entry_receita.place(x=710, y=180, width=210, height=140)

# Botão Saida do Sistema
        from botoes_image import sairSistema

        self.sairSistema = PhotoImage(data=base64.b64decode(sairSistema))
        self.sairSistema = self.sairSistema.subsample(5,5)
        self.sairSistema1 = Label(self.root, image=self.sairSistema)
        self.sairSistema1.image = self.sairSistema

        self.sairSistema = Button(self.root, image=self.sairSistema, bg=self.lb_bg, activebackground=self.lb_bg, bd=0, highlightthickness=0, command=self.sair)
        self.sairSistema.place(x=1210, y=655)

#Botão Revisão
        from botoes_image import revisao

        self.revisao = PhotoImage(data=base64.b64decode(revisao))
        self.revisao = self.revisao.subsample(6, 6)
        self.revisao1 = Label(self.root, image=self.revisao)
        self.revisao1.image = self.revisao

        self.revisao = Button(self.root, bg=self.bt_bg, fg=self.bt_fg, image=self.revisao,
                                       activebackground=self.bt_bg, bd=0, highlightthickness=0, command=self.btRevisao, relief=FLAT)
        self.revisao.place(x=175, y=320, width=55, height=70)

        self.labelRevisao = Label(self.root, text='REVISÃO', bg=self.lb_bg, fg='yellow', font=('arial', 10, 'bold'))
        self.labelRevisao.place(x=175, y=390)

        self.entry_tipo = Entry(self.root, bg=self.lb_bg, fg='#ffffff', font=('arial', 25, 'bold'), relief=FLAT)
        self.entry_tipo.place(x=740, y=343, width=200, height=40)

# Botão Consulta
        from botoes_image import consulta

        self.consulta = PhotoImage(data=base64.b64decode(consulta))
        self.consulta = self.consulta.subsample(6, 6)
        self.consulta1 = Label(self.root, image=self.consulta)
        self.consulta1.image = self.consulta

        self.consulta = Button(self.root, bg=self.bt_bg, fg=self.bt_fg, image=self.consulta,
                              activebackground=self.bt_bg, bd=0, highlightthickness=0, command=self.btConsulta, relief=FLAT)
        self.consulta.place(x=360, y=320, width=55, height=70)

        self.labelConsulta = Label(self.root, text='CONSULTA', bg=self.lb_bg, fg='yellow', font=('arial', 10, 'bold'))
        self.labelConsulta.place(x=350, y=390)

        self.entry_tipo = Entry(self.root, bg=self.lb_bg, fg='#ffffff', font=('arial', 25, 'bold'), relief=FLAT)
        self.entry_tipo.place(x=720, y=350, width=200, height=40)

# Botão Wahtsapp
        from botoes_image import whatsapp

        self.video = PhotoImage(data=base64.b64decode(whatsapp))
        self.video = self.video.subsample(3, 3)
        self.video1 = Label(self.root, image=self.video)
        self.video1.image = self.video

        self.bt_video = Button(self.root, bg=self.bt_bg, fg=self.bt_fg, image=self.video,
                               activebackground=self.bt_bg, bd=0, highlightthickness=0, command=self.btVideo, relief=FLAT)
        self.bt_video.place(x=535, y=320, width=55, height=70)

        self.labelVideo = Label(self.root, text='VÍDEO', bg=self.lb_bg, fg='yellow', font=('arial', 10, 'bold'))
        self.labelVideo.place(x=540, y=390)

        self.entry_tipo = Entry(self.root, bg=self.lb_bg, fg='#ffffff', font=('arial', 25, 'bold'), relief=FLAT)
        self.entry_tipo.place(x=720, y=350, width=200, height=40)

# Botão Limpar
        from botoes_image import limpar

        self.bt_limpar = PhotoImage(data=base64.b64decode(limpar))
        self.bt_limpar = self.bt_limpar.subsample(13, 13)
        self.bt_limpar1 = Label(self.root, image=self.bt_limpar)
        self.bt_limpar1.image = self.bt_limpar

        self.bt_limpar = Button(self.root, bg=self.bt_bg, fg=self.bt_fg, image=self.bt_limpar,
                               activebackground=self.bt_bg, bd=0, highlightthickness=0, command=self.limpar_campos, relief=FLAT)
        self.bt_limpar.place(x=195, y=605, width=80, height=120)

        self.lblimpar = Label(self.root, text='LIMPAR TELA', bg=self.lb_bg, fg=self.lb_fg, font=('arial', 10, 'bold'))
        self.lblimpar.place(x=185, y=695)

# Botão Buscar
        from botoes_image import lupa

        self.bt_buscar = PhotoImage(data=base64.b64decode(lupa))
        self.bt_buscar = self.bt_buscar.subsample(2, 2)
        self.bt_buscar1 = Label(self.root, image=self.bt_buscar)
        self.bt_buscar1.image = self.bt_buscar

        self.bt_buscar = Button(self.root, bg=self.bt_bg, fg=self.bt_fg, image=self.bt_buscar,
                                activebackground=self.bt_bg, bd=0, highlightthickness=0, command=self.pesquisar, relief=FLAT)
        self.bt_buscar.place(x=365, y=605, width=110, height=120)

        self.lbbuscar = Label(self.root, text='PESQUISAR', bg=self.lb_bg, fg=self.lb_fg, font=('arial', 10, 'bold'))
        self.lbbuscar.place(x=380, y=695)

# Botão Cadastrar
        from botoes_image import cadastrar

        self.bt_novo = PhotoImage(data=base64.b64decode(cadastrar))
        self.bt_novo = self.bt_novo.subsample(7, 7)
        self.bt_novo1 = Label(self.root, image=self.bt_novo)
        self.bt_novo1.image = self.bt_novo

        self.bt_novo = Button(self.root, bg=self.bt_bg, fg=self.bt_fg, image=self.bt_novo,
                                activebackground=self.bt_bg, bd=0, highlightthickness=0, command=self.inserir_dados, relief=FLAT)
        self.bt_novo.place(x=570, y=600, width=120, height=120)

        self.lbnovo = Label(self.root, text='CADASTRAR', bg=self.lb_bg, fg=self.lb_fg, font=('arial', 10, 'bold'))
        self.lbnovo.place(x=585, y=695)

# Botão Alterar
        from botoes_image import medico

        self.bt_alterar = PhotoImage(data=base64.b64decode(medico))
        self.bt_alterar = self.bt_alterar.subsample(7, 7)
        self.bt_alterar1 = Label(self.root, image=self.bt_alterar)
        self.bt_alterar1.image = self.bt_alterar

        self.bt_alterar = Button(self.root, bg=self.bt_bg, fg=self.bt_fg, image=self.bt_alterar,
                              activebackground=self.bt_bg, bd=0, highlightthickness=0, command=self.atualizar, relief=FLAT)
        self.bt_alterar.place(x=770, y=605, width=120, height=120)

        self.lbalterar = Label(self.root, text='ALTERAR', bg=self.lb_bg, fg=self.lb_fg, font=('arial', 10, 'bold'))
        self.lbalterar.place(x=797, y=700)

# Botão Agendamento
        from botoes_image import agenda

        self.bt_marcar_consulta = PhotoImage(data=base64.b64decode(agenda))
        self.bt_marcar_consulta = self.bt_marcar_consulta.subsample(4, 4)
        self.bt_marcar_consulta1 = Label(self.root, image=self.bt_marcar_consulta)
        self.bt_marcar_consulta1.image = self.bt_marcar_consulta

        self.bt_marcar_consulta = Button(self.root, bg=self.bt_bg, fg=self.bt_fg, image=self.bt_marcar_consulta,
                                 activebackground=self.bt_bg, bd=0, highlightthickness=0, command=self.marcar_consulta, relief=FLAT)
        self.bt_marcar_consulta.place(x=965, y=605, width=120, height=120)

        self.lbagenda = Label(self.root, text='AGENDAMENTO', bg=self.lb_bg, fg=self.lb_fg, font=('arial', 10, 'bold'))
        self.lbagenda.place(x=965, y=700)

# Data Formatada
    def format_data(self, event=None):
        self.text = self.entry_nascimento.get()[:10]
        self.new_text = ""

        for index in range(len(self.text)):

            if not self.text[index] in "0123456789":
                continue
            if index in  [1, 4]:
                self.new_text += self.text[index] + "/"
            else:
                self.new_text += self.text[index]

        self.entry_nascimento.delete(0, "end")
        self.entry_nascimento.insert(0, self.new_text)

    def mostra_idade(self):
            try:
                dataNasc = self.entry_nascimento.get()

                a = (datetime.strptime(dataNasc, '%d/%m/%Y').date())
                b = (datetime.today().strftime('%Y-%m-%d'))
                c = (datetime.strptime(b, '%Y-%m-%d').date())

                self.idade = int((c - a).days / 365.25)

                self.entry_anos.delete(0, END)
                self.entry_nascimento.delete(0, END)
                self.entry_nascimento.insert(END, dataNasc)

                self.idadeatual = StringVar()
                self.idadeatual.set(self.idade)

                self.entry_idade = Entry(self.root, bg=self.lb_bg, fg='red', textvariable=self.idadeatual, font=('arial', 15, 'bold'), relief=FLAT)
                self.entry_idade.place(x=913, y=123, width=75, height=27)

                self.entry_idade1 = Label(self.root, bg=self.lb_bg, fg='red', text='anos', font=('arial', 15, 'bold'))
                self.entry_idade1.place(x=950, y=120, width=60, height=27)

            except:
                self.entry_nascimento.delete(0, END)
                msg = 'Preencher a data de nascimento corretamente'
                messagebox.showinfo('Cadastro de Paciente', msg)

# Data da Consulta
    def data_consulta(self):
            self.dia_atual = (datetime.today().strftime('%d/%m/%Y'))
            self.TextoLabel = StringVar()
            self.TextoLabel.set(self.dia_atual)

            self.entry_dataConsulta = Entry(self.root, textvariable=self.TextoLabel, bg=self.lb_bg, fg='yellow', font=('arial', 18, 'bold'), relief=FLAT)
            self.entry_dataConsulta.place(x=1100, y=50, width=120, height=20)

    def sair(self):
        try:
            os.remove('nova_foto.png')
            os.remove("visual.png")
            os._exit(0)
        except:
            try:
                os.remove("visual.png")
                os._exit(0)
            except:
                os._exit(0)

        self.root.destroy()
        os._exit(0)

    def grid_cliente2(self):
        self.lista_grid2 = ttk.Treeview(self.root, columns=('col1', 'col2'))

        self.lista_grid2.heading('#1', text='CÓDIGO')
        self.lista_grid2.heading('#2', text='NOME')

        self.lista_grid2.column('#0', width=0)
        self.lista_grid2.column('#1', width=60)
        self.lista_grid2.column('#2', width=120)
        self.lista_grid2.place(x=1055, y=110, width=210, height=280)

        self.delete_grid2 = Button(self.root, text='DELETAR ITEM', bg='red', fg='#ffffff', font=('arial', 10, 'bold'), command=self.deletar_grid2)
        self.delete_grid2.place(x=1055, y=385, width=210, height=35)

        self.lb_treeview2 = Label(self.root, text='CONSULTAS', bg=self.lb_bg, fg=self.lb_fg, font=self.lb_font)
        self.lb_treeview2.place(x=1100,y=80)

    def grid_cliente(self):
        self.lista_grid = ttk.Treeview(self.root, columns=('col1', 'col2', 'col3','col4', 'col5', 'col6','col7', 'col8', 'col9','col10', 'col11', 'col12')) #, 'col13', 'col14'))

        self.lista_grid.heading('#1', text='CÓDIGO')
        self.lista_grid.heading('#2', text='NOME')
        self.lista_grid.heading('#3', text='E.CIVÍL')
        self.lista_grid.heading('#4', text='RELIGIÃO')
        self.lista_grid.heading('#5', text='PROFISSÃO')
        self.lista_grid.heading('#6', text='CIDADE')
        self.lista_grid.heading('#7', text='ESTADO/UF')
        self.lista_grid.heading('#8', text='TELEFONE')
        self.lista_grid.heading('#9', text='D.CONSULTA')
        self.lista_grid.heading('#10', text='NASCIMENTO')
        self.lista_grid.heading('#11', text='IDADE')
        self.lista_grid.heading('#12', text='TIPO')
        #self.lista_grid.heading('#13', text='CÓDIGO')
        #self.lista_grid.heading('#14', text='CÓDIGO')

        self.lista_grid.column('#0', width=0)
        self.lista_grid.column('#1', width=60)
        self.lista_grid.column('#2', width=120)
        self.lista_grid.column('#3', width=90)
        self.lista_grid.column('#4', width=90)
        self.lista_grid.column('#5', width=120)
        self.lista_grid.column('#6', width=150)
        self.lista_grid.column('#7', width=90)
        self.lista_grid.column('#8', width=100)
        self.lista_grid.column('#9', width=130)
        self.lista_grid.column('#10', width=90)
        self.lista_grid.column('#11', width=50)
        self.lista_grid.column('#12', width=120)
        #self.lista_grid.column('#13', width=150)
        #self.lista_grid.column('#14', width=150)
        self.lista_grid.place(x=22, y=519, width=1230, relheight=0.14)
        self.lista_grid.bind("<Double-1>", self.click)

    def foto_imagem(self):
        self.lb_rosto = PhotoImage(file='visual.png')
        self.lb_rosto = self.lb_rosto.subsample(10, 10)
        self.lb_rosto1 = Label(self.root, image=self.lb_rosto)
        self.lb.rosto1.image = self.lb_rosto
        self.lb.rosto1.place(x=600, y=200)

# Tirar foto webCam
    def foto5(self):
        try:
            os.remove('nova_foto.png')
            os.remove("visual.png")
            self.foto()
        except:
            os.remove("visual.png")
            self.foto()

    def foto(self):
        if self.entry_nome.get() == '':
            msg = 'NECESSÁRIO FAZER O CADASTRO'
            messagebox.showwarning('Cadastro de paciente',msg)

        else:
            self.webcam = cv2.VideoCapture(0, cv2.CAP_DSHOW)

            if self.webcam.isOpened():

                validacao, frame = self.webcam.read()

                while validacao:
                    validacao, frame = self.webcam.read()

                    cv2.imshow(60 * ' ' + '**** CLICAR NO ESC PARA TIRAR FOTO ***', frame)

                    key = cv2.waitKey(5)

                    if key == 27:  # 27 é a tecla Esc
                        #self.efeitoSonoro()
                        break

                cv2.imwrite("nova_foto.png", frame)
                self.webcam.release()
                cv2.destroyAllWindows()
                self.abrir_foto()

    def foto_pesquisa(self):
        # pasta = os.path.dirname(__file__)

        self.img = Image.open('visual.png')
        self.img.save("visual.png")

        self.letra1 = PhotoImage(file="visual.png")  # pasta + "\\visual.png")
        self.letra1 = self.letra1.subsample(2, 2)

        self.letra = Label(self.root, image=self.letra1)
        self.letra.place(x=715, y=185, width=200, height=130)

    def abrir_foto(self):
        self.capturar_campos()

        if self.entry_nome.get() == '':
            msg = 'NECESSÁRIO TIRAR UMA FOTO'
            messagebox.showinfo('PORTARIA', msg)
        else:
            try:
                self.lb_rosto = PhotoImage(file="nova_foto.png")
                self.lb_rosto = self.lb_rosto.subsample(2, 2)
                self.lb_rosto1 = Label(self.root, image=self.lb_rosto)
                self.lb_rosto1.place(x=715, y=185, width=200, height=130)

                self.botao = Button(self.root, text='ALTERAR', activebackground=self.bt_bg, bd=0, highlightthickness=0, command=self.foto, relief=FLAT)
                self.botao.place(x=865, y=300, width=50, height=13)
            except:
                pass
            #self.efeitoSonoro()

    def fechar_foto(self):
        self.letra.destroy()
        self.destroi.destroy()

    def menus(self):
        menubar = Menu(self.root)

        self.root.config(menu=menubar)
        filemenu1 = Menu(menubar, tearoff=0)
        filemenu2 = Menu(menubar, tearoff=0)
        filemenu3 = Menu(menubar, tearoff=0)
        filemenu4 = Menu(menubar, tearoff=0)

        corda = self.dia_atual
        menubar.add_cascade(label=corda, menu=filemenu4, activebackground='#efefef', activeforeground='black')
        filemenu4.add_command(label='Calendário', command=self.calendario)

        menubar.add_cascade(label='Funções', menu=filemenu1)
        filemenu1.add_command(label='Atestado', command=self.atestado)
        filemenu1.add_command(label='Listar Paciente', command=self.listar_dados)

        menubar.add_cascade(label='Estatística', menu=filemenu2)
        filemenu2.add_command(label='Média de idade', command=self.media_idade)
        filemenu2.add_command(label='Maior idade', command=self.maior_idade)
        filemenu2.add_command(label='Menor idade', command=self.menor_idade)

        menubar.add_cascade(label='Ferramentas', menu=filemenu3)
        filemenu3.add_command(label='Tocar MP3', command=self.ouvir_mp3)
        filemenu3.add_command(label='Google', command=self.google)
        filemenu3.add_command(label='Gmail', command=self.gmail)
        filemenu3.add_command(label='Terra', command=self.terra)        

principal()

