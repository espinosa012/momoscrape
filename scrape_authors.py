from    selenium                            import 	webdriver
from    selenium.webdriver.support.wait     import 	WebDriverWait
from    selenium.webdriver.chrome.options   import 	Options
from 	selenium.webdriver.common.keys 		import 	Keys
from 	selenium.webdriver.common.proxy 	import 	Proxy, ProxyType
from 	selenium.webdriver.support 			import 	expected_conditions as EC 	# available since 2.26.0
from 	selenium.webdriver.support.ui 		import 	WebDriverWait
from 	selenium.webdriver.common.by 		import 	By
from 	selenium.webdriver.support.ui 		import 	WebDriverWait 				# available since 2.timeout.0
from 	selenium.webdriver.support 			import 	expected_conditions as EC 
from 	urllib.request 						import 	urlopen 
from 	urllib.error 						import 	HTTPError
from 	bs4 								import 	BeautifulSoup
from 	pymongo 							import	MongoClient

import 				os
import 				wget
import 				requests

#	Base de datos
client  			= 	MongoClient('localhost', 27017)
momodb				=	client.momodb
agroupations		=	momodb.agroupations
authors_components	=	momodb.authors_components_
old_authors_components	=	momodb.authors_components
#	Colección para guardar la id de los autores que no tengan relleno el campo agroupations
no_agroupations 	=	momodb.no_agroupations
#	Colección para guardar la id de los autores cuyo scrape hay aoriginado error
authors_error 		=	momodb.authors_error
image_error 		=	momodb.image_error

def rescrape_with_selenium():
	#	Obtenemos el array de ids con los autores que queremos scrapear
	#	Definimos el driver
	driver 		= 	webdriver.Firefox()
	#	Iteramos las ids
	for i in range(7267, 8500):
		try:
			driver.get('https://www.elbuscadordelfalla.com/CarnavalCadiz/Autor/{}/'.format(i))
			#	Esperamos que la págna termine de cargar
			WebDriverWait(driver,20).until(EC.presence_of_element_located((By.CLASS_NAME, "card")))	
		except Exception as e:
			raise Exception('Exception with driver: {}'.format(e))
		
		print('getting source')
		ac 	=	get_author_component(i, html_content=driver.page_source)
		authors_components.insert_one(ac)
		print(ac['name'])

		input()

	return html_content

'''
		try:
			ac 	=	get_author_component(i, html_content=driver.page_source)
			authors_components.insert_one(ac)
			print(ac['name'])

		except Exception as e:
			print(e)
			if 'author not found' in str(e):
				pass
			elif 'Could not get agroupation for author' in str(e):
				authors_error.insert_one({'id_':i})
			elif 'Exception downloading image' in str(e):
				image_error.insert_one({'id_':i})
			elif 'no_agroupations' in str(e):			 
				no_agroupations.insert_one({'id_':i})
			else:
				#	Probablemente error de conexión remota
				print(e)
				authors_error.insert_one({'id_':i})
'''









def get_author_component(id_, html_content=None):
	#	BeautifulSoap
	if not html_content:
		url 	= 	'https://www.elbuscadordelfalla.com/CarnavalCadiz/Autor/{}/'.format(id_)
		try:
			req 	= 	requests.get(url)
			soup 	= 	BeautifulSoup(req.content, 'html.parser')
		except Exception as e:
			raise(e)
	else:
		soup 	=	BeautifulSoup(html_content, 'html.parser')

	#	Documento de la colección de autores/componentes:
	author_component 	=	{
		'id_'			:id_,
		'name'			:'',
		'nickname'		:'',
		'origin'		:'',
		'antifaz'		:'',
		'agroupations'	:{},
		'img'			:None	
	}

	try:
		author_component['name'] 	=	soup.find_all('h3')[0].string.strip()
	except:
		raise Exception('author not found ({})'.format(id_))

	#	Obtenemos la info de las 2 cards
	basic_info 			=	soup.find_all('div',{'class':'card'})[0].find_all('div',{'class':'form-group'})
	agroupations_info	=	soup.find_all('div',{'class':'card mt-3'})[0]

	author_component['nickname'] 	=	basic_info[0].find('label', {'class':'form-control'}).string.strip()
	author_component['origin']		=	basic_info[1].find('label', {'class':'form-control'}).string.strip()
	#	Si antifaz de oro:
	try:
		author_component['antifaz']	=	basic_info[2].find('label', {'class':'form-control'}).string.strip()	
	except:
		pass

	#	Obtenemos el array de agrupaciones
	for a in agroupations_info.find_all('a'):
		try:
			agroupation_id 	=	a['href'].split('/')[-2]
			try:
				role 			=	agroupations.find_one({'id_':agroupation_id}, {'authors_components'})['authors_components'][str(id_)]	
				author_component['agroupations'][agroupation_id] 	=	role		
			except:
				print('could not get role')
		except:
			print('Could not get agroupation for author: {}'.format(id_))
			

	try:
		#	Obtenemos la imagen del sitio web
		img_src 	=	'https://www.elbuscadordelfalla.com{}'.format(soup.find('div', {'class':'container body-content'}).find('img')['src'])	
		download_author_image(img_src, id_)
		author_component['img']			=	True		

	except Exception as e:
		if 'no_image' == str(e):
			author_component['img'] 	=	False
		else:
			raise Exception('Exception downloading image for author: {}'.format(id_))

	
	if not author_component['agroupations']:
		raise Exception('no agroupations: {}'.format(id_))

	return author_component



def download_author_image(img_src, id_):
	directory 	= 	os.path.join('../img/authors_components/', '{}.jpg'.format(id_))
	if 'sin_imagen' not in img_src:
		wget.download(img_src, directory, bar=None)
	else:
		raise Exception('no_image')



def fulfill_database():
	#for error in image_error.find():
	#for error in no_agroupations.find():
	for i in get_remaining_authors():
		try:
			ac 	=	get_author_component(i)
			authors_components.insert_one(ac)
			print(ac['name'])

		except Exception as e:
			if 'author not found' in str(e):
				pass
			elif 'Could not get agroupation for author' in str(e):
				authors_error.insert_one({'id_':i})
			elif 'Exception downloading image' in str(e):
				image_error.insert_one({'id_':i})
			elif 'no_agroupations' in str(e):			 
				no_agroupations.insert_one({'id_':i})
			else:
				#	Probablemente error de conexión remota
				print(e)
				authors_error.insert_one({'id_':i})

def get_remaining_authors():
	file 	=	open('rescrape.txt', 'r')
	lines 	=	file.readlines()
	ids 	=	[]
	for line in lines:
		ids.append(int(line.split(':')[1].strip()))

	return ids
		

rescrape_with_selenium()