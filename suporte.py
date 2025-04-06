#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
import shelve
import datetime

def cad_clientes_teste():
	db_cliente = shelve.open("dbs/clientes.dbm")
	
	for i in range(1000):
	
		dados = ["cliente"+str(i+1),"data",0,"Masculino" if (i % 2) else "Feminino","cel","{:0=11}".format(i),
		"endereco","email","Quitado",0.0,0.0,"lightgreen","ativo"]
		db_cliente[str(i+1)] = dados
	
	db_cliente.sync()
	db_cliente.close()

def cad_produtos_teste():
	db_produto = shelve.open("dbs/produtos.dbm")
	
	for i in range(300):
		cod = "codbarra"+"{:0=5}".format(i)
		dados = ["Produto"+str(i),"[['M',2]]",2,0,"Cosméticos",
				50.0,
				100.0,
				100.0,
				50.0,
				200.0,
				150.0,
				100.0,
				"alguem","nenhuma","lightblue","ativo"]
				
		db_produto[cod] = dados
		
		#for k,v in db_produto.items():
		#	print(k,v)
	
	db_produto.sync()
	db_produto.close()



def iniciar_contas():
	db_conta = shelve.open("dbs/contas.dbm")
	db_conta["Nubank"] = 0.0
	db_conta["BB"] = 0.0
	db_conta["FundoCaixa"] = 1000.0
	db_conta["Sangria"] = 0.0
	db_conta["Pagbank"] = 0.0
	db_conta.sync()
	db_conta.close()

def testes_variados():
	i = 0
	while( i < 5):
		if i == 410:
			break
		i+=1
	else:
		print(i)


def consulta_crediario():
	db_crediario = shelve.open("dbs/crediarios.dbm")
	db_cliente = shelve.open("dbs/clientes.dbm")
	
	for cliente, historico in db_crediario.items():
		print("Crediário de " + db_cliente[cliente][0])
		for hist in historico:
			datahora = datetime.datetime.fromtimestamp(float(hist[0] if hist[0] else "0"))
			print(datahora, "{:10}".format(hist[1]), hist[2])
	
	db_crediario.close()
	db_cliente.close()

def consulta_contas():
	db_conta = shelve.open("dbs/contas.dbm")
	print("Contas:")
	for key, item in db_conta.items():
		print("Conta: {:10} Valor: R$ {:8.2f}".format(key,item))
	db_conta.close()

def consulta_entradas():
	db_est = shelve.open("dbs/entrsaitransf.dbm")
	entradas = db_est["entradas"]
	print("ENTRADAS: ")
	for item in entradas:
		print(item)
	db_est.close()
	
def consulta_saidas():
	db_est = shelve.open("dbs/entrsaitransf.dbm")
	entradas = db_est["saidas"]
	print("SAIDAS: ")
	for item in entradas:
		print(item)
	db_est.close()

def consulta_transferencias():
	db_est = shelve.open("dbs/entrsaitransf.dbm")
	entradas = db_est["transferencias"]
	print("TRANSFERENCIAS: ")
	for item in entradas:
		print(item)
	db_est.close()

def primeira_vez():
	db_conta = shelve.open("dbs/contas.dbm")
	print("Olá, Izaias e Mel. Vamos configurar o saldo de suas contas.")
	
	while True:
		saldo = input("Entre com o Saldo do Nubank: ")
		
		try:
			valor = float(saldo.replace(",","."))
		except:
			print("Oooops. Acho que digitou o valor errado. Vamos tentar novamente...")
			continue
		
		confirmacao = input("Confere o valor de R$ {:.2f}? S/N".format(valor))
		
		if confirmacao.lower() is not "n":
			print("Valor R$ {:.2f} confirmado.".format(valor))
			db_conta["Nubank"] = valor
			break
		else:
			continue
		
	
	while True:
		saldo = input("Entre com o Saldo do Banco do Brasil: ")
		
		try:
			valor = float(saldo.replace(",","."))
		except:
			print("Oooops. Acho que digitou o valor errado. Vamos tentar novamente...")
			continue
		
		confirmacao = input("Confere o valor de R$ {:.2f}? S/N".format(valor))
		
		if confirmacao.lower() is not "n":
			print("Valor R$ {:.2f} confirmado.".format(valor))
			db_conta["BB"] = valor
			break
		else:
			continue
		
	
	while True:
		saldo = input("Entre com o Saldo do Fundo de Caixa: ")
		
		try:
			valor = float(saldo.replace(",","."))
		except:
			print("Oooops. Acho que digitou o valor errado. Vamos tentar novamente...")
			continue
		
		confirmacao = input("Confere o valor de R$ {:.2f}? S/N".format(valor))
		
		if confirmacao.lower() is not "n":
			print("Valor R$ {:.2f} confirmado.".format(valor))
			db_conta["FundoCaixa"] = valor
			break
		else:
			continue
		
			
	while True:
		saldo = input("Entre com o Saldo da Sangria: ")
		
		try:
			valor = float(saldo.replace(",","."))
		except:
			print("Oooops. Acho que digitou o valor errado. Vamos tentar novamente...")
			continue
		
		confirmacao = input("Confere o valor de R$ {:.2f}? S/N".format(valor))
		
		if confirmacao.lower() is not "n":
			print("Valor R$ {:.2f} confirmado.".format(valor))
			db_conta["Sangria"] = valor
			break
		else:
			continue
		
	
	while True:
		saldo = input("Entre com o Saldo do Pagbank: ")
		
		try:
			valor = float(saldo.replace(",","."))
		except:
			print("Oooops. Acho que digitou o valor errado. Vamos tentar novamente...")
			continue
		
		confirmacao = input("Confere o valor de R$ {:.2f}? S/N".format(valor))
		
		if confirmacao.lower() is not "n":
			print("Valor R$ {:.2f} confirmado.".format(valor))
			db_conta["Pagbank"] = valor
			break
		else:
			continue
		
	
	db_conta.sync()
	db_conta.close()
	
	print()
	consulta_contas()
	
#iniciar_contas()
#consulta_crediario()
#print()
#consulta_contas()
#print()
#consulta_entradas()
#consulta_saidas()
#consulta_transferencias()
primeira_vez()
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
