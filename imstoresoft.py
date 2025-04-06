#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi
gi.require_version('Gdk', '3.0')
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import Gdk

import shelve
from datetime import datetime
import sys

from pathlib import Path

from io import StringIO

import matplotlib.pyplot as plt
import numpy as np

#from PIL import Image
#from PIL import ImageFont
#from PIL import ImageDraw 

##########################################################
#
#  Funções auxiliares
#
##########################################################

class InactiveItem(LookupError):
	pass

class NoProduct(LookupError):
	pass



#def def aux_geraCupomVendaFechadaImg(datahora, cliente, venda):
#	img = Image.open("cupom.jpg")
#	draw = ImageDraw.Draw(img)
#	# font = ImageFont.truetype(<font-file>, <font-size>)
#	font = ImageFont.truetype("sans-serif.ttf", 12)
#	# draw.text((x, y),"Sample Text",(r,g,b))
#	draw.text((0, 0),"Sample Text",(255,255,255),font=font)
#	img.save('sample-out.jpg')
	

def aux_geraCupomVendaFechada(datahora, cliente, venda, _file=sys.stdout):
	print("*"*80,file=_file)
	print("*{}IM Store{}*".format(" "*35," "*35),file=_file)
	print("*"*80,file=_file)
	dh = datetime.fromtimestamp(float(datahora))
	print("Data da compra: {:0>2}/{:0>2}/{} {:0>2}h{:0>2}".format(dh.day,dh.month,dh.year,dh.hour,dh.minute),file=_file)
	print("Cliente: " + cliente,file=_file)
	
	print(file=_file)
	
	print("ITEM  DESCRIÇÃO                          TAM  QTDE  PREÇO UNT (R$)  PREÇO T (R$)",file=_file)
	for item in venda[1]:
		if venda[2] in ("Crediário","Cartão Parcelado"):
			precoUnt = float(item[7].replace(",","."))
			precoT = float(item[9].replace(",","."))
		else:
			precoUnt = float(item[6].replace(",","."))
			precoT = float(item[8].replace(",","."))
		print("{:>4}  {:<33}  {:<3}  {:>4}  {:14.2f}  {:12.2f}".format(item[0],item[3][:33],item[4],item[5],precoUnt,precoT),file=_file)
	print("-"*80,file=_file)
	
	print("{:>80}".format("Subtotal R$ {:8.2f}".format(venda[3])),file=_file)
	print("{:>80}".format("Desconto R$ {:8.2f}".format(venda[5])),file=_file)
	print("{:>80}".format("Total R$ {:8.2f}".format(venda[6])),file=_file)
	
	print("Forma de Pagamento: " + venda[2],file=_file)
	
	

def aux_corrigePreco(preco:str)->str:
	if not preco:
		return "0"
	
	if preco == "," or preco == ".":
		return "0"
	
	return preco

def aux_verificaEntradaPreco(entry, event):
	
	if event.keyval in (Gdk.KEY_Left, Gdk.KEY_Right, Gdk.KEY_Tab,
						Gdk.KEY_BackSpace, Gdk.KEY_Delete):
		return False
	
	
	if event.string.isdigit():		
		return False #permite entrada
	
	#limita .,
	if event.string in ".,":
		if "." in entry.props.text or "," in entry.props.text:
			return True # se ja tem . ou , não permita colocar novamente
		else:
			return False
	#
	
	return True
	

def aux_verificaEntradaPrecoPN(entry, event):
	
	if event.keyval in (Gdk.KEY_Left, Gdk.KEY_Right, Gdk.KEY_Tab,
						Gdk.KEY_BackSpace, Gdk.KEY_Delete):
		return False #permite entrada
	
	if event.string.isdigit():		
		return False #permite entrada
	
	#limita .,
	if event.string in ".,":
		if "." in entry.props.text or "," in entry.props.text:
			return True # se ja tem . ou , não permita colocar novamente
		else:
			return False
	#
	
	#limita +-
	if event.string in "+-":
		if len(entry.props.text) > 0:
			return True
		else:
			return False
		
	#
	
	return True


def aux_verificaEntradaCPF(entry, event):
	if event.keyval in (Gdk.KEY_Left, Gdk.KEY_Right, Gdk.KEY_Tab,
						Gdk.KEY_BackSpace, Gdk.KEY_Delete):
		return False #permite entrada
	
	if event.string.isdigit():
		return False #permite entrada
	
	return True

##########################################################
#
#  Janela Principal
#
##########################################################

class JanelaPrincipal:
	def __init__(self):
		self.janelaCadastroCliente = builder.get_object("janelaCadastroCliente")
		self.janelaCadastroProduto = builder.get_object("janelaCadastroProduto")
		self.janelaVenda = builder.get_object("janelaVenda")
		self.janelaEntradaSaidaTransf = builder.get_object("janelaEntradaSaidaTransf")
		self.janelaRelatorios = builder.get_object("janelaRelatorios")
	
	def bt_cad_cliente_clicked(self, button):
		self.janelaCadastroCliente.show()
	
	def bt_cad_produto_clicked(self, button):
		self.janelaCadastroProduto.show()
		
	def bt_venda_clicked(self, button):
		self.janelaVenda.show()
	
	def bt_entradasaidatransf_clicked(self, button):
		self.janelaEntradaSaidaTransf.show()
	
	def bt_relatorios_clicked(self, button):
		self.janelaRelatorios.show()


##########################################################
#
#  Janela Entrada/Saida/Transferencia
#
##########################################################

