from urllib.request import urlopen 
from urllib.error 	import HTTPError
from bs4 			import BeautifulSoup
from pymongo 		import MongoClient
from bson.objectid 	import ObjectId

from urllib.request import 	urlopen 
from urllib.error 	import 	HTTPError
from bs4 			import 	BeautifulSoup
from pymongo 		import	MongoClient

import 				os
import 				wget
import 				requests

client  			= 	MongoClient('localhost', 27017)
momodb				=	client.momodb
agroupations		=	momodb.agroupations
agroupations_		=	momodb.agroupations_
agroupations__		=	momodb.agroupations__
authors_components	=	momodb.authors_components
authors_components_	=	momodb.authors_components_
authors_components__=	momodb.authors_components__

def set_authorship():
	#	Para cada author_component, definimos las agrupaciones de las que es autor (si procede)
	for ac in authors_components_.find():
		id_ 		=	str(ac['id_'])

		authorship 	=	[]

		for ag in agroupations__.find({'authors':str(id_)}):
			authorship.append({
				'id_':ag['id_'],
				'role':ag['authors_components'][id_]
			})
		print(authorship)

		authors_components__.insert_one(ac)
		authors_components__.update_one({'id_':id_}, {'$set':{'id_':str(id_)}}),
		authors_components__.update_one({'id_':id_}, {'$set':{'authorship':authorship}})
		input('ok?')

		# no sé por qué no pone el campo authorship
set_authorship()


def set_roles():
	for ag in agroupations.find():
		id_ =	ag['id_']

		authors 	=	[]
		directors	=	[]
		guitar 		=	[]
		bombo 		=	[]
		caja 		=	[]
		components 	=	[]



		for ac in list(ag['authors_components'].keys()):
			if 'Letra' in ag['authors_components'][ac] or 'Música' in ag['authors_components'][ac]:
				authors.append(ac)
			if 'Dirección' in ag['authors_components'][ac]:
				directors.append(ac)
			if 'Guitarra' in ag['authors_components'][ac]:
				guitar.append(ac)
			if 'Bombo' in ag['authors_components'][ac]:
				bombo.append(ac)
			if 'Caja' in ag['authors_components'][ac]:
				caja.append(ac)
			if 'Componente' in ag['authors_components'][ac]:
				components.append(ac)

		#	Actualizamos documento
		agroupations__.insert_one(ag)
		agroupations__.update_one({'id_':id_}, {'$set':{'authors':authors, 'directors':directors, 'guitar':guitar,
			'bombo':bombo, 'caja':caja, 'components':components}})

		#print(agroupations.find_one({'id_':id_}))


#	Corregimos los que tienen el raning sin asignar
'''for ag in agroupations.find({'ranking':".Sin Asignar"}):
	print(ag['name'] + ' -- ' + ag['id_'])
	ranking =	input('Ranking: ').strip()
	print(ranking)
	agroupations.update_one({'id_':ag['id_']}, {'$set':{'ranking':ranking}})
	ag 	=	agroupations.find_one({'id_':ag['id_']})
	print(ag['name'] + ' -- ' + ag['id_'] + ' -- ' + ag['ranking'])
	input('ok?')
'''
'''
#	Asignamos campo imagen a las que corresponda
for it in os.listdir('../img/agroupations/'):
	id_ 	= 	it.split('.')[0]

	agroupations.update_one({'id_':id_}, {'$set':{'image':True}})
'''

'''
#	Actalizamos las de 2020
for ag_ in agroupations_.find({'year':'2020'}):
	id_ 	=	str(ag_['id_'])
	ranking	=	ag_['ranking']
	custome =	ag_['custome']

	#	Buscamos en la antigua y actualizamos
	agroupations.update_one({'id_':id_}, {'$set':{'ranking':ranking, 'custome':custome}})'''
'''
#	Buscamos elementos duplicados
for ag in agroupations.find():
	id_ 	=	ag['id_']

	items 	=	[]
	for ag in agroupations.find({'id_':id_}):
		items.append(ag)
	if len(items) != 1:
		print(items)'''