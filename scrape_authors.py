import	os
import	wget

from 	urllib.request 						import 	urlopen 
from 	bs4 								import 	BeautifulSoup
from 	pymongo 							import	MongoClient

#	Base de datos
client  			= 	MongoClient('localhost', 27017)
momodb				=	client.momodb
agroupations		=	momodb.agroupations
authors_components	=	momodb.authors_components


def get_soup(id_):
	url 	=	'http://elbuscadordelfalla.com/CarnavalCadiz/Autor/{}/'.format(id_)
	# 	BeautifulSoap
	ebdf 	=	urlopen(url)
	return BeautifulSoup(ebdf, 'html.parser')


def get_author_component(id_):
	soup =	get_soup(id_)
	
	#	Documento de la colección de autores/componentes:
	author_component 	=	{
		'id_'			:id_,
		'name'			:'',
		'nickname'		:'',
		'origin'		:'',
		'antifaz'		:None,	#	Para autores con antifaz, aparecerá el año en str
		'agroupations'	:[],
		'img'			:None	
	}
	try:
		author_component['name'] 	=	soup.find_all('h3')[0].string.strip()
	except:
		raise Exception('author not found ({})'.format(id_))
	
	basic_info 			=	soup.find_all('div',{'class':'card'})[0].find_all('div',{'class':'form-group'})
	agroupations_info	=	soup.find_all('div',{'class':'card mt-3'})[0]

	author_component['nickname'] 	=	basic_info[0].find('label', {'class':'form-control'}).string.strip()
	author_component['origin']		=	basic_info[1].find('label', {'class':'form-control'}).string.strip()
	
	# antifaz de oro:
	try:
		author_component['antifaz']	=	basic_info[2].find('label', {'class':'form-control'}).string.strip()	
	except:
		pass	
	
	author_component['agroupations']	=	get_agroupations(soup)
	#	Algunos autores/componentes no tienen imagen
	try:
		author_component['img']	=	get_author_component_image_url(soup)
	except:
		pass
	return author_component


def get_author_component_image_url(soup):
		img_src	=	soup.find('img', {'class':'img-fluid'})['src']
		return 'https://www.elbuscadordelfalla.com{}'.format(img_src)


def get_agroupations(soup):
	#	Devuelve una lista de items {'agroupation_id', 'role'} 
	agroupations 	=	[]

	agroupations_info	=	soup.find_all('div',{'class':'card mt-3'})[0]
	for a in agroupations_info.find_all('a'):
		try:
			agroupation_id 	=	a['href'].split('/')[-2]

			#	Para determinar el rol del autor/componente en cada una de las agrupaciones, necesita buscar la correspondencia en la base de datos de agrupaciones.
			#	En caso de que no exista base de datos de agrupaciones, dejará el campo 'role' vacío.
			try:
				role 			=	agroupations.find_one({'id_':agroupation_id}, {'authors_components'})['authors_components'][str(id_)]	
				agroupations.append({'agroupation':agroupation_id, 'role':role})
			except:
				agroupations.append({'agroupation':agroupation_id, 'role':''})
		except:
			print('Could not get agroupation for author: {}'.format(id_))

	return agroupations

def download_author_component_image(img_url, id_, img_path='.'):
	#	img_path: ruta donde se descargará la imagen
	#	img_url: valor del campo imagen del documento agroupation
	#	El nombre del fichero de imagen será el campo id_ del documento agroupation
	directory 	= 	os.path.join(img_path, '{}.jpg'.format(id_))
	if 'sin_imagen' not in img_url:
		wget.download(img_url, directory, bar=None)
	else:
		raise Exception('No se pudo descargar la imagen (id_: {})'.format(id_))

def save_author_component(author_component):
	#	Recibe un diccionario con la información de la agrupación y lo almacena en una base de datos Mongo en el servidor local (necesita MongoDB para funcionar)
	client  			= 	MongoClient('localhost', 27017)
	authors_comp_coll	=	client.momodb.authors_components

	try:
		authors_comp_coll.insert_one(author_component)
	except Exception as e:
		print('No se puedo guardar en base de datos el autor/componente con id {}'.format(author_component['id_']))