class EntradaSaidaTransf():
	
	def __init__(self):
		#janela
		self.buttonFecharCaixa = builder.get_object("buttonFecharCaixa")
		
		#Entrada
		self.comboboxtextTipoE = builder.get_object("comboboxtextTipoE")
		self.comboboxtextContaDestinoE = builder.get_object("comboboxtextContaDestinoE")
		self.entryValorE = builder.get_object("entryValorE")
		self.searchentryCPFE = builder.get_object("searchentryCPFE")
		self.entryCodClienteE = builder.get_object("entryCodClienteE")
		self.labelNomeClienteE = builder.get_object("labelNomeClienteE")
		self.entryDescricaoE = builder.get_object("entryDescricaoE")
		self.liststoreEntradas = builder.get_object("liststoreEntradas")
		self.selectionEntrada = builder.get_object("treeview-selectionEntrada")
		self.boxClienteE = builder.get_object("boxClienteE")
		self.boxDescricaoE = builder.get_object("boxDescricaoE")
		
		#Saídas
		self.comboboxtextTipoS = builder.get_object("comboboxtextTipoS")
		self.comboboxtextContaOrigemS = builder.get_object("comboboxtextContaOrigemS")
		self.entryValorS = builder.get_object("entryValorS")
		self.entryDescricaoS = builder.get_object("entryDescricaoS")
		self.liststoreSaidas = builder.get_object("liststoreSaidas")
		self.selectionSaida = builder.get_object("treeview-selectionSaida")
		
		#transferencias
		self.comboboxtextContaOrigemT = builder.get_object("comboboxtextContaOrigemT")
		self.comboboxtextContaDestinoT = builder.get_object("comboboxtextContaDestinoT")
		self.entryValorT = builder.get_object("entryValorT")
		self.entryDescricaoT = builder.get_object("entryDescricaoT")
		self.liststoreTransferencias = builder.get_object("liststoreTransferencias")
		self.selectionTransferencia = builder.get_object("treeview-selectionTransf")
		
	
	def esconderJanelaEST(self, window, *args): #aproveitável para todas
		window.hide()
		return True
	
	def janelaEntradaSaidaTransfShow(self, widget):
		print("Entrei janela EntradaSaidaTransf")
		self.db_EntSaiTransf = shelve.open("dbs/entrsaitransf.dbm")
		self.db_contas = shelve.open("dbs/contas.dbm")
		self.db_cliente = shelve.open("dbs/clientes.dbm")
		
		#carregando entradas
		try:
			entradas = self.db_EntSaiTransf["entradas"]
		except KeyError:
			pass
		else:
			if len(self.liststoreEntradas) == 0:
				for dados in entradas:
					dados[2] = "{:.2f}".format(dados[2]).replace(".",",")
					self.liststoreEntradas.append(dados)
		
		#carregando saidas
		try:
			saidas = self.db_EntSaiTransf["saidas"]
		except KeyError:
			pass
		else:
			if len(self.liststoreSaidas) == 0:
				for dados in saidas:
					self.liststoreSaidas.append(dados)
		
		#carregando trasferencias
		try:
			transferencias = self.db_EntSaiTransf["transferencias"]
		except KeyError:
			pass
		else:
			if len(self.liststoreTransferencias) == 0:
				for dados in transferencias:
					self.liststoreTransferencias.append(dados)
		
		#verificando se caixa foi fechado no dia
		hoje = datetime.now()
		dia, mes, ano = hoje.day, hoje.month, hoje.year
		p = Path('./dbs/fechamentos')
		
		bFecharCaixa_sensitive = True
		
		print("Varrendo fechamentos...")
		for i in p.iterdir():
			print(i)
			data = i.as_posix().split("/")[-1].rstrip(".db")
			data = data.rstrip(".dbm")
			
			data = datetime.fromtimestamp(float(data))
			
			if (dia,mes,ano) == (data.day,data.month,data.year):
				bFecharCaixa_sensitive = False
				break
		
		self.buttonFecharCaixa.props.sensitive = bFecharCaixa_sensitive
		
	
	###############ENTRADAS################
	
	def E_tipo_changed(self, combobox):
		self.boxClienteE.props.visible = (combobox.get_active_id() == "0")
		self.boxDescricaoE.props.visible = (combobox.get_active_id() != "0")
	
	def janelaEntradaSaidaTransfHide(self, widget):
		print("Saindo janela EntradaSaidaTransf")
		self.db_EntSaiTransf.close()
		self.db_contas.close()
		self.db_cliente.close()
	
	def bAdicionarEntrada_clicked(self, button):
		print("Botão adicionar entrada clicado")
		
		if self.comboboxtextTipoE.get_active_id() == "0" and \
			self.entryCodClienteE.props.text == "": # tem que ver se o que foi digitado corresponde a um cliente!
			#mensagem de erro
			print("Não é possível receber crediário sem CPF")
			return
		
		try:
			valor = float(self.entryValorE.props.text.replace(",","."))
		except ValueError:
			print("Não é possível add Entrada com valor inválido.")
			return
		
		datahora = str(datetime.now().timestamp())
		
		if self.comboboxtextTipoE.get_active_id() == "0":
			desc = self.labelNomeClienteE.props.label
			codCliente = self.entryCodClienteE.props.text
		else:
			desc = self.entryDescricaoE.props.text
			codCliente = ""
		
		contaDest = self.comboboxtextContaDestinoE.get_active_text()
		
		dados = [self.comboboxtextTipoE.get_active_text(),
				contaDest,
				valor,desc,codCliente,datahora]
		
		try:
			entradas = self.db_EntSaiTransf["entradas"]
			entradas.append(dados)
			self.db_EntSaiTransf["entradas"] = entradas
		except KeyError:
			self.db_EntSaiTransf["entradas"] = [dados]
		
		self.db_EntSaiTransf.sync()
		dados[2] = "{:.2f}".format(valor).replace(".",",")
		self.liststoreEntradas.append(dados)
		
		#processamento
		
		#atualizando contas
		if contaDest == "Fundo de Caixa":
			self.db_contas["FundoCaixa"] = self.db_contas["FundoCaixa"] + valor
		elif contaDest == "Pagbank":
			self.db_contas["Pagbank"] = self.db_contas["Pagbank"] + valor
		elif contaDest == "Banco do Brasil":
			self.db_contas["BB"] = self.db_contas["BB"] + valor
		elif contaDest == "Nubank":
			self.db_contas["Nubank"] = self.db_contas["Nubank"] + valor
		self.db_contas.sync()
		
		#atualizando crediário cliente
		if self.comboboxtextTipoE.get_active_id() == "0":
			db_crediario = shelve.open("dbs/crediarios.dbm")
			
			try:
				historico = db_crediario[codCliente]
				historico.append([datahora,"Pagamento",valor]) 
				db_crediario[codCliente] = historico
				
				print(historico)
			
			except KeyError: #é o primeiro item do histórico
				db_crediario[codCliente] = \
					[[None,"Dívida anterior",self.db_cliente[codCliente][10]],[datahora,"Pagamento",valor]]
			
			cliente = self.db_cliente[codCliente]
			cliente[10] -= valor
			if cliente[10] == 0.0:
				cliente[8] = "Quitado"
			self.db_cliente[codCliente] = cliente
			
			self.db_cliente.sync()
			
			db_crediario.sync()
			db_crediario.close()
		
		self.limpaCamposEntradas()
	
	def bRemoverEntrada_clicked(self, button):
		print("Botão remover entrada clicado")
		
		sel = self.selectionEntrada.get_selected()
		model = sel[0]
		ID = sel[1]
		if not ID:
			return
		
		tipo, contaDest, valor, desc, codCliente, datahora = model[ID]
		valor = float(valor.replace(",","."))
		
		#atualizando contas
		if contaDest == "Fundo de Caixa":
			self.db_contas["FundoCaixa"] = self.db_contas["FundoCaixa"] - valor
		elif contaDest == "Pagbank":
			self.db_contas["Pagbank"] = self.db_contas["Pagbank"] - valor
		elif contaDest == "Banco do Brasil":
			self.db_contas["BB"] = self.db_contas["BB"] - valor
		elif contaDest == "Nubank":
			self.db_contas["Nubank"] = self.db_contas["Nubank"] - valor
		self.db_contas.sync()
		
		#atualizando crediário
		if tipo == "Recebimento Crediário":
			print("Entrei para apagar crediário")
			db_crediario = shelve.open("dbs/crediarios.dbm")
			
			historico = db_crediario[codCliente]
			
			i = 0
			while (i < len(historico)):
				if historico[i][0] == datahora:
					del historico[i]
				i+=1
			
			db_crediario[codCliente] = historico
			
			db_crediario.sync()
			db_crediario.close()
			
			cliente = self.db_cliente[codCliente]
			cliente[10] += valor
			if cliente[10] > 0.0:
				cliente[8] = "A Quitar"
			self.db_cliente[codCliente] = cliente
			
			self.db_cliente.sync()
		
		#apagando entrada liststore
		self.liststoreEntradas.remove(ID)
		
		#atualizando DBM Entrada
		entradas = self.db_EntSaiTransf["entradas"]
		i = 0
		while (i < len(entradas)):
			if entradas[i][5] == datahora:
				del entradas[i]
			i+=1
		self.db_EntSaiTransf["entradas"] = entradas
		self.db_EntSaiTransf.sync()
		
		#limpando campos
		self.limpaCamposEntradas()

	
	def buscaCPFEntrada(self, searchentry):
		if len(searchentry.props.text) < 11:
			self.labelNomeClienteE.props.label = "Cliente não encontrado"
			self.entryCodClienteE.props.text = ""
			return
		
		print("Pesquisando por CPF: " + searchentry.props.text)
		
		for key,item in self.db_cliente.items():
			if item[5] == searchentry.props.text and item[12] == "ativo":
				print("Cliente encontrado ("+ key + "). Carregando dados...")
				self.entryCodClienteE.props.text = key
				self.labelNomeClienteE.props.label = item[0][:35]
				
				return
				
		
		#se não encontrei, então
		self.labelNomeClienteE.props.label = "Cliente não encontrado"
		self.entryCodClienteE.props.text = ""


	def limpaCamposEntradas(self):
		self.comboboxtextTipoE.set_active(0)
		self.comboboxtextContaDestinoE.set_active(0)
		self.entryValorE.props.text = ""
		self.searchentryCPFE.props.text = ""
		self.entryDescricaoE.props.text = ""
		self.selectionEntrada.unselect_all()
	
	
	def verificaValorEST(self, entry, event):
		print("Digitei " + event.string)
		return aux_verificaEntradaPreco(entry, event)
		

	def bLimparEntrada_clicked(self, button):
		self.limpaCamposEntradas()
	
	###############SAIDAS################
	
	def limpaCamposSaidas(self):
		self.comboboxtextTipoS.set_active(0)
		self.comboboxtextContaOrigemS.set_active(0)
		self.entryValorS.props.text = ""
		self.entryDescricaoS.props.text = ""
		self.selectionSaida.unselect_all()
	
	
	def bLimparSaida_clicked(self, button):
		self.limpaCamposSaidas()
	
	
	def bAdicionarSaida_clicked(self, button):
		print("Botão adicionar saída clicado")
		
		datahora = str(datetime.now().timestamp())
		
		try:
			t = float(self.entryValorS.props.text.replace(",","."))
		except ValueError:
			print("Erro com campo valor. Não cadastrado")
			return
		
		contaOrigem = self.comboboxtextContaOrigemS.get_active_text()
		
		dados = [self.comboboxtextTipoS.get_active_text(),
				 contaOrigem,
				 self.entryValorS.props.text.replace(".",","),
				 self.entryDescricaoS.props.text, datahora]
		
		self.liststoreSaidas.append(dados)
		
		try:
			saidas = self.db_EntSaiTransf["saidas"]
			saidas.append(dados)
			self.db_EntSaiTransf["saidas"] = saidas
		except KeyError:
			self.db_EntSaiTransf["saidas"] = [dados]
		
		self.db_EntSaiTransf.sync()
		
		valor = float(dados[2].replace(",","."))
		
		#atualizando contas
		if contaOrigem == "Pagbank":
			self.db_contas["Pagbank"] = self.db_contas["Pagbank"] - valor
		elif contaOrigem == "Banco do Brasil":
			self.db_contas["BB"] = self.db_contas["BB"] - valor
		elif contaOrigem == "Nubank":
			self.db_contas["Nubank"] = self.db_contas["Nubank"] - valor
		elif contaOrigem == "Sangria":
			self.db_contas["Sangria"] = self.db_contas["Sangria"] - valor
		
		self.db_contas.sync()
		self.limpaCamposSaidas()
	
		
	def bRemoverSaida_clicked(self, button):
		print("Botão remover saída clicado")
		
		sel = self.selectionSaida.get_selected()
		model = sel[0]
		ID = sel[1]
		if not ID:
			return
		
		tipo, contaOrigem, valor, desc, datahora = model[ID]
		
		valor = float(valor.replace(",","."))
		
		#apagando entrada liststore
		self.liststoreSaidas.remove(ID)
		
		#atualizando contas
		if contaOrigem == "Pagbank":
			self.db_contas["Pagbank"] = self.db_contas["Pagbank"] + valor
		elif contaOrigem == "Banco do Brasil":
			self.db_contas["BB"] = self.db_contas["BB"] + valor
		elif contaOrigem == "Nubank":
			self.db_contas["Nubank"] = self.db_contas["Nubank"] + valor
		elif contaOrigem == "Sangria":
			self.db_contas["Sangria"] = self.db_contas["Sangria"] + valor
		
		self.db_contas.sync()	
		
		#atualizando DBM Saida
		saidas = self.db_EntSaiTransf["saidas"]
		i = 0
		while (i < len(saidas)):
			if saidas[i][4] == datahora:
				del saidas[i]
			i+=1
		self.db_EntSaiTransf["saidas"] = saidas
		self.db_EntSaiTransf.sync()
		
		#limpando campos
		self.limpaCamposSaidas()
		
		###############TRANSFERENCIAS################
		
	def limpaCamposTransf(self):
		self.comboboxtextContaOrigemT.set_active(4)
		self.comboboxtextContaDestinoT.set_active(3)
		self.entryValorT.props.text = ""
		self.entryDescricaoT.props.text = ""
		self.selectionTransferencia.unselect_all()
	
	def bLimparTransf_clicked(self, button):
		limpaCamposTransf()
	
	def bAdicionarTransf_clicked(self, button):
		print("Botão adicionar transferencia clicado")
		
		datahora = str(datetime.now().timestamp())
		
		#testando campo - variável val não usada
		try:
			val = float(self.entryValorT.props.text.replace(",","."))
		except ValueError:
			print("Erro com campo valor. Cadastro não realizado.")
			return
		
		contaOrigem = self.comboboxtextContaOrigemT.get_active_text()
		contaDest = self.comboboxtextContaDestinoT.get_active_text()
		
		dados = [contaOrigem,
				 contaDest,
				 self.entryValorT.props.text.replace(".",","),
				 self.entryDescricaoT.props.text, datahora]
		
		self.liststoreTransferencias.append(dados)
		
		try:
			transferencias = self.db_EntSaiTransf["transferencias"]
			transferencias.append(dados)
			self.db_EntSaiTransf["transferencias"] = transferencias
		except KeyError:
			self.db_EntSaiTransf["transferencias"] = [dados]
		
		self.db_EntSaiTransf.sync()
		
		valor = float(dados[2].replace(",","."))
		
		#atualizando contas Origem
		if contaOrigem == "Pagbank":
			self.db_contas["Pagbank"] = self.db_contas["Pagbank"] - valor
		elif contaOrigem == "Banco do Brasil":
			self.db_contas["BB"] = self.db_contas["BB"] - valor
		elif contaOrigem == "Nubank":
			self.db_contas["Nubank"] = self.db_contas["Nubank"] - valor
		elif contaOrigem == "Sangria":
			self.db_contas["Sangria"] = self.db_contas["Sangria"] - valor
		elif contaOrigem == "Fundo de Caixa":
			self.db_contas["FundoCaixa"] = self.db_contas["FundoCaixa"] - valor
			
		#atualizando contas Destino
		if contaDest == "Pagbank":
			self.db_contas["Pagbank"] = self.db_contas["Pagbank"] + valor
		elif contaDest == "Banco do Brasil":
			self.db_contas["BB"] = self.db_contas["BB"] + valor
		elif contaDest == "Nubank":
			self.db_contas["Nubank"] = self.db_contas["Nubank"] + valor
		elif contaDest == "Sangria":
			self.db_contas["Sangria"] = self.db_contas["Sangria"] + valor
		
		self.db_contas.sync()
		
		self.limpaCamposTransf()
		
		
	def bRemoverTransf_clicked(self, button):
		print("Botão remover transferencia clicado")
		
		sel = self.selectionTransferencia.get_selected()
		model = sel[0]
		ID = sel[1]
		if not ID:
			return
		
		contaOrigem, contaDest, valor, desc, datahora = model[ID]
		
		valor = float(valor.replace(",","."))
		
		#apagando entrada liststore
		self.liststoreTransferencias.remove(ID)
		
		#atualizando contas Origem
		if contaOrigem == "Pagbank":
			self.db_contas["Pagbank"] = self.db_contas["Pagbank"] + valor
		elif contaOrigem == "Banco do Brasil":
			self.db_contas["BB"] = self.db_contas["BB"] + valor
		elif contaOrigem == "Nubank":
			self.db_contas["Nubank"] = self.db_contas["Nubank"] + valor
		elif contaOrigem == "Sangria":
			self.db_contas["Sangria"] = self.db_contas["Sangria"] + valor
		elif contaOrigem == "Fundo de Caixa":
			self.db_contas["FundoCaixa"] = self.db_contas["FundoCaixa"] + valor
			
		#atualizando contas Destino
		if contaDest == "Pagbank":
			self.db_contas["Pagbank"] = self.db_contas["Pagbank"] - valor
		elif contaDest == "Banco do Brasil":
			self.db_contas["BB"] = self.db_contas["BB"] - valor
		elif contaDest == "Nubank":
			self.db_contas["Nubank"] = self.db_contas["Nubank"] - valor
		elif contaDest == "Sangria":
			self.db_contas["Sangria"] = self.db_contas["Sangria"] - valor
		
		self.db_contas.sync()
		
		#atualizando DBM Transferencia
		transferencias = self.db_EntSaiTransf["transferencias"]
		i = 0
		while (i < len(transferencias)):
			if transferencias[i][4] == datahora:
				del transferencias[i]
			i+=1
		self.db_EntSaiTransf["transferencias"] = transferencias
		self.db_EntSaiTransf.sync()
		
		#limpando campos
		self.limpaCamposTransf()
		
		
	def bFecharCaixa_clicked(self, button):
		print("Botão Fechar Caixa Clicado")
		
		datahora = str(datetime.now().timestamp())
		self.db_fechamento = shelve.open("dbs/fechamentos/{}.dbm".format(datahora))
		
		self.db_vendasDia = shelve.open("dbs/vendasDia.dbm")
		
		vendasDia = {}
		
		for id_venda in self.db_vendasDia:
			vendasDia[id_venda] = self.db_vendasDia[id_venda]
		
		self.db_fechamento["vendasDia"] = vendasDia
		
		try:
			self.db_fechamento["entradas"] = self.db_EntSaiTransf["entradas"]
		except KeyError:
			self.db_fechamento["entradas"] = []
		
		try:
			self.db_fechamento["saidas"] = self.db_EntSaiTransf["saidas"]
		except KeyError:
			self.db_fechamento["saidas"] = []
			
		try:
			self.db_fechamento["transferencias"] = self.db_EntSaiTransf["transferencias"]
		except KeyError:
			self.db_fechamento["transferencias"] = []
		
		print("VENDAS ",self.db_fechamento["vendasDia"])
		print("ENTRADAS", self.db_fechamento["entradas"])
		print("SAIDAS", self.db_fechamento["saidas"])
		print("TRANSFERENCIAS",self.db_fechamento["transferencias"])
		
		
		#limpar liststores da janela
		self.liststoreEntradas.clear()
		self.liststoreSaidas.clear()
		self.liststoreTransferencias.clear()
		
		#limpar dbs
		for id_venda in self.db_vendasDia:
			del self.db_vendasDia[id_venda]
			
		try:
			del self.db_EntSaiTransf["entradas"]
		except KeyError:
			pass
		
		try:
			del self.db_EntSaiTransf["saidas"]
		except KeyError:
			pass
			
		try:
			del self.db_EntSaiTransf["transferencias"]
		except KeyError:
			pass		
		
		#fechando dbs
		self.db_vendasDia.close()
		
		self.db_fechamento.sync()
		self.db_fechamento.close()
		
		
		#não permite fechar novamente
		button.props.sensitive = False
		
##########################################################
#
#  Relatórios
#
##########################################################

