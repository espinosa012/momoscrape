from urllib.request import urlopen 
from urllib.error 	import HTTPError
from bs4 			import BeautifulSoup
from pymongo 		import	MongoClient

from urllib.request import 	urlopen 
from urllib.error 	import 	HTTPError
from bs4 			import 	BeautifulSoup
from pymongo 		import	MongoClient

import 				os
import 				wget
import 				requests
#	Base de datos
client  			= 	MongoClient('localhost', 27017)
momodb				=	client.momodb
agroupations		=	momodb.agroupations
agroupations_		=	momodb.agroupations_
authors_components	=	momodb.authors_components
	

def get_agroupation(id_):
	url 	=	'http://elbuscadordelfalla.com/CarnavalCadiz/Agrupacion/{}/'.format(id_)
	# 	BeautifulSoap
	ebdf 	=	urlopen(url)
	soup 	=	BeautifulSoup(ebdf, 'html.parser')

	agroupation 	=	{
		'id_'				:id_,
		'name'				:'',
		'year'				:'',
		'modality'			:'',
		'cal'				:'',
		'origin'			:'',
		'tipo'				:'',
		'previous'			:'',
		'img'				:bool(),
		
		'authors'			:[],
		'components'		:[],	
	}

	#	name
	try:
		agroupation['name']	=	soup.find('h3').string.strip().title().replace('Cadiz', 'Cádiz')
	except:
		raise Exception('Agroupation {} not found'.format(id_))


	basic_info 				=	soup.find_all('div',{'class':'card-body'})[0].find_all('div', {'class':'form-group'})

	#	Basic info
	agroupation['year'] 	= 	basic_info[0].find('label', {'class':'form-control'}).string.strip()
	agroupation['modality'] = 	basic_info[1].find('label', {'class':'form-control'}).string.strip()
	agroupation['cal'] 		= 	basic_info[2].find('label', {'class':'form-control'}).string.strip().title()
	try:
		agroupation['origin'] 	= 	basic_info[3].find('label', {'class':'form-control'}).string.strip()
	except:
		pass
	agroupation['tipo'] 	= 	basic_info[4].find('label', {'class':'form-control'}).string.strip()
	try:
		agroupation['previous']	= 	int(basic_info[5].find('a')['href'].split('/')[-2])
	except:
		pass

	'''
	print(agroupation)
	print(authors_components.find_all('div', {'class':'media-body'}))
	input()

	#	Obtenemos los componentes
	for ac in authors_components.find_all('div', {'class':'media-body'}):
		id_ 	=	ac.find('a')['href'].split('/')[-2]
		role	=	ac.find('li').string.strip()
		agroupation['authors_components'][id_]	=	role

	agroupations_.insert_one(agroupation)
	print(agroupation['name'])
	'''
	return agroupation



def get_soup(id_):
	url 	=	'http://elbuscadordelfalla.com/CarnavalCadiz/Agrupacion/{}/'.format(id_)
	# 	BeautifulSoap
	ebdf 	=	urlopen(url)
	return BeautifulSoup(ebdf, 'html.parser')





def set_agroupation_authors():
	for ag in agroupations_.find():
		try:
			authors 	=	scrape_authors(ag['id_'])
			agroupations_.update_one({'id_':ag['id_']}, {'$set':{'authors':authors}})
		except:
			print('Authors error: ', ag['id_'])




def set_agroupations_components():
	for ag in agroupations_.find():
		try:
			components 	=	scrape_components(ag['id_'])
			agroupations_.update_one({'id_':ag['id_']}, {'$set':{'components':components}})
		except:
			print('Compnents error: ', ag['id_'])



def scrape_authors(id_):
	authors_list=	[]

	soup 		=	get_soup(id_)
	components 	=	soup.find_all('div',{'class':'card-body'})[1].find_all('div', {'class':'media-body'})

	authors_roles 	=	['Letra', 'Música']
	for c in components:
		role	=	c.find('li').string.strip()

		for ar in authors_roles:
			if ar in role:
				authors_list.append({
					'id_':c.find('a')['href'].split('/')[-2],
					'role':role
				}) 
				break

	return authors_list



