import 				os
import 				wget

from urllib.request import urlopen 
from bs4 			import BeautifulSoup
from pymongo 		import MongoClient

def get_soup(id_):
	url 	=	'http://elbuscadordelfalla.com/CarnavalCadiz/Agrupacion/{}/'.format(id_)
	# 	BeautifulSoap
	ebdf 	=	urlopen(url)
	return BeautifulSoup(ebdf, 'html.parser')


def get_agroupation(id_):
	soup 	= 	get_soup(id_)

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
		agroupation['tipo'] 	= 	basic_info[4].find('label', {'class':'form-control'}).string.strip()
		agroupation['previous']	= 	int(basic_info[5].find('a')['href'].split('/')[-2])
	except:
		pass

	agroupation['authors']		=	scrape_authors(id_, soup)
	agroupation['components']	=	scrape_components(id_, soup)
	
	#	Algunas agrupaciones no tienen imágenes
	try:
		agroupation['img']			= 	get_agroupation_image_url(soup)
	except:
		pass
	return agroupation


def scrape_authors(id_, soup):
	authors_list=	[]

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



def scrape_components(id_, soup):
	components_list 	=	[]

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


def get_agroupation_image_url(soup):
		img_src	=	soup.findAll('div', {'class':'col-md-6'})[1].find('img')['src']
		return 'https://www.elbuscadordelfalla.com{}'.format(img_src)




def download_agroupation_image(img_url, id_, img_path='.'):
	#	img_path: ruta donde se descargará la imagen
	#	img_url: valor del campo imagen del documento agroupation
	#	El nombre del fichero de imagen será el campo id_ del documento agroupation
	directory 	= 	os.path.join(img_path, '{}.jpg'.format(id_))
	if 'sin_imagen' not in img_url:
		wget.download(img_url, directory, bar=None)
	else:
		raise Exception('No se pudo descargar la imagen (id_: {})'.format(id_))




def save_agroupation(agroupation):
	#	Recibe un diccionario con la información de la agrupación y lo almacena en una base de datos Mongo en el servidor local (necesita MongoDB para funcionar)
	client  			= 	MongoClient('localhost', 27017)
	agroupations_coll	=	client.momodb.agroupations

	try:
		agroupations_coll.insert_one(agroupation)
	except Exception as e:
		print('No se puedo guardar en base de datos la agrupación con id {}'.format(agroupation['id_']))