class Relatorios:
	def __init__(self):
		#Relatório Cliente
		self.searchentryCPFClienteR = builder.get_object("searchentryCPFClienteR")
		self.textviewCrediario = builder.get_object("textviewCrediario")
		
		self.comboboxtextClienteR = builder.get_object("comboboxtextClienteR")
		self.textviewClienteR = builder.get_object("textviewClienteR")
		
		#Relatórios Produto
		self.comboboxtextProdutoR = builder.get_object("comboboxtextProdutoR")
		self.textviewProdutoR = builder.get_object("textviewProdutoR")
		
		#Relatórios Venda
		self.comboboxtextVendasR = builder.get_object("comboboxtextVendasR")
		self.textviewVendasR = builder.get_object("textviewVendasR")
		self.calendarVendasR = builder.get_object("calendarVendasR")
		self.textviewConsultaVendasR = builder.get_object("textviewConsultaVendasR")
		
		#Relatórios EST
		self.textviewConsultaESTR = builder.get_object("textviewConsultaESTR")
		self.comboboxtextConsultaESTR = builder.get_object("comboboxtextConsultaESTR")
		self.calendarESTR = builder.get_object("calendarESTR")
		self.textviewExtratoESTR = builder.get_object("textviewExtratoESTR")
		
		
	def aux_gera_extrato_EST(self, entradas, saidas, transf):
		tEntradas = 0	
		tSaidas = 0	
		tTransf = 0
		
		saldo = 0
		
		msg_e = ""
		for e in entradas:
			msg_e += "  {:<21}  ".format(e[0])
			msg_e += "{:<22}  ".format(e[3][:22])
			msg_e += "{:<15}  ".format(e[1])
			msg_e += "R$ {:>7.2f}  ".format(e[2]) + "\n"
			
			tEntradas += e[2]
			
		if msg_e:
			msg_e_c =  "------------------------------------------------------------------------------\n"
			msg_e_c += "                                   ENTRADAS\n"
			msg_e_c += "------------------------------------------------------------------------------\n\n"
			
			msg_e_c += "          TIPO                  DESCRIÇÃO             CONTA          VALOR \n"
			msg_e_c += "  ---------------------  ----------------------  ---------------  ----------\n"
			
			msg_e_f =  "                                                        --------  ----------\n"
			msg_e_f += "                                                           Total  R$ {:>7.2f}\n\n".format(tEntradas)
			
			msg_e = msg_e_c + msg_e + msg_e_f
		
		msg_s = ""
		for s in saidas:
			msg_s += "  {:<21}  ".format(s[0])
			msg_s += "{:<22}  ".format(s[3][:22])
			msg_s += "{:<15}  ".format(s[1])
			valor = float(s[2].replace(",","."))
			msg_s += "R$ {:>7.2f}  ".format(valor) + "\n"
			
			tSaidas += valor
			
		if msg_s:
			msg_s_c =  "------------------------------------------------------------------------------\n"
			msg_s_c += "                                    SAÍDAS\n"
			msg_s_c += "------------------------------------------------------------------------------\n\n"
			
			msg_s_c += "          TIPO                  DESCRIÇÃO             CONTA         VALOR \n"
			msg_s_c += "  ---------------------  ----------------------  ---------------  ----------\n"
			
			msg_s_f =  "                                                        --------  ----------\n"
			msg_s_f += "                                                           Total  R$ {:>7.2f}\n\n".format(tSaidas)
			
			msg_s = msg_s_c + msg_s + msg_s_f
		
		msg_saldo = ""
		if msg_e or msg_s:
			saldo = tEntradas - tSaidas
			msg_saldo =  "-------------------------------\n"
			msg_saldo += " Entradas - Saídas: R$ {:7.2f}\n".format(saldo)
			msg_saldo += "-------------------------------\n\n"
		
		msg_t = ""
		for t in transf:
			msg_t += "  {:<16}  ".format(t[0])
			msg_t += "{:<16}  ".format(t[1])
			msg_t += "{:<26}  ".format(t[3][:26])
			valor = float(t[2].replace(",","."))
			msg_t += "R$ {:>7.2f}  ".format(valor) + "\n"
			
			tTransf += valor
			
		if msg_t:
			msg_t_c =  "------------------------------------------------------------------------------\n"
			msg_t_c += "                                 TRANSFERÊNCIAS\n"
			msg_t_c += "------------------------------------------------------------------------------\n\n"
			
			msg_t_c += "    CONTA ORIGEM     CONTA DESTINO            DESCRIÇÃO             VALOR \n"
			msg_t_c += "  ----------------  ----------------  --------------------------  ----------\n"
			
			msg_t_f =  "                                                        --------  ----------\n"
			msg_t_f += "                                                           Total  R$ {:>7.2f}\n\n".format(tTransf)
			
			msg_t = msg_t_c + msg_t + msg_t_f
		
		msg = msg_e + msg_s + msg_saldo + msg_t
		
		return msg
		
	def comboboxtextProdutoR_changed(self, comboboxtext):
		print("Combobox Consulta Produto changed")
		op = comboboxtext.get_active_text()
		
		db_produto = shelve.open("dbs/produtos.dbm")
		msg = ""
		
		if op == "Todos os Produtos":
			lVista = 0
			lPrazo = 0
			vInvestido = 0
			qtde_prod = 0
			
			msg_h  = "       PRODUTO            CATEGORIA     QTDE    PCOMPRA    LVISTA     LPRAZO\n"
			msg_h += "----------------------  -------------  ------  ---------  ---------  ---------\n\n"
			
			msg_b = ""
			
			for id_c, val in db_produto.items():
				if val[15] == "ativo":
					msg_b += "{:<24}".format(val[0][:22])	
					msg_b += "{:<15}".format(val[4][:13])	
					msg_b += "{:>6}  ".format(val[2])	
					msg_b += "R$ {:>6.2f}  ".format(val[5])
					msg_b += "R$ {:>6.2f}  ".format(val[8])	
					msg_b += "R$ {:>6.2f}".format(val[11]) + "\n"
					
					und = val[2]
					qtde_prod += und
					vInvestido += (val[5] * und)
					lVista += (val[8] * und)
					lPrazo += (val[11] * und)
			
			msg_f = "\n"
			msg_f += "Quantidade Total de Produtos: {}\n".format(qtde_prod)
			msg_f += "Valor do Estoque: R$ {:.2f}\n".format(vInvestido)
			msg_f += "Potencial de Lucro em Vendas à Vista: R$ {:.2f}\n".format(lVista)
			msg_f += "Potencial de Lucro em Vendas a Prazo: R$ {:.2f}\n".format(lPrazo)
			
			if msg_b:
				msg = msg_h + msg_b + msg_f
			else:
				msg = "Nenhum Produto Cadastrado."
				
		elif op == "Resumo de Produtos":
			lVista = 0
			lPrazo = 0
			vInvestido = 0
			qtde_prod = 0
			
			msg_h  = ""
			
			msg_b = ""
			
			for id_c, val in db_produto.items():
				if val[15] == "ativo":
					
					und = val[2]
					qtde_prod += und
					vInvestido += (val[5] * und)
					lVista += (val[8] * und)
					lPrazo += (val[11] * und)
			
			msg_b += "Quantidade Total de Produtos: {}\n".format(qtde_prod)
			msg_b += "Valor do Estoque: R$ {:.2f}\n".format(vInvestido)
			msg_b += "Potencial de Lucro em Vendas à Vista: R$ {:.2f}\n".format(lVista)
			msg_b += "Potencial de Lucro em Vendas a Prazo: R$ {:.2f}\n".format(lPrazo)
			
			if msg_b:
				msg = msg_h + msg_b
			else:
				msg = "Nenhum Produto Cadastrado."
		
		elif op == "Produtos por Categoria":
			cat = {}
			lVista = 0
			lPrazo = 0
			vInvestido = 0
			qtde_prod = 0
			
			msg_h  = "     CATEGORIA        QTDE    INVESTIDO     LVISTA       LPRAZO\n"
			msg_h += "-------------------  ------  -----------  -----------  -----------\n\n"
			
			msg_b = ""
			
			for id_c, val in db_produto.items():
				if val[15] == "ativo":
					
					try:
						linha = cat[val[4]]
					except KeyError:
						cat[val[4]] = {}
						cat[val[4]]["qtde"] = val[2]
						cat[val[4]]["investido"] =  val[5] * val[2]
						cat[val[4]]["lvista"] = val[8] * val[2]
						cat[val[4]]["lprazo"] = val[11] * val[2]
					else:
						cat[val[4]]["qtde"] += val[2]
						cat[val[4]]["investido"] += (val[5] * val[2])
						cat[val[4]]["lvista"] += (val[8] * val[2])
						cat[val[4]]["lprazo"] += (val[11] * val[2])
						
						
			for c, v in cat.items():
				msg_b += "{:<19}".format(c[:19])
				msg_b += "  {:>6}".format(v["qtde"])	
				msg_b += "  R$ {:>8.2f}".format(v["investido"])
				msg_b += "  R$ {:>8.2f}".format(v["lvista"])	
				msg_b += "  R$ {:>8.2f}".format(v["lprazo"]) + "\n"
				
				qtde_prod += v["qtde"]
				vInvestido += v["investido"]
				lVista += v["lvista"]
				lPrazo += v["lprazo"]
			
			msg_f = "\n-------------------  ------  -----------  -----------  -----------\n"
			msg_f+= "{:>19}  ".format("Totais")
			msg_f+= "{:>6}  ".format(qtde_prod)
			msg_f+= "R$ {:>8.2f}  ".format(vInvestido)
			msg_f+= "R$ {:>8.2f}  ".format(lVista)
			msg_f+= "R$ {:>8.2f}  ".format(lPrazo)
			
			if msg_b:
				msg = msg_h + msg_b + msg_f
			else:
				msg = "Nenhum Produto Cadastrado."
		
		self.textviewProdutoR.get_buffer().set_text(msg,len(msg.encode()))
		
		db_produto.close()
		
		
	def comboboxtextClienteR_changed(self, comboboxtext):
		print("Combobox Consulta Cliente changed")
		op = comboboxtext.get_active_text()
		
		db_cliente = shelve.open("dbs/clientes.dbm")
		msg = ""
		
		if op == "Todos os Clientes":
			msg_h  = "          NOME              CPF       SITUAÇÃO\n"
			msg_h += "----------------------  -----------  ----------\n\n"
			
			msg_b = ""
			
			for id_c, val in db_cliente.items():
				if val[12] == "ativo":
					msg_b += "{:<24}".format(val[0][:22])	
					msg_b += "{:<13}".format(val[5])	
					msg_b += "{:<12}".format(val[8]) + "\n"	
			
			if msg_b:
				msg = msg_h + msg_b
			else:
				msg = "Nenhum Cliente Cadastrado."
			
			
		elif op == "Clientes com Dívida":
			dTotal = 0
			msg_h  = "          NOME              CPF        VALOR\n"
			msg_h += "----------------------  -----------  ----------\n\n"
			
			msg_b = ""
			
			for id_c, val in db_cliente.items():
				if val[12] == "ativo" and val[10] > 0:
					msg_b += "{:<24}".format(val[0][:22])	
					msg_b += "{:<13}".format(val[5])	
					msg_b += "R$ {:>7.2f}".format(val[10]) + "\n"
					
					dTotal += val[10]
			
			msg_f = "\n------\nTotal em Dívidas: R$ {:.2f}".format(dTotal)
					
			if msg_b:
				msg = msg_h + msg_b + msg_f
			else:
				msg = "Nenhum Cliente com Dívida."
			
			
		elif op == "Aniversariantes do Mês":
			mes_atual = datetime.today().month
			msg_h  = "          NOME              NASC      SITUAÇÃO\n"
			msg_h += "----------------------  -----------  ----------\n\n"
			
			msg_b = ""
			
			for id_c, val in db_cliente.items():
				if val[12] == "ativo":
					
					try:
						dia,mes,ano = val[1].split("/")
						if mes == str(mes_atual):
							msg_b += "{:<24}".format(val[0][:22])
							msg_b += "{:<13}".format(val[1])
							msg_b += "{:<12}".format(val[8]) + "\n"
					except:
						continue
				
			if msg_b:
				msg = msg_h + msg_b
			else:
				msg = "Não há aniversariantes neste mês."
					
			
		self.textviewClienteR.get_buffer().set_text(msg,len(msg.encode()))
		db_cliente.close()
		
	def esconderJanelaV(self, window, *args):
		window.hide()
		return True
		
	
	def janelaRelatoriosShow(self, widget):
		print("Entrei Janela Relatórios")
		
		
	def buscaCPFClienteR(self, searchentry):
		if len(searchentry.props.text) < 11:
			self.textviewCrediario.get_buffer().set_text("",0)
			return
		
		db_cliente = shelve.open("dbs/clientes.dbm")
		db_crediario = shelve.open("dbs/crediarios.dbm")
		
		print("Pesquisando por CPF: " + searchentry.props.text)
		
		cred_hist = ""
		
		for key,item in db_cliente.items():
			if item[5] == searchentry.props.text and item[12] == "ativo":
				print("Cliente encontrado (" + key + "). Carregando dados...")
				
				cred_hist += "Crediário de " + db_cliente[key][0] + "\n\n"
				cred_hist_c = "   DATA/HORA           C/P          VALOR\n\n"
				
				cred_hist_b = ""
				
				try:
					for hist in db_crediario[key]:
						print(hist)
						if hist[0]:
							dh = datetime.fromtimestamp(float(hist[0]))
							cred_hist_b += "{:<18}".format("{:0>2}/{:0>2}/{} {:0>2}:{:0>2}".format(dh.day,dh.month,dh.year,dh.hour,dh.minute))
						else:
							cred_hist_b += " "*18
							
						cred_hist_b += "{:<16}".format(hist[1]) + "R$ {:>6.2f}".format(hist[2]) + "\n"
				except:
					cred_hist_c = "Não possui histórico.\n"
					pass
					
				cred_hist += cred_hist_c + cred_hist_b + "\n"
				cred_hist += "Saldo Devedor: R$ {:.2f}".format(db_cliente[key][10])
				
				self.textviewCrediario.get_buffer().set_text(cred_hist,len(cred_hist.encode()))
				
				break
		else:
			msg = "Cliente não cadastrado no sistema!"
			self.textviewCrediario.get_buffer().set_text(msg,len(msg.encode()))
		

		db_cliente.close()
		db_crediario.close()
		
	########### Relas EST #################
	
	def comboboxtextESTRGraf_changed(self, comboboxtext):
		print("Mudei Comboboxtext EST Gráficos")
		
		db_est = shelve.open("dbs/entrsaitransf.dbm")
		
		op = comboboxtext.get_active_text()
		
		if op == "Extrato Entradas, Saídas e Transferências (em aberto)":
			
			tEntradas = 0
			tSaidas = 0
			tTransferencias = 0
			
			try:
				entradas = db_est["entradas"]
			except KeyError:
				entradas = []
			
			for i in entradas:
				tEntradas += i[2]
			
			try:
				saidas = db_est["saidas"]
			except KeyError:
				saidas = []
			
			for i in saidas:
				tSaidas += float(i[2].replace(",","."))
	
			try:
				transf = db_est["transferencias"]
			except KeyError:
				transf = []
			
			for i in transf:
				tTransferencias += float(i[2].replace(",","."))
			
			vA = [tEntradas]
			vB = [tSaidas]
			vC = [tTransferencias]
			
			x1 = np.arange(len(vA))
			x2 = [x + 0.25 for x in x1]
			x3 = [x + 0.5 for x in x1]
			
			plt.bar(x1, vA, width=0.125, label='Entradas', color='g')
			plt.bar(x2, vB, width=0.125, label='Saídas', color='r')
			plt.bar(x3, vC, width=0.125, label='Transferências', color='b')
			
			leg = ["Em aberto"]
			
			plt.xticks([x + 0.25 for x in range(len(vA))], leg)
			
			plt.legend()
			
			plt.title("Totais EST (em aberto)")
			
			plt.show()
		
		elif op == "Resumo de Contas":
			db_conta = shelve.open("dbs/contas.dbm")
			
			vA = [db_conta["Nubank"]]
			vB = [db_conta["BB"]]
			vC = [db_conta["FundoCaixa"]]
			vD = [db_conta["Sangria"]]
			vE = [db_conta["Pagbank"]]
			
			x1 = np.arange(len(vA))
			x2 = [x + 0.25 for x in x1]
			x3 = [x + 0.5 for x in x1]
			x4 = [x + 0.75 for x in x1]
			x5 = [x + 1 for x in x1]
			
			plt.bar(x1, vA, width=0.125, label='Nubank', color='g')
			plt.bar(x2, vB, width=0.125, label='Banco do Brasil', color='r')
			plt.bar(x3, vC, width=0.125, label='Fundo de Caixa', color='b')
			plt.bar(x4, vD, width=0.125, label='Sangria', color='brown')
			plt.bar(x5, vE, width=0.125, label='Pagbank', color='gray')
			
			leg = ["Saldos"]
			
			plt.xticks([x + 0.25 for x in range(len(vA))], leg)
			
			plt.legend()
			
			plt.title("Contas")
			
			plt.show()
			
			
			db_conta.close()
			
		
		db_est.close()
		
	
	def comboboxtextESTR_changed(self, comboboxtext):
		print("Mudei Comboboxtext EST")
		
		op = comboboxtext.get_active_text()
		
		db_est = shelve.open("dbs/entrsaitransf.dbm")
		msg = ""
		
		data_s = []
		
		if op == "Extrato Entradas, Saídas e Transferências (em aberto)":			
			try:
				entradas = db_est["entradas"]
			except KeyError:
				entradas = []
			
			try:
				saidas = db_est["saidas"]
			except KeyError:
				saidas = []
				
			try:
				transf = db_est["transferencias"]
			except KeyError:
				transf = []
			
			msg = self.aux_gera_extrato_EST(entradas, saidas, transf)
			
			if not msg:
				msg = "Ainda não registros de Entradas, Saídas e Transferências."
			
		elif op == "Resumo de Contas":
			db_conta = shelve.open("dbs/contas.dbm")
			msg =  "--------------------------------\n"
			msg += "         SALDO DE CONTAS\n"
			msg += "--------------------------------\n\n"
			msg += "       CONTA          SALDO\n" 
			msg += "  ---------------  -----------\n" 
			
			for key, item in db_conta.items():
				msg += "  {:<15}  R$ {:8.2f}\n".format(key,item)
			
			db_conta.close()
		
		elif op == "Resumo de EST (7 dias)":
			datas_ts = [(datetime.now().timestamp() - d * 24*60*60) for d in range(7,0,-1)]
		elif op == "Resumo de EST (15 dias)":
			datas_ts = [(datetime.now().timestamp() - d * 24*60*60) for d in range(15,0,-1)]
		elif op == "Resumo de EST (30 dias)":
			datas_ts = [(datetime.now().timestamp() - d * 24*60*60) for d in range(30,0,-1)]
		
		if op in ("Resumo de EST (7 dias)","Resumo de EST (15 dias)","Resumo de EST (30 dias)"):
			
			msg += "------------------------------------------------\n"
			msg += "   RESUMO DE ENTRADAS, SAÍDAS E TRANSFERÊNCIAS\n"
			msg += "------------------------------------------------\n\n"
			
			tGEntradas = 0
			tGSaídas = 0
			tGTransferencias = 0
			
			for i in datas_ts:
				data = datetime.fromtimestamp(i)
				
				p = Path('./dbs/fechamentos')
				print("Varrendo fechamentos...")
				
				vendasNomeDB = None
				
				for i in p.iterdir():
					print(i)
					tmpstamp = i.as_posix().split("/")[-1].rstrip(".db")
					tmpstamp = tmpstamp.rstrip(".dbm")
					
					dataArq = datetime.fromtimestamp(float(tmpstamp))
					
					if (data.day,data.month,data.year) == (dataArq.day,dataArq.month,dataArq.year):
						print("Achei Venda(s) em",dataArq)
						vendasNomeDB = i.as_posix()
						break
				
				msg +=   " --------------------\n"
				msg +=   "   DATA: {:0>2}/{:0>2}/{}\n".format(data.day,data.month,data.year)
				msg +=   " --------------------\n\n"
				
				msg_c =  "       EST           VALOR\n"
				msg_c += "  --------------  -----------\n"
			
				if vendasNomeDB:
					tEntradas = 0
					tSaidas = 0
					tTransferencias = 0
					
					db_fechamento = shelve.open(vendasNomeDB)
					
					for i in db_fechamento["entradas"]:
						tEntradas += i[2]
					tGEntradas += tEntradas
					
					for i in db_fechamento["saidas"]:
						tSaidas += float(i[2].replace(",","."))
					tGSaídas += tSaidas
					
					for i in db_fechamento["transferencias"]:
						tTransferencias += float(i[2].replace(",","."))
					tGTransferencias += tTransferencias
					
					msg_c += "  {:<14}  R$ {:>8.2f}\n".format("Entradas",tEntradas)
					msg_c += "  {:<14}  R$ {:>8.2f}\n".format("Saídas",tSaidas)
					msg_c += "  {:<14}  R$ {:>8.2f}\n\n".format("Transferências",tTransferencias)
					
					msg += msg_c
					
					db_fechamento.close()
					
					
				else:
					msg += "    Caixa não fechado no dia.\n\n"
			
			msg += "Total de:\n"
			msg += "  Entradas       R$ {:>.2f}:\n".format(tGEntradas)
			msg += "  Saídas         R$ {:>.2f}:\n".format(tGSaídas)
			msg += "  Transferências R$ {:>.2f}:\n".format(tGTransferencias)
			
		
		self.textviewConsultaESTR.get_buffer().set_text(msg,len(msg.encode()))
		
		db_est.close()
	
	
	def notebookEST_switch_pageR(self, notebook, page, page_num):
		self.calendarESTR.select_day(datetime.now().day)
		
	def calTrocaDayRelaEST_selected(self, calendar):
		print("Selecionei Dia em Extrato EST")
		
		data_sel = calendar.get_date()
		dh_fechamento = None
		fechamentoNomeDB = None
		
		p = Path('./dbs/fechamentos')
		print("Varrendo fechamentos...")
		
		achei = False
		for i in p.iterdir():
			print(i)
			tmpstamp = i.as_posix().split("/")[-1].rstrip(".db")
			tmpstamp = tmpstamp.rstrip(".dbm")
			
			data = datetime.fromtimestamp(float(tmpstamp))
			
			if (data_sel.day,data_sel.month + 1,data_sel.year) == (data.day,data.month,data.year):
				print("Achei fechamento em",data)
				fechamentoNomeDB = i.as_posix()
				achei = True
				dh_fechamento = data
				break
		
		msg = ""
		if achei:
			db_fechamento = shelve.open(fechamentoNomeDB)
			entradas = db_fechamento["entradas"]
			saidas = db_fechamento["saidas"]
			transf = db_fechamento["transferencias"]
		
			msg = self.aux_gera_extrato_EST(entradas, saidas, transf)
			
			if not msg:
				msg = "Caixa Fechado sem registro de Entradas, Saídas e Transferências.\n"
			
			msg += "Hora do Fechamento: {:0>2}:{:0>2}".format(dh_fechamento.hour,dh_fechamento.minute)
		
		else:
			msg = "Caixa não fechado no dia selecionado."
		
		self.textviewExtratoESTR.get_buffer().set_text(msg,len(msg.encode()))
	
		
	######### Relas Vendas ################
	
	def comboboxtextVendaR_changed(self, comboboxtext):
		print("Mudei Comboboxtext Consulta Vendas")
		
		op = comboboxtext.get_active_text()
		
		msg = ""
		datas_ts = []
		
		if op == "Resumo de Vendas (hoje)":
			db_vendasDia = shelve.open("dbs/vendasDia.dbm")
			db_cliente = shelve.open("dbs/clientes.dbm")
			
			msg_c =  "--------------------------------------------------------------------------------\n"
			msg_c += "                         VENDAS HOJE (CAIXA ABERTO)\n"
			msg_c += "--------------------------------------------------------------------------------\n\n"
			
			msg_c += "               CLIENTE             HORA      FORMA PAGAMENTO      VALOR VENDA\n"
			msg_c += "  ------------------------------  -------  --------------------  -------------\n" 
			
			tVendas = 0
			forma_pag = {}
			
			for dh, v in db_vendasDia.items():
				print(dh,v)
				msg += "  {:<30}".format(db_cliente[v[0]][0][:30])
				
				horario = datetime.fromtimestamp(float(dh))
				hora, minu = horario.hour, horario.minute
				msg += "    {:0>2}:{:0>2}".format(hora,minu)
				
				msg += "  {:<20}".format(v[2])
				msg += "     R$ {:>7.2f}".format(v[6]) + "\n"
				tVendas += v[6]
				
				try:
					forma_pag[v[2]] += v[6]
				except KeyError:
					forma_pag[v[2]] = v[6]
			
			msg_f =  "                                                      ---------  -------------\n"
			msg_f += "                                                          Total     R$ {:>7.2f}\n\n".format(tVendas)
			
			msg_fp = "Total recebido em:\n"
			for forma, total in forma_pag.items():
				msg_fp += "  {:<18} R$ {:8.2f}\n".format(forma,total)
			
			if msg:
				msg = msg_c + msg + msg_f + msg_fp
			else:
				msg = "Ainda não há registros de vendas no caixa aberto."
			
			db_vendasDia.close()
			db_cliente.close()
		
		elif op == "Resumo de Vendas (7 dias)":
			datas_ts = [(datetime.now().timestamp() - d * 24*60*60) for d in range(7,0,-1)]
		elif op == "Resumo de Vendas (15 dias)":
			datas_ts = [(datetime.now().timestamp() - d * 24*60*60) for d in range(15,0,-1)]
		elif op == "Resumo de Vendas (30 dias)":
			datas_ts = [(datetime.now().timestamp() - d * 24*60*60) for d in range(30,0,-1)]
		elif op == "Vendas Por Categoria":
			msg = "Não implementado"
		
		if op in ("Resumo de Vendas (7 dias)","Resumo de Vendas (15 dias)","Resumo de Vendas (30 dias)"):
			db_cliente = shelve.open("dbs/clientes.dbm")
			
			msg += "--------------------------------------------------------------------------------\n"
			msg += "                               RESUMO DE VENDAS\n"
			msg += "--------------------------------------------------------------------------------\n\n"
			
			forma_pag = {}
			tGeral = 0
			
			for i in datas_ts:
				data = datetime.fromtimestamp(i)
				
				p = Path('./dbs/fechamentos')
				print("Varrendo fechamentos...")
				
				vendasNomeDB = None
				
				for i in p.iterdir():
					print(i)
					tmpstamp = i.as_posix().split("/")[-1].rstrip(".db")
					tmpstamp = tmpstamp.rstrip(".dbm")
					
					dataArq = datetime.fromtimestamp(float(tmpstamp))
					
					if (data.day,data.month,data.year) == (dataArq.day,dataArq.month,dataArq.year):
						print("Achei Venda(s) em",dataArq)
						vendasNomeDB = i.as_posix()
						break
				
				msg +=   " --------------------\n"
				msg +=   "   DATA: {:0>2}/{:0>2}/{}\n".format(data.day,data.month,data.year)
				msg +=   " --------------------\n\n"
				
				msg_c =  "               CLIENTE             HORA      FORMA PAGAMENTO      VALOR VENDA\n"
				msg_c += "  ------------------------------  -------  --------------------  -------------\n"
				
				if vendasNomeDB:
					db_vendas = shelve.open(vendasNomeDB)
					vendasDia = db_vendas["vendasDia"]
					db_vendas.close()
					
					msg_b = ""
					
					tVendas = 0
					
					for dh, v in vendasDia.items():
						print(dh,v)
						msg_b += "  {:<30}".format(db_cliente[v[0]][0][:30])
						
						horario = datetime.fromtimestamp(float(dh))
						hora, minu = horario.hour, horario.minute
						msg_b += "    {:0>2}:{:0>2}".format(hora,minu)
						
						msg_b += "  {:<20}".format(v[2])
						msg_b += "     R$ {:>7.2f}".format(v[6]) + "\n"
						tVendas += v[6]
						
						try:
							forma_pag[v[2]] += v[6]
						except KeyError:
							forma_pag[v[2]] = v[6]
					
					tGeral += tVendas
					
					msg_f =  "                                                      ---------  -------------\n"
					msg_f += "                                                          Total     R$ {:>7.2f}\n\n".format(tVendas)
					
					if msg_b:
						msg += msg_c + msg_b + msg_f
					else:
						msg += "    Nenhuma venda realizada no dia.\n\n"
				else:
					msg += "    Caixa não fechado no dia.\n\n"
			
			msg_fp = "Total recebido em:\n"
			for forma, total in forma_pag.items():
				msg_fp += "  {:<18}  R$ {:8.2f}\n".format(forma,total)
			msg_fp += "     ---------------  -----------\n"
			msg_fp += "  {:>18}  R$ {:8.2f}".format("Total Geral",tGeral)
			
			msg += msg_fp
			
			db_cliente.close()
			
		
		self.textviewConsultaVendasR.get_buffer().set_text(msg,len(msg.encode()))
	
	def notebookVenda_switch_pageR(self, notebook, page, page_num):
		self.calendarVendasR.select_day(datetime.now().day)
	
	
	def calTrocaDayRela_selected(self, calendar):
		print("Selecionei Dia em Vendas de Relatório")
		data_sel = calendar.get_date()
		
		db_vendasDia = shelve.open("dbs/vendasDia.dbm")
		
		#remove todas as entradas do comboboxtext e liststore
		self.comboboxtextVendasR.remove_all()
		self.textviewVendasR.get_buffer().set_text("",len(""))
		
		#verificando nas vendas do Dia (caixa não fechado)
		achei = False
		for datahora in db_vendasDia:
			data = datetime.fromtimestamp(float(datahora))
			
			if (data_sel.day,data_sel.month + 1,data_sel.year) == (data.day,data.month,data.year):
				print("Achei nas Vendas do dia",data_sel)
				achei = True
				break
		# se achei nas vendas do Dia, carrego no comboboxtext
		
		self.dictVendasDia = {}
		self.dictVendasDia["vendasDia"] = {}
		if achei:
			for datahora in db_vendasDia:
				data = datetime.fromtimestamp(float(datahora))
				dh_cb = "{:0>2}/{:0>2} {:0>2}:{:0>2}:{:0>2}".format(data.day,data.month,data.hour,data.minute,data.second)
				self.dictVendasDia[dh_cb] = datahora
				
				self.comboboxtextVendasR.append_text(dh_cb)
				
				self.dictVendasDia["vendasDia"][datahora] = db_vendasDia[datahora]
		
			self.comboboxtextVendasR.set_active(0)
			
		db_vendasDia.close()
		
		vendasNomeDB = None
		achei = False
		
		#mesmo se achar no dia, verifica nas vendas fechadas
		if True:#if not achei:
			p = Path('./dbs/fechamentos')
			print("Varrendo fechamentos...")
			for i in p.iterdir():
				print(i)
				tmpstamp = i.as_posix().split("/")[-1].rstrip(".db")
				tmpstamp = tmpstamp.rstrip(".dbm")
				
				data = datetime.fromtimestamp(float(tmpstamp))
				
				if (data_sel.day,data_sel.month + 1,data_sel.year) == (data.day,data.month,data.year):
					print("Achei Venda(s) em",data)
					vendasNomeDB = i.as_posix()
					achei = True
					break
			
			if achei:
				db_vendasDia = shelve.open(vendasNomeDB)
				#for i in db_vendasDia:
				#	print(i,db_vendasDia[i])
				vendas = db_vendasDia["vendasDia"]
					
				#self.dictVendasDia = {}
				self.dictVendasDia["vendasDia"].update(vendas)
			
				for datahora in vendas:
					data = datetime.fromtimestamp(float(datahora))
					dh_cb = "{:0>2}/{:0>2} {:0>2}:{:0>2}:{:0>2}".format(data.day,data.month,data.hour,data.minute,data.second)
					self.dictVendasDia[dh_cb] = datahora
					
					self.comboboxtextVendasR.append_text(dh_cb)
				
				self.comboboxtextVendasR.set_active(0)
		
				db_vendasDia.close()
			
			if not self.dictVendasDia["vendasDia"]:
				msg = "Não há registro de vendas no dia selecionado."
				self.textviewVendasR.get_buffer().set_text(msg,len(msg.encode()))
				
				
		
	def comboboxtextMudaHoraRela_changed(self, comboboxtext):
		print("Combobox changed em Relatório de Venda")
		try:
			#print(self.dictVendasDia)
			#print(comboboxtext.get_active_text())
			vendaSelID = self.dictVendasDia[comboboxtext.get_active_text()]
		except:
			
			return
		
		self.textviewVendasR.get_buffer().set_text("",len(""))
		
		print(self.dictVendasDia["vendasDia"][vendaSelID])
		
		db_cliente = shelve.open("dbs/clientes.dbm")
		cliente = db_cliente[self.dictVendasDia["vendasDia"][vendaSelID][0]][0]
		db_cliente.close()
		
		f = StringIO()
		
		aux_geraCupomVendaFechada(vendaSelID,cliente,self.dictVendasDia["vendasDia"][vendaSelID],_file=f)
		
		f.seek(0)
		msg = f.read()
		
		self.textviewVendasR.get_buffer().set_text(msg,len(msg.encode()))
		
		