def scrape_components(id_):
	components_list 	=	[]

	url 	=	'http://elbuscadordelfalla.com/CarnavalCadiz/Agrupacion/{}/'.format(id_)
	# 	BeautifulSoap
	ebdf 	=	urlopen(url)
	soup 	=	BeautifulSoup(ebdf, 'html.parser')

	components 			=	soup.find_all('div',{'class':'card-body'})[1].find_all('div', {'class':'media-body'})

	components_roles 	=	 ['Guitarra', 'Dirección', 'Caja', 'Bombo', 'Componente']
	for c in components:
		role	=	c.find('li').string.strip()

		for cr in components_roles:
			if cr in role:
				components_list.append({
					'id_':c.find('a')['href'].split('/')[-2], 
					'role':role
				})



	#	Devuelve una lista de diccionarios {'id_':comp_id, 'role':comp_role}

	return components_list




















def get_agroupation_image(id_):
	url 	=	'http://elbuscadordelfalla.com/CarnavalCadiz/Agrupacion/{}/'.format(id_)
	ebdf 	=	urlopen(url)
	soup 	=	BeautifulSoup(ebdf, 'html.parser')

	try:
		agroupation 	=	agroupations_.find_one({'id_':id_})
	except:
		raise Exception('agroupation not found in collection')

	try:
		#	Obtenemos la imagen del sitio web
		img_src 	=	soup.findAll('div', {'class':'col-md-6'})[1].find('img')['src']
		#img_src 	=	'https://www.elbuscadordelfalla.com{}'.format(soup.find('div', {'class':'container body-content'}).find('img')['src'])	
		download_agroupation_image(img_src, id_)
		agroupation['img']			=	True		
	except Exception as e:
		if 'no_image' == str(e):
			agroupation['img'] 	=	False
		else:
			raise Exception('Exception downloading image for author: {}'.format(id_))


def download_agroupation_image(img_src, id_):
	image_url 	=	'https://elbuscadordelfalla.com{}'.format(img_src)
	directory 	= 	os.path.join('../img/agroupations/', '{}.jpg'.format(id_))
	if 'sin_imagen' not in img_src:
		wget.download(image_url, directory, bar=None)
	else:
		raise Exception('no_image')



def complete_database():
	#	Obtenemos las ids del fichero
	ids 	=	get_remaining_agroupations()

	#	Buscamos documento en la antigua base de datos
	for id_ in ids:
		try:
			try:
				old 	=	agroupations.find_one({'id_':str(id_)})
			except:
				raise Exception('agroupation not found in old db: {}'.format(id_))
				
			print(old['name'], old['year'])

			old['id_']		=	int(old['id_'])
			old['image']	=	False

			try:
				agroupations_.insert_one(old)
			except:
				raise Exception('error inserting doc in new collection')

		except Exception as e:
			print(e)


def get_remaining_agroupations():
	file 	=	open('agrerror.txt', 'r')
	lines 	=	file.readlines()
	ids 	=	[]
	for line in lines:
		ids.append(int(line.split(':')[1].strip()))

	return ids


def set_images():	

	for ag in agroupations_.find():
		img 	=	ag['image']
		if img:
			pass
		else:
			try:
				print('getting image for: {}'.format(ag['id_']))
				get_agroupation_image(ag['id_'])
			except Exception as e:
				print('error ({}) : {}'.format(ag['id_'], e))
			
	'''
	try:
		get_agroupation_image(ag['id_'])
	except:
		print('error: {}'.format(ag['id_']))
	'''	
	

def fill_db():
	#	Agroupations
	for i in range(1307, 8000):
		try:
			agroupations_.insert_one(get_agroupation(i))
		except:
			print('Error: ', i)



set_agroupation_authors()

#set_images()

'''
	for it in os.listdir('../img/agroupations/'):
		try:
			id_ 	=	int(it.split('.')[0])
			ag 		= agroupations_.find_one({'id_':id_})
			if not ag['image']:
				agroupations_.update_one({'id_':id_}, {'$set':{'image':True}})
				print(ag['name'], ag['image'])
		except Exception as e:
			#print('error: {}'.format(ag['id_']))
			print('error: {}'.format(e))

	'''
#agr img: vamos por 6906 