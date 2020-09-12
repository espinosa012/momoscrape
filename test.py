from scrape_agroupations import *
from scrape_authors import *

ac 	=	get_author_component(1593)
download_author_component_image(ac['img'], ac['id_'])
print(ac)