##########################################################
#
#  Venda
#
##########################################################

class Venda:
	def __init__(self):
		#campos
		self.searchentryProdutoV = builder.get_object("searchentryProdutoV")
		self.textviewNomeProdutoV = builder.get_object("textviewNomeProdutoV")
		self.comboboxtextTamProdutoV = builder.get_object("comboboxtextTamProdutoV")
		self.adjustmentQtdeVenda = builder.get_object("adjustmentQtdeVenda")
		self.entryPrecoUntV = builder.get_object("entryPrecoUntV")
		self.entryPrecoUntVistaV = builder.get_object("entryPrecoUntVistaV")
		self.entryCodClienteV = builder.get_object("entryCodClienteV")
		self.searchentryCPFClienteV = builder.get_object("searchentryCPFClienteV")
		
		#campos fecharvenda
		self.comboboxtextFormaPagamentoFV = builder.get_object("comboboxtextFormaPagamentoFV")
		self.labelSubtotalFV = builder.get_object("labelSubtotalFV")
		self.labelTotalFV = builder.get_object("labelTotalFV")
		self.entryDescontoPorc = builder.get_object("entryDescontoPorc")
		self.entryDescontoValor = builder.get_object("entryDescontoValor")
		
		
		self.entryBuscaCliente = builder.get_object("entryBuscaCliente")
		self.entryBuscaProduto = builder.get_object("entryBuscaProduto")


		#label
		self.labelNomeClienteQuitadoV = builder.get_object("labelNomeClienteQuitadoV")
		self.labelNomeClienteCredV = builder.get_object("labelNomeClienteCredV")
		self.labelNomeClienteMeAQuitarV = builder.get_object("labelNomeClienteMeAQuitarV")
		self.labelNomeClienteMaAQuitarV = builder.get_object("labelNomeClienteMaAQuitarV")
		self.labelSubtotalV = builder.get_object("labelSubtotalV")
		self.labelSubtotalAvista = builder.get_object("labelSubtotalAvista")
		
		
		#janelas
		self.janelaVenda = builder.get_object("janelaVenda")
		self.messagedialogPerguntaSairVenda = builder.get_object("messagedialogPerguntaSairVenda")
		self.janelaFecharVenda = builder.get_object("janelaFecharVenda")
		self.dialogBuscaCliente = builder.get_object("dialogBuscaCliente")
		self.dialogBuscaProduto = builder.get_object("dialogBuscaProduto")
		self.dialogTroca = builder.get_object("dialogTroca")
		self.messagedialogAlertaFaltaCliente = builder.get_object("messagedialogAlertaFaltaCliente")
		
		#liststore
		self.liststoreItensVenda = builder.get_object("liststoreItensVenda")
		
		self.liststoreBuscaClientes = builder.get_object("liststoreBuscaClientes")
		self.selectionBuscaCliente = builder.get_object("treeview-selectionBuscaCliente")	
		
		self.liststoreBuscaProdutos = builder.get_object("liststoreBuscaProdutos")
		self.selectionBuscaProduto = builder.get_object("treeview-selectionBuscaProduto")
		
		#buttons
		self.buttonAplicarBuscaCliente = builder.get_object("buttonAplicarBuscaCliente")
		
		
		#campos TrocaItem
		self.calendarTrocaData = builder.get_object("calendarTrocaData")
		self.comboboxtextTrocaHora = builder.get_object("comboboxtextTrocaHora")
		self.labelTrocaNomeCliente = builder.get_object("labelTrocaNomeCliente")
		self.labelTrocaFormaPagamento = builder.get_object("labelTrocaFormaPagamento")
		self.selectionTroca = builder.get_object("treeview-selectionTroca")
		self.labelTrocaDesconto = builder.get_object("labelTrocaDesconto")
		self.labelValorTroca = builder.get_object("labelValorTroca")
		self.liststoreTrocaProduto = builder.get_object("liststoreTrocaProduto")
		
		
		#variáveis
		self.subtotal = 0.0
		self.subtotalAvista = 0.0
		self.idVenda = 0
		

	def esconderJanelaV(self, window, *args): #aproveitável para todas
		window.hide()
		return True
	
	def bt_cancelarVenda_clicked(self, button):
		print("Botão cancelar venda clicado")
		self.messagedialogPerguntaSairVenda.show()
	
	def bt_fecharVenda_clicked(self, button):
		print("Botão fechar venda clicado")
		self.janelaFecharVenda.show()
	
	def bt_TrocaItem_clicked(self, button):
		print("Botão Troca Item clicado")
		self.dialogTroca.show()

	####################################################################
	def bt_busca_cliente_clicked(self, button):
		print("Botão Busca cliente clicado")
		self.dialogBuscaCliente.show()
	
	def dialogBuscaClienteShow(self, widget):
		print("Entrei janela Busca Cliente")
		self.entryBuscaCliente.props.text = ""
		self.liststoreBuscaClientes.clear()
	
	def bLocalizarBC_clicked(self, button):
		print("Cliquei Localizar Cliente")
		nome = self.entryBuscaCliente.props.text
		
		self.liststoreBuscaClientes.clear()
		
		for idCliente, itens in self.db_cliente.items():
			if nome.lower() in itens[0].lower():
				self.liststoreBuscaClientes.append([idCliente,itens[0],itens[5],itens[1],itens[9],itens[10]])
		
	
	def busca_cliente_bt_clicked_cancelar(self, button):
		print("Botão Cancelar Busca Cliente")
		self.dialogBuscaCliente.hide()
		
	
	def busca_cliente_bt_clicked_aplicar(self, button):
		print("Botão Aplicar Busca Cliente")
		
		sel = self.selectionBuscaCliente.get_selected()
		model = sel[0]
		idC = sel[1]
		
		if not idC:
			return
		
		dados = model[idC]
		
		if len(dados[2]) == 11:
			self.searchentryCPFClienteV.props.text = dados[2]
		else:
			self.entryCodClienteV.props.text = dados[0]
			self.setNameColor(dados[5],dados[4],dados[1])
		
		self.dialogBuscaCliente.hide()
	####################################################################	
	
	####################################################################
	def bt_busca_produto_clicked(self, button):
		print("Botão Busca produto clicado")
		self.dialogBuscaProduto.show()
		
		
	def dialogBuscaProdutoShow(self, widget):
		print("Entrei janela Busca Produto")
		self.entryBuscaProduto.props.text = ""
		self.liststoreBuscaProdutos.clear()
	
	def bLocalizarBP_clicked(self, button):
		print("Cliquei Localizar Produto")
		nome = self.entryBuscaProduto.props.text
		
		self.liststoreBuscaProdutos.clear()
		
		for idProduto, itens in self.db_produto.items():
			if nome.lower() in itens[0].lower():
				self.liststoreBuscaProdutos.append([idProduto,itens[0]])
	
	def busca_produto_bt_clicked_cancelar(self, button):
		print("Botão Cancelar Busca Produto")
		self.dialogBuscaProduto.hide()
	
	def busca_produto_bt_clicked_aplicar(self, button):
		print("Botão Aplicar Busca Produto")
		
		sel = self.selectionBuscaProduto.get_selected()
		model = sel[0]
		idP = sel[1]
		
		if not idP:
			return
		
		dados = model[idP]
		
		self.searchentryProdutoV.props.text = dados[0]
		
		self.dialogBuscaProduto.hide()
		
	
	####################################################################
		
		
	def bt_cancelarItem_clicked(self, button):
		def apagaItemDB(listaItens,idItem):
			i = 0
			while (i < len(listaItens)):
				if listaItens[i][0] == idItem:
					del listaItens[i]
					break
				i+=1
			for j in range(i,len(listaItens)):
				listaItens[j][0] = str(j+1)
				
			return listaItens
		
		def devolveProdDB(prod, tam, qtde):
			tamqtdeUpdate = self.devolve_tamQtde(prod[1],tam,qtde)
			prod[1] = tamqtdeUpdate
			prod[2] += int(qtde)
			return prod
		
		def devolveTroca(prod, tam, qtde):
			tamqtdeUpdate = self.atualiza_tamQtde(prod[1],tam,qtde)
			prod[1] = tamqtdeUpdate
			prod[2] -= int(qtde)
			return prod
			
		print("Botao cancelar item clicado")
		selection = builder.get_object("treeview-selectionItensVenda")
		sel = selection.get_selected()
		
		model = sel[0]
		IterItem = sel[1]
		if not IterItem:
			print("Nenhum item selecionado.")
			return
		
		idItem = model[IterItem][0]
		tipoItem = model[IterItem][1]
		idProd = model[IterItem][2]
		tam = model[IterItem][4]
		qtde = model[IterItem][5]
		sTPrazo = model[IterItem][9]
		sTVista = model[IterItem][8]
		
		#1 apaga item do banco e ajusta ids
		self.db_vendaAberta["itens"] = apagaItemDB(self.db_vendaAberta["itens"],idItem)
		self.db_vendaAberta.sync()
		
		self.idVenda -= 1
		
		#2 atualiza produtos
		if tipoItem == "Incluso":
			self.db_produto[idProd] = devolveProdDB(self.db_produto[idProd], tam, qtde)
		elif tipoItem == "Troca":
			self.db_produto[idProd] = devolveTroca(self.db_produto[idProd], tam, qtde)
		self.db_produto.sync()
		
		#3 atualiza treeview
		model.clear()
		
		for item in self.db_vendaAberta["itens"]:
			model.append(item)

		
		#4 atualiza subtotais
		self.subtotal -= float(sTPrazo.replace(",","."))
		self.labelSubtotalV.props.label = "{:9.2f}".format(self.subtotal).replace(".",",")
		self.subtotalAvista += float(sTVista.replace(",","."))
		self.labelSubtotalAvista.props.label = "{:9.2f}".format(self.subtotalAvista).replace(".",",")
	
	
	def janelaFecharVendaShow(self, widget):
		print("Entrei Janela Fechar venda")
		self.comboboxtextFormaPagamentoFV.props.active = 0		
		
	def fecharJanelaFecharVenda(self, widget):
		print("Saindo da janela Fechar venda")
		self.comboboxtextFormaPagamentoFV.props.active = -1
	
	
	def mudaFormaPagamentoFV(self, combobox):
		
		if self.comboboxtextFormaPagamentoFV.props.active == -1:
			return
		
		if combobox.get_active_text() in ("Crediário","Cartão Parcelado"):
			self.labelSubtotalFV.props.label = self.labelSubtotalV.props.label
			self.labelTotalFV.props.label =  self.labelSubtotalV.props.label
		else:
			self.labelSubtotalFV.props.label = self.labelSubtotalAvista.props.label
			self.labelTotalFV.props.label =  self.labelSubtotalAvista.props.label
		
		self.entryDescontoPorc.props.text = "0,0"
		self.entryDescontoValor.props.text = "0,0"

	
	def calcPorcDesconto(self, entry, icon_pos, event):
		print("CalcValorPorc")
		try:
			valorDesconto = float(self.entryDescontoValor.props.text.replace(",","."))
			subtotal = float(self.labelSubtotalFV.props.label.replace(",","."))
			porc = (valorDesconto / subtotal ) * 100
			total = subtotal - valorDesconto
			entry.props.text = "{:.2f}".format(porc).replace(".",",")
			self.labelTotalFV.props.label = "{:9.2f}".format(total).replace(".",",")
		except Exception as e:
			print(e)
	
	
	def calcValorDesconto(self, entry, icon_pos, event):
		print("CalcValorDesc")
		try:
			porcDesconto = float(self.entryDescontoPorc.props.text.replace(",","."))/100
			subtotal = float(self.labelSubtotalFV.props.label.replace(",","."))
			valorDesconto = subtotal * porcDesconto
			total = subtotal - valorDesconto
			entry.props.text = "{:.2f}".format(valorDesconto).replace(".",",")
			self.labelTotalFV.props.label = "{:9.2f}".format(total).replace(".",",")
		except Exception as e:
			print(e)
		
		
	def dialogConfirmaCancelarVenda(self, dialog, response):
		print("Cliquei em " + str(response))
		
		if response in (Gtk.ResponseType.NO, Gtk.ResponseType.DELETE_EVENT):
			dialog.hide()
		
		if response == Gtk.ResponseType.YES:
			#cancelar a venda, devolver itens etc.
			
			itens = None
			#apaga cliente da venda
			try:
				del self.db_vendaAberta["cliente"]
			except KeyError: #pode acontecer de a venda ser cancelada sem ter selecionado cliente
				pass
				
			try:
				itens = self.db_vendaAberta["itens"]
				del self.db_vendaAberta["itens"]
			except KeyError: #pode acontecer de a venda ser cancelada sem ter selecionado cliente
				pass
			
			
			#devolvendo itens da venda
			print("Devolvendo itens")
			if itens:
				for item in itens:
					prod = self.db_produto[item[2]]
					tipoItem = item[1]
					print("Cancelando item ->",item)
					if tipoItem == "Incluso":
						tamqtdeUpdate = self.devolve_tamQtde(prod[1],item[4],item[5])
						prod[1] = tamqtdeUpdate
						prod[2] += int(item[5])
						self.db_produto[item[2]] = prod
					elif tipoItem == "Troca":
						tamqtdeUpdate = self.atualiza_tamQtde(prod[1],item[4],item[5])
						prod[1] = tamqtdeUpdate
						prod[2] -= int(item[5])
						self.db_produto[item[2]] = prod
					self.db_produto.sync()
			
			self.limpaTudoVenda()
			
			dialog.hide()
			self.janelaVenda.hide()
		
	
	def limpaTudoVenda(self):
		self.searchentryCPFClienteV.props.text = ""
		self.searchentryProdutoV.props.text = ""
		self.labelSubtotalV.props.label = "     0,00"
		self.labelSubtotalAvista.props.label = "     0,00"
		self.subtotal = 0.0
		self.subtotalAvista = 0.0
		self.idVenda = 0
		self.liststoreItensVenda.clear()
		self.limpaCamposProduto()
		
	
	def janelaVendaShow(self, widget):
		print("Entrei janela Venda")
		
		self.db_cliente = shelve.open("dbs/clientes.dbm")
		self.db_produto = shelve.open("dbs/produtos.dbm")
		self.db_vendaAberta = shelve.open("dbs/vendaAberta.dbm")
		
		#se existir uma venda aberta, carregar cliente e itens
		try:
			self.searchentryCPFClienteV.props.text = self.db_cliente[self.db_vendaAberta["cliente"]][5]
		except KeyError:
			pass
		
		try:
			itens = self.db_vendaAberta["itens"]
		except KeyError:
			pass
		else:
			for item in itens:
				self.liststoreItensVenda.append(item)
				self.subtotal += float(item[9].replace(",","."))
				self.subtotalAvista += float(item[8].replace(",","."))
				
			# atualiza subtotal
			self.labelSubtotalV.props.label = "{:9.2f}".format(self.subtotal).replace(".",",")
			self.labelSubtotalAvista.props.label = "{:9.2f}".format(self.subtotalAvista).replace(".",",")
		
		
	
	def closeJanelaVenda(self, widget):
		print("Saí janela Venda")
		
		self.db_cliente.close()
		self.db_produto.close()
		self.db_vendaAberta.close()
	
	
	def setNameColor(self, divida, crediario, nome):
		self.labelNomeClienteQuitadoV.props.label = \
		self.labelNomeClienteMeAQuitarV.props.label = \
		self.labelNomeClienteMaAQuitarV.props.label = \
		self.labelNomeClienteCredV.props.label = nome
		
		self.labelNomeClienteQuitadoV.props.visible = divida == 0
		self.labelNomeClienteCredV.props.visible = divida < 0
		
		self.labelNomeClienteMeAQuitarV.props.visible = divida > 0 and divida/crediario <= 0.5
		
		self.labelNomeClienteMaAQuitarV.props.visible = divida > 0 and divida/crediario > 0.5
	
	
	def buscaCPFClienteV(self, searchentry):
		if len(searchentry.props.text) < 11:
			self.entryCodClienteV.props.text = "0"
			self.setNameColor(0, 0, "Nenhum Cliente Selecionado")
			
			try:
				del self.db_vendaAberta["cliente"]
			except KeyError:
				pass
				
			return
		
		print("Pesquisando por CPF: " + searchentry.props.text)
		
		for key,item in self.db_cliente.items():
			if item[5] == searchentry.props.text and item[12] == "ativo":
				print("Cliente encontrado ("+ key + "). Carregando dados...")
				self.entryCodClienteV.props.text = key
				
				self.setNameColor(item[10], item[9], item[0])
				
				self.db_vendaAberta["cliente"] = str(key)
				
				return
				
		
		#se não encontrei, então
		self.entryCodClienteV.props.text = "0"
		setNameColor(0, 0, "Nenhum Cliente Selecionado") 
		
	
	
	def buscaProdCodBarra(self, searchentry):
		print("Pesquisei por '" + searchentry.props.text+"'")
		
		#verificar se esta ativo e sem tem algum tamanho cadastrado
		
		if not searchentry.props.text:
			print("Campo vazio.")
			self.limpaCamposProduto()
			return
		
		try:
			dados = self.db_produto[searchentry.props.text]
			
			if dados[15] == "inativo":
				raise InactiveItem
			
			if int(dados[2]) <= 0:
				raise NoProduct
		
			print(dados)
			
		except KeyError:
			self.limpaCamposProduto()
			return
		except InactiveItem:
			print("Produto Invativo")
			self.limpaCamposProduto()
			return
		except NoProduct:
			print("Item esgotado")
			self.limpaCamposProduto()
			return
		
		self.textviewNomeProdutoV.get_buffer().set_text(dados[0],len(dados[0].encode()))
		self.entryPrecoUntV.props.text = "{:.2f}".format(dados[10]).replace(".",",")
		self.entryPrecoUntVistaV.props.text  = "{:.2f}".format(dados[7]).replace(".",",")
		tamqtde = eval(dados[1])
		
		print(tamqtde)
		
		self.comboboxtextTamProdutoV.remove_all()
		
		for tam,qtde in tamqtde:
			if qtde > 0:
				self.comboboxtextTamProdutoV.append(str(qtde),tam)
		
		self.comboboxtextTamProdutoV.props.active = 0
			
		
	def carregarQtdeApartirTamV(self, combobox):
		if not combobox.props.active_id:
			return
			
		print("Selecionado ==> "+str(combobox.props.active_id) +"->"+combobox.get_active_text())
		self.adjustmentQtdeVenda.set_upper(int(combobox.props.active_id))
		self.adjustmentQtdeVenda.props.value = 1
		
	def limpaCamposProduto(self):
		self.textviewNomeProdutoV.get_buffer().set_text("",0)
		self.comboboxtextTamProdutoV.remove_all()
		self.adjustmentQtdeVenda.set_upper(1)
		self.entryPrecoUntV.props.text = ""
		self.entryPrecoUntVistaV.props.text = ""
		
	
	def devolve_tamQtde(self, listaTamQtde : str, tam : str, qtde : str):
		lista = eval(listaTamQtde)
		i = 0
		while( i < len(lista)):
			if lista[i][0] == tam:
				lista[i][1] += int(qtde)
				break
			i+=1
		else:
			lista.append([tam,int(qtde)])
		
		return str(lista)
	
	def atualiza_tamQtde(self, listaTamQtde : str, tam : str, qtde : str):
		lista = eval(listaTamQtde)
		i = 0
		while( i < len(lista)):
			if lista[i][0] == tam:
				lista[i][1] -= int(qtde)
				break
			i+=1
		
		if lista[i][1] <= 0:
			del lista[i]
		
		return str(lista)	
	
	
	def pegarItems(self):
		self.idVenda += 1
		idItem = str(self.idVenda)
		tipo = "Incluso"
		codBarra = self.searchentryProdutoV.props.text
		produto = self.textviewNomeProdutoV.props.buffer.props.text
		tam = self.comboboxtextTamProdutoV.get_active_text()
		qtde = self.adjustmentQtdeVenda.props.value
		precoUntVista = float(self.entryPrecoUntVistaV.props.text.replace(",","."))
		precoUntPrazo = float(self.entryPrecoUntV.props.text.replace(",","."))
		precoTotalAvista = precoUntVista * qtde
		precoTotalPrazo = precoUntPrazo * qtde
		cor = ""
		
		return [idItem, tipo, codBarra, produto, tam, str(int(qtde)),
				"{:.2f}".format(precoUntVista).replace(".",","),
				"{:.2f}".format(precoUntPrazo).replace(".",","),
				"{:.2f}".format(precoTotalAvista).replace(".",","),
				"{:.2f}".format(precoTotalPrazo).replace(".",","),
				cor]
	
	def buttonAdicionarItemVendaClicked(self,button):
		print("Botão adicionar item clicado")
		
		#verifica se tem algum produto selecionado pelo campo de preco
		if not self.entryPrecoUntV.props.text:
			print("Nenhum produto selecionado")
			return
		
		#1 - adicionar no liststore
		dados = self.pegarItems()
		self.liststoreItensVenda.append(dados)
		
		#2 - adicionar no db
		try:
			lista_itens = self.db_vendaAberta["itens"]
			lista_itens.append(dados)
			self.db_vendaAberta["itens"] = lista_itens
			self.db_vendaAberta.sync()
			print(self.db_vendaAberta["itens"])
		
		except KeyError: #é o primeiro item da lista no banco
			self.db_vendaAberta["itens"] = [dados]
		
		#3 - atualizar o db produtos
		prod = self.db_produto[self.searchentryProdutoV.props.text]
		tamqtdeUpdate = self.atualiza_tamQtde(prod[1],dados[4],dados[5])
		prod[1] = tamqtdeUpdate
		prod[2] -= int(dados[5])
		self.db_produto[self.searchentryProdutoV.props.text] = prod
		self.db_produto.sync()
		
		
		#4 - atualiza subtotal
		self.subtotal += float(dados[9].replace(",","."))
		self.labelSubtotalV.props.label = "{:9.2f}".format(self.subtotal).replace(".",",")
		self.subtotalAvista += float(dados[8].replace(",","."))
		self.labelSubtotalAvista.props.label = "{:9.2f}".format(self.subtotalAvista).replace(".",",")

		
		self.limpaCamposProduto()
		self.searchentryProdutoV.props.text = ""
		
		self.searchentryProdutoV.grab_focus()
		
	
	def bt_responseDialogFV(self,dialog,response):
		dialog.hide()
	
	def buttonFecharVendaClicked(self, button):
		try:
			self.db_vendaAberta["cliente"]
		except KeyError:
			self.messagedialogAlertaFaltaCliente.show()
			return
		
		formaPagamento = self.comboboxtextFormaPagamentoFV.get_active_text()
		datahora = str(datetime.now().timestamp())
		totalVenda = float(self.labelTotalFV.props.label.replace(",","."))
		
		db_vendasDia = shelve.open("dbs/vendasDia.dbm")
		
		try:
			db_vendasDia[datahora] = [
				self.db_vendaAberta["cliente"],
				self.db_vendaAberta["itens"],
				formaPagamento,
				float(self.labelSubtotalFV.props.label.replace(",",".")),
				float(self.entryDescontoPorc.props.text.replace(",",".")),
				float(self.entryDescontoValor.props.text.replace(",",".")),
				totalVenda
				#valor recebido?
				]
		except ValueError:
			print("Erro em algum campo (Valor desconto ou porcentagem) na hora de fechar venda.")
			db_vendasDia.close()
			return
		
		print(db_vendasDia[datahora])
		db_vendasDia.sync()
		
		
		db_contas = shelve.open("dbs/contas.dbm")
		
		print("Forma de pagamento: "+formaPagamento)
		if formaPagamento == "Boleto":
			db_contas["Nubank"] = db_contas["Nubank"] + totalVenda
		elif formaPagamento == "Cartão à Vista":
			db_contas["Pagbank"] = db_contas["Pagbank"] + totalVenda
		elif formaPagamento == "Dinheiro":
			db_contas["FundoCaixa"] = db_contas["Pagbank"] + totalVenda
		elif formaPagamento == "Trasnferência BB":
			db_contas["BB"] = db_contas["BB"] + totalVenda
		elif formaPagamento == "Trasnferência Nubank":
			db_contas["Nubank"] = db_contas["Nubank"] + totalVenda
		elif formaPagamento == "Cartão Parcelado":
			db_contas["Pagbank"] = db_contas["Pagbank"] + totalVenda * 0.9441
		
		db_contas.sync()
		db_contas.close()
		
		if formaPagamento == "Crediário":
			db_crediario = shelve.open("dbs/crediarios.dbm")
			
			try:
				historico = db_crediario[self.db_vendaAberta["cliente"]]
				historico.append([datahora,"Compra",totalVenda]) #datahora já eh a chave da venda
				db_crediario[self.db_vendaAberta["cliente"]] = historico
				
				print(historico)
			
			except KeyError: #é o primeiro item do histórico
				db_crediario[self.db_vendaAberta["cliente"]] = \
					[[None,"Dívida anterior",self.db_cliente[self.db_vendaAberta["cliente"]][10]],[datahora,"Compra",totalVenda]]

			
			cliente = self.db_cliente[self.db_vendaAberta["cliente"]]
			cliente[10] += totalVenda
			if cliente[10] > 0.0:
				cliente[8] = "A Quitar"
			self.db_cliente[self.db_vendaAberta["cliente"]] = cliente
			self.db_cliente.sync()
			
			db_crediario.sync()
			db_crediario.close()
		
				
		aux_geraCupomVendaFechada(datahora, self.db_cliente[self.db_vendaAberta["cliente"]][0], db_vendasDia[datahora])
		aux_geraCupomVendaFechada(datahora, self.db_cliente[self.db_vendaAberta["cliente"]][0], db_vendasDia[datahora],_file=open("cupom.txt","w"))
		
		self.janelaFecharVenda.hide()
		self.limpaTudoVenda()
		
		
		db_vendasDia.close()
		
		#Limpa db venda aberta
		#del self.db_vendaAberta["cliente"] #já apaga quando limpa campo cpfcliente
		del self.db_vendaAberta["itens"]
	
	 #####################################
	################# TROCA ###############
	 #####################################
	
	def bt_Troca_Cancelar_clicked(self, button):
		print("Botão Cancelar Troca Clicked")
		self.dialogTroca.hide()
	
	def dialogTrocaItemShow(self, widget):
		print("Entrei Janela Troca")
		self.TrocaID = None
		self.calendarTrocaData.select_day(datetime.now().day)
		
	def calTrocaDay_selected(self, calendar):
		print("Selecionei Dia")
		data_sel = calendar.get_date()
		
		db_vendasDia = shelve.open("dbs/vendasDia.dbm")
		
		#remove todas as entradas do comboboxtext e liststore
		self.comboboxtextTrocaHora.remove_all()
		self.liststoreTrocaProduto.clear()
		
		#verificando nas vendas do Dia (caixa não fechado)
		achei = False
		for datahora in db_vendasDia:
			data = datetime.fromtimestamp(float(datahora))
			
			if (data_sel.day,data_sel.month + 1,data_sel.year) == (data.day,data.month,data.year):
				print("Achei nas Vendas do dia",data_sel)
				achei = True
				break
		# se achei nas vendas do Dia, carrego no comboboxtext
		
		self.dictVendasDia = {}
		self.dictVendasDia["vendasDia"] = {}
		if achei:
			for datahora in db_vendasDia:
				data = datetime.fromtimestamp(float(datahora))
				dh_cb = "{:0>2}/{:0>2} {:0>2}:{:0>2}:{:0>2}".format(data.day,data.month,data.hour,data.minute,data.second)
				self.dictVendasDia[dh_cb] = datahora
				
				self.comboboxtextTrocaHora.append_text(dh_cb)
				
				self.dictVendasDia["vendasDia"][datahora] = db_vendasDia[datahora]
		
			self.comboboxtextTrocaHora.set_active(0)
			
		db_vendasDia.close()
		vendasNomeDB = None
		achei = False
		
		#mesmo se achar no dia, verifica nas vendas fechadas
		if True:#if not achei:
			p = Path('./dbs/fechamentos')
			print("Varrendo fechamentos...")
			for i in p.iterdir():
				print(i)
				tmpstamp = i.as_posix().split("/")[-1].rstrip(".db")
				tmpstamp = tmpstamp.rstrip(".dbm")
				
				data = datetime.fromtimestamp(float(tmpstamp))
				
				if (data_sel.day,data_sel.month + 1,data_sel.year) == (data.day,data.month,data.year):
					print("Achei Venda(s) em",data)
					vendasNomeDB = i.as_posix()
					achei = True
					break
			
			if achei:
				db_vendasDia = shelve.open(vendasNomeDB)
				#for i in db_vendasDia:
				#	print(i,db_vendasDia[i])
				vendas = db_vendasDia["vendasDia"]
					
				#self.dictVendasDia = {}
				self.dictVendasDia["vendasDia"].update(vendas)
			
				for datahora in vendas:
					data = datetime.fromtimestamp(float(datahora))
					dh_cb = "{:0>2}/{:0>2} {:0>2}:{:0>2}:{:0>2}".format(data.day,data.month,data.hour,data.minute,data.second)
					self.dictVendasDia[dh_cb] = datahora
					
					self.comboboxtextTrocaHora.append_text(dh_cb)
				
				self.comboboxtextTrocaHora.set_active(0)
		
				db_vendasDia.close()
				
		
	def comboboxtextTrocaHora_changed(self, comboboxtext):
		print("Combobox changed")
		try:
			#print(self.dictVendasDia)
			#print(comboboxtext.get_active_text())
			vendaSelID = self.dictVendasDia[comboboxtext.get_active_text()]
		except:
			self.labelTrocaNomeCliente.props.label = "Nenhuma Venda Selecionada"
			self.labelTrocaFormaPagamento.props.label = "Nenhuma Venda Selecionada"
			return
		
		self.liststoreTrocaProduto.clear()
		self.labelValorTroca.props.label = "0,00"
		
		print(self.dictVendasDia["vendasDia"][vendaSelID])# to be continue
		
		self.labelTrocaNomeCliente.props.label = self.db_cliente[self.dictVendasDia["vendasDia"][vendaSelID][0]][0]
		
		formaPag = self.labelTrocaFormaPagamento.props.label = self.dictVendasDia["vendasDia"][vendaSelID][2]
		
		self.labelTrocaDesconto.props.label = "{:.2f}".format(self.dictVendasDia["vendasDia"][vendaSelID][4])
		
		for venda in self.dictVendasDia["vendasDia"][vendaSelID][1]:
			if venda[1] == "Incluso":
				if formaPag in ("Crediário","Cartão Parcelado"):
					valorUnt = venda[7]
				else:
					valorUnt = venda[6]
				
				self.liststoreTrocaProduto.append([venda[0],venda[3],venda[4],venda[5],valorUnt,venda[2]])
				
	
	def prodTrocaSelecionado(self, selection):
		print("Produto Selecionado")
		sel = selection.get_selected()
		model = sel[0]
		self.TrocaID = sel[1]
		if not self.TrocaID:
			return
		
		valorProd = float(model[self.TrocaID][4].replace(",","."))
		valorDesc = 1 - float(self.labelTrocaDesconto.props.label)/100
		
		valorTroca = valorProd * valorDesc
		
		self.labelValorTroca.props.label = "{:.2f}".format(valorTroca).replace(".",",")
	
	def pegarItemsTroca(self):		
		self.idVenda += 1
		idItem = str(self.idVenda)
		tipo = "Troca"
		
		codBarra = self.liststoreTrocaProduto[self.TrocaID][5]
		produto = " *** TROCA *** " + self.liststoreTrocaProduto[self.TrocaID][1][:30]
		tam = self.liststoreTrocaProduto[self.TrocaID][2]
		qtde = "1"
		
		precoUntVista = \
		precoUntPrazo = \
		precoTotalAvista = \
		precoTotalPrazo = "-"+self.labelValorTroca.props.label
		
		cor = "green"
		
		return [idItem, tipo, codBarra, produto, tam, qtde,
				precoUntVista,
				precoUntPrazo,
				precoTotalAvista,
				precoTotalPrazo,
				cor]
				
	
	def bt_Troca_Adicionar_clicked(self, button):
		print("Adicionar Troca Clicado")
		
		#0 - primeiro verifica se tem algum produto selecionado
		if not self.TrocaID:
			print("Nenhum item selecionado para troca")
			return
		
		#1 - adicionar no liststore
		dados = self.pegarItemsTroca()
		self.liststoreItensVenda.append(dados)
		
		#2 - adicionar no db
		try:
			lista_itens = self.db_vendaAberta["itens"]
			lista_itens.append(dados)
			self.db_vendaAberta["itens"] = lista_itens
			self.db_vendaAberta.sync()
			print(self.db_vendaAberta["itens"])
		
		except KeyError: #é o primeiro item da lista no banco
			self.db_vendaAberta["itens"] = [dados]
		
		#3 - atualizar o db produtos
		prod = self.db_produto[dados[2]]
		tamqtdeUpdate = self.devolve_tamQtde(prod[1],dados[4],dados[5])
		prod[1] = tamqtdeUpdate
		prod[2] += int(dados[5])
		self.db_produto[dados[2]] = prod
		self.db_produto.sync()
		
		#4 - atualiza subtotal
		self.subtotal += float(dados[9].replace(",","."))
		self.labelSubtotalV.props.label = "{:9.2f}".format(self.subtotal).replace(".",",")
		self.subtotalAvista += float(dados[8].replace(",","."))
		self.labelSubtotalAvista.props.label = "{:9.2f}".format(self.subtotalAvista).replace(".",",")

		self.dialogTroca.hide()
		
		self.limpaCamposProduto()
		self.searchentryProdutoV.props.text = ""
		
		self.searchentryProdutoV.grab_focus()
		
		
		
		
	
	
	
##########################################################
#
#  Cadastro Produto
#
##########################################################

class CadastroProduto:
	def __init__(self):
		
		#campos
		self.entryCodBarraP = builder.get_object("entryCodBarraP")
		self.entryNomeP = builder.get_object("entryNomeP")
		self.comboboxtextTamanhoP = builder.get_object("comboboxtextTamanhoP")
		self.adjustmentQtdeCadProd = builder.get_object("adjustmentQtdeCadProd")
		self.comboboxtextCategoriaP = builder.get_object("comboboxtextCategoriaP")
		self.entryPrecoCompraP = builder.get_object("entryPrecoCompraP")
		self.entryPrecoVendaP = builder.get_object("entryPrecoVendaP")
		self.entryMargemLucroP = builder.get_object("entryMargemLucroP")
		self.labelLucroP = builder.get_object("labelLucroP")
		self.entryPrecoVenda2P = builder.get_object("entryPrecoVenda2P")
		self.entryMargemLucro2P = builder.get_object("entryMargemLucro2P")
		self.labelLucro2P = builder.get_object("labelLucro2P")
		self.entryFornecedorP = builder.get_object("entryFornecedorP")
		self.entryObservacaoP = builder.get_object("entryObservacaoP")
		self.entryTotalQtde = builder.get_object("entryTotalQtde")
		
		#liststore
		self.lsProdutosCadastrados = builder.get_object("liststoreProdutosCadastrados")
		self.liststoreTamanhosP = builder.get_object("liststoreTamanhosP")
		
		
		#self.scrolledwindowProduto = builder.get_object("scrolledwindowProduto")
		
		#botoes
		self.buttonAdicionarP = builder.get_object("buttonAdicionarP")
		self.buttonRemoverP = builder.get_object("buttonRemoverP")
		self.buttonAtualizarP = builder.get_object("buttonAtualizarP")
		
		self.buttonAdicionarTamQtdeP = builder.get_object("buttonAdicionarTamQtdeP")
		self.buttonRemoverTamQtdeP = builder.get_object("buttonRemoverTamQtdeP")
		
		#dialogos
		self.messagedialogAlertaCodBarra = builder.get_object("messagedialogAlertaCodBarra")
		self.messagedialogCadastroOKP = builder.get_object("messagedialogCadastroOKP")
		
		#variáveis
		#self.primeiravezjanelaproduto = True
	

	
	def esconderJanelaP(self, window, *args): #aproveitável para todas
		window.hide()
		return True
		

	def janelaCadProdutoShow(self, widget): 
		print("Entrei Janela Produto")
		
		self.db_produto = shelve.open("dbs/produtos.dbm")
		
		self.set_mod_addP()
		
		self.limpaCamposCadastroProduto()
		self.lsProdutosCadastrados.clear()
		
		for key,item in self.db_produto.items():
			
			if item[15] == "ativo":
				dados = [key] + item
				self.lsProdutosCadastrados.append(dados)
		
	
	
	def closeJanelaProduto(self, widget): 
		print("Fechei Janela Produto")
		
		self.db_produto.close()
	
	
	def limpaCamposCadastroProduto(self):
		self.entryCodBarraP.props.text = ""
		self.entryNomeP.props.text = ""
		self.comboboxtextTamanhoP.props.active = 0
		self.adjustmentQtdeCadProd.props.value = 0
		self.comboboxtextCategoriaP.props.active = 0
		self.entryPrecoCompraP.props.text = ""
		self.entryPrecoVendaP.props.text = ""
		self.entryMargemLucroP.props.text = "100"
		self.labelLucroP.props.label = "     0,00"
		self.entryPrecoVenda2P.props.text = ""
		self.entryMargemLucro2P.props.text = "100"
		self.labelLucro2P.props.label = "     0,00"
		self.entryFornecedorP.props.text = ""
		self.entryObservacaoP.props.text = ""
		
		self.entryTotalQtde.props.text = "0"
		
		selectionP = builder.get_object("treeview-selectionProduto")
		selectionP.unselect_all()
		
		self.liststoreTamanhosP.clear()
		
		self.entryCodBarraP.grab_focus() #nao funcionou
		
	
	def buttonLimparP_clicked(self,button):
		self.limpaCamposCadastroProduto()
		self.set_mod_addP()

	def set_mod_addP(self):
		self.buttonAdicionarP.props.sensitive = True
		self.buttonRemoverP.props.sensitive = False
		self.buttonAtualizarP.props.sensitive = False
		
		self.labelCodBarraP = builder.get_object("labelCodBarraP")
		self.labelCodBarraP.props.sensitive = True
		self.entryCodBarraP.props.sensitive = True
		
	
	def set_mod_rem_updateP(self):
		self.buttonAdicionarP.props.sensitive = False
		self.buttonRemoverP.props.sensitive = True
		self.buttonAtualizarP.props.sensitive = True
		
		self.labelCodBarraP = builder.get_object("labelCodBarraP")
		self.labelCodBarraP.props.sensitive = False
		self.entryCodBarraP.props.sensitive = False


	def bt_responseDialogP(self, dialog, response):
		dialog.hide()
		

	def pegarDadosProduto(self):
		codigoBarra = self.entryCodBarraP.props.text
		nome = self.entryNomeP.props.text
		
		qtdeTotal = 0 if not self.entryTotalQtde.props.text else int(self.entryTotalQtde.props.text)
		
		idcategoria = self.comboboxtextCategoriaP.props.active
		categoria = self.comboboxtextCategoriaP.get_active_text()
		precoCompra = aux_corrigePreco(self.entryPrecoCompraP.props.text)
		margemLucro = aux_corrigePreco(self.entryMargemLucroP.props.text)
		precoVenda = aux_corrigePreco(self.entryPrecoVendaP.props.text)
		lucro = self.labelLucroP.props.label
		margemLucro2 = aux_corrigePreco(self.entryMargemLucro2P.props.text)
		precoVenda2 = aux_corrigePreco(self.entryPrecoVenda2P.props.text)
		lucro2 = self.labelLucro2P.props.label
		fornecedor = self.entryFornecedorP.props.text
		observacao = self.entryObservacaoP.props.text
		
		#construir lista a partir dos dados do liststore tam x qtde
		tamQtde = []
		
		for items in self.liststoreTamanhosP:
			tamQtde.append([items[0],items[1]])
		
		#####
		
		cor = "lightgreen" if qtdeTotal >= 5 else ("lightblue" if qtdeTotal >=2 else "red")
		
		status = "ativo"
		
		return [codigoBarra,nome,str(tamQtde),qtdeTotal,idcategoria,categoria,
				float(precoCompra.strip().replace(",",".")),
				float(margemLucro.strip().replace(",",".")),
				float(precoVenda.strip().replace(",",".")),
				float(lucro.strip().replace(",",".")),
				float(margemLucro2.strip().replace(",",".")),
				float(precoVenda2.strip().replace(",",".")),
				float(lucro2.strip().replace(",",".")),
				fornecedor,observacao,cor,status]
		
		
	def bAddProdutoClicked(self, button):
		print("Você clicou no botão Cadastrar Produto")
		
		#valida campo CodBarra
		if not self.entryCodBarraP.props.text:
			self.messagedialogAlertaCodBarra.show()
			return
		
		dados = self.pegarDadosProduto()
		print(dados)
		
		self.lsProdutosCadastrados.append(dados)
		
		self.db_produto[dados[0]] = dados[1:]
		
		self.db_produto.sync()
		
		self.limpaCamposCadastroProduto()
		
		self.messagedialogCadastroOKP.show()
		#posso emitir mensagem por erro tbm. coloco um try antes de dados =
	
	
	def produtoSelecionado(self, selection):
		sel = selection.get_selected()
		model = sel[0]
		self.IDP = sel[1]
		if not self.IDP:
			return
		
		dados = model[self.IDP]
		
		self.cod_produto = dados[0]
		
		self.entryCodBarraP.props.text = dados[0]
		self.entryNomeP.props.text = dados[1]
		
		self.entryTotalQtde.props.text = str(dados[3])
		self.comboboxtextCategoriaP.props.active = dados[4]
		self.entryPrecoCompraP.props.text = "{:.2f}".format(dados[6]).replace(".",",")
		self.entryMargemLucroP.props.text = "{:.2f}".format(dados[7]).replace(".",",")
		self.entryPrecoVendaP.props.text  = "{:.2f}".format(dados[8]).replace(".",",")
		self.labelLucroP.props.label = "{:9.2f}".format(dados[9]).replace(".",",")
		self.entryMargemLucro2P.props.text = "{:.2f}".format(dados[10]).replace(".",",")
		self.entryPrecoVenda2P.props.text  = "{:.2f}".format(dados[11]).replace(".",",")
		self.labelLucro2P.props.label = "{:9.2f}".format(dados[12]).replace(".",",")
		self.entryFornecedorP.props.text =  dados[13]
		self.entryObservacaoP.props.text =  dados[14]
		
		self.liststoreTamanhosP.clear()
		
		tamQtde = eval(dados[2])
		for item in tamQtde:
			self.liststoreTamanhosP.append(item)
		
		self.set_mod_rem_updateP()
	
	def bRemProdutoClicked(self, button):
		print("Você clicou no botão Remover Produto")
		
		dados = list(self.db_produto[self.cod_produto])
		dados[15] = "inativo"
		
		self.db_produto[self.cod_produto] = dados
		self.db_produto.sync()
		
		print("Produto removido: " + str(self.db_produto[self.cod_produto]))
		
		self.lsProdutosCadastrados.remove(self.IDP)
		
		self.limpaCamposCadastroProduto()
		self.set_mod_addP()

		
	def bAtualizarProdutoClicked(self,button):
		print("Você clicou no botão Atualizar Produto")
		dados = self.pegarDadosProduto()
		
		self.db_produto[dados[0]] = dados[1:]
		self.db_produto.sync()
		
		self.lsProdutosCadastrados[self.IDP] = dados
		
		self.limpaCamposCadastroProduto()
		self.set_mod_addP()
	
	
	def calcPrecoVendaClicked(self, entry, icon_pos, event):
		try:
			pc = float(self.entryPrecoCompraP.props.text.replace(",","."))
			pv = (float(self.entryMargemLucroP.props.text.replace(",","."))/100 + 1) * pc
			entry.props.text = str(pv).replace(".",",")
			self.labelLucroP.props.label = "{:9.2f}".format(pv - pc).replace(".",",")
		except:
			pass
	
	def calcMargemLucroClicked(self, entry, icon_pos, event):
		try:
			pc = float(self.entryPrecoCompraP.props.text.replace(",","."))
			pv = float(self.entryPrecoVendaP.props.text.replace(",","."))
			ml = (pv / pc - 1) * 100
			entry.props.text = str(ml).replace(".",",")
			self.labelLucroP.props.label = "{:9.2f}".format(pv - pc).replace(".",",")
		except:
			pass
	
	
	def calcPrecoVenda2Clicked(self, entry, icon_pos, event):
		try:
			pc = float(self.entryPrecoCompraP.props.text.replace(",","."))
			pv = (float(self.entryMargemLucro2P.props.text.replace(",","."))/100 + 1) * pc
			entry.props.text = str(pv).replace(".",",")
			self.labelLucro2P.props.label = "{:9.2f}".format(pv - pc).replace(".",",")
		except:
			pass
	
	def calcMargemLucro2Clicked(self, entry, icon_pos, event):
		try:
			pc = float(self.entryPrecoCompraP.props.text.replace(",","."))
			pv = float(self.entryPrecoVenda2P.props.text.replace(",","."))
			ml = (pv / pc - 1) * 100
			entry.props.text = str(ml).replace(".",",")
			self.labelLucro2P.props.label = "{:9.2f}".format(pv - pc).replace(".",",")
		except:
			pass
	
	
	
	def bAddTamQtdeClicked(self, button):
		dados = [self.comboboxtextTamanhoP.get_active_text(),
				self.adjustmentQtdeCadProd.props.value]
				
		self.liststoreTamanhosP.append(dados)
		
		self.entryTotalQtde.props.text = str(int(self.entryTotalQtde.props.text) + int(dados[1]))
	
	def tamQtdeSelecionado(self, selection):
		sel = selection.get_selected()
		model = sel[0]
		self.IDTQ = sel[1]
		
		if not self.IDTQ:
			return
		
		self.qtdeSub = model[self.IDTQ][1]
	
	def bRemTamQtdeClicked(self, button):
		self.entryTotalQtde.props.text = str(int(self.entryTotalQtde.props.text) - self.qtdeSub)
		
		self.liststoreTamanhosP.remove(self.IDTQ)
		

	def verificaEntradaPreco(self, entry, event):
		print("Digitei " + event.string)
		
		return aux_verificaEntradaPreco(entry, event)


	def buscaCodBarraProd(self,widget,event):
		print("Saindo do Entry Cod. Barra")
		print("==> " + self.entryCodBarraP.props.text)
		
		if not self.entryCodBarraP.props.text:
			print("Campo vazio.")
			return
		
		try:
			dados = self.db_produto[self.entryCodBarraP.props.text]
			#não verifiquei para o caso de existir, porém inativo. Se tiver inativo, vai cadastrar por cima
		
			print("Codigo cadastrado")
			print("Carregando dados")
			
			#negocio é so como fazer para selecionar de forma eficiente
			#pelo que estou vendo, terei que pegar o primeiro Iter e sair
			#percorrendo até encontrar os cod barra para pegar o iter e continuar o processamento
			
			it = self.lsProdutosCadastrados.get_iter_first()
			
			selectionP = builder.get_object("treeview-selectionProduto")
			
			while it:
				if self.lsProdutosCadastrados.get_value(it,0) == self.entryCodBarraP.props.text:
					selectionP.select_iter(it)
					break

				it = self.lsProdutosCadastrados.iter_next(it)
			
			
		except KeyError:
			print("Código ainda não cadastrado")
			
		except ValueError:
			print("Fechei janela com o campo Cód Barra selecionado")
			
		
		

##########################################################
#
#  Cadastro Cliente
#
##########################################################
	
	
class CadastroCliente:
	
	def __init__(self):
		
		#campos
		self.entryCod = builder.get_object("entryCod")
		self.entryNome = builder.get_object("entryNome")
		self.entryNascimento = builder.get_object("entryNascimento")
		self.comboboxtextSexo = builder.get_object("comboboxtextSexo")
		self.entryCelular = builder.get_object("entryCelular")
		self.entryCPF = builder.get_object("entryCPF")
		self.entryEndereco = builder.get_object("entryEndereco")
		self.entryEmail = builder.get_object("entryEmail")
		self.labelSituacao = builder.get_object("labelSituacao")
		self.entryCrediario = builder.get_object("entryCrediario")
		self.entryDivida = builder.get_object("entryDivida")
		self.labelDivida = builder.get_object("labelDivida")
		
		#liststore
		self.lsClientesCadastrados = builder.get_object("liststoreClientesCadastrados")
		#self.scrolledwindowcliente = builder.get_object("scrolledwindowcliente")
		
		
		#botoes
		self.buttonAdicionarC = builder.get_object("buttonAdicionarC")
		self.buttonRemoverC = builder.get_object("buttonRemoverC")
		self.buttonAtualizarC = builder.get_object("buttonAtualizarC")
		
		#janelas
		self.messagedialogCadastroOKC = builder.get_object("messagedialogCadastroOKC")
		
		
		#variáveis
		#self.primeiravezjanelacliente = True

		
	def quit(self, *args): #incluir no glade
		print("Saindo...")
		Gtk.main_quit()
		
	def bt_responseDialogC(self, dialog, response):
		dialog.hide()

		
	def set_mod_add(self):
		self.buttonAdicionarC.props.sensitive = True
		self.buttonRemoverC.props.sensitive = False
		self.buttonAtualizarC.props.sensitive = False
	
	def set_mod_rem_update(self):
		self.buttonAdicionarC.props.sensitive = False
		self.buttonRemoverC.props.sensitive = True
		self.buttonAtualizarC.props.sensitive = True
	
	def limpaCamposCadastroCliente(self):
		self.entryCod.props.text = str(len(self.db_cliente) + 1)
		self.entryNome.props.text = ""
		self.entryNascimento.props.text = ""
		self.comboboxtextSexo.props.active = 0
		self.entryCelular.props.text = ""
		self.entryCPF.props.text = ""
		self.entryEndereco.props.text = ""
		self.entryEmail.props.text = ""
		self.labelSituacao.props.label = "Quitado"
		self.entryDivida.props.text = ""
		self.entryCrediario.props.text = ""
		selection = builder.get_object("treeview-selectionCliente")
		selection.unselect_all()
		
		self.entryNome.grab_focus()
		

	def buttonLimparC_clicked(self,button):
		self.limpaCamposCadastroCliente()
		self.set_mod_add()
	
	
	def clienteSelecionado(self, selection):
		sel = selection.get_selected()
		model = sel[0]
		self.IDC = sel[1]
		if not self.IDC:
			return
		
		dados = model[self.IDC]
		
		self.cod_cliente = str(dados[0])
		
		self.entryCod.props.text = str(dados[0])
		self.entryNome.props.text = dados[1]
		self.entryNascimento.props.text = dados[2]
		self.comboboxtextSexo.props.active = dados[3]
		self.entryCelular.props.text = dados[5]
		self.entryCPF.props.text = dados[6]
		self.entryEndereco.props.text = dados[7]
		self.entryEmail.props.text = dados[8]
		self.labelSituacao.props.label = dados[9]
		self.entryCrediario.props.text = "{:.2f}".format(dados[10]).replace(".",",")
		self.entryDivida.props.text = "{:.2f}".format(dados[11]).replace(".",",")
		
		self.set_mod_rem_update()
	

	
	def esconderJanela(self, window, *args): #aproveitável para todas
		window.hide()
		return True
		
		
	def closeJanelaCliente(self, button):
		print("Fechei Janela Cliente")
		
		self.db_cliente.close()
		
		
	def janelaCadClienteShow(self, button):
		print("Entrei Janela Cliente")
		
		self.db_cliente = shelve.open("dbs/clientes.dbm")
		
		self.set_mod_add()
		
		self.limpaCamposCadastroCliente()
		self.lsClientesCadastrados.clear()

		self.entryCod.props.text = str(len(self.db_cliente) + 1)
		
		for key,item in self.db_cliente.items():
			if item[12] == "ativo":
				dados = [int(key),] + item
				self.lsClientesCadastrados.append(dados)
			
		
	
	
	def pegarDadosCliente(self):
		codigo = self.entryCod.props.text
		nome = self.entryNome.props.text
		nascimento = self.entryNascimento.props.text
		sexo = self.comboboxtextSexo.get_active_text()
		idsexo = self.comboboxtextSexo.props.active
		celular = self.entryCelular.props.text
		cpf = self.entryCPF.props.text
		endereco = self.entryEndereco.props.text
		email = self.entryEmail.props.text
		situacao = self.labelSituacao.props.label
		crediario = aux_corrigePreco(self.entryCrediario.props.text)
		divida = aux_corrigePreco(self.entryDivida.props.text)
		status = "ativo"
		
		cor = "lightgreen" if situacao == "Quitado" else "red"
		if situacao == "Quitado":
			cor = "lightgreen"
		elif situacao == "A Quitar":
			cor = "red"
		else:
			cor = "blue"
		
		return [int(codigo),nome,nascimento,int(idsexo),sexo,celular,cpf,
				endereco,email,situacao,
				float(crediario.replace(",",".")),
				float(divida.replace(",","."))
				,cor,status]
		
	
	def bAddClienteClicked(self, button):
		print("Você clicou no botão Cadastrar")
		
		dados = self.pegarDadosCliente()
		print(dados)
		
		self.lsClientesCadastrados.append(dados)
		#vad = self.scrolledwindowcliente.get_vadjustment()
		#print(vad.props.value,vad.props.lower)
		#vad.props.value = vad.props.upper
		#self.scrolledwindowcliente.set_vadjustment(vad)
		
		self.db_cliente[str(dados[0])] = dados[1:]
		
		self.db_cliente.sync()
		
		self.limpaCamposCadastroCliente()
		
		self.messagedialogCadastroOKC.show()
		
	
	def bRemClienteClicked(self, button):
		print("Você clicou no botão Remover")
		
		dados = list(self.db_cliente[self.cod_cliente])
		dados[12] = "inativo"
		
		self.db_cliente[self.cod_cliente] = dados
		self.db_cliente.sync()
		
		print(self.db_cliente[self.cod_cliente])
		
		self.lsClientesCadastrados.remove(self.IDC)
		
		self.limpaCamposCadastroCliente()
		self.set_mod_add()
		
	def bAtualizarClienteClicked(self,button):
		print("Você clicou no botão Atualizar")
		dados = self.pegarDadosCliente()
		
		self.db_cliente[str(dados[0])] = dados[1:]
		self.db_cliente.sync()
		
		self.lsClientesCadastrados[self.IDC] = dados
		
		self.limpaCamposCadastroCliente()
		self.set_mod_add()
	
	
	def comboboxtextSituacao_changed(self,comboboxtext):
		if comboboxtext.props.active == 0:
			self.labelDivida.props.sensitive = False
			self.entryDivida.props.sensitive = False
		else:
			self.labelDivida.props.sensitive = True
			self.entryDivida.props.sensitive = True
		
	
	def verificaEntradaCPF(self,entry, event):
		print("Digitei " + event.string)
		return aux_verificaEntradaCPF(entry, event)
	
	def verificaEntradaPrecoCred(self, entry, event):
		print("Digitei " + event.string)
		return aux_verificaEntradaPreco(entry, event)

	def verificaEntradaPrecoDiv(self, entry, event):
		print("Digitei " + event.string)
		return aux_verificaEntradaPrecoPN(entry, event)
		
	
	def verificaDivida(self, entry, event):
		print("Saindo campo divida")
		print("Valor ==> " + entry.props.text)
		
		if not entry.props.text:
			self.labelSituacao.props.label = "Quitado"
		else:
			valor = float(entry.props.text.replace(",","."))
			if valor > 0.0:
				self.labelSituacao.props.label = "A Quitar"
			elif valor == 0.0:
				self.labelSituacao.props.label = "Quitado"
			else:
				self.labelSituacao.props.label = "Crédito"
	
	
	def buscaCadastroCPFCliente(self, entry, event):
		
		if len(entry.props.text) < 11:
			return
		
		print("Buscando Cadastro Cliente pelo CPF")
		
		for key,item in self.db_cliente.items():
			if item[5] == entry.props.text and item[12] == "ativo":
				print("Cliente está cadastrado. Carregando dados")
				break

		it = self.lsClientesCadastrados.get_iter_first()
		
		selectionC = builder.get_object("treeview-selectionCliente")
		
		while it:
			if self.lsClientesCadastrados.get_value(it,6) == self.entryCPF.props.text:
				selectionC.select_iter(it)
				break

			it = self.lsClientesCadastrados.iter_next(it)


#################
#
# Handler
#
#################

class Handler(JanelaPrincipal,CadastroCliente,CadastroProduto,Venda,EntradaSaidaTransf,Relatorios):	
	def __init__(self):
		JanelaPrincipal.__init__(self)
		CadastroCliente.__init__(self)
		CadastroProduto.__init__(self)
		Venda.__init__(self)
		EntradaSaidaTransf.__init__(self)
		Relatorios.__init__(self)

builder = Gtk.Builder()
builder.add_from_file("IMStoreStock.glade")
builder.connect_signals(Handler())

window = builder.get_object("janelaprincipal")
window.show_all()

Gtk.main